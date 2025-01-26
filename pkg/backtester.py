import math
import os
import pathlib
import copy
import statistics
import simplejson as json
from datetime import datetime, timedelta
import cbbpy.mens_scraper as CbbpyScraper

from .model import ModelBase
from .scraper import (
    TeamRankingsDataScraper,
    #TeamRankingsScheduleScraper,
)
from .errors import TeamNotFoundException
from .names import (
    is_kenpom_team,
    is_donch_team,
    is_teamrankings_team,
    normalize_to_teamrankings_names,
)
from .utils import repl


class Backtester(object):
    """
    Class that manages the entire backtesting process.
    This takes as input a model to backtest,
    a reqired start/end date, and an optional team name.
    If 
    """
    def __init__(
        self, 
        model: ModelBase, 
        start_date: str,
        end_date: str,
        teams: list = None
    ):
        """
        Inputs:
        start_date and end_date should be dates in the format YYYY-MM-DD
        """
        self.model = model
        self.model_parameters = model.model_parameters

        # Directories
        self.datadir = os.path.join(self.model_parameters['data_directory'])
        self.sched_datadir = os.path.join(self.datadir, 'schedule', 'json')
        self.bktst_datadir = os.path.join(self.datadir, 'backtest', 'json')

        if not os.path.exists(self.sched_datadir):
            pathlib.Path(self.sched_datadir).mkdir(parents=True)
        if not os.path.exists(self.bktst_datadir):
            pathlib.Path(self.bktst_datadir).mkdir(parents=True)

        # Verify the dates are valid, but keep as str
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d")

        start_dt = datetime.strptime(self.start_date, "%Y-%m-%d")
        end_dt   = datetime.strptime(self.end_date,   "%Y-%m-%d")

        # Assemble the list of dates we are scraping
        self.all_dates = []
        counter_dt = start_dt
        while counter_dt <= end_dt:
            this_date = counter_dt.strftime("%Y-%m-%d")
            self.all_dates.append(this_date)
            counter_dt += timedelta(days=1)

        # If user wants, they can provide a list of teams
        self.teams = []
        if teams is not None:
            for team in teams:
                # Verify the team is valid, then stash
                if is_teamrankings_team(team):
                    self.teams.append(team)
                elif is_donch_team(team):
                    self.teams.append(donchess2teamranking(team))
                elif is_kenpom_team(team):
                    self.teams.append(donchess2teamranking(kenpom2donchess(team)))

        # Verbosity
        self.nohush = not ('quiet' in self.model_parameters and self.model_parameters['quiet'] is True)


    def _get_schedule_fpath_json(self, stamp):
        """Get path to JSON file for schedule data for given date stamp"""
        fname = "schedule_" + stamp + ".json"
        fpath = os.path.join(self.sched_datadir, fname)
        return fpath

    def _get_backtest_fpath_json(self, test_name):
        """Get path to JSON file for schedule data for given date stamp"""
        stamp = datetime.now().strftime("%Y%m%d")
        test_name = repl(test_name)
        fname = test_name + "_" + stamp + ".json"
        fpath = os.path.join(self.bktst_datadir, fname)
        return fpath

    def _get_schedule_data(self):
        """
        Get (scrape) schedule data (everything required for
        model prediction input) for the given date.

        This uses the NCAA API (via CBBpy) to get schedule data.

        Use the stashed start/end dates from constructor.
        """
        schedule_data = []
        
        def _flatten(inputd):
            d = {}
            for k,v in inputd.items():
                k0 = list(v.keys())[0]
                d[k] = v[k0]
            return d

        # Do this one day at a time for efficiency
        for date in self.all_dates:
            today_data = []
            fpath = self._get_schedule_fpath_json(date) 
            try:
                if self.nohush:
                    print(f"Loading schedule data from {fpath}")
                with open(fpath, 'r') as f:
                    today_data = json.load(f)
            except json.decoder.JSONDecodeError:
                print(f"Invalid JSON file at {fpath}, try removing the file and re-running")

            except FileNotFoundError:
                print(f"No file at {fpath}, creating ourselves")
                # Call the NCAA API,
                # Receive the resulting JSON,
                # transform into a format our program likes,
                # Stash to a JSON file on disk
                gameids = CbbpyScraper.get_game_ids(date)

                today_data = []
                for gameid in gameids:
                    (game_info, _, _) = CbbpyScraper.get_game(gameid, box=False, pbp=False)
                    game_info = _flatten(game_info.to_dict())

                    if self.nohush:
                        print(f"Now on {game_info['away_team']} @ {game_info['home_team']} ({game_info['game_day']})")

                    # game_id                       401708334
                    # game_status                       Final
                    # home_team             Kentucky Wildcats
                    # home_id                              96
                    # home_rank                             8
                    # home_record                        14-4
                    # home_score                           97
                    # away_team          Alabama Crimson Tide
                    # away_id                             333
                    # away_rank                             4
                    # away_record                        15-3
                    # away_score                          102
                    # home_point_spread                  -2.5
                    # home_win                          False
                    # num_ots                               0
                    # is_conference                      True
                    # is_neutral                        False
                    # is_postseason                     False
                    # tournament
                    # game_day               January 18, 2025
                    # game_time                  09:00 AM PST
                    # game_loc                  Lexington, KY
                    # arena                        Rupp Arena
                    # arena_capacity                      NaN
                    # attendance                      21108.0
                    # tv_network                         ESPN
                    # referee_1                 Patrick Evans
                    # referee_2               Steven Anderson
                    # referee_3                   Joe Lindsay

                    olsonator_game = {}

                    # NCAA API uses January D, YYYY as the game day format
                    olsonator_game['game_date'] = datetime.strptime(game_info['game_day'], "%B %d, %Y").strftime("%Y-%m-%d")

                    # NCAA API uses 09:00 AM PST as the game time format
                    t = game_info['game_time'].split(" ")[0]
                    h, m = t.split(":")
                    game_time = int(h + m)
                    if 'PM' in game_info['game_time']:
                        game_time += 1200
                    olsonator_game['game_time'] = game_time

                    olsonator_game['vegas_away_spread'] = None
                    try:
                        away_spread = -1.0*float(game_info['home_point_spread'])
                        olsonator_game['vegas_away_spread'] = away_spread
                    except (KeyError, ValueError):
                        if self.nohush:
                            print(f"No Vegas spread info for {game_info['away_team']} @ {game_info['home_team']} ({game_info['game_day']})")

                    olsonator_game['neutral_site'] = game_info['is_neutral']
                    olsonator_game['is_conference'] = game_info['is_conference']

                    olsonator_game['away_rank'] = game_info['away_rank']
                    olsonator_game['home_rank'] = game_info['home_rank']

                    # The NCAA API introduces a whole new set of names (includes mascot)
                    try:
                        olsonator_game['away_team'] = normalize_to_teamrankings_names(game_info['away_team'])
                        olsonator_game['home_team'] = normalize_to_teamrankings_names(game_info['home_team'])
                    except TeamNotFoundException:
                        continue

                    olsonator_game['away_points'] = game_info['away_score']
                    olsonator_game['home_points'] = game_info['home_score']
                    olsonator_game['away_spread'] = game_info['home_score'] - game_info['away_score']
                    olsonator_game['total']       = game_info['away_score'] + game_info['home_score']

                    today_data.append(olsonator_game)

                fpath = self._get_schedule_fpath_json(date)
                with open(fpath, 'w') as f:
                    json.dump(today_data, f, indent=4, ignore_nan=True)
                if self.nohush:
                    print(f"Schedule data has been dumped to file {fpath}")

            schedule_data += today_data

        return schedule_data

    def prepare(self):
        """
        Prepare (download and scrape) all data that models
        require to make predictions about all games in this
        backtest.
        """
        # Procedure:
        # - check game date requested
        # - create instance of scraper class
        # - pass it a date and ask it to fetch data for that date
        # - child class:
        #    - uses selenium
        #    - requests pre-set urls
        #    - scrapes resulting pags for tempo, off eff, def eff
        #    - dumps to file
        # - that's it, we're done.
        # - (we don't want to handle any results here)

        tr = TeamRankingsDataScraper(self.model_parameters)

        for this_date in self.all_dates:
            if self.nohush:
                print(f"Backtester is now scraping data about teams on {this_date}")
            tr.fetch_all(this_date)

    def backtest(self, test_name):
        """
        Obtain a schedule of game information, incl results,
        on each requested game in the date range. 
        Iterate over each game to generate a prediction.
        
        Use the test_name parameter to save the results to a file.
        """
        # Procedure (for now):
        # - abstract away how we get the schedule into a get_schedule_data(date) method
        #   - rearrange the schedule to look like the game inputs we expect
        #   - return that schedule (list of game dicts)
        #   - use the NCAA API via cbbpy
        #   - stash the resulting games schedule in a json file
        #   - have a method to get that json file (prefix + date)
        # 
        # - once we have schedule, collect info:
        #   - real away spread
        #   - vegas away spread,
        #   - model away spread,
        # 
        #   - real away/home/total
        #   - vegas over/under total (<-- not readily available)
        #   - model predictions (away/home/total)
        # 
        #   - vegas moneyline (<-- not readily available??)
        #   - model euclidean win% projection

        schedule_data = self._get_schedule_data()
        model = self.model

        if self.nohush:
            print(f"Starting the backtest")

        results = []
        for game in schedule_data:
            our_team = game['home_team'] in self.teams or game['away_team'] in self.teams
            if len(self.teams)==0 or our_team:
                try:
                    away_points, home_points = model.predict(game)
                except TeamNotFoundException:
                    continue
                item = copy.deepcopy(game)
                item['predicted_away_points'] = round(away_points,1)
                item['predicted_home_points'] = round(home_points,1)
                item['predicted_away_spread'] = round(home_points - away_points, 1)
                item['predicted_total']       = round(home_points + away_points, 1)
                results.append(item)

        fpath = self._get_backtest_fpath_json(test_name)
        with open(fpath, 'w') as f:
            json.dump(results, f, indent=4, ignore_nan=True)

        if self.nohush:
            print(f"Backtest results for all games have been dumped to file {fpath}")

        ################################################

        if self.nohush:

            # Print a statistical summary
            print("")
            print("")
            print("\t==================================================")
            print(f"\tModel Backtest Summary: {test_name}")
            print("\t==================================================")

            print(f"\tTest name:\t\t{test_name}")

            # Start date
            print(f"\tStart date:\t\t{self.start_date}")

            # End date
            print(f"\tEnd date:\t\t{self.end_date}")

            # Number of days
            end = datetime.strptime(self.end_date, "%Y-%m-%d")
            start = datetime.strptime(self.start_date, "%Y-%m-%d")
            ndays = (end-start).days
            print(f"\tN days:\t\t\t{ndays}")

            # Number of games 
            print(f"\tN games:\t\t{len(schedule_data)}")

            # Teams
            if len(self.teams)>0:
                tms = ", ".join(self.teams)
            else:
                tms = "(all)"
            print(f"\tTeams:\t\t\t{tms}")

            vegas_spread_e = []
            model_spread_e = []
            model_spread_vsvegas = [0, 0]

            for item in results:

                if 'vegas_away_spread' not in item or item['vegas_away_spread'] is None:
                    continue

                e = item['vegas_away_spread'] - item['away_spread']
                vegas_spread_e.append(e*e)

                f = item['predicted_away_spread'] - item['away_spread']
                model_spread_e.append(f*f)

                # Example: real away spread is -10
                # vegas says -6
                # prediction says -4
                # we would have bet against the spread being so high (-), and lost
                # 
                # Example: real away spread is +6
                # vegas says +2
                # prediction says +4
                # we would have bet against the spread being so small (+), and won
                #
                # If vegas spread is between real and predicted, we lost against vegas
                # Another way to check is to see if vegas - real has same sign as vegas - prediction
                # If they do have the same sign, they're on the same side of vegas, meaning we won
                s1 = item['vegas_away_spread'] - item['predicted_away_spread']
                s2 = item['vegas_away_spread'] - item['away_spread']
                if (s1>0)==(s2>0):
                    # Won the bet
                    model_spread_vsvegas[0] += 1
                else:
                    # Lost the bet
                    model_spread_vsvegas[1] += 1
            
            vegas_spread_mse = statistics.mean(vegas_spread_e)
            model_spread_mse = statistics.mean(model_spread_e)

            # Vegas Spread MSE
            print(f"\tVegas Spread MSE:\t{round(vegas_spread_mse,1)}")

            # Model Spread MSE
            print(f"\tModel Spread MSE:\t{round(model_spread_mse,1)}")

            # Model Spread W-L vs Vegas
            print(f"\tWin-Loss vs Vegas:\t{model_spread_vsvegas[0]} - {model_spread_vsvegas[1]}")

            # Win Pct vs Vegas
            win_pct = 100*(model_spread_vsvegas[0]/(model_spread_vsvegas[0] + model_spread_vsvegas[1]))
            win_pct = round(win_pct, 1)
            print(f"\tWin-Loss % vs Vegas:\t{win_pct}%")

            # ROI vs Vegas (assuming -110 odds for every bet)
            amount = 110
            profit = 100
            investment = sum(model_spread_vsvegas)*amount
            gross = model_spread_vsvegas[0]*(amount + profit)
            net = gross - investment
            roi_110 = 100*(net/investment)

            print(f"\tROI vs Vegas (-110):\t{round(roi_110,1)}%")

            # Table is complete
            print("")
            print("")

        # Procedure (for future):
        # - open selenium
        # - ask for teamrankings schedule page
        # - (similar to donchess, has link to each game, with page for each)
        # - (would be nice to have odds on that page, but have to dig into each...)
        # 
        # game pages look like https://www.teamrankings.com/ncaa-basketball/matchup/mountaineers-red-wolves-2025-01-23
        # 
        # /spread-movement - page with final vegas spread
        # /box-score - page with final score

