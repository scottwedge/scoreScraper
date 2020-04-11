import scrapy
from scrapy.crawler import CrawlerProcess
from typing import List
import re

GAMEID = 401071116


def get_urls(game_id: int):
    return {
        "gamecast": f"https://www.espn.com/nba/game?gameId={game_id}",
        "boxscore": f"https://www.espn.com/nba/boxscore?gameId={game_id}",
        "matchup": f"https://www.espn.com/nba/matchup?gameId={game_id}",
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


class Team:
    def __init__(self, **kwargs):
        allowed_keys = set(["location", "name", "abbreviation",])
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)


class TeamStats:
    def __init(self, **kwargs):
        pass


class Player:
    def __init__(self, **kwargs):
        allowed_keys = set(["player_id", "first_name", "last_name", "position"])
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)


class PlayerStats:
    def __init__(self, **kwargs):
        default_attr = dict(
            player=None,
            min=0,
            fgm=0,
            fga=0,
            fg_per=0,
            x3pa=0,
            x3pm=0,
            x3p_per=0,
            fta=0,
            ftm=0,
            ft_per=0,
            oreb=0,
            dreb=0,
            reb=0,
            ast=0,
            stl=0,
            blk=0,
            to=0,
            pf=0,
            plusminus=0,
            pts=0,
        )

        default_attr.update(kwargs)
        allowed_attr = list(default_attr.keys())
        self.__dict__.update(
            (k, v) for k, v in default_attr.items() if k in allowed_attr
        )


class NBASpider(scrapy.Spider):
    name = "nba_boxscores"

    def __init__(self, ids: List[int], *args, **kwargs):
        super(NBASpider, self).__init__(*args, **kwargs)
        self.game_ids = ids

    def start_requests(self):
        for g in self.game_ids:
            urls = get_urls(g)

            yield scrapy.Request(
                url=urls["gamecast"],
                callback=self.parse_game,
                cb_kwargs=dict(game_id=g),
            )
            yield scrapy.Request(
                url=urls["boxscore"],
                callback=self.parse_boxscore,
                cb_kwargs=dict(game_id=g),
            )
            yield scrapy.Request(
                url=urls["matchup"],
                callback=self.parse_matchup,
                cb_kwargs=dict(game_id=g),
            )

    # Parses game information located in the gamecast tab of a game ESPN recorded
    def parse_game(self, response, game_id):
        record_re = r"[0-9]{1,2}-[0-9]{1,2}"
        time_re = r"data-date=\"([A-Z0-9-:]*)\""

        away_record = self.new_record(
            response.xpath('//div[@class="team away"]//div[@class="record"]').re_first(
                record_re
            )
        )

        away_away_record = self.new_record(
            response.xpath(
                '//div[@class="team away"]//div[@class="record"]/span[@class="inner-record"]'
            ).re_first(record_re)
        )

        home_record = self.new_record(
            response.xpath('//div[@class="team home"]//div[@class="record"]').re_first(
                record_re
            )
        )

        home_home_record = self.new_record(
            response.xpath(
                '//div[@class="team home"]//div[@class="record"]/span[@class="inner-record"]'
            ).re_first(record_re)
        )

        game_time = response.xpath(
            '//div[@class="game-date-time"]//span[@data-date]'
        ).re_first(time_re)

        game_line = self.new_line(
            response.xpath('//div[@class="odds-details"]//li').getall()
        )

        game = Game(
            date=game_time,
            home_record=home_record.__dict__,
            home_home_record=home_home_record.__dict__,
            away_record=away_record.__dict__,
            away_away_record=away_away_record.__dict__,
            line=game_line.__dict__,
        )
        return {"game_id": game_id, "data_group": "game", "data": game.__dict__}

    def parse_matchup(self, response, game_id):
        pass

    def parse_boxscore(self, response, game_id):
        home_team_stats = self.new_players(
            response.xpath(
                '//div[@class="col column-two gamepackage-home-wrap"]//tbody//tr'
            ).getall()
        )
        away_team_stats = self.new_players(
            response.xpath(
                '//div[@class="col column-one gamepackage-away-wrap"]//tbody//tr'
            ).getall()
        )

        return {
            "game_id": game_id,
            "type": "boxscore",
            "data": {"home": home_team_stats, "away": away_team_stats},
        }

    @staticmethod
    def new_players(boxscore: List[str]) -> List[PlayerStats]:
        name_re = r"id/(?P<pid>[0-9]+)/(?P<first>[a-z]+)-(?P<last>[a-z]+).*position\">(?P<pos>[A-Z]{1,2})"
        dnp_re = r"DNP"

        players = list()
        for line in boxscore:
            re_name = re.search(name_re, line)
            if not re_name:
                continue
            player = Player(
                player_id=re_name.group("pid"),
                first_name=re_name.group("first"),
                last_name=re_name.group("last"),
                position=re_name.group("pos"),
            )
            p_stat_kwargs = {"player": player.__dict__}

            if not re.search(dnp_re, line):
                ft_re = re.search(r"\"ft\">(?P<m>[0-9]{1,2})-(?P<a>[0-9]{1,2})", line)
                x3p_re = re.search(r"\"3pt\">(?P<m>[0-9]{1,2})-(?P<a>[0-9]{1,2})", line)
                fg_re = re.search(r"\"fg\">(?P<m>[0-9]{1,2})-(?P<a>[0-9]{1,2})", line)
                p_stat_kwargs["fta"] = int(ft_re.group("a"))
                p_stat_kwargs["ftm"] = int(ft_re.group("m"))
                if p_stat_kwargs["fta"] != 0:
                    p_stat_kwargs["ft_per"] = int(ft_re.group("m")) / int(
                        ft_re.group("a")
                    )
                else:
                    p_stat_kwargs["ft_per"] = 0
                p_stat_kwargs["fga"] = int(fg_re.group("a"))
                p_stat_kwargs["fgm"] = int(fg_re.group("m"))
                if p_stat_kwargs["fga"] != 0:
                    p_stat_kwargs["fg_per"] = int(fg_re.group("m")) / int(
                        fg_re.group("a")
                    )
                else:
                    p_stat_kwargs["fg_per"] = 0
                p_stat_kwargs["x3pa"] = int(x3p_re.group("a"))
                p_stat_kwargs["x3pm"] = int(x3p_re.group("m"))
                if p_stat_kwargs["x3pa"] != 0:
                    p_stat_kwargs["x3p_per"] = int(x3p_re.group("m")) / int(
                        x3p_re.group("a")
                    )
                else:
                    p_stat_kwargs["x3p_per"] = 0
            ps = PlayerStats(**p_stat_kwargs)
            players.append(ps.__dict__)

        return players

    @staticmethod
    def new_record(record: str) -> Record:
        r = record.split("-")
        return Record(r[0], r[1])

    @staticmethod
    def new_team(html_str: str) -> Team:
        team_re = r">([A-Za-z]+)<"
        out = re.findall(team_re, html_str)
        return Team(location=out[0], name=out[1], abbreviation=out[2],)

    @staticmethod
    def new_line(html_list: str) -> Line:
        line_re = r"([A-Z]{3} [0-9-.]+)"
        ou_re = r"([0-9]{2,3})"
        line = re.search(line_re, html_list[0])
        ou = re.search(ou_re, html_list[1])
        line_split = line.group(0).split()
        return Line(
            favorite=line_split[0], line=float(line_split[1]), ou=int(ou.group(0))
        )


process = CrawlerProcess(settings={"COOKIES_ENABLED": False, "DOWNLOAD_DELAY": 2,})

process.crawl(NBASpider, ids=["401071116"])
process.start()
