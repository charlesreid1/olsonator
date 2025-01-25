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
One-Team Backtest of the Olsonator NCAA basketball model

This script creates a plain vanilla version of a model,
and runs a backtest on a range of games.

This passes the "teams" keyword to the backtester,
which will only backtest games involving that team.
"""


DATADIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))


def backtest():
    # Create a model with default parameter set
    model_params = {'data_directory': DATADIR}
    model = NCAABModel(model_params)

    # Run a backtest for a single team
    backtester = Backtester(model, start_date="2025-01-10", end_date="2025-01-23", teams=["Arizona"])
    backtester.prepare()
    backtester.backtest(test_name="backtest_az")

    backtester = Backtester(model, start_date="2025-01-10", end_date="2025-01-23", teams=["Arizona", "Arizona St"])
    backtester.prepare()
    backtester.backtest(test_name="backtest_az2")

    backtester = Backtester(model, start_date="2025-01-10", end_date="2025-01-23", teams=["Tennessee", "Texas Tech"])
    backtester.prepare()
    backtester.backtest(test_name="backtest_tntxt")


if __name__=="__main__":
    backtest()
