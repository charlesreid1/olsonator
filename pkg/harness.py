from datetime import datetime, timedelta

from .scraper import TeamRankingsDataScraper


class ModelDataHarness(object):
    def __init__(self, model_parameters: dict):
        self.model_parameters = model_parameters

    def prepare(self, game: dict):
        """
        Prepare (download and scrape) all data that models
        require to make a game prediction.
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

        # Date, with dashes
        game_date = game['game_date']

        ### # TODO: Ask for kenpom ratings if game was within 90 days
        ### game_dt = datetime.strptime(game_date, "%Y-%m-%d")
        ### diff = game_dt - datetime.today()
        ### within_90_days = diff < timedelta(days=90)

        # Ask for teamrankings.com pages
        tr = TeamRankingsDataScraper(self.model_parameters)
        tr.fetch_all(game_date)

