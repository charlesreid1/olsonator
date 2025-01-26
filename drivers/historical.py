import sys
import os
import json
import glob

# hack
pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, pkg_root)

from pkg.model import NCAABModel
from pkg.harness import ModelDataHarness


"""
Make a prediction about a game 10 years ago with the Olsonator NCAA basketball model

This demonstrates the flexibility of the ModelDataHarness class.
"""


DATADIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))


def harness():
    # Create a model with default parameter set
    model_params = {'data_directory': DATADIR}
    model = NCAABModel(model_params)

    # https://www.teamrankings.com/ncaa-basketball/matchup/cougars-broncos-2015-01-01
    basic_game = {
        'game_date': '2015-01-01', 
        'game_time': '1400 PST', 
        'home_team': 'Santa Clara',
        'away_team': 'BYU',
        'neutral_site': False
    }

    # Use the ModelDataHarness to download 2015 NCAAB data
    print("Preparing ModelDataHarness...")
    harness = ModelDataHarness(model_params)
    harness.prepare(basic_game)

    # Make the prediction
    away_points, home_points = model.predict(basic_game)



if __name__=="__main__":
    harness()

