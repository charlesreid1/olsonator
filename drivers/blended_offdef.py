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
Make a modified Olsonator NCAA basketball model

This script creates a variation on the base NCAA basketball model.
Insead of using the season value for offensive and defensive
efficiency, this model blends 95% of the season value with
5% of the last 3 games. This consistently leads to a (small)
improvement in model performance.
"""


DATADIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))


class BlendedOffDefNCAABModel(NCAABModel):
    """
    This class blends the offensive and defensive ratings.
    Instead of returning the season-wide offensive/defensive ratings for a team,
    blend the season-wide with recent performance.

    Based on several backtests of several ranges,
    the optimal blend ratio for 2024 is
    95% season, 5% last3, 0% last 1

    This consistently outperforms just using the season rating,
    for numerous backtesting window lengths.
    """

    def get_school_off_eff(self, gp, school):
        """Return the offensive efficiency for this school"""
        game_date = gp['game_date'].replace("-", "")
        year = self._get_year(game_date)
        seas_eff  = self._get_school_template_func(gp, school, "off_eff", f"off_eff_{year}")
        try:
            last3_eff = self._get_school_template_func(gp, school, "off_eff", "off_eff_last_3")
        except KeyError:
            last3_eff = seas_eff

        return 0.95*seas_eff + 0.05*last3_eff

    def get_school_def_eff(self, gp, school):
        """Return the defensive efficiency for this school"""
        game_date = gp['game_date'].replace("-", "")
        year = self._get_year(game_date)
        seas_eff  = self._get_school_template_func(gp, school, "def_eff", f"def_eff_{year}")
        try:
            last3_eff = self._get_school_template_func(gp, school, "def_eff", f"def_eff_last_3")
        except KeyError:
            last3_eff = seas_eff

        return 0.95*seas_eff + 0.05*last3_eff


def backtest():
    model_params = {
        'data_directory': DATADIR,
        'quiet': True,
        'print_stats': True
    }

    start_date = "2024-11-15"
    end_date   = "2025-01-25"

    # Run backtest on each model
    model = BlendedOffDefNCAABModel(model_params)
    backtester = Backtester(model, start_date=start_date, end_date=end_date)
    backtester.prepare()
    backtester.backtest(test_name="blended_offdef")


if __name__=="__main__":
    backtest()
