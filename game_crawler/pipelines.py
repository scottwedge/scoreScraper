import json
import scrapy
from db import nba
import os

# TODO add SQL Pipeline instead

USER = os.environ["dbName"]
PASSWORD = os.environ["dbPass"]


class DBWriterPipeline(object):
    data_dict = {}
    set_types = set(["player_stats", "team_stats", "game"])

    def open_spider(self, spider):
        self.db = nba.nbaDB(USER, PASSWORD)
        self.db.create_all(self.db.engine)

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        game = self.data_dict.get(item["game_id"], {})
        game[item["type"]] = item["data"]
        if game.keys() == self.set_types:
            del self.data_dict[item["game_id"]]
            line = json.dumps(game) + "\n"
            self.file.write(line)
        else:
            self.data_dict[item["game_id"]] = game

        return item

    def map_to_db(self, item):
        game_data = item.get("game")
        player_data = item.get("player_stats")
        team_data = item.get("team_stats")
        game = nba.Game(
            id=game_data["game_id"],
            date=game_data["date"],
            home_wins=game_data["home_record"]["wins"],
            home_losses=game_data["home_record"]["losses"],
            home_home_wins=game_data["home_home_record"]["wins"],
            home_home_losses=game_data["home_home_record"]["losses"],
            away_wins=game_data["away_record"]["wins"],
            away_losses=game_data["away_record"]["losses"],
            away_home_wins=game_data["away_away_record"]["wins"],
            away_home_losses=game_data["away_away_record"]["losses"],
            over_under=game_data["line"]["ou"],
            favorite=game_data["line"]["favorite"],
            spread=game_data["line"]["spread"],
        )
        player_stats = self.map_player_stats(
            player_data,
            team_data["home_stats"]["team"]["abbreviation"],
            team_data["away_stats"]["team"]["abbreviation"],
        )
        team_stats = self.map_team_stats(team_data)

        game.player_stats = player_stats
        game.team_stats = team_stats

        return game

    @staticmethod
    def map_player_stats(player_data, home_pk, away_pk):
        player_db_list = []
        for k in player_data.keys():
            for ps in player_data[k]:
                stat = nba.PlayerStat(
                    player_id=ps["player"]["id"],
                    game_id=ps["game_id"],
                    team_id=home_pk,
                    minutes=ps["min"],
                    points=ps["pts"],
                    drebs=ps["drebs"],
                    orebs=ps["orebs"],
                    rebounds=ps["reb"],
                    assists=ps["ast"],
                    turnovers=ps["to"],
                    fgm=ps["fgm"],
                    fga=ps["fga"],
                    fg_per=ps["fg_per"],
                    ftm=ps["ftm"],
                    fta=ps["fta"],
                    ft_per=ps["ft_per"],
                    x3pm=ps["x3pm"],
                    x3pa=ps["x3pa"],
                    x3p_per=ps["x3p_per"],
                    steals=ps["stl"],
                    fouls=ps["pf"],
                    plus_minus=ps["plusminus"],
                    player=nba.Player(
                        id=ps["player"]["player_id"],
                        first_name=ps["player"]["first_name"],
                        last_name=ps["player"]["last_name"],
                        pos=ps["player"]["position"],
                    ),
                )
                player_db_list.append(stat)
        return player_db_list

    @staticmethod
    def map_team_stats(team_data):
        team_db_list = []
        for k in team_data.keys():
            team = team_data[k]
            team_stat = nba.TeamStat(
                game_id=team["game_id"],
                team_id=team["team"]["abbreviation"],
                home=True if (k == "home") else False,
                fgm=team["fgm"],
                fga=team["fga"],
                fg_per=team["fg_per"],
                x3pm=team["x3pm"],
                x3pa=team["x3pa"],
                x3p_per=team["x3p_per"],
                ftm=team["ftm"],
                fta=team["fta"],
                ft_per=team["ft_per"],
                oreb=team["oreb"],
                dreb=team["dreb"],
                reb=team["reb"],
                ast=team["ast"],
                stl=team["stl"],
                blk=team["blk"],
                to=team["to"],
                pts_off_to=team["pts_off_to"],
                fast_break_pts=team["fast_break_pts"],
                points_in_paint=team["points_in_paint"],
                pf=team["pf"],
                technical=team["technical"],
                flagrant=team["flagrant"],
                largest_lead=team["largest_lead"],
                pts=team["pts"],
                team=nba.Team(
                    location=team["team"]["long_name"],
                    name=team["team"]["name"],
                    abbr=team["team"]["abbreviation"],
                ),
            )
            team_db_list.append(team_stat)
        return team_db_list


class JsonWriterPipeline(object):
    def open_spider(self, spider):
        self.file = open("items.json", "w")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item
