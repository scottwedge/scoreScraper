import scrapy
from scrapy.crawler import CrawlerProcess
from typing import List

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
        self.date = kwargs.get("date", None)
        self.home_record = kwargs.get("home_record", None)
        self.home_home_record = kwargs.get("home_home_record", None)
        self.away_record = kwargs.get("away_record", None)
        self.away_away_record = kwargs.get("away_record", None)
        self.line = kwargs.get("line", None)
        self.team_stats = kwargs.get("team_stats", [])
        self.player_stats = kwargs.get("player_stats", [])

class Team:
    def __init__(self, **kwargs):
        pass

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

            yield scrapy.Request(url=urls["gamecast"], callback=self.parse_gamecast)
            yield scrapy.Request(url=urls["player"], callback=self.parse_player)
            yield scrapy.Request(url=urls["team"], callback=self.parse_player)

    def parse_gamecast(self, response):
        away_name = response.xpath(
            '//div[@class="team away"]//a[@class="team-name"]'
        ).get()
        away_record = response.xpath(
            '//div[@class="team away"]//div[@class="record"]'
        ).get()
        home_name = response.xpath(
            '//div[@class="team home"]//a[@class="team-name"]'
        ).get()
        home_record = response.xpath(
            '//div[@class="team home"]//div[@class="record"]'
        ).get()
        game_time = response.xpath(
            '//div[@class="game-date-time"]//span[@data-date]'
        ).get()
        odd_details = response.xpath('//div[@class="odds-details"]').get()
        print(away_name)

    def parse_team(self, response):
        pass

    def parse_player(self, response):
        pass


process = CrawlerProcess(settings={"COOKIES_ENABLED": False, "DOWNLOAD_DELAY": 2,})

process.crawl(NBASpider, ids=["401071116"])
process.start()
