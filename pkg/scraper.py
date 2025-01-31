import os
import json
import time
from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup

from .errors import TeamRankingTableNotFoundException


class TeamRankingsDataScraper(object):
    """
    Class that fetches team data from TeamRankings.com,
    scrapes the data, and stores the resulting
    JSON data under `data/teamrankings/`
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

    def _get_datatable(self, html):
        """Get the main DataTables table. Useful b/c we never need the soup otherwise."""
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', attrs={"id": "DataTables_Table_0"})
        if table is None:
            raise TeamRankingTableNotFoundException("data table cannot be found???")
        return table

    def _html2json(self, html, prefix):
        """Extract data from HTML and send to JSON."""
        table = self._get_datatable(html)

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
        for k in self.urls.keys():
            fpath = self._get_fpath_json(k, game_date_nodashes)
            if (force is True) or (os.path.exists(fpath) is False):
                url = self.urls[k]
                if game_date_dashes != datetime.now().strftime("%Y-%m-%d"):
                    url += f"?date={game_date_dashes}"

                this_src = self._get_page_html(url)
                this_json = self._html2json(this_src, k)

                with open(fpath, 'w') as f:
                    json.dump(this_json, f)


class TeamRankingsScheduleScraper(TeamRankingsDataScraper):
    """
    Class that fetches schedule data from TeamRankings.com,
    scrapes the data, and stores the resulting
    JSON data under `data/teamrankings/`
    """
    urls = {
        "daily":   "https://www.teamrankings.com/ncb/schedules",
    }

    def _html2json(self, html):
        """Extract data from HTML and return in JSON format."""
        table = self._get_datatable(html)

        schedule = []

        table_rows = table.find('tbody').find_all('tr')
        for row in table_rows:
            game = {}
            cols = row.find_all('td')
            for j, (header, col) in enumerate(zip(headers, cols)):
                if j==0:
                    # irrelevant rank
                    pass
                elif j==1:
                    # hotness
                    pass
                elif j==2:
                    # matchup name, plus link
                    import pdb; pdb.set_trace()
                    link = col.find('a').href
                    text = col.find('a').text
                    teams = text.split(" at ")
                    game['game_link'] = link
                    game['away_team'] = teams[0]
                    game['home_team'] = teams[1]
                elif j==3:
                    # time (always eastern time, format is "9:00 PM")
                    pass
                elif j==4:
                    # location (not simple to determine if this is neutral site or not, default to no)
                    pass

            schedule.append(game)

        # This does not save the JSON to a file, only returns it
        return schedule

    def _get_movementtable(self, html):
        """Get the main movement table on odds pages. Useful b/c we never need the soup otherwise."""
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', attrs={"class": "movement-table"})
        if table is None:
            raise TeamRankingTableNotFoundException("movement table cannot be found???")
        return table

    def _html2json_ml(self, html1, html2):
        """Extract moneyline odds data from HTML, and send to JSON"""
        soup = BeautifulSoup(html, 'html.parser')
        for lab in ['tab-001', 'tab-002']:
            div = soup.find('div', attrs={'id': lab})
            table = div.find('table')



        odds = {}
        return odds

    def _html2json_sp(self, html):
        """Extract spread odds data from HTML, and send to JSON"""
        table = self._get_movementtable(html)
        row1 = table.find('tr')
        cols = row1.find_all('td')

        odds = {}
        return odds

    def _html2json_ou(self, html):
        """Extract o/u odds data from HTML, and send to JSON"""
        table = self._get_movementtable(html)
        row1 = table.find('tr')
        cols = row1.find_all('td')

        col0 = cols[0]
        col2 = cols[2]

        # Format "Total 165.5"
        ou_total = float(col0.text.split(" ")[1])
        ou_open  = float(col2.text)

        odds = {}
        odds['vegas_ou_total'] = round(ou_total, 1)
        odds['vegas_ou_open']  = round(ou_open,  1)
        return odds

    def fetch_all(self, game_date_dashes, force=False):
        game_date_nodashes = game_date_dashes.replace("-", "")

        # Step 1: Get daily schedule and compile links to each game
        k = "daily"
        fpath = self._get_fpath_json(k, game_date_nodashes)
        if (force is True) or (os.path.exists(fpath) is False):
            url = self.urls[k]
            if game_date_dashes != datetime.now().strftime("%Y-%m-%d"):
                url += f"?date={game_date_dashes}"

            sched_src = self._get_page_html(url)
            sched_json = self._html2json(sched_src)

            # Step 1b: export schedule data
            with open(fpath, 'w') as f:
                json.dump(sched_json, f)

        else:
            with open(fpath, 'r') as f:
                sched_json = json.load(f)

        # Step 2: Visit each game's link (or two) to get odds
        for game in sched_json:
            game_url = game['game_url']

            ml_fpath = self._get_fpath_json("daily_ml", game_date_nodashes)
            ml_src = self._get_page_html(url + "/money-line-movement")
            ml_json = self._html2json_ml(ml_src)

            sp_fpath = self._get_fpath_json("daily_sp", game_date_nodashes)
            sp_src = self._get_page_html(url + "/spread-movement")
            sp_json = self._html2json_sp(sp_src)

            ou_fpath = self._get_fpath_json("daily_ou", game_date_nodashes)
            ou_src = self._get_page_html(url + "/over-under-movement")
            ou_json = self._html2json_ou(ou_src)




