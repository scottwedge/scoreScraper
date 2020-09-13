import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from typing import List, Dict
import re

from game_crawlers.nba.fields import (
    Game,
    Record,
    Line,
    Team,
    Player,
    PlayerStats,
    TeamStats,
)


class NBAESPNSpider(scrapy.Spider):
    name = "nba_boxscores"

    def __init__(self, ids: List[int], *args, **kwargs):
        super(NBAESPNSpider, self).__init__(*args, **kwargs)
        self.game_ids = ids

    @staticmethod
    def get_urls(game_id: int):
        return {
            "gamecast": f"https://www.espn.com/nba/game?gameId={game_id}",
            "boxscore": f"https://www.espn.com/nba/boxscore?gameId={game_id}",
            "teamstats": f"https://www.espn.com/nba/matchup?gameId={game_id}",
        }

    def start_requests(self):
        for g in self.game_ids:
            urls = self.get_urls(g)
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
                url=urls["teamstats"],
                callback=self.parse_teamstats,
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

        bet_info = response.xpath('//div[@class="odds-details"]//li').getall()
        game_line = (
            self.new_line(bet_info)
            if bet_info
            else Line(favorite="n/a", spread=0, ou=0)
        )

        game = Game(game_id=game_id)
        game["date"] = game_time
        game["home_record"] = dict(home_record)
        game["home_home_record"] = dict(home_home_record)
        game["away_record"] = dict(away_record)
        game["away_away_record"] = dict(away_away_record)
        game["line"] = dict(game_line)
        return {"type": "game", "game_id": game_id, "data": dict(game)}

    # parse_matchup parses the nba matchup tab and returns team summary statistics
    def parse_teamstats(self, response, game_id):
        fields = TeamStats().fields

        away_html_str = response.xpath(
            '//div[@class="team away"]//a[@class="team-name"]'
        ).get()
        if away_html_str is None:
            away_html_str = response.xpath(
                '//div[@class="team away"]//div[@class="team-name"]'
            ).get()
        away_team = self.new_team(away_html_str)

        home_html_str = response.xpath(
            '//div[@class="team home"]//a[@class="team-name"]'
        ).get()
        if home_html_str is None:
            home_html_str = response.xpath(
                '//div[@class="team home"]//div[@class="team-name"]'
            ).get()
        home_team = self.new_team(home_html_str)

        away_score = response.xpath(
            '//div[@class="team away"]//div[@class="score-container"]'
        ).re_first(r"[0-9]{2,3}")
        home_score = response.xpath(
            '//div[@class="team home"]//div[@class="score-container"]'
        ).re_first(r"[0-9]{2,3}")

        team_stat_strings = response.xpath("//tr[@data-stat-attr]").getall()

        away_team_stat = TeamStats(
            team=dict(away_team), game_id=game_id, pts=away_score, home=False
        )
        home_team_stat = TeamStats(
            team=dict(home_team), game_id=game_id, pts=home_score, home=True
        )

        stats_dict = self.new_team_stats(team_stat_strings)
        # work through stats and set default value if stat not found

        no_default = ["team", "game_id", "home", "pts"]
        for field in fields:
            if field not in no_default:
                home_team_stat[field] = stats_dict.get("home").get(field, 0)
                away_team_stat[field] = stats_dict.get("away").get(field, 0)

        team_stats = dict()
        team_stats["home_stats"] = dict(home_team_stat)
        team_stats["away_stats"] = dict(away_team_stat)
        return {"type": "team_stats", "game_id": game_id, "data": team_stats}

    # parse_boxscore parses the nba boxscore html page and returns lists of player stats.
    def parse_boxscore(self, response, game_id: str):
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
        player_stats = dict()
        player_stats["home_stats"] = home_team_stats
        player_stats["away_stats"] = away_team_stats
        return {"type": "player_stats", "game_id": game_id, "data": player_stats}

    def new_team_stats(self, team_stat: List[str]) -> Dict:
        stat_map = {
            "fieldGoalsMade": "fgm",
            "fieldGoalsAttempted": "fga",
            "fieldGoalPct": "fg_per",
            "threePointFieldGoalsMade": "x3pm",
            "threePointFieldGoalsAttempted": "x3pa",
            "threePointFieldGoalPct": "x3p_per",
            "freeThrowsMade": "ftm",
            "freeThrowsAttempted": "fta",
            "freeThrowPct": "ft_per",
            "totalRebounds": "reb",
            "offensiveRebounds": "oreb",
            "defensiveRebounds": "dreb",
            "assists": "ast",
            "steals": "stl",
            "blocks": "blk",
            "totalTurnovers": "to",
            "turnoverPoints": "pts_off_to",
            "fastBreakPoints": "fast_break_pts",
            "pointsInPaint": "points_in_paint",
            "fouls": "pf",
            "technicalFouls": "technical",
            "flagrantFouls": "flagrant",
            "largestLead": "largest_lead",
        }

        shot_list = [
            "fieldGoalsMade-fieldGoalsAttempted",
            "threePointFieldGoalsMade-threePointFieldGoalsAttempted",
            "freeThrowsMade-freeThrowsAttempted",
        ]

        stat_re = r"data-stat-attr.*\"(?P<stat>[a-zA-Z-]*)\".*>(?P<away>[0-9-]+).*>(?P<home>[0-9-]+)"
        combined_stat_dict = {"home": dict(), "away": dict()}

        for s in team_stat:
            # remove whitespace characters so regex works
            s = re.sub(r"[\s]", "", s)
            stats = re.search(stat_re, s)

            if stats.group("stat") in shot_list:
                stat_made, stat_attempt = self.split_stat_name(stats.group("stat"))
                home_made_val, home_att_val = self.split_shots(stats.group("home"))
                away_made_val, away_att_val = self.split_shots(stats.group("away"))
                mapped_stat_made = stat_map.get(stat_made)
                mapped_stat_att = stat_map.get(stat_attempt)
                combined_stat_dict["home"][mapped_stat_made] = home_made_val
                combined_stat_dict["home"][mapped_stat_att] = home_att_val
                combined_stat_dict["away"][mapped_stat_made] = away_made_val
                combined_stat_dict["away"][mapped_stat_att] = away_att_val

            else:
                mapped_stat = stat_map.get(stats.group("stat"))
                combined_stat_dict["home"][mapped_stat] = stats.group("home")
                combined_stat_dict["away"][mapped_stat] = stats.group("away")

        return combined_stat_dict

    @staticmethod
    def split_stat_name(stat: str) -> tuple:
        s = stat.split("-")
        return (s[0], s[1])

    @staticmethod
    def split_shots(shots: str) -> tuple:
        s = shots.split("-")
        return (s[0], s[1])

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
            try:
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
                pm = re.search(r"\"plusminus\">\+{0,1}([0-9-]{1,3})", line).group(1)
                p_stat_kwargs["plusminus"] = pm if (pm != "--") else 0
            except AttributeError:
                pass

            ps = PlayerStats()

            # work through stats and set default value if stat not found
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
        if record is not None:
            r = record.split("-")
            return Record(losses=r[0], wins=r[1])
        return Record()

    # new_team parses the team html string, including location, full name, and abbreviation
    @staticmethod
    def new_team(html_str: str) -> Team:
        team_re = r">([A-Za-z0-9/ ]+)<"
        out = re.findall(team_re, html_str)
        return Team(location=out[0], name=out[1], abbreviation=out[2],)

    # new_line returns the over/under and spread information for a game
    @staticmethod
    def new_line(html_list: List[str]) -> Line:
        even_re = r"EVEN"
        line_re = r"([A-Z]{2,3} [0-9-.]+)"
        ou_re = r"([0-9]{2,3})"
        line_fav = None
        spread = None
        o = None
        for l in html_list:
            if re.search("Line", l):
                if re.search(even_re, l):
                    line_fav = "EVEN"
                    spread = 0
                else:
                    line = re.search(line_re, l)
                    if line is None:
                        line_fav = None
                        spread = None
                    else:
                        line_split = line.group(0).split()
                        line_fav = line_split[0]
                        spread = float(line_split[1])
            elif re.search("Over/Under", l):
                ou = re.search(ou_re, l)
                if ou is None:
                    o = None
                else:
                    o = int(ou.group(0))
        return Line(favorite=line_fav, spread=spread, ou=o)
