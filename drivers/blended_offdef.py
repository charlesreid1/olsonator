import sys
import os
import json
import glob

# hack
pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, pkg_root)

from pkg.model import NCAABModel
from pkg.backtester import Backtester


DATADIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))


class BlendedOffDefNCAABModel(NCAABModel):
    def get_school_off_eff(self, gp, school):
        """Return the offensive efficiency for this school"""
        game_date = gp['game_date'].replace("-", "")
        year = self._get_year(game_date)
        
        seas_eff  = self._get_school_template_func(gp, school, "off_eff", f"off_eff_{year}")
        last3_eff = self._get_school_template_func(gp, school, "off_eff", f"off_eff_last_3")

        # 70/30 has poor performance, 90/10 much better, 95/5 even better
        return 0.95*seas_eff + 0.05*last3_eff

    def get_school_def_eff(self, gp, school):
        """Return the defensive efficiency for this school"""
        game_date = gp['game_date'].replace("-", "")
        year = self._get_year(game_date)

        seas_eff  = self._get_school_template_func(gp, school, "def_eff", f"def_eff_{year}")
        last3_eff = self._get_school_template_func(gp, school, "def_eff", f"def_eff_last_3")

        return 0.95*seas_eff + 0.05*last3_eff


def backtest():
    model_params = {
        'data_directory': DATADIR,
        'quiet': True,
        'print_stats': True
    }

    start_date = "2024-12-15"
    end_date   = "2025-01-20"

    # Run backtest on each model
    model = BlendedOffDefNCAABModel(model_params)
    backtester = Backtester(model, start_date=start_date, end_date=end_date)
    backtester.prepare()
    backtester.backtest(test_name="blended_offdef")


if __name__=="__main__":
    backtest()
