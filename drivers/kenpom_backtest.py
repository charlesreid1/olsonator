import sys
import os
import json
import glob

# hack
pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, pkg_root)

from pkg.model import KenpomNCAABModel
from pkg.backtester import KenpomBacktester


"""
Backtest thte Olsonator NCAA basketball model using Kenpom numbers

This script creates a Kenpom version of a model and backtests it.
"""


DATADIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))


def backtest():
    # Create a model with default parameter set
    model_params = {
        'data_directory': DATADIR,
        'quiet': True,
        'print_stats': True
    }
    # The Kenpom model is mostly similar to the regular NCAA model,
    # but overrrides functionality for obtaining off/def ratings
    # to get it from the right file and format.
    model = KenpomNCAABModel(model_params)

    # Need a Kenpom backtester that creates a Kenpom scraper
    backtester = KenpomBacktester(model, start_date="2024-11-04", end_date="2025-02-01")
    backtester.prepare()
    backtester.backtest(test_name="backtest_all")


if __name__=="__main__":
    backtest()
    #import cProfile
    #cProfile.run('backtest()')

