import os
import json
import statistics

# Names are hard
from .names import (
    is_kenpom_team,
    is_donch_team,
    is_teamrankings_team,
    donch2kenpom, 
    kenpom2donch,
    donch2teamrankings,
    teamrankings2donch,
    normalize_to_teamrankings_names
)
from .constants import HOME_ADVANTAGE
from .utils import assert_required_keys_present
from .errors import ModelParameterException, ModelPredictException


class ModelBase(object):
    """
    Define a base class for a model.

    As of now, this is just for NCAAB,
    and there is only one NCAAB model,
    but that may change in future.

    Any Model should accept a dict of
    model parameters in its constructor.
    The most important model parameter
    is the data directory, which is where
    the model can find any data it needs
    for this game/date.
    """
    required_model_params = ['data_directory']

    required_game_params = [
        'game_date',
        'game_time',
        'home_team',
        'away_team',
        'neutral_site'
    ]

    def __init__(self, model_parameters = {}):
        self.model_parameters = model_parameters

        try:
            assert_required_keys_present(model_parameters, self.required_model_params)
        except KeyError:
            msg = f"Error: missing a required key in model inputs: {self.required_model_params}"
            raise ModelParameterException(msg)

    def predict(self, game_parameters):
        """
        Every Model should have a predict() method,
        which accepts a dict of game input parameters:
        - game_date
        - game_time
        - home_team
        - away_team
        - neutral_site yes/no

        The predict() method should return a tuple:
        (predicted_away_points, predicted_home_points)
        """
        return NotImplemented


class NCAABModel(ModelBase):
    """
    Define a class for an NCAAB basketball game.
    """
    def _get_fpath_json(self, prefix, stamp):
        """
        Get the filename + path of the JSON file containing
        team raning data
        
        prefix should be a stat name (like tempo)
        stamp should be a YYYYMMDD datestamp
        """
        fname = prefix + "_" + stamp + ".json"
        trpath = os.path.join(self.model_parameters['data_directory'], 'teamrankings')
        jdatadir = os.path.join(trpath, 'json')
        fpath = os.path.join(jdatadir, fname)
        return fpath

    def _get_avg_template_func(self, game_parameters, fpath_prefix, dimension):
        """
        Template function for fetching data,
        computing the average of a dimension,
        and returning it.
        """
        game_date = game_parameters['game_date'].replace("-", "")
        with open(self._get_fpath_json(fpath_prefix, game_date), 'r') as f:
            dat = json.load(f)

        # JSON object just loaded is a list of dictionaries,
        # with each dimension prefixed by "tempo" or "off_eff" or etc
        # [{  'tempo_team': 'Drake',
        #     'tempo_rank': 120,
        #     'tempo_2024': 
        #     'tempo_last3': 
        #     'tempo_last1': 
        #     'tempo_home': 
        #     'tempo_away': 
        # }, ..., ]

        # Use whole season rating
        # This is a first pass approach, modify later to try to improve the model
        m = []
        for item in dat:
            m.append(item[dimension])
        return statistics.mean(m)

    def get_avg_tempo(self, gp):
        game_date = gp['game_date'].replace("-", "")
        year = int(game_date[0:4]) - 1
        return self._get_avg_template_func(gp, "tempo", f"tempo_{year}")

    def get_avg_off_eff(self, gp):
        game_date = gp['game_date'].replace("-", "")
        year = int(game_date[0:4]) - 1
        return self._get_avg_template_func(gp, "off_eff", f"off_eff_{year}")

    def get_avg_def_eff(self, gp):
        game_date = gp['game_date'].replace("-", "")
        year = int(game_date[0:4]) - 1
        return self._get_avg_template_func(gp, "def_eff", f"def_eff_{year}")

    def _get_school_template_func(self, game_parameters, school, fpath_prefix, dimension):
        """
        Template function for fetching data,
        getting the dimension value for a given school,
        and returning it.
        """
        game_date = game_parameters['game_date'].replace("-", "")
        with open(self._get_fpath_json(fpath_prefix, game_date), 'r') as f:
            dat = json.load(f)
        for item in dat:
            if item[f'{fpath_prefix}_team']==school:
                return item[dimension]

    def get_school_tempo(self, gp, school):
        game_date = gp['game_date'].replace("-", "")
        year = int(game_date[0:4]) - 1
        return self._get_school_template_func(gp, school, "tempo", f"tempo_{year}")

    def get_school_off_eff(self, gp, school):
        game_date = gp['game_date'].replace("-", "")
        year = int(game_date[0:4]) - 1
        return self._get_school_template_func(gp, school, "off_eff", f"off_eff_{year}")

    def get_school_def_eff(self, gp, school):
        game_date = gp['game_date'].replace("-", "")
        year = int(game_date[0:4]) - 1
        return self._get_school_template_func(gp, school, "def_eff", f"def_eff_{year}")

    def get_pct_adjustment(self, school_val, avg_val):
        """Return the tempo % adjustment for this school"""
        school_val_pct = 100*school_val/avg_val
        school_val_pct_add = school_val_pct - 100
        return school_val_pct_add

    def get_home_adjustment(self, game_parameters, away_points, home_points):
        """
        Adjust the given score for home court advantage.
        Returns tuple:
        (away_points, home_points)
        """
        # Currently using a very simple approach of giving home team +N points on the spread
        # But to keep the point total similar, we add/subtract N/2 from each side
        # (otherwise, introduces bias toward the over on over/under predictions)
        away_points -= HOME_ADVANTAGE/2.0
        home_points += HOME_ADVANTAGE/2.0
        return (away_points, home_points)

    def predict(self, game_parameters):
        """
        Given a dictionary of game parameters,
        load tempo/offensive/defensive data,
        make a prediction and return the score.
        
        Returns a tuple:
        (away_points, home_points)
        """
        try:
            assert_required_keys_present(game_parameters, self.required_game_params)
        except KeyError:
            msg = f"Error: missing a required key in game inputs: {self.required_game_params}"
            raise ModelPredictException(msg)

        # Whatever names we were given, find our way to the teamrankings ones
        away_team = normalize_to_teamrankings_names(game_parameters['away_team'])
        home_team = normalize_to_teamrankings_names(game_parameters['home_team'])

        game_descr = away_team + " @ " + home_team
        print(f"Generating model prediction for {game_descr}")

        # Tempo gives the rate at which a team has possession of the ball
        # Offensive/defensive efficiency is the rate at which a team gets/gives up points when they have possession
        # These combine to give us expected points scored
        
        # ----------
        # Part 1 - calculate league average tempo/off/def
        avg_tempo   = self.get_avg_tempo(game_parameters)

        away_tempo = self.get_school_tempo(game_parameters, away_team)
        away_tempo_pct_add = self.get_pct_adjustment(away_tempo, avg_tempo)

        home_tempo = self.get_school_tempo(game_parameters, home_team)
        home_tempo_pct_add = self.get_pct_adjustment(home_tempo, avg_tempo)

        # Additive, not multiplicative
        e_tempo = (100 + away_tempo_pct_add + home_tempo_pct_add)*avg_tempo/100

        # ----------
        # Part 2 - calculate expected offense/defense output, get adjusted output

        # Offense
        avg_off_eff = 100*self.get_avg_off_eff(game_parameters)

        away_off_eff = 100*self.get_school_off_eff(game_parameters, away_team)
        away_off_eff_pct_add = self.get_pct_adjustment(away_off_eff, avg_off_eff)

        home_off_eff = 100*self.get_school_off_eff(game_parameters, home_team)
        home_off_eff_pct_add = self.get_pct_adjustment(home_off_eff, avg_off_eff)

        # Defense
        avg_def_eff = 100*self.get_avg_def_eff(game_parameters)

        away_def_eff = 100*self.get_school_def_eff(game_parameters, away_team)
        away_def_eff_pct_add = self.get_pct_adjustment(away_def_eff, avg_def_eff)

        home_def_eff = 100*self.get_school_def_eff(game_parameters, home_team)
        home_def_eff_pct_add = self.get_pct_adjustment(home_def_eff, avg_def_eff)

        # Defense efficiency = points allowed, so higher def percent add = more points allowed to opponent
        e_away_off_output = (100 + away_off_eff_pct_add + home_def_eff_pct_add)*avg_off_eff/100
        e_home_off_output = (100 + home_off_eff_pct_add + away_def_eff_pct_add)*avg_off_eff/100

        # ----------
        # Part 3 - get expected number of points for each team

        # away/home offensive output is expected number of points per 100 possessions
        # normalize by 100 to get points per possession
        # then multiply by tempo, which is expected number of possessions
        e_away_points = e_tempo*(e_away_off_output/100.0)
        e_home_points = e_tempo*(e_home_off_output/100.0)

        # -----------
        # Part 4 - modify expectd number of points for known factors

        # adjust for home court advantage
        e_away_points, e_home_points = self.get_home_adjustment(game_parameters, e_away_points, e_home_points)

        # TODO: travel effects

        # TODO: team-specific home court advantages

        return (round(e_away_points, 1), round(e_home_points, 1))

