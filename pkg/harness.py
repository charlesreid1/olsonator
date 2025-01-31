from datetime import datetime, timedelta

from .scraper import TeamRankingsDataScraper


class ModelDataHarness(object):
    def __init__(self, model_parameters: dict):
        self.model_parameters = model_parameters

    def prepare(self, game_parameters: dict):
        """
        Prepare (download and scrape) data needed
        to make a game prediction for a single game.
        """
        # Procedure:
        # - create a data scraper, pass it model parameters
        # - ask it to fetch the date in game_parameters

        # Date, with dashes
        game_date = game_parameters['game_date']

        # Scraper for teamrankings.com data pages
        tr = TeamRankingsDataScraper(self.model_parameters)
        tr.fetch_all(game_date)
