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
Make a prediction with the Olsonator NCAA basketball model

This script creates a plain vanilla version of a model.
It assembles a dictionary with game information for a
few example games, then shows how to make a prediction
for those games using the model.

This demonstrates the use of the ModelDataHarness class.
"""


DATADIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))


def harness():
    # Create a model with default parameter set
    model_params = {'data_directory': DATADIR}
    model = NCAABModel(model_params)

    #basic_game = {
    #    'game_date': '2025-01-11', 
    #    'game_time': '0900 PST', 
    #    'home_team': 'Duke Blue Devils', 
    #    'away_team': 'Notre Dame Fighting Irish', 
    #    'neutral_site': False
    #}
    basic_game = {
        'game_date': '2025-01-16', 
        'game_time': '2000 PST', 
        'home_team': 'Gonzaga Bulldogs',
        'away_team': 'Oregon State Beavers',
        'neutral_site': False
    }

    # If we try to make a prediction, the model assumes that
    # it will be able to find all the data it needs.
    # Unfortunately, if data for this date and these teams
    # is not available, the model prediction will fail
    if False:
        try:
            model.predict(basic_game)
        except FileNotFoundError:
            pass

    # To ensure the data we need is downloaded before calling
    # predict(), we need to use a ModelDataHarness class.
    # We can pass the game we are going to make a prediction for
    # to the prepare() method of that class, and it will determine
    # what data it needs to download, and download it.
    print("Preparing ModelDataHarness...")
    harness = ModelDataHarness(model_params)
    harness.prepare(basic_game)

    # The next time we make a model prediction for this game,
    # the data will be available on disk and the model will have
    # no problem.
    away_points, home_points = model.predict(basic_game)
    print(f"{basic_game['away_team']} {away_points} - {home_points} {basic_game['home_team']}")

    # Note that the backtesting class handles the
    # creation of the ModelDataHarness under the hood,
    # since it gets more complicated with backtesting.


if __name__=="__main__":
    harness()

