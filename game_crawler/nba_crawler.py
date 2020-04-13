import scrapy
from scrapy.crawler import CrawlerProcess
from typing import List
import re

GAMEID = 401071116


class Game(scrapy.Item):
    game_id = scrapy.Field()
    date = scrapy.Field()
    home_record = scrapy.Field()
    home_home_record = scrapy.Field()
    away_record = scrapy.Field()
    away_away_record = scrapy.Field()
    line = scrapy.Field()
    team_stats = scrapy.Field()
    player_stats = scrapy.Field()


class Record(scrapy.Item):
    wins = scrapy.Field()
    losses = scrapy.Field()


class Line(scrapy.Item):
    favorite = scrapy.Field()
    spread = scrapy.Field()
    ou = scrapy.Field()


class Team(scrapy.Item):
    location = scrapy.Field()
    name = scrapy.Field()
    abbreviation = scrapy.Field()


class TeamStats(scrapy.Item):
    team = scrapy.Field()
    game_id = scrapy.Field()
    fgm = scrapy.Field()
    fga = scrapy.Field()
    fg_per = scrapy.Field()
    x3pa = scrapy.Field()
    x3pm = scrapy.Field()
    x3p_per = scrapy.Field()
    fta = scrapy.Field()
    ftm = scrapy.Field()
    ft_per = scrapy.Field()
    oreb = scrapy.Field()
    dreb = scrapy.Field()
    reb = scrapy.Field()
    ast = scrapy.Field()
    stl = scrapy.Field()
    blk = scrapy.Field()
    to = scrapy.Field()
    pts_off_to = scrapy.Field()
    fast_break_pts = scrapy.Field()
    points_in_paint = scrapy.Field()
    pf = scrapy.Field()
    technical = scrapy.Field()
    flagrant = scrapy.Field()
    pts = scrapy.Field()


class Player(scrapy.Item):
    player_id = scrapy.Field()
    first_name = scrapy.Field()
    last_name = scrapy.Field()
    position = scrapy.Field()


class PlayerStats(scrapy.Item):
    player = scrapy.Field()
    game_id = scrapy.Field()
    min = scrapy.Field()
    fgm = scrapy.Field()
    fga = scrapy.Field()
    fg_per = scrapy.Field()
    x3pa = scrapy.Field()
    x3pm = scrapy.Field()
    x3p_per = scrapy.Field()
    fta = scrapy.Field()
    ftm = scrapy.Field()
    ft_per = scrapy.Field()
    oreb = scrapy.Field()
    dreb = scrapy.Field()
    reb = scrapy.Field()
    ast = scrapy.Field()
    stl = scrapy.Field()
    blk = scrapy.Field()
    to = scrapy.Field()
    pf = scrapy.Field()
    plusminus = scrapy.Field()
    pts = scrapy.Field()


# class Record:
#     def __init__(self, wins: int, losses: int):
#         self.wins = wins
#         self.losses = losses


# class Line:
#     def __init__(self, favorite: str = None, line: int = 0, ou: int = 0):
#         self.favorite = favorite
#         self.line = line
#         self.ou = ou


# class Game:
#     def __init__(self, **kwargs):
#         allowed_keys = set(
#             [
#                 "date",
#                 "home_record",
#                 "home_home_record",
#                 "away_record",
#                 "away_away_record",
#                 "line",
#             ]
#         )
#         self.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)


# class Team:
#     def __init__(self, **kwargs):
#         allowed_keys = set(["location", "name", "abbreviation",])
#         self.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)


# class TeamStats:
#     def __init(self, **kwargs):
#         default_attr = dict(
#             team=None,
#             game_id=None,
#             fgm=0,
#             fga=0,
#             fg_per=0,
#             x3pa=0,
#             x3pm=0,
#             x3p_per=0,
#             fta=0,
#             ftm=0,
#             ft_per=0,
#             oreb=0,
#             dreb=0,
#             reb=0,
#             ast=0,
#             stl=0,
#             blk=0,
#             to=0,
#             pf=0,
#             pts=0,
#         )

#         default_attr.update(kwargs)
#         allowed_attr = list(default_attr.keys())
#         self.__dict__.update(
#             (k, v) for k, v in default_attr.items() if k in allowed_attr
#         )


# class Player:
#     def __init__(self, **kwargs):
#         allowed_keys = set(["player_id", "first_name", "last_name", "position"])
#         self.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)


# class PlayerStats:
#     def __init__(self, **kwargs):
#         default_attr = dict(
#             player=None,
#             game_id=None,
#             min=0,
#             fgm=0,
#             fga=0,
#             fg_per=0,
#             x3pa=0,
#             x3pm=0,
#             x3p_per=0,
#             fta=0,
#             ftm=0,
#             ft_per=0,
#             oreb=0,
#             dreb=0,
#             reb=0,
#             ast=0,
#             stl=0,
#             blk=0,
#             to=0,
#             pf=0,
#             plusminus=0,
#             pts=0,
#         )

#         default_attr.update(kwargs)
#         allowed_attr = list(default_attr.keys())
#         self.__dict__.update(
#             (k, v) for k, v in default_attr.items() if k in allowed_attr
#         )


class NBASpider(scrapy.Spider):
    name = "nba_boxscores"

    def __init__(self, ids: List[int], *args, **kwargs):
        super(NBASpider, self).__init__(*args, **kwargs)
        self.game_ids = ids

    @staticmethod
    def get_urls(game_id: int):
        return {
            "gamecast": f"https://www.espn.com/nba/game?gameId={game_id}",
            "boxscore": f"https://www.espn.com/nba/boxscore?gameId={game_id}",
            "matchup": f"https://www.espn.com/nba/matchup?gameId={game_id}",
        }

    def start_requests(self):
        for g in self.game_ids:
            urls = self.get_urls(g)
            item = Game()
            item["game_id"] = g
            yield scrapy.Request(
                url=urls["gamecast"],
                callback=self.parse_game,
                cb_kwargs=dict(game_id=g),
                meta={"item": item},
            )
            yield scrapy.Request(
                url=urls["boxscore"],
                callback=self.parse_boxscore,
                cb_kwargs=dict(game_id=g),
                meta={"item": item},
            )
            yield scrapy.Request(
                url=urls["matchup"],
                callback=self.parse_matchup,
                cb_kwargs=dict(game_id=g),
                meta={"item": item},
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

        bet_info = response.xpath('//div[@class="odds-details"]//li').getall()
        game_line = self.new_line(bet_info) if bet_info else Line()

        item = response.meta["item"]
        item["date"] = game_time
        item["home_record"] = dict(home_record)
        item["home_home_record"] = dict(home_home_record)
        item["away_record"] = dict(away_record)
        item["away_away_record"] = dict(away_away_record)
        item["line"] = dict(game_line)

    # parse_matchup parses the nba matchup tab and returns team summary statistics
    def parse_matchup(self, response, game_id):
        pass

    # parse_boxscore parses the nba boxscore html page and returns lists of player stats.
    def parse_boxscore(self, response, game_id):
        home_team_stats = self.new_player_stats(
            game_id,
            response.xpath(
                '//div[@class="col column-two gamepackage-home-wrap"]//tbody//tr'
            ).getall(),
        )
        away_team_stats = self.new_player_stats(
            game_id,
            response.xpath(
                '//div[@class="col column-one gamepackage-away-wrap"]//tbody//tr'
            ).getall(),
        )
        item = response.meta["item"]
        item["player_stats"] = {
            "home": home_team_stats,
            "away": away_team_stats,
        }

    # new_player_stats parses the boxscore html table and returns player stats corresponding
    # to each row in the table
    @staticmethod
    def new_player_stats(game_id: int, boxscore: List[str]) -> List[PlayerStats]:
        name_re = r"id/(?P<pid>[0-9]+)/(?P<first>[a-z]+)-(?P<last>[a-z]+).*position\">(?P<pos>[A-Z]{1,2})"

        players = list()
        fields = PlayerStats().fields
        for line in boxscore:
            # find name information on the table row
            re_name = re.search(name_re, line)
            if not re_name:
                continue
            player = Player(
                player_id=re_name.group("pid"),
                first_name=re_name.group("first"),
                last_name=re_name.group("last"),
                position=re_name.group("pos"),
            )
            p_stat_kwargs = {"player": dict(player), "game_id": game_id}

            # check whether play was a DNP and then pull stats
            if not re.search(r"DNP", line):
                # define the regex statements for shooting statistics per line
                ft_re = re.search(r"\"ft\">(?P<m>[0-9]{1,2})-(?P<a>[0-9]{1,2})", line)
                x3p_re = re.search(r"\"3pt\">(?P<m>[0-9]{1,2})-(?P<a>[0-9]{1,2})", line)
                fg_re = re.search(r"\"fg\">(?P<m>[0-9]{1,2})-(?P<a>[0-9]{1,2})", line)

                # parse and calculate shooting fields
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

                # parse general statistic fields
                p_stat_kwargs["min"] = re.search(
                    r"\"min\">{0,1}([0-9]{1,3})", line
                ).group(1)
                p_stat_kwargs["pts"] = re.search(
                    r"\"pts\">{0,1}([0-9]{1,3})", line
                ).group(1)
                p_stat_kwargs["oreb"] = re.search(
                    r"\"oreb\">{0,1}([0-9]{1,3})", line
                ).group(1)
                p_stat_kwargs["dreb"] = re.search(
                    r"\"dreb\">{0,1}([0-9]{1,3})", line
                ).group(1)
                p_stat_kwargs["reb"] = re.search(
                    r"\"reb\">{0,1}([0-9]{1,3})", line
                ).group(1)
                p_stat_kwargs["ast"] = re.search(
                    r"\"ast\">{0,1}([0-9]{1,3})", line
                ).group(1)
                p_stat_kwargs["stl"] = re.search(
                    r"\"stl\">{0,1}([0-9]{1,3})", line
                ).group(1)
                p_stat_kwargs["blk"] = re.search(
                    r"\"blk\">{0,1}([0-9]{1,3})", line
                ).group(1)
                p_stat_kwargs["pf"] = re.search(
                    r"\"pf\">{0,1}([0-9]{1,3})", line
                ).group(1)
                p_stat_kwargs["plusminus"] = re.search(
                    r"\"plusminus\">([0-9-+]{1,3})", line
                ).group(1)


            ps = PlayerStats()
            for k in fields:
                if k not in ["player", "game_id"]:
                    ps[k] = p_stat_kwargs.get(k, 0)
                else:
                    ps[k] = p_stat_kwargs.get(k, None)
            players.append(dict(ps))
        return players

    # new_record splits the record string and returns a Record object.
    @staticmethod
    def new_record(record: str) -> Record:
        r = record.split("-")
        return Record(losses=r[0], wins=r[1])

    # new_team parses the team html string, including location, full name, and abbreviation
    @staticmethod
    def new_team(html_str: str) -> Team:
        team_re = r">([A-Za-z]+)<"
        out = re.findall(team_re, html_str)
        return Team(location=out[0], name=out[1], abbreviation=out[2],)

    # new_line returns the over/under and spread information for a game
    @staticmethod
    def new_line(html_list: str) -> Line:
        line_re = r"([A-Z]{3} [0-9-.]+)"
        ou_re = r"([0-9]{2,3})"
        line = re.search(line_re, html_list[0])
        ou = re.search(ou_re, html_list[1])
        line_split = line.group(0).split()
        return Line(
            favorite=line_split[0], spread=float(line_split[1]), ou=int(ou.group(0))
        )


process = CrawlerProcess(settings={"COOKIES_ENABLED": False, "DOWNLOAD_DELAY": 2,})

process.crawl(NBASpider, ids=["401071116"])
process.start()
