import os
import json
import statistics
from functools import cache
from geopy import distance
from tzfpy import get_tz

# Names are hard
from .teams import (
    is_kenpom_team,
    is_donch_team,
    is_teamrankings_team,
    donch2kenpom,
    kenpom2donch,
    donch2teamrankings,
    teamrankings2donch,
    normalize_to_teamrankings_names,
    normalize_to_donchess_names,
)
from .constants import (
    HOME_ADVANTAGE,
    GEO_LATLONG,
)
from .utils import (
    assert_required_keys_present,
    get_utc_offset_int,
)
from .errors import (
    ModelParameterException,
    ModelPredictException,
    TeamNotFoundException,
)


class ModelBase(object):
    """
    Define a base class for a model.
    (Currently just NCAA basketball)

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
    def get_avg_tempo(self, game_date):
        """Return the average tempo for entire league"""
        year = self._get_year(game_date)
        return self._get_avg_template_func(game_date, "tempo", f"tempo_{year}")

    def get_avg_off_eff(self, game_date):
        """Return the average offensive efficiency for entire league"""
        year = self._get_year(game_date)
        return self._get_avg_template_func(game_date, "off_eff", f"off_eff_{year}")

    def get_avg_def_eff(self, game_date):
        """Return the average defensive efficiency for entire league"""
        year = self._get_year(game_date)
        return self._get_avg_template_func(game_date, "def_eff", f"def_eff_{year}")

    def get_school_tempo(self, gp, school):
        """Return the tempo (posessions) for this season for this school"""
        game_date = gp['game_date'].replace("-", "")
        year = self._get_year(game_date)
        return self._get_school_template_func(gp, school, "tempo", f"tempo_{year}")

    ### def get_school_off_eff(self, gp, school):
    ###     """Return the offensive efficiency for this season for school"""
    ###     game_date = gp['game_date'].replace("-", "")
    ###     year = self._get_year(game_date)
    ###     return self._get_school_template_func(gp, school, "off_eff", f"off_eff_{year}")

    def get_school_off_eff(self, gp, school):
        """Return the offensive efficiency (blend of season average and last 3 average) for this school"""
        game_date = gp['game_date'].replace("-", "")
        year = self._get_year(game_date)
        seas_eff  = self._get_school_template_func(gp, school, "off_eff", f"off_eff_{year}")
        try:
            last3_eff = self._get_school_template_func(gp, school, "off_eff", "off_eff_last_3")
        except KeyError:
            last3_eff = seas_eff
        return 0.95*seas_eff + 0.05*last3_eff

    ### def get_school_def_eff(self, gp, school):
    ###     """Return the defensive efficiency for this season for this school"""
    ###     game_date = gp['game_date'].replace("-", "")
    ###     year = self._get_year(game_date)
    ###     return self._get_school_template_func(gp, school, "def_eff", f"def_eff_{year}")

    def get_school_def_eff(self, gp, school):
        """Return the defensive efficiency (blend of season average and last 3 average) for this school"""
        game_date = gp['game_date'].replace("-", "")
        year = self._get_year(game_date)
        seas_eff  = self._get_school_template_func(gp, school, "def_eff", f"def_eff_{year}")
        try:
            last3_eff = self._get_school_template_func(gp, school, "def_eff", f"def_eff_last_3")
        except KeyError:
            last3_eff = seas_eff
        return 0.95*seas_eff + 0.05*last3_eff

    def get_home_factor(self, game_parameters, away_points, home_points):
        """
        Adjust the given score for home court advantage.
        Takes tuple:
        (unadjusted_away_points, unadjusted_home_points)
        Returns tuple:
        (away_points, home_points)
        """
        # Currently using a very simple approach of giving home team +N points on the spread
        # But to keep the point total similar, we add/subtract N/2 from each side
        # (otherwise, introduces bias toward the over on over/under predictions)
        away_points -= HOME_ADVANTAGE/2
        home_points += HOME_ADVANTAGE/2
        return (away_points, home_points)

    def get_geotime_factor(self, game_parameters, away_points, home_points):

        if game_parameters['neutral_site']:
            # Skip, assume both teams equally affected
            return (away_points, home_points)

        # ---------------------------
        # Travel distance factors:

        # Get lat long and dist btwn
        away_latlong = GEO_LATLONG[normalize_to_donchess_names(game_parameters['away_team'])]
        home_latlong = GEO_LATLONG[normalize_to_donchess_names(game_parameters['home_team'])]
        dist = distance.distance(away_latlong, home_latlong).miles

        # Large travel distance factor:
        LARGE_DISTANCE_MODIFIER = 6.0
        # (Note: increasing this value sligtly increases MSE, but also increases W-L vs Vegas)
        # Home has edge if travel distance > 2000 miles
        if dist > 2000:
            away_points -= LARGE_DISTANCE_MODIFIER/2
            home_points += LARGE_DISTANCE_MODIFIER/2

        # Short distances (regional/state matchups):
        # Visitors have an edge (fan base is closer)
        # intense rivalries have 2x edge (draws local fans)
        # FL - TB/Jax/Mia
        # TX - Dal/Hou
        # Southeast - Atl/Car
        # LA - LAR/LAC
        # Southwest - LV/LA
        # Midwest - Ind/Cin
        # East - Phi, NY, Wash, NE, Bos, Bal, Buf
        #
        # Probably best handled by separate function looking for
        # matchup factors by identifying big rivalries, or using
        # GEO_CITIES to spot particular matchups in those regions

        # ---------------------------
        # Time zone factors:

        # Get the time zone
        away_tz = get_tz(*reversed(away_latlong))
        home_tz = get_tz(*reversed(home_latlong))

        # Now use the time zone to get UTC offset
        # The offset values will look like:
        # [far west] Hawaii  = 9 -> 4
        # [west] Los_Angeles = 8 -> 3
        # [mountain] Denver  = 7 -> 2
        # [central] Chicago  = 6 -> 1
        # [eastern] New_York = 5 -> 0
        away_offset = abs(get_utc_offset_int(away_tz))-5
        home_offset = abs(get_utc_offset_int(home_tz))-5

        # Number of hours difference in timezones btwn away/home
        # If offset diff is POSITIVE, home is more east and away is more west (away team is more disadvantaged)
        # If offset diff is NEGATIVE, home is more west and away is more east (away team is less disadvantaged)
        # If the magnitude is larger, then time difference effects are more likely
        offset_diff = away_offset - home_offset

        OFFSET_MODIFIER = 0.5

        if offset_diff > 0:
            away_points -= 2*offset_diff*OFFSET_MODIFIER/2
            home_points += offset_diff*OFFSET_MODIFIER/2
        else:
            away_points -= offset_diff*OFFSET_MODIFIER/2
            home_points += offset_diff*OFFSET_MODIFIER/2

        # Account for effects of early start/late start:

        # The game_time in game_parameters is always Pacific time
        start_hr = int(game_parameters['game_time'])//100

        # The two factors below (early start and late start) reduced accuracy and increased MSE??

        # If start <= 10 AM, penalize West (2) and Mountain teams (1)
        EARLYSTART_MODIFIER = 0.0
        if start_hr <= 10:
            # Early start: penalty is based on central time offset
            central_offset = 6
            central_dist = away_offset - central_offset
            if central_dist > 0:
                # central_dist is the multiplier that increases the modifier for more tzs
                away_points -= central_dist*(EARLYSTART_MODIFIER)/2
                home_points += central_dist*(EARLYSTART_MODIFIER)/2

        # If start >= 5 PM, penalize East (6) central (3) mountain (1)
        LATESTART_MODIFIER = 3.0
        if start_hr >= 17:
            # Late start: penalty is based on pacific time offset
            # Note that this factor/penalty is double the prior one
            pacific_offset = 8
            pacific_dist = 2*(pacific_offset - away_offset)
            if pacific_dist > 0:
                away_points -= pacific_dist*(LATESTART_MODIFIER)/2
                home_points += pacific_dist*(LATESTART_MODIFIER)/2

        # TODO: If we had info about both teams' prior game,
        # we could determine if second game on the road
        return (away_points, home_points)

    # def get_conf_adjustment(self, X):
    # - same division: +1 visitor
    # - diff conferences: +1 home

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
        # This may throw a TeamNotFoundException, catch it wherever we are calling predict()
        away_team = normalize_to_teamrankings_names(game_parameters['away_team'])
        home_team = normalize_to_teamrankings_names(game_parameters['home_team'])

        game_date = game_parameters['game_date'].replace("-", "")
        game_descr = away_team + " @ " + home_team

        # Tempo gives the rate at which a team has possession of the ball
        # Offensive/defensive efficiency is the rate at which a team gets/gives up points when they have possession
        # These combine to give us expected points scored

        # ----------
        # Part 1 - calculate league average tempo/off/def
        avg_tempo   = self.get_avg_tempo(game_date)

        away_tempo = self.get_school_tempo(game_parameters, away_team)
        away_tempo_pct_add = self._get_pct_adjustment(away_tempo, avg_tempo)

        home_tempo = self.get_school_tempo(game_parameters, home_team)
        home_tempo_pct_add = self._get_pct_adjustment(home_tempo, avg_tempo)

        # Additive, not multiplicative
        e_tempo = (100 + away_tempo_pct_add + home_tempo_pct_add)*avg_tempo/100

        # ----------
        # Part 2 - calculate expected offense/defense output, get adjusted output

        # Offense
        avg_off_eff = 100*self.get_avg_off_eff(game_date)

        away_off_eff = 100*self.get_school_off_eff(game_parameters, away_team)
        away_off_eff_pct_add = self._get_pct_adjustment(away_off_eff, avg_off_eff)

        home_off_eff = 100*self.get_school_off_eff(game_parameters, home_team)
        home_off_eff_pct_add = self._get_pct_adjustment(home_off_eff, avg_off_eff)

        # Defense
        avg_def_eff = 100*self.get_avg_def_eff(game_date)

        away_def_eff = 100*self.get_school_def_eff(game_parameters, away_team)
        away_def_eff_pct_add = self._get_pct_adjustment(away_def_eff, avg_def_eff)

        home_def_eff = 100*self.get_school_def_eff(game_parameters, home_team)
        home_def_eff_pct_add = self._get_pct_adjustment(home_def_eff, avg_def_eff)

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
        e_away_points, e_home_points = self.get_home_factor(game_parameters, e_away_points, e_home_points)

        # geography and timezone effects
        e_away_points, e_home_points = self.get_geotime_factor(game_parameters, e_away_points, e_home_points)

        # TODO: team-specific home court advantages

        if not ('quiet' in self.model_parameters and self.model_parameters['quiet'] is True):
            p = f"Generated model prediction for {game_parameters['game_date']}"
            if e_away_points > e_home_points:
                print(f"{p}: {away_team} {round(e_away_points,1)} - {round(e_home_points,1)} {home_team}")
            else:
                print(f"{p}: {home_team} {round(e_home_points,1)} - {round(e_away_points,1)} {away_team}")

        SPREAD_TOO_NARROW = 2
        SPREAD_TOO_WIDE = 20
        if abs(e_away_points-e_home_points) < SPREAD_TOO_NARROW:
            msg = f"Error: could not make prediction, spread is too narrow (< {SPREAD_TOO_NARROW})"
            raise ModelPredictException(msg)
        if abs(e_away_points-e_home_points) > SPREAD_TOO_WIDE:
            msg = f"Error: could not make prediction, spread is too wide (< {SPREAD_TOO_WIDE})"
            raise ModelPredictException(msg)

        return (round(e_away_points, 1), round(e_home_points, 1))


    # ----------------------------------------
    # Below are private utility/helper methods

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

    @cache
    def _get_avg_template_func(self, game_date, fpath_prefix, dimension):
        """
        Template function for fetching data,
        computing the average of a dimension,
        and returning it.
        """
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

        m = []
        for item in dat:
            if item[dimension] is not None:
                m.append(item[dimension])
        if len(m)>0:
            return statistics.mean(m)

    def _get_year(self, game_date):
        # Any game after August is part of the next season
        if int(game_date[4:6])>8:
            year = int(game_date[0:4])
        else:
            year = int(game_date[0:4]) - 1
        return year

    def _get_school_template_func(self, game_parameters, school, fpath_prefix, dimension):
        """
        Template function for fetching data, getting the
        dimension value for a given school, and returning it.
        """
        game_date = game_parameters['game_date'].replace("-", "")
        with open(self._get_fpath_json(fpath_prefix, game_date), 'r') as f:
            dat = json.load(f)
        for item in dat:
            if item[f'{fpath_prefix}_team']==school:
                if item[dimension] is not None:
                    return item[dimension]
        raise TeamNotFoundException(f"Team {school} on date {game_date} could not be found")

    def _get_pct_adjustment(self, school_val, avg_val):
        """Return the tempo % adjustment for this school"""
        if school_val is None:
            return 0
        school_val_pct = 100*school_val/avg_val
        school_val_pct_add = school_val_pct - 100
        return school_val_pct_add
