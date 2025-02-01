import os
import re
import json
import time
from datetime import datetime, timedelta
from selenium import webdriver
from bs4 import BeautifulSoup

from .errors import TeamRankingsParseError


class TeamRankingsDataScraper(object):
    """
    Class that fetches team data from TeamRankings.com,
    scrapes the data, and stores the resulting
    JSON data under `/data/teamrankings/json/`
    """

    urls = {
        "tempo":   "https://www.teamrankings.com/ncaa-basketball/stat/possessions-per-game",
        "off_eff": "https://www.teamrankings.com/ncaa-basketball/stat/offensive-efficiency",
        "def_eff": "https://www.teamrankings.com/ncaa-basketball/stat/defensive-efficiency",
    }
    data_subdir = 'teamrankings'

    def __init__(self, model_parameters):
        self.model_parameters = model_parameters
        self.trdir = os.path.join(self.model_parameters['data_directory'], self.data_subdir)
        self.jdatadir = os.path.join(self.trdir, 'json')

        if not os.path.exists(self.trdir):
            os.mkdir(self.trdir)
        if not os.path.exists(self.jdatadir):
            os.mkdir(self.jdatadir)

        # Verbosity
        self.nohush = not ('quiet' in self.model_parameters and self.model_parameters['quiet'] is True)

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
            ffopt.set_preference("general.useragent.override", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.1")
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
            raise TeamRankingsTableNotFoundException("data table cannot be found???")
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
        """
        For the given date, download corresponding HTML pages with team data,
        scrape the team data from the page, and export to JSON file.
        """
        game_date_nodashes = game_date_dashes.replace("-", "")
        for k in self.urls.keys():
            fpath = self._get_fpath_json(k, game_date_nodashes)
            if (force is True) or (os.path.exists(fpath) is False):
                url = self.urls[k]
                if game_date_dashes != datetime.now().strftime("%Y-%m-%d"):
                    url += f"?date={game_date_dashes}"

                this_src = self._get_page_html(url)
                this_json = self._html2json(this_src, k)

                if self.nohush:
                    print(f"Dumping TeamRankings team data to {fpath}")
                with open(fpath, 'w') as f:
                    json.dump(this_json, f)


class TeamRankingsScheduleScraper(TeamRankingsDataScraper):
    """
    Class that fetches schedule data from TeamRankings.com,
    scrapes the data, and stores the resulting
    JSON data under `/data/schedule/json/`
    """

    urls = {
        "trschedule":   "https://www.teamrankings.com/ncb/schedules",
    }
    data_subdir = 'schedule'

    def _html2json_sched(self, html):
        """Extract schedule data from HTML and return in JSON format."""
        table = self._get_datatable(html)

        schedule = []

        table_rows = table.find('tbody').find_all('tr')

        if "No data available" in table_rows[0].text:
            msg = "No data found on schedule page, specified date may be invalid"
            raise TeamRankingsParseError(msg)

        x = re.compile(r'\#\d+(.*)at.*\#\d+(.*)')
        v = re.compile(r'\#\d+(.*)vs.*\#\d+(.*)')
        for row in table_rows:
            add_game = True
            game = {}
            cols = row.find_all('td')
            for j, col in enumerate(cols):
                # col 1 = irrelevant rank
                # col 2 = hotness
                # col 3 = matchup name plus link
                # col 4 = time
                # col 5 = location
                if j==2:
                    # matchup name, plus link
                    try:
                        link = "https://teamrankings.com" + col.find('a').attrs['href']
                    except AttributeError:
                        # Game does not have link, skip it
                        add_game = False
                        break
                    text = col.find('a').text
                    is_neutral = False
                    try:
                        # Match "A at B"
                        g = x.search(text)
                        away_team = g[1].strip()
                        home_team = g[2].strip()
                    except TypeError:
                        # No matches for "A at B", try "A vs. B" (neutral site)
                        g = v.search(text)
                        away_team = g[1].strip()
                        home_team = g[2].strip()
                        is_neutral = True
                    game['game_url']   = link
                    game['away_team']  = away_team
                    game['home_team']  = home_team
                    game['is_neutral'] = is_neutral
                elif j==3:
                    # time (always eastern time, format is "9:00 PM")
                    # convert to west coast time, format HHMM
                    dt = datetime.strptime(col.text, "%I:%M %p") - timedelta(hours=3)
                    game['game_time'] = dt.strftime("%H%M")
                    pass

            if add_game:
                schedule.append(game)

        # This does not save the JSON to a file, only returns it
        return schedule

    def _get_movementtable(self, html):
        """Get the main movement table on odds pages. Useful b/c we never need the soup otherwise."""
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', attrs={"class": "movement-table"})
        if table is None:
            raise TeamRankingsParseError("Odds table cannot be found on game page")
        return table

    def _html2json_ml(self, html):
        """Extract moneyline odds data from HTML, and send to JSON"""
        soup = BeautifulSoup(html, 'html.parser')

        ### # Figure out team names from h1 title at top
        ### away_team, home_team = None, None
        ### h1s = soup.find_all('h1')
        ### for h1 in h1s:
        ###     txt = h1.text
        ###     if "Money Line Movement" in txt:
        ###         teams = h1.text.split(": ")[0]
        ###         atags = h1.find_all('a')
        ###         away_team = atags[0].text
        ###         home_team = atags[1].text

        # Figure out which abbrs map to away/home via header text "Matchup Menu: TEX @ OSU"
        away_abbr, home_abbr = None, None
        h2s = soup.find_all('h2')
        for h2 in h2s:
            txt = h2.text
            if "Matchup Menu" in txt:
                versus = txt.split(":")[1]
                teams = versus.split(" @ ")
                away_abbr = teams[0].strip()
                home_abbr = teams[1].strip()

        away_ml, home_ml = None, None
        for lab in ['tab-001', 'tab-002']:
            div = soup.find('div', attrs={'id': lab})
            table = div.find('table')
            cell = table.find('tbody').find('tr').find('td')
            k, v = cell.text.split(" ")
            if k==away_abbr:
                away_ml = v
            if k==home_abbr:
                home_ml = v

        odds = {}
        odds['vegas_away_moneyline'] = away_ml
        odds['vegas_home_moneyline'] = home_ml
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
        """
        For the given date, download corresponding HTML pages with schedule data,
        scrape the schedule data from the page, and export to JSON file.
        """
        game_date_nodashes = game_date_dashes.replace("-", "")

        # ----------------------
        # Step 1: Get daily schedule and compile links to each game
        # (must match backtester _get_schedule_fpath_json())
        k = "trschedule"
        fpath = self._get_fpath_json(k, game_date_nodashes)
        if (force is True) or (os.path.exists(fpath) is False):
            url = self.urls[k]
            if game_date_dashes != datetime.now().strftime("%Y-%m-%d"):
                url += f"?date={game_date_dashes}"

            if self.nohush:
                print(f"Retrieving TeamRankings.com daily schedule for {game_date_dashes}")

            try:
                sched_src = self._get_page_html(url)
                sched_json = self._html2json_sched(sched_src)
                for game in sched_json:
                    game['game_date'] = game_date_dashes
            except TeamRankingsParseError as e:
                # No games on this date
                sched_json = []

            # Step 1b: export schedule data
            if self.nohush:
                print(f"Dumping TeamRankings schedule data to {fpath}")
            with open(fpath, 'w') as f:
                json.dump(sched_json, f, indent=4)

        else:
            # Load existing schedule data
            with open(fpath, 'r') as f:
                sched_json = json.load(f)

        # ----------------------
        # Step 2: Visit each game's link (or two) to get results, odds
        for game in sched_json:
            game_url = game['game_url']

            if self.nohush:
                print(f"Retrieving TeamRankings.com odds data for {game['away_team']} @ {game['home_team']} ({game['game_date']})")

            ml_fpath = self._get_fpath_json("daily_ml", game_date_nodashes)
            ml_src = self._get_page_html(game_url + "/money-line-movement")
            ml_json = self._html2json_ml(ml_src)

            sp_fpath = self._get_fpath_json("daily_sp", game_date_nodashes)
            sp_src = self._get_page_html(game_url + "/spread-movement")
            sp_json = self._html2json_sp(sp_src)

            ou_fpath = self._get_fpath_json("daily_ou", game_date_nodashes)
            ou_src = self._get_page_html(game_url + "/over-under-movement")
            ou_json = self._html2json_ou(ou_src)




