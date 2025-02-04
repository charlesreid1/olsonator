import os
import copy
import simplejson as json
import pathlib
from datetime import datetime, timedelta

from .backtester import Backtester
from .model import ModelBase
from .constants import (
    CONFERENCES, 
    SPREAD_CONFIDENCES, 
    OU_CONFIDENCES,
    ML_CONFIDENCES,
)
from .errors import TeamNotFoundException, ModelPredictException
from .teams import normalize_to_donchess_names
from .utils import (
    repl,
    pythagorean_win_pct,
    decimal2american,
    american2decimal,
    bet_win_american,
)


class Forwardtester(Backtester):
    def __init__(
        self,
        model: ModelBase,
        today: bool = False,
        tomorrow: bool = False,
        teams: list = None
    ):
        if not (today or tomorrow):
            err = "Please provide today=True or tomorrow=True to Forwardtester class"
            raise ValueError(err)

        tod = datetime.now()
        tom = datetime.now() + timedelta(days=1)
        fmt = "%Y-%m-%d"
        if today:
            start_date = tod.strftime(fmt)
        else:
            start_date = tom.strftime(fmt)

        if tomorrow:
            end_date = tom.strftime(fmt)
        else:
            end_date = tod.strftime(fmt)

        super().__init__(model, start_date=start_date, end_date=end_date, teams=teams)

        self.fwdtst_datadir = os.path.join(self.datadir, 'fwdtest', 'json')

        if not os.path.exists(self.fwdtst_datadir):
            pathlib.Path(self.fwdtst_datadir).mkdir(parents=True)

    def _get_schedule_fpath_json(self, stamp):
        """Get path to JSON file for schedule data for given date stamp"""
        fname = "todtom_" + stamp + ".json"
        fpath = os.path.join(self.sched_datadir, fname)
        return fpath

    def _get_forwardtest_fpath_json(self, test_name):
        """Get path to JSON file for schedule data for given date stamp"""
        stamp = datetime.now().strftime("%Y%m%d")
        test_name = repl(test_name)
        fname = test_name + "_" + stamp + ".json"
        fpath = os.path.join(self.fwdtst_datadir, fname)
        return fpath

    def backtest(self, *args, **kwargs):
        raise NotImplementedError("Forwardtester class does not implement a backtest() method")

    def forwardtest(self, test_name):
        """
        Obtain schedule of game information for each game in date range.
        Iterate over each game and make a prediction.

        The forward test has no results, so insert predicted score
        and spread into the game info, and then stash it in the 
        forwardtest directory.

        Return it and/or print a summary.
        """
        schedule_data = self._get_schedule_data()
        model = self.model

        if self.nohush:
            print(f"Starting the forwardtest")

        if len(schedule_data)==0:
            raise Exception("No schedule data")

        results = []
        for game in schedule_data:
            game_descr = f"{game['away_team']} @ {game['home_team']} ({game['game_date']})"
            our_team = game['home_team'] in self.teams or game['away_team'] in self.teams
            if len(self.teams)==0 or our_team:
                try:
                    away_points, home_points = model.predict(game)
                except (TeamNotFoundException, ModelPredictException):
                    # Note: first few days of season, no off/def data, so no predictions
                    continue

                # Ensure this matches backtest() method

                away_ml_decimal = pythagorean_win_pct(away_points, home_points)
                away_ml_american = decimal2american(away_ml_decimal)
                home_ml_american = decimal2american(1-away_ml_decimal)

                item = copy.deepcopy(game)
                item['predicted_away_points'] = round(away_points,1)
                item['predicted_home_points'] = round(home_points,1)

                # Spread
                item['predicted_away_spread'] = round(home_points - away_points, 1)

                # Moneyline
                item['predicted_away_moneyline'] = away_ml_american
                item['predicted_home_moneyline'] = home_ml_american

                # Over/under
                item['predicted_total']       = round(home_points + away_points, 1)

                results.append(item)

        if len(results)==0:
            raise Exception("No results")

        fpath = self._get_forwardtest_fpath_json(test_name)
        with open(fpath, 'w') as f:
            json.dump(results, f, indent=4, ignore_nan=True)

        if self.nohush:
            print(f"Forwardtest results for all games have been dumped to file {fpath}")

        if self.nohush:

            # Print a summary of predictions, grouped by time

            print("")
            print("")
            print("\t==================================================")
            print(f"\tPredictions Summary: {test_name}")
            print("\t==================================================")
            print(f"\tTest name:\t\t{test_name}")
            print(f"\tStart date:\t\t{self.start_date}")
            print(f"\tEnd date:\t\t{self.end_date}")
            if len(self.teams)>0:
                tms = ", ".join(self.teams)
            else:
                tms = "(all)"
            print(f"\tTeams:\t\t\t{tms}")
            print("")

            unique_times = {g['game_time'] for g in results}
            for start_time in sorted(list(unique_times)):
                print("")
                print(f"{start_time} Pacific:")
                print("--------------")

                window_games = [g for g in results if g['game_time']==start_time]
                window_games.sort(key = lambda x: x['away_team'])

                for game in window_games:
                
                    # For each game, print the matchup, and the expected spread for the dog
                    matchup = f"{game['away_team']} @ {game['home_team']}:"

                    ateam = game['away_team']
                    aconference = CONFERENCES[normalize_to_donchess_names(ateam)]

                    hteam = game['home_team']
                    hconference = CONFERENCES[normalize_to_donchess_names(hteam)]

                    # dog + spread (+ points needed on the spread for the dog to cover)
                    if game['predicted_away_points'] < game['predicted_home_points']:
                        spread = game['predicted_away_spread']
                        dog_spread = f"{game['away_team']} (+{spread})"
                    elif game['predicted_home_points'] < game['predicted_away_points']:
                        spread = -1*game['predicted_away_spread']
                        dog_spread = f"{game['home_team']} (+{spread})"

                    # confidence in spread
                    aspconfidence = SPREAD_CONFIDENCES[aconference]
                    hspconfidence = SPREAD_CONFIDENCES[hconference]
                    conf_spread = int((aspconfidence + hspconfidence)//2)

                    # o/u
                    total = game['predicted_total']
                    over_under = f"T: {total}"

                    # confidence in ou
                    aouconfidence = OU_CONFIDENCES[aconference]
                    houconfidence = OU_CONFIDENCES[hconference]
                    conf_ou = int((aouconfidence + houconfidence)//2)

                    # dog moneyline
                    away_ml_american = game['predicted_away_moneyline']
                    home_ml_american = game['predicted_home_moneyline']

                    away_ml_decimal = american2decimal(away_ml_american)
                    home_ml_decimal = american2decimal(home_ml_american)

                    # confidence in ml
                    amlconfidence = ML_CONFIDENCES[aconference]
                    hmlconfidence = ML_CONFIDENCES[hconference]
                    conf_ml = int((amlconfidence + hmlconfidence)//2)

                    # confidence in ml

                    if away_ml_decimal < 0.5:
                        dog_moneyline = f"{game['away_team']} ({away_ml_american})"
                    elif home_ml_decimal < 0.5:
                        dog_moneyline = f"{game['home_team']} ({home_ml_american})"

                    #print(f"{matchup:24s}\t{dog_spread:20s}\t{conf_spread}")
                    #print(f"{matchup:24s}\t| {dog_moneyline:20s}\t{conf_ml}\t| {dog_spread:20s}\t{conf_spread}\t| {over_under:8s}\t{conf_ou}")
                    print(f"{matchup:24s}\t| {dog_moneyline:20s}\t{conf_ml}\t| {dog_spread:20s}\t{conf_spread}\t| {over_under:8s}\t{conf_ou}")

            print("")
            print("")
