import json
import os
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
)


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
        self.model = model
        self.model_parameters = model.model_parameters

        # Directories
        self.trdir = os.path.join(self.model_parameters['data_directory'], 'backtester')
        self.jdatadir = os.path.join(self.trdir, 'json')

        if not os.path.exists(self.trdir):
            os.mkdir(self.trdir)
        if not os.path.exists(self.jdatadir):
            os.mkdir(self.jdatadir)

        # Verify the dates are valid, but keep as str
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d")

        # Ensure we are limiting scraping by not backtesting more than 90 days at a time
        start_dt = datetime.strptime(self.start_date, "%Y-%m-%d")
        end_dt   = datetime.strptime(self.end_date,   "%Y-%m-%d")

        # Assemble the list of dates we are scraping
        self.all_dates = []
        counter_dt = start_dt
        while counter_dt <= end_dt:
            this_date = counter_dt.strftime("%Y-%m-%d")
            self.all_dates.append(this_date)
            counter_dt += timedelta(days=1)

        if (end_dt - start_dt) > timedelta(days=90):
            msg = "Requesting more than 90 days of data is not allowed. "
            msg += "Make sure you have your dates correct. "
            msg += "If dates are correct, remove this exception from the code."
            raise Exception(msg)

        self.teams = []
        for team in teams:
            if team is not None:
                # Verify the team is valid, then stash
                if is_teamrankings_team(team):
                    self.teams.append(team)
                elif is_donch_team(team):
                    self.teams.append(donchess2teamranking(team))
                elif is_kenpom_team(team):
                    self.teams.append(donchess2teamranking(kenpom2donchess(team)))

    def _get_schedule_fpath_json(self, stamp):
        """Get path to JSON file for schedule data for given date stamp"""
        fname = "schedule_" + stamp + ".json"
        fpath = os.path.join(self.jdatadir, fname)
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
                print(f"Loading schedule data from {fpath}")
                with open(fpath, 'r') as f:
                    today_data = json.load(f)
            except json.decoder.JSONDecodeError:
                print(f"Invalid JSON file at {fpath}, no idea")

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
                    print(f"Now on {game_info['game_day']} - {game_info['away_team']} @ {game_info['home_team']}")

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

                    olsonator_game['neutral_site'] = game_info['is_neutral']

                    # The NCAA API introduces a whole new set of names (includes mascot)
                    olsonator_game['home_team'] = game_info['home_team']
                    olsonator_game['away_team'] = game_info['away_team']

                    today_data.append(olsonator_game)

                with open(self._get_schedule_fpath_json(date), 'w') as f:
                    json.dump(today_data, f, indent=4)

            schedule_data += today_data

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
            print(f"Backtester is now preparing data for games on {this_date}")
            tr.fetch_all(this_date)


        # TBD.........






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
        # - once we have schedule:
        #   - real spread
        #   - vegas A spread,
        #   - model A spread,
        # 
        #   - real away/home/total
        #   - vegas over/under total
        #   - model predictions (away/home/total)
        # 
        #   - vegas moneyline
        #   - model euclidean win% projection

        schedule_data = self._get_schedule_data()



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




