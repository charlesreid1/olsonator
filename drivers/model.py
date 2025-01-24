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

    basic_game = {
        'game_date': '2025-01-11', 
        'game_time': '0900 PST', 
        'home_team': 'Duke Blue Devils', 
        'away_team': 'Notre Dame Fighting Irish', 
        'neutral_site': False
    }

    # If we try to make a prediction, the model assumes that
    # it will be able to find all the data it needs.
    # Unfortunately, if data for this date and these teams
    # is not available, the model prediction will fail
    try:
        model.predict(basic_game)
    except FileNotFoundError:
        pass

    # To ensure we have the data we need downloaded already,
    # we need to use a ModelDataHarness class.
    # We can pass the game we are going to make a prediction for
    # to the prepare() method of that class, and it will determine
    # what data it needs to download, and download it.
    harness = ModelDataHarness(model_params)
    harness.prepare(basic_game)

    # The next time we make a model prediction for this game,
    # the data will be available on disk and the model will have
    # no problem.
    #model.predict(basic_game)


if __name__=="__main__":
    harness()

