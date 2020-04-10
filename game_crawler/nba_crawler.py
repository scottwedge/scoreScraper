import scrapy
from scrapy.crawler import CrawlerProcess
from typing import List
import re

GAMEID = 401071116


def get_urls(game_id: int):
    return {
        "gamecast": f"https://www.espn.com/nba/game?gameId={game_id}",
        "player": f"https://www.espn.com/nba/boxscore?gameId={game_id}",
        "team": f"https://www.espn.com/nba/matchup?gameId={game_id}",
    }


class Record:
    def __init__(self, wins: int, losses: int):
        self.wins = wins
        self.losses = losses


class Line:
    def __init__(self, favorite: str, line: int, ou: int):
        self.favorite = favorite
        self.line = line
        self.ou = ou


class Game:
    def __init__(self, **kwargs):
        allowed_keys = set(
            [
                "date",
                "home_record",
                "home_home_record",
                "away_record",
                "away_away_record",
                "line",
            ]
        )
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)
        self.team_stats = []
        self.player_stats = []

    def add_team_stat(self, stats):
        self.team_stats.append(stats)
    
    def add_player_stat(self, stats):
        self.player_stats.append(stats)

class Team:
    def __init__(self, **kwargs):
        allowed_keys = set(
            [
                "location",
                "name",
                "abbreviation",
            ]
        )
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)


class TeamStats:
    def __init(self, **kwargs):
        pass


class Player:
    def __init__(self, **kwargs):
        pass


class PlayerStats:
    def __init__(self, **kwargs):
        pass


class NBASpider(scrapy.Spider):
    name = "nba_boxscores"

    def __init__(self, ids: List[int], *args, **kwargs):
        super(NBASpider, self).__init__(*args, **kwargs)
        self.game_ids = ids

    def start_requests(self):
        for g in self.game_ids:
            urls = get_urls(g)

            yield scrapy.Request(url=urls["gamecast"], callback=self.parse_game)
            yield scrapy.Request(url=urls["player"], callback=self.parse_player)
            yield scrapy.Request(url=urls["team"], callback=self.parse_player)

    # Parses game information located in the gamecast tab of a game ESPN recorded
    def parse_game(self, response):
        record_re = r'[0-9]{1,2}-[0-9]{1,2}'
        time_re = r'data-date=\"([A-Z0-9-:]*)\"'

        away_name = self.new_team(response.xpath(
            '//div[@class="team away"]//a[@class="team-name"]'
        ).get())

        away_record = self.new_record(response.xpath(
            '//div[@class="team away"]//div[@class="record"]'
        ).re_first(record_re))

        away_away_record = self.new_record(response.xpath(
            '//div[@class="team away"]//div[@class="record"]/span[@class="inner-record"]'
        ).re_first(record_re))

        home_name = self.new_team(response.xpath(
            '//div[@class="team home"]//a[@class="team-name"]'
        ).get())

        home_record = self.new_record(response.xpath(
            '//div[@class="team home"]//div[@class="record"]'
        ).re_first(record_re))

        home_home_record = self.new_record(response.xpath(
            '//div[@class="team home"]//div[@class="record"]/span[@class="inner-record"]'
        ).re_first(record_re))

        game_time = response.xpath(
            '//div[@class="game-date-time"]//span[@data-date]'
        ).re_first(time_re)

        game_line =self.new_line(response.xpath('//div[@class="odds-details"]//li').getall())
        
        return Game(
                date = game_time,
                home_record = home_record,
                home_home_record = home_home_record,
                away_record = away_record,
                away_away_record = away_away_record,
                line = game_line
        ).__dict__

    def parse_team(self, response):
        pass

    def parse_player(self, response):
        pass
    
    @staticmethod
    def new_record(record: str):
        r = record.split("-")
        return Record(r[0], r[1])
    
    @staticmethod
    def new_team(html_str:str):
        team_re = r'>([A-Za-z]+)<'
        out = re.findall(team_re, html_str)
        return Team(
            location=out[0],
            name= out[1],
            abbreviation=out[2],
        )
    
    @staticmethod
    def new_line(html_list:str):
        line_re = r'([A-Z]{3} [0-9-.]+)'
        ou_re = r'([0-9]{2,3})'
        line = re.search(line_re, html_list[0])
        ou = re.search(ou_re, html_list[1])
        line_split = line.group(0).split()
        return Line(
            favorite=line_split[0],
            line = float(line_split[1]),
            ou = int(ou.group(0))
        )


process = CrawlerProcess(settings={"COOKIES_ENABLED": False, "DOWNLOAD_DELAY": 2,})

process.crawl(NBASpider, ids=["401071116"])
process.start()
