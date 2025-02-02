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


DATADIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))


def backtest():
    # Create a model with default parameter set
    model_params = {
        'data_directory': DATADIR,
        'quiet': True,
        'print_stats': True
    }
    model = NCAABModel(model_params)

    confs = sorted(list(set(CONFERENCES.values())))

    print_teams(confs)
    do_backtests(confs, model)


def do_backtests(confs, model):
    for c in confs:
        conf_teams = [k for k,v in CONFERENCES.items() if v == c]
        backtester = Backtester(model, start_date="2024-11-04", end_date="2025-01-31", teams=conf_teams)
        backtester.prepare()
        backtester.backtest(test_name=f"backtest_{c}")


def print_teams(confs):

    print()
    for c in confs:
        conf_teams = [k for k,v in CONFERENCES.items() if v == c]
        print(f"{c} Conference:")
        for t in conf_teams:
            print(f" - {t}")
        print()



if __name__=="__main__":
    backtest()


