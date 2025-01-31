import sys
import os
import json
import glob

# hack
pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, pkg_root)

from pkg.model import NCAABModel
from pkg.backtester import Backtester
from pkg.constants import CONFERENCES


"""
Backtest by Conference of the Olsonator NCAA basketball model
"""


CONFERENCE = "B12"

DATADIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))


def backtest():
    # Create a model with default parameter set
    model_params = {
        'data_directory': DATADIR,
        'quiet': True,
        'print_stats': True
    }
    model = NCAABModel(model_params)

    conf_teams = [k for k,v in CONFERENCES.items() if v == CONFERENCE]

    backtester = Backtester(model, start_date="2025-01-10", end_date="2025-01-23", teams=conf_teams)
    backtester.prepare()
    backtester.backtest(test_name=f"backtest_{CONFERENCE}")


if __name__=="__main__":
    backtest()


