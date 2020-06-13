from selenium import webdriver
from selenium.webdriver import DesiredCapabilities, FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
from typing import List
from itertools import chain
import re
import os
import json
from calendar import monthrange
from datetime import datetime

from nba_seasons import Seasons


"""
GameDriver is a class that uses selenium webdrivers to get a list of
games from ESPN given a range of dates.
"""


class GameDriver:
    def __init__(self, url, options):
        self.driver = webdriver.Firefox(options=options)
        self.driver.set_page_load_timeout(30)
        self.base_url = url

    def get_games_daterange(self, start: datetime, end: datetime) -> List[str]:
        if start > end:
            raise ValueError("start date cannot be later than end date")
        d = self._get_dates(start, end)
        for date in d:
            print(f"getting game urls for {date}")
            games = self._get_games_url(date)
            self.write_to_file(games, date)

    def _date_to_url(self, d: datetime) -> str:
        return f"{self.base_url}{d.year}{d.month :02d}{d.day :02d}"

    def _get_games_url(self, date: str) -> List[str]:
        retry = 0
        t = datetime.now()
        u = self._date_to_url(date)
        while retry < 3:
            try:
                self.driver.get(u)
                retry = 3
            except TimeoutException:
                print("timed out, retrying")
                retry += 1
            except Exception as e:
                print(e)
                retry = 3

        l = self.driver.find_elements_by_xpath('//a[@class="mobileScoreboardLink"]')
        out = [re.findall(r"gameId=([0-9]+)", i.get_attribute("href")) for i in l]
        print(
            f"found {len(out)} games on {date} - call took {(datetime.now() - t).seconds} seconds"
        )
        return list(chain.from_iterable(out))

    @staticmethod
    def _get_dates(start: datetime, end: datetime) -> List[datetime]:
        d = (end + timedelta(days=1) - start).days
        return [start + timedelta(days=i) for i in range(d)]

    @staticmethod
    def _dt_to_str(date: datetime) -> str:
        return f"game_ids_{date.year}{date.month}{date.day}"

    def write_to_file(self, games: dict, date: datetime):
        if not os.path.exists("game_ids"):
            os.makedirs("game_ids")
        with open(os.path.join("game_ids_", f"{self._dt_to_str(date)}.json"), "w") as f:
            json.dump(games, f)
        print(f"wrote game ids for {date} to file")


if __name__ == "__main__":
    game_id_dict = {}
    options = Options()
    options.headless = True
    u = "https://www.espn.com/nba/scoreboard/_/date/"
    g_driver = GameDriver(u, options)
    for k in Seasons.season_info.keys():
        game_id_dict[k] = dict()
        try:
            g_driver.get_games_daterange(
                Seasons.season_info[k].get("regular_season_start"),
                Seasons.season_info[k].get("regular_season_end"),
            )
            g_driver.get_games_daterange(
                Seasons.season_info[k].get("post_season_start"),
                Seasons.season_info[k].get("post_season_end"),
            )
        except Exception as e:
            print(e)
            print(f"failed to get game_ids for season {k}")
    g_driver.driver.close()
    with open("game_ids.json", "w") as f:
        json.dump(game_id_dict, f)
    print("wrote game ids to file")
