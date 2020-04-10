from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from datetime import datetime, timedelta
from typing import List
from calendar import monthrange
import logging


"""
GameDriver is a class that uses selenium webdrivers to get a list of
games from ESPN given a range of dates.

"""


class GameDriver:
    def __init__(self, url, season_start, season_end, options):
        self.driver = webdriver.Firefox(options=options)
        self.base_url = url
        self.start = season_start
        self.end = season_end

    def get_games_daterange(self, start: datetime, end: datetime) -> List[str]:
        if start > end:
            raise ValueError("start date cannot be later than end date")
        game_links = []
        d = self._get_dates(start, end)
        d = self._trim_dates(d)
        for date in d:
            logging.debug(f"getting game urls for {date}")
            game_links.extend(self._get_games_url(self._date_to_url))

    def get_games_seasons(self, start: int, end: int) -> List[str]:
        game_links = []
        for i in range((end - start) + 1):
            dates = self._season_to_dates(start + i)
        for d in dates:
            logging.debug(f"getting game urls for {d}")
            game_links.extend(self._get_games_url(self._date_to_url(d)))
        return game_links

    def _date_to_url(self, d: datetime) -> str:
        return f"{self.base_url}{d.year}{d.month :02d}{d.day :02d}"

    def _get_games_url(self, url: str) -> List[str]:
        self.driver.get(url)
        l = self.driver.find_elements_by_xpath('//a[@class="mobileScoreboardLink"]')
        out = [i.get_attribute("href") for i in l]
        d = url.split("/")[-1]
        logging.debug(f"found {len(out)} games on {d}")
        return out

    @staticmethod
    def _get_dates(start: datetime, end: datetime) -> List[datetime]:
        d = (end + timedelta(days=1) - start).days
        return [start + timedelta(days=i) for i in range(d)]

    def _season_to_dates(self, season) -> List[datetime]:
        start = datetime(season, self.start, 1)
        if self.start < self.end:
            end = datetime(season, self.end, monthrange(season, self.end)[1])
        else:
            end = datetime(season + 1, self.end, monthrange(season + 1, self.end)[1])
        return self._get_dates(start, end)

    def _trim_dates(self, dates: List[datetime]) -> List[datetime]:
        if self.end < self.start:
            return [d for d in dates if d.month < self.end or d.month > self.start]
        else:
            return [d for d in dates if d.month < self.end and d.month > self.start]


options = Options()
options.headless = True
u = "https://www.espn.com/nba/scoreboard/_/date/"
a = GameDriver(u, 10, 4, options)

try:
    a.get_games_seasons(2016, 2017)
except Exception:
    print("failed")
    a.driver.close()
