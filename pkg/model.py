import os
import json

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

    def predict(self, game_parameters):
        try:
            assert_required_keys_present(game_parameters, self.required_game_params)
        except KeyError:
            msg = f"Error: missing a required key in game inputs: {self.required_game_params}"
            raise ModelPredictException(msg)

        game_descr = game_parameters['away_team'] + " @ " + game_parameters['home_team']
        game_date = game_parameters['game_date'].replace("-", "")

        print(f"Generating prediction for {game_descr}")

        # Load tempo, off_eff, def_eff
        with open(self._get_fpath_json("tempo", game_date), 'r') as f:
            tempo_json = json.load(f)
        with open(self._get_fpath_json("off_eff", game_date), 'r') as f:
            off_json = json.load(f)
        with open(self._get_fpath_json("def_eff", game_date), 'r') as f:
            def_json = json.load(f)

        # Might 
        import pdb; pdb.set_trace()
        a=0





