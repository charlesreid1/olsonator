from datetime import datetime, timedelta

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
        team: str = None
    ):
        self.model = model
        self.model_parameters = model.model_parameters

        # Verify the dates are valid, but keep as str
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d")

        if team is not None:
            # Verify the team is valid, then stash
            if is_teamrankings_team(team):
                self.team = team
            elif is_donch_team(team):
                self.team = donchess2teamranking(team)
            elif is_kenpom_team(team):
                self.team = donchess2teamranking(kenpom2donchess(team))

    def prepare(self):
        """
        Prepare (download and scrape) all data that models
        require to make predictions about all games in this
        backtest.
        """
        # Procedure:
        # - check game date requested
        # - open selenium/requests
        # - ask for teamrankings pages:
        #    - Tempo -> go to correct date
        #    - Offensive efficiency -> go to correct date
        #    - Defensive efficiency -> go to correct date
        # - (use a TeamRankings wrapper class, dump results)
        # - (we don't want to handle any results here - just download)

        start_dt = datetime.strptime(self.start_date, "%Y-%m-%d")
        end_dt   = datetime.strptime(self.end_date,   "%Y-%m-%d")

        if (end_dt - start_dt) > timedelta(days=90):
            msg = "Requesting more than 90 days of data is not allowed. "
            msg += "Make sure you have your dates correct. "
            msg += "If dates are correct, remove this exception from the code."
            raise Exception(msg)

        tr = TeamRankingsDataScraper(self.model_parameters)

        counter_dt = start_dt
        while counter_dt <= end_dt:
            this_date = counter_dt.strftime("%Y-%m-%d")
            print(f"Backtester is now preparing data for games on {this_date}")
            tr.fetch_all(this_date)
            counter_dt += timedelta(days=1)

