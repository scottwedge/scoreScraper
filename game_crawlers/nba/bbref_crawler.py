from scrapy import Spider, Request
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from typing import List, Dict
import re
from datetime import datetime, timedelta

from game_crawlers.nba.seasons import Seasons
from game_crawlers.nba.fields import (
    Game,
    Record,
    Line,
    Team,
    Player,
    PlayerStats,
    TeamStats,
)


class BBRefScoreboard:
    """
    Class to pull list of dates that NBA games were played using range for regular and post season
    schedules. Some games may still be empty, but get_scoreboard_urls() will return the urls for 
    all days where a game possibly occured.
    """

    def __init__(self):
        pass

    def get_scoreboard_urls(self):
        url_list = list()
        for _, v in Seasons.season_info.items():
            url_list = url_list + list(
                self._get_bbref_url(v["regular_season_start"], v["regular_season_end"])
            )
            url_list = url_list + list(
                self._get_bbref_url(v["post_season_start"], v["post_season_end"])
            )
        return url_list

    def get_urls_date(self, date: datetime):
        return f"https://www.basketball-reference.com/boxscores/?month={date.month}&day={date.day}&year={date.year}"

    def _get_bbref_url(self, start, end):
        for d in self._get_dates(start, end):
            yield f"https://www.basketball-reference.com/boxscores/?month={d.month}&day={d.day}&year={d.year}"

    @staticmethod
    def _get_dates(start: datetime, end: datetime) -> List[datetime]:
        d = (end + timedelta(days=1) - start).days
        return [start + timedelta(days=i) for i in range(d)]


class BBRefSpider(Spider):
    """
    Scrapy Spider that handles all logic for parsing the scoreboard page and then the boxscore
    for basketball-reference website games. 
    """

    name = "nba_boxscores"
    base_url = "https://www.basketball-reference.com"

    def __init__(self, urls: List[str], *args, **kwargs):
        super(BBRefSpider, self).__init__(*args, **kwargs)
        self.urls = urls

    def start_requests(self):
        for l in self.urls:
            yield Request(
                url=l, callback=self.parse_scoreboard,
            )

    def parse_scoreboard(self, response):
        games = response.xpath('//p[@class="links"]/a/@href').extract()
        for g in games:
            if re.search(r"boxscores/[0-9]", g):
                game_id = re.search(r'boxscores/([0-9A-Z])*.html', g).group(1)
                yield Request(
                    url=g, 
                    callback=self.parse_boxscore,
                    cb_kwargs=dict(game_id=game_id),
                )

    def parse_boxscore(self, response, game_id):
        game = self.get_game_information(response, game_id)
        team_stats = self.get_team_stats(response, game_id)
        player_stats = self.get_player_stats(response, game_id)

        return {
            "game_data": game,
            "team_stats": team_stats,
            "player_stats": player_stats,
            }

    def get_game_information(self, response, game_id):
        date_str = response.xpath('//div[@class="scorebox_meta"]').re_first(r'[0-9]{1,2}:[0-9]{2}.*[0-9]{4}')
        date = self.parse_date(date_str)

        records = response.xpath('//div[@class="scorebox"]/div/div').re(r'[0-9]{1,2}-[0-9]{1,2}')
        scores = response.xpath('//div[@class="scorebox"]/div/div[@class="scores"]').re('[0-9]{2,3}')

        ar, hr = self.get_away_home_records(records, scores)

        return Game(game_id = game_id, date = date, home_record = hr, away_record = ar)
    
    def get_team_stats(self, response, game_id: str):
        # team_information contains len = 2 list of strings with team name information
        team_information = response.xpath("//strong/a[@itemprop='name']").getall()

        # regex parses <a href="/teams/POR/2006.html" itemprop="name">Portland Trail Blazers</a> into groups
        # POR -> "abbr", Portland Trail Blazers -> "name"
        away = re.search(r'teams/(?P<abbr>[A-Z]{3}).*>(?P<name>[A-Za-z ]+)<', team_information[0])
        home = re.search(r'teams/(?P<abbr>[A-Z]{3}).*>(?P<name>[A-Za-z ]+)<', team_information[1])

        away_team = Team( name = away.group("name"), abbreviation = away.group("abbr"))
        home_team = Team(name = home.group("name"), abbreviation = home.group("abbr"))

        away_stats = self.parse_team_stats(response, away.group("abbr"))
        home_stats = self.parse_team_stats(response, home.group("abbr"))

        away_stat_obj = TeamStats(team = dict(away_team), game_id = game_id)
        home_stat_obj = TeamStats(team = dict(home_team), game_id = game_id)

        return {"home_stats": dict(home_team_stats), "away_stats": dict(away_team_stats)}
    

    def get_player_stats(self, response):
        pass

    def parse_team_stats(self, response, team_abbr: str):
        # xpath is dynamically named after the teams abbreviation, so that needs to get passed into the 
        # function so that we can accurately pull statistics. Team stats are found in foot of table
        # and xpath will return a list of stats to parse
        basic_xpath_str = '//table[@id="box-' + team_abbr + '-game-basic"]//tfoot//td'
        advanced_xpath_str = '//table[@id="box-' + team_abbr + '-game-advanced"]//tfoot//td'

        # something is strange with the html in the four_fact and scoreline tables, scrapy
        # is unable to find the link when referencing the id directly to the table. The
        # current workaround will use the string comment from the section above the table
        # which has all the required data.
        four_factor_xpath = '//div[@id="all_four_factors"]/comment()'
        scoreline_xpath = '//div[@id="all_line_score"]/comment()'

        basic_box = response.xpath(basic_xpath_str).getall()
        advanced_box = response.xpath(advanced_xpath_str).getall()
        four_factor = response.xpath(four_factor_xpath).get()
        scoreline = response.xpath(scoreline_xpath).get()

        team_stat_dict = {}
        team_stat_dict.update(self.parse_basic_box(basic_box))
        team_stat_dict.update(self.parse_advanced_box(advanced_box))
        team_stat_dict.update(self.parse_four_factor(four_factor))
        team_stat_dict.update(self.parse_scoreline(scoreline)) 

        return 

    def parse_player_stats(self, response, team_abbr: str):
        # xpath is dynamically named after the teams abbreviation, so that needs to get passed into the 
        # function so that we can accurately pull statistics. Player stats are found in body of table
        # and xpath will return a list of stats to parse.
        basic_xpath_str = '//table[@id="box-' + team_abbr + '-game-basic"]//tbody/tr[not(@class="thead")]'
        advanced_xpath_str = '//table[@id="box-' + team_abbr + '-game-advanced"]//tbody/tr[not(@class="thead")]'

    @staticmethod
    def parse_basic_box(basic_box: str) -> dict:
        return {}

    @staticmethod
    def parse_advanced_box(advanced_box: str) -> dict:
        return {}

    @staticmethod
    def parse_four_factor(four_factor: str) -> dict:
        return {}
    
    @staticmethod
    def parse_scoreline(scoreline: str) -> dict:
        return {}

    @staticmethod
    def get_away_home_records(record_string: List[str], scores: List[int]):
        # record_string = ['away_wins-away_losses', 'home_wins'-'home_losses']
        # scores = [away_score, home_score]
        split_away = record_string[0].split("-") # results in ['away_wins', 'away_losses']
        split_home = record_string[1].split("-") # results in ['home_wins', 'home_losses']

        # BasketballReference record includes the result of the game in question
        # we need to determine game winner and update the record values for wins
        # and losses to get an accurate record up to, but not including the current game.
        away_losses = split_away[1] if scores[0] > scores[1] else split_away[1] - 1
        away_wins = split_away[0] if scores[0] < scores[1] else split_away[0] - 1

        home_losses = split_home[1] if scores[1] > scores[0] else split_home[1] - 1
        home_wins = split_home[0] if scores[1] < scores[0] else split_home[0] - 1

        away_record = Record(wins = away_wins, losses = away_losses)
        home_record = Record(wins = home_wins, losses = home_losses)
        return away_record, home_record

    def parse_date(self, date_str: str) -> datetime:
        return datetime.strptime(date_str, '%I:%M %p, %B %d, %Y')

