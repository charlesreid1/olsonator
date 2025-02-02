import os
import re
import json
import time
from datetime import datetime, timedelta
import requests
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
        # If we try to use requests, none of the tables load, and all data is None
        return self._get_page_html_selenium(url)

    def _get_page_html_requests(self, url):
        """
        Use requests to fetch the url,
        then return the HTML source of the loaded page.
        (This is much faster than using Selenium, so use it when possible)
        """
        resp = requests.get(url)
        time.sleep(2)
        src = resp.content
        return src

    def _get_page_html_selenium(self, url):
        """
        Use Selenium webdriver to fetch the url,
        then return the HTML source of the loaded page.
        (This is extremely slow, only use if absolutely necessary)
        """
        ffopt = webdriver.FirefoxOptions()
        ffopt.add_argument("--headless")
        ffopt.set_preference("general.useragent.override", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.1")
        browser = webdriver.Firefox(options=ffopt)
        browser.set_page_load_timeout(4)

        try:
            browser.get(url)
            time.sleep(2)
        except:
            pass

        src = browser.page_source

        try:
            browser.close()
        except:
            pass

        return src

    def _get_datatable(self, html):
        """Get the main DataTables table. Useful b/c we never need the soup otherwise."""
        soup = BeautifulSoup(html, 'html.parser')
        #table = soup.find('table', attrs={"id": "DataTables_Table_0"})
        table = soup.find('table', attrs={"class": "datatable"})
        if table is None:
            raise TeamRankingsParseError("Data table cannot be found on page")
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
        dt = datetime.strptime(game_date_dashes, "%Y-%m-%d")
        t = datetime.now()
        # If we are requesting predictions for tomorrow, it will
        # nominally ask for stats from tomorrow. Use today's date instead.
        if dt > t:
            game_date_dashes = t.strftime("%Y-%m-%d")

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

    def _get_page_html(self, url):
        return self._get_page_html_requests(url)

    def _html2json_sched(self, html):
        """Extract schedule data from HTML and return in JSON format."""
        table = self._get_datatable(html)

        schedule = []

        table_rows = table.find('tbody').find_all('tr')

        if len(table_rows)==0 or "No data available" in table_rows[0].text:
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
                    game['game_url']     = link
                    game['away_team']    = away_team
                    game['home_team']    = home_team
                    game['neutral_site'] = is_neutral
                elif j==3:
                    # time (always eastern time, format is "9:00 PM")
                    # convert to west coast time, format HHMM
                    dt = datetime.strptime(col.text.strip(), "%I:%M %p") - timedelta(hours=3)
                    game['game_time'] = dt.strftime("%H%M")

            if add_game:
                schedule.append(game)

        # This does not save the JSON to a file, only returns it
        return schedule

    def _get_movementtable(self, soup):
        """Get the main movement table on odds pages. Useful b/c we never need the soup otherwise."""
        table = soup.find('table', attrs={"class": "movement-table"})
        if table is None:
            raise TeamRankingsParseError("Odds table cannot be found on game page")
        return table

    def _get_team_abbrs_matchup_menu(self, soup):
        """
        Get team abbreviations from header text.
        Example: "Matchup Menu: TEX @ OSU"
        """
        away_abbr, home_abbr = None, None
        h2s = soup.find_all('h2')
        for h2 in h2s:
            txt = h2.text
            if "Matchup Menu" in txt:
                versus = txt.split(":")[1]
                teams = versus.split(" @ ")
                away_abbr = teams[0].strip()
                home_abbr = teams[1].strip()
        return away_abbr, home_abbr

    def _html2json_g(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        away_score, home_score = None, None
        tables = soup.find_all('table', attrs={'class': 'matchup-table'})
        for table in tables:
            header1 = table.find('tr').find('th')
            if "Final Score" in header1.text:
                rows = table.find('tbody').find_all('tr')
                away_row, home_row = rows[0], rows[1]

                away_cols, home_cols = away_row.find_all('td'), home_row.find_all('td')
                try:
                    away_score = int(away_cols[3].text)
                    home_score = int(home_cols[3].text)
                except IndexError:
                    msg = "Could not find game outcome in table"
                    raise TeamRankingsParseError(msg)

        outcome = {}
        outcome['away_score'] = away_score
        outcome['home_score'] = home_score
        return outcome

    def _html2json_ml(self, html):
        """Extract moneyline odds data from HTML, and send to JSON"""
        soup = BeautifulSoup(html, 'html.parser')
        away_abbr, home_abbr = self._get_team_abbrs_matchup_menu(soup)

        odds = {}

        away_ml, home_ml = None, None
        for lab in ['tab-001', 'tab-002']:
            div = soup.find('div', attrs={'id': lab})
            try:
                table = div.find('table')
            except AttributeError:
                msg = "Could not find moneyline odds table"
                raise TeamRankingsParseError(msg)

            cells = table.find('tbody').find('tr').find_all('td')
            
            current, opening_ml = cells[0].text, cells[2].text
            k, current_ml = current.split(" ")

            if k==away_abbr:
                odds['vegas_away_moneyline']         = int(current_ml) 
                odds['vegas_away_moneyline_opening'] = int(opening_ml) 
            elif k==home_abbr:
                odds['vegas_home_moneyline']         = int(current_ml) 
                odds['vegas_home_moneyline_opening'] = int(opening_ml) 

        return odds

    def _html2json_sp(self, html):
        """Extract spread odds data from HTML, and send to JSON"""
        soup = BeautifulSoup(html, 'html.parser')
        away_abbr, home_abbr = self._get_team_abbrs_matchup_menu(soup)

        table = soup.find('table', attrs={"class": "movement-table"})

        try:
            cells = table.find('tr').find_all('td')
        except AttributeError:
            msg = "Could not find spread odds table"
            raise TeamRankingsParseError(msg)

        current, opening_sp = cells[0].text, cells[2].text
        k, current_sp = current.split(" ")

        odds = {}

        if k==away_abbr:
            away_spread = float(current_sp)
            home_spread = -1*float(current_sp)
            away_open   = float(opening_sp) 
            home_open   = -1*float(opening_sp) 
        elif k==home_abbr:
            away_spread = -1*float(current_sp)
            home_spread = float(current_sp)
            away_open   = -1*float(opening_sp)
            home_open   = float(opening_sp)

        odds['vegas_away_spread']         = round(away_spread,1)
        odds['vegas_home_spread']         = round(home_spread,1)
        odds['vegas_away_spread_opening'] = round(away_open,1)
        odds['vegas_home_spread_opening'] = round(home_open,1)

        return odds

    def _html2json_ou(self, html):
        """Extract o/u odds data from HTML, and send to JSON"""
        soup = BeautifulSoup(html, 'html.parser')
        away_abbr, home_abbr = self._get_team_abbrs_matchup_menu(soup)

        table = soup.find('table', attrs={"class": "movement-table"})
        try:
            cells = table.find('tr').find_all('td')
        except AttributeError:
            msg = "Could not find over/under odds table"
            raise TeamRankingsParseError(msg)


        # Format "Total 165.5"
        current, opening_ou = cells[0].text, float(cells[2].text)
        current_ou = float(current.split(" ")[1])

        odds = {}
        odds['vegas_ou_opening'] = round(opening_ou, 1)
        odds['vegas_ou_total']   = round(current_ou, 1)
        return odds

    def fetch_all(self, game_date_dashes, force=False):
        """
        For the given date, download corresponding HTML pages with schedule data,
        scrape the schedule data from the page, and export to JSON file.
        """
        dt = datetime.strptime(game_date_dashes, "%Y-%m-%d")
        t = datetime.now()

        # If we are requesting sched data for today/tomorrow,
        # we won't have outcomes, and sched data goes in a different file
        todtom = False
        if dt > t:
            todtom = True

        game_date_nodashes = game_date_dashes.replace("-", "")

        # ----------------------
        # Step 1: Get daily schedule, compile game info plus links to each game
        # (the name below must match backtester _get_schedule_fpath_json())
        if todtom:
            # This is the prefix used for game data when we don't yet know the outcome (fwdtest)
            k = "todtom"
        else:
            # This is the prefix used for game data when we know the outcome (backtest)
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

            # Don't export schedule to JSON file yet, first get odds data

        else:
            # Load existing schedule data
            with open(fpath, 'r') as f:
                sched_json = json.load(f)

        # ----------------------
        # Step 2: Gather results and odds for each game (requires visiting multiple links)
        for game in sched_json:
            if 'odds' in game.keys():
                # Game already has odds data in it, so skip
                continue

            game_descr = f"{game['away_team']} @ {game['home_team']} ({game['game_date']})"

            # -------------
            # 2a) Results
            # If today/tomorrow game, no need to get game outcome
            if not todtom:
                if self.nohush:
                    print(f"Retrieving TeamRankings.com outcome data for {game_descr}")

                game_url = game['game_url']

                # Get the game page, to get the final score
                g_src = self._get_page_html(game_url)

                try:
                    g_json = self._html2json_g(g_src)
                except TeamRankingsParseError:
                    # Could not find outcome of game
                    if self.nohush:
                        print(f"Could not find outcome of game {game_descr}, skipping")
                    continue

                # Game outcome gets copied directly into game dict
                for k, v in g_json.items():
                    game[k] = v

            # -------------
            # 2b) Odds

            if self.nohush:
                print(f"Retrieving TeamRankings.com odds data for {game_descr}")

            # Now get each odds page
            try:
                ml_src = self._get_page_html(game_url + "/money-line-movement")
                ml_json = self._html2json_ml(ml_src)
            except TeamRankingsParseError:
                ml_json = {}

            try:
                sp_src = self._get_page_html(game_url + "/spread-movement")
                sp_json = self._html2json_sp(sp_src)
            except TeamRankingsParseError:
                sp_json = {}

            try:
                ou_src = self._get_page_html(game_url + "/over-under-movement")
                ou_json = self._html2json_ou(ou_src)
            except TeamRankingsParseError:
                ou_json = {}

            # Game odds get copied into "odds" sub-dict
            game['odds'] = {}
            game['odds']['moneyline'] = ml_json
            game['odds']['spread']    = sp_json
            game['odds']['ou']        = ou_json

            # Save some time by dumping schedule each time we have added new odds data to one game
            with open(fpath, 'w') as f:
                json.dump(sched_json, f, indent=4)

        # ----------------------
        # Step 3: Final dump of game info plus odds data
        with open(fpath, 'w') as f:
            json.dump(sched_json, f, indent=4)

