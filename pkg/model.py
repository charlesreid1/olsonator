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
    def predict(self, game_parameters):

        try:
            assert_required_keys_present(game_parameters, self.required_game_params)
        except KeyError:
            msg = f"Error: missing a required key in game inputs: {self.required_game_params}"
            raise ModelPredictException(msg)


