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

This script creates a plain vanilla version of a model.

It then runs two backtests of that model: one backtest
using games from a single team, and one backtest using 
all games and all teams.

The model prepare() method ensures the model has all the
data it needs, or it scrapes the web to obtain it.

The backtest() method iterates through each game.
For each game, it passes game information to the model,
which uses that input data plus data obtained in the
prepare() method to return predictions about the score.

The backtest() method assembles a dataframe with
information about the real and predicted score
for each of the games, but does no further analysis.

The backtest() method can return the dataframe itself,
or you can do nothing else, and the dataframe will be
dumped to a file on disk for fast reloading later.
"""


DATADIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))


def backtest():
    # Create a model with default parameter set
    model_params = {'data_directory': DATADIR}
    model = NCAABModel(model_params)

    # Run a backtest for a single team
    backtester = Backtester(model, start_date="2025-01-18", end_date="2025-01-22", team="Arizona")
    backtester.prepare()
    backtester.backtest(test_name="backtest_arizona")

    ## # Run a backtest for all teams
    ## backtester = Backtester(model=model, start_date="2025-01-21", end_date="2025-01-22")
    ## backtester.prepare()
    ## backtester.backtest(test_name="backtest_all")


if __name__=="__main__":
    backtest()
