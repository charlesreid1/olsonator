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
Create a custom Olsonator NCAA basketball model

This script shows how to extend the functionality of the base
NCAAB model to change the way it calculates certain things.

Specifically, we modify how the model calculates home advantage
to compare two different methods.
"""


DATADIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))


class CustomNCAABModel(NCAABModel):
    def get_home_adjustment(self, game_parameters, away_points, home_points):
        """
        Override parent version of this method, which uses
        a hard-coded home advantage value, and use a custom
        value (or procedure) instead.
        """
        home_adv = 8.0
        away_points -= home_adv/2.0 
        home_points += home_adv/2.0
        return (away_points, home_points)


def backtest():
    # Create a model with default parameter set
    model_params = {
        'data_directory': DATADIR,
        'quiet': True,
        'print_stats': True
    }
    model = CustomNCAABModel(model_params)

    # Run a backtest for all teams
    backtester = Backtester(model, start_date="2025-01-10", end_date="2025-01-20")
    backtester.prepare()
    backtester.backtest(test_name="custom_homeadv")


if __name__=="__main__":
    backtest()
