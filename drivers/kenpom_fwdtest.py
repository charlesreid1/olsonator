import sys
import os
import json
import glob

# hack
pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, pkg_root)

from pkg.model import KenpomNCAABModel
from pkg.fwdtester import Forwardtester


"""
Forward test the Olsonator NCAA basketball model

This script creates a model, and runs forward tests
of the model to make predictions of NCAAB games
(today or tomorrow).
"""


DATADIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))


def fwdtest():
    # Create a model with default parameter set
    model_params = {
        'data_directory': DATADIR,
        'quiet': False,
        'print_stats': True
    }
    model = KenpomNCAABModel(model_params)

    # Run a backtest for all teams
    fwd = Forwardtester(model, today=True, tomorrow=False)
    fwd.prepare()
    fwd.forwardtest(test_name="fwd_all_kenpom")


if __name__=="__main__":
    fwdtest()
    #import cProfile
    #cProfile.run('backtest()')

