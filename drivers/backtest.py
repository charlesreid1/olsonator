import sys
import os
import json
import glob

# hack
pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, pkg_root)

from pkg.model import NCAABModel
from pkg.backtester import Backtester


"""
Backtest the Olsonator NCAA basketball model

This script creates a plain vanilla version of a model,
and back-tests it.

The model prepare() method ensures the model has all the
data it needs, or it scrapes the web to obtain it.

The backtest() method iterates through each game.
For each game, it passes game information to the model,
which uses that input data plus data obtained in the
prepare() method to return predictions about the score.

The backtest() method assembles a JSON file with results
for each game for later analysis, plus it prints a brief
statistics summary table, so you don't have to analyze the JSON.
"""


DATADIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))


def backtest():
    # Create a model with default parameter set
    model_params = {
        'data_directory': DATADIR,
        'quiet': False,
        'print_stats': True
    }
    model = NCAABModel(model_params)

    # Run a backtest for all teams
    backtester = Backtester(model, start_date="2024-11-04", end_date="2025-02-01")
    backtester.prepare()
    backtester.backtest(test_name="backtest_all")


if __name__=="__main__":
    backtest()
    #import cProfile
    #cProfile.run('backtest()')
