import os
import json
import time
from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup

from .errors import TeamRankingTableNotFoundException


class TeamRankingsDataScraper(object):
    """
    Class that fetches pages from TeamRankings.com,
    scrapes them for data, and stores the resulting
    HTML and JSON data under `data/teamrankings/`
    for later use by models.
    """

    urls = {
        "tempo":   "https://www.teamrankings.com/ncaa-basketball/stat/possessions-per-game",
        "off_eff": "https://www.teamrankings.com/ncaa-basketball/stat/offensive-efficiency",
        "def_eff": "https://www.teamrankings.com/ncaa-basketball/stat/defensive-efficiency",
    }

    def __init__(self, model_parameters):
        self.model_parameters = model_parameters
        self.trdir = os.path.join(self.model_parameters['data_directory'], 'teamrankings')
        self.jdatadir = os.path.join(self.trdir, 'json')

        if not os.path.exists(self.trdir):
            os.mkdir(self.trdir)
        if not os.path.exists(self.jdatadir):
            os.mkdir(self.jdatadir)

    def _get_fpath_json(self, prefix, stamp):
        """
        Get the filename + path of the JSON file where we are
        storing all of the data scraped from today's HTML
        
        prefix should be a stat name (like tempo)
        stamp should be a YYYYMMDD datestamp
        """
        fname = prefix + "_" + stamp + ".json"
        fpath = os.path.join(self.jdatadir, fname)
        return fpath

    def _get_page_html(self, url):
        """
        Use Selenium webdriver to fetch the url,
        then return the HTML source of the loaded page
        """
        try:
            ffopt = webdriver.FirefoxOptions()
            ffopt.add_argument("--headless")
            browser = webdriver.Firefox(options=ffopt)
            browser.get(url)
            time.sleep(3)
            src = browser.page_source
        finally:
            try:
                browser.close()
            except:
                pass
        return src 

    def _html2json(self, html, prefix):
        soup = BeautifulSoup(html, 'html.parser')

        table = soup.find('table', attrs={"id": "DataTables_Table_0"})
        if table is None:
            raise TeamRankingTableNotFoundException("data table cannot be found???")

        # Extract column headers, adding the prefix to each
        headers = []
        header_row = table.find('thead').find('tr')
        column_headers = header_row.find_all('th')
        for column_header in column_headers:
            header = prefix + "_" + column_header.text.lower().replace(' ','_')
            headers.append(header)

        ranking = []

        table_rows = table.find('tbody').find_all('tr')
        for row in table_rows:
            item = {}
            cols = row.find_all('td')
            for j, (header, col) in enumerate(zip(headers, cols)):
                if j==0:
                    # Column 0 is always an integer rank
                    item[header] = int(col.text)
                elif j==1:
                    # Column 1 is always team name
                    item[header] = col.text
                elif j>1:
                    # Column 2+ is always floats
                    try:
                        item[header] = float(col.text)
                    except ValueError:
                        item[header] = None
            ranking.append(item)

        return ranking

    def fetch_all(self, game_date_dashes, force=False):
        game_date_nodashes = game_date_dashes.replace("-", "")
        for k in ['tempo', 'off_eff', 'def_eff']:
            fpath = self._get_fpath_json(k, game_date_nodashes)
            if (force is True) or (os.path.exists(fpath) is False):
                url = self.urls[k]
                if game_date_dashes != datetime.now().strftime("%Y-%m-%d"):
                    url += f"?date={game_date_dashes}"

                this_src = self._get_page_html(url)
                this_json = self._html2json(this_src, k)

                with open(fpath, 'w') as f:
                    json.dump(this_json, f)
