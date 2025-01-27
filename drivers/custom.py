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


class CustomNCAABModel1(NCAABModel):
    home_advantage = 1.0

    def get_home_factor(self, game_parameters, away_points, home_points):
        """
        Override parent version of this method, which uses
        a hard-coded home advantage value, and use a custom
        value (or procedure) instead.
        """
        away_points -= self.home_advantage/2.0 
        home_points += self.home_advantage/2.0
        return (away_points, home_points)


class CustomNCAABModel2(CustomNCAABModel1):
    home_advantage = 2.0

class CustomNCAABModel3(CustomNCAABModel1):
    home_advantage = 3.0

class CustomNCAABModel4(CustomNCAABModel1):
    home_advantage = 4.0

class CustomNCAABModel5(CustomNCAABModel1):
    home_advantage = 5.0


def backtest():
    model_params = {
        'data_directory': DATADIR,
        'quiet': True,
        'print_stats': True
    }

    start_date = "2024-12-15"
    end_date   = "2025-01-20"

    # Run backtest on each model
    model = CustomNCAABModel1(model_params)
    backtester = Backtester(model, start_date=start_date, end_date=end_date)
    backtester.prepare()
    backtester.backtest(test_name="custom_homeadv1")

    model2 = CustomNCAABModel2(model_params)
    backtester2 = Backtester(model2, start_date=start_date, end_date=end_date)
    backtester2.prepare()
    backtester2.backtest(test_name="custom_homeadv2")

    # This one will have the highest ROI
    model3 = CustomNCAABModel3(model_params)
    backtester3 = Backtester(model3, start_date=start_date, end_date=end_date)
    backtester3.prepare()
    backtester3.backtest(test_name="custom_homeadv3")

    model4 = CustomNCAABModel4(model_params)
    backtester4 = Backtester(model4, start_date=start_date, end_date=end_date)
    backtester4.prepare()
    backtester4.backtest(test_name="custom_homeadv4")

    model5 = CustomNCAABModel5(model_params)
    backtester5 = Backtester(model5, start_date=start_date, end_date=end_date)
    backtester5.prepare()
    backtester5.backtest(test_name="custom_homeadv5")


if __name__=="__main__":
    backtest()
