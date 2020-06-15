from sqlalchemy import (
    create_engine,
    Table,
    Column,
    Boolean,
    Integer,
    String,
    Float,
    Date,
    MetaData,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from game_crawler.nba_seasons import Seasons
from datetime import datetime
import pytz
from typing import List


Base = declarative_base()


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    season = Column(String)
    regular_season = Column(Boolean)
    home_wins = Column(Integer)
    home_losses = Column(Integer)
    home_home_wins = Column(Integer)
    home_home_losses = Column(Integer)
    away_wins = Column(Integer)
    away_losses = Column(Integer)
    away_away_wins = Column(Integer)
    away_away_losses = Column(Integer)
    over_under = Column(Integer)
    favorite = Column(String)
    spread = Column(Integer)
    team_stats = relationship("TeamStat", back_populates="game", cascade="save-update")
    player_stats = relationship(
        "PlayerStat", back_populates="game", cascade="save-update"
    )


class Team(Base):
    __tablename__ = "teams"

    abbr = Column(String, primary_key=True)
    location = Column(String, nullable=False)
    name = Column(String, nullable=False)
    game_stats = relationship("TeamStat", back_populates="team")
    player_stats = relationship("PlayerStat")


class TeamStat(Base):
    __tablename__ = "team_stats"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    game = relationship("Game", back_populates="team_stats")
    team_abbr = Column(String, ForeignKey("teams.abbr"))
    team = relationship("Team", back_populates="game_stats", cascade="save-update")
    home = Column(Boolean)
    fgm = Column(Integer)
    fga = Column(Integer)
    fg_per = Column(Float)
    x3pa = Column(Integer)
    x3pm = Column(Integer)
    x3p_per = Column(Float)
    fta = Column(Integer)
    ftm = Column(Integer)
    ft_per = Column(Float)
    oreb = Column(Integer)
    dreb = Column(Integer)
    reb = Column(Integer)
    ast = Column(Integer)
    stl = Column(Integer)
    blk = Column(Integer)
    to = Column(Integer)
    pts_off_to = Column(Integer)
    fast_break_pts = Column(Integer)
    points_in_paint = Column(Integer)
    pf = Column(Integer)
    technical = Column(Integer)
    flagrant = Column(Integer)
    largest_lead = Column(Integer)
    pts = Column(Integer)


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    position = Column(String)
    height = Column(Integer)
    weight = Column(Integer)
    draft_yr = Column(Integer)
    draft_rd = Column(Integer)
    draft_pk = Column(Integer)
    stats = relationship("PlayerStat", back_populates="player")


class PlayerStat(Base):
    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    player = relationship("Player", back_populates="stats", cascade="save-update")
    game_id = Column(Integer, ForeignKey("games.id"))
    game = relationship("Game", back_populates="player_stats")
    team_abbr = Column(String, ForeignKey("teams.abbr"))
    team = relationship("Team", back_populates="player_stats")
    minutes = Column(Integer)
    points = Column(Integer)
    drebs = Column(Integer)
    orebs = Column(Integer)
    rebounds = Column(Integer)
    assists = Column(Integer)
    turnovers = Column(Integer)
    fgm = Column(Integer)
    fga = Column(Integer)
    fg_per = Column(Float)
    ftm = Column(Integer)
    fta = Column(Integer)
    ft_per = Column(Float)
    x3pm = Column(Integer)
    x3pa = Column(Integer)
    x3p_per = Column(Float)
    steals = Column(Integer)
    fouls = Column(Integer)
    plus_minus = Column(Integer)


class nbaDB:
    def __init__(self, user, password):
        self.engine = create_engine(
            f"postgresql://{user}:{password}@localhost:5432/nba_stats", echo=True
        )
        Sess = sessionmaker(bind=self.engine)
        self.session = Sess()

    def add_record(self, record: dict):
        team_data = record.get("team_stats")
        player_data = record.get("player_stats")
        g = self.map_to_db(record)
        ps = self.map_player_stats(
            player_data,
            team_data.get("home_stats", {}).get("team", {}).get("abbreviation", ""),
            team_data.get("away_stats", {}).get("team", {}).get("abbreviation", ""),
        )
        ts = self.map_team_stats(team_data)

        players = self.map_players(player_data)
        teams = self.map_teams(team_data)

        for p in players:
            instance = self.session.query(Player).filter(Player.id == p.id).first()
            if not instance:
                self.session.add(p)

        for t in teams:
            instance = self.session.query(Team).filter(Team.abbr == t.abbr).first()
            if not instance:
                self.session.add(t)

        g.team_stats = ts
        g.player_stats = ps

        self.session.add(g)

    def map_to_db(self, item: dict) -> Game:
        game_data = item.get("game")
        s = self.get_season(game_data.get("date", ""))
        rs = self.regular_season(game_data.get("date", ""), s)
        game = Game(
            id=game_data.get("game_id", ""),
            date=game_data.get("date", ""),
            season=s,
            regular_season=rs,
            home_wins=game_data.get("home_record", {}).get("wins", ""),
            home_losses=game_data.get("home_record", {}).get("losses", ""),
            home_home_wins=game_data.get("home_home_record", {}).get("wins", ""),
            home_home_losses=game_data.get("home_home_record", {}).get("losses", ""),
            away_wins=game_data.get("away_record", {}).get("wins", ""),
            away_losses=game_data.get("away_record", {}).get("losses", ""),
            away_away_wins=game_data.get("away_away_record", {}).get("wins", ""),
            away_away_losses=game_data.get("away_away_record", {}).get("losses", ""),
            over_under=game_data.get("line", {}).get("ou", ""),
            favorite=game_data.get("line", {}).get("favorite", ""),
            spread=game_data.get("line", {}).get("spread", ""),
        )
        return game

    @staticmethod
    def get_season(date: str) -> String:
        etz = pytz.timezone("US/Eastern")
        d = datetime.strptime(date, "%Y-%m-%dT%H:%M%z")
        d = d.replace(tzinfo=pytz.utc).astimezone(etz)
        for k, v in Seasons.season_info.items():
            rss = etz.localize(
                v["regular_season_start"]
            )  # converts datetime to offset aware to match datetime of game
            pse = etz.localize(
                v["post_season_end"]
            )  # converts datetime to offset aware to match datetime of game
            if d >= rss and d <= pse:
                return k

    @staticmethod
    def regular_season(date: str, season: str) -> Boolean:
        etz = pytz.timezone("US/Eastern")
        d = datetime.strptime(date, "%Y-%m-%dT%H:%M%z")
        d = d.replace(tzinfo=pytz.utc).astimezone(etz)
        rss = etz.localize(Seasons.season_info[season]["regular_season_start"])
        rse = etz.localize(Seasons.season_info[season]["regular_season_end"])
        if d >= rss and d <= rse:
            return True
        return False

    @staticmethod
    def map_player_stats(player_data, home_pk, away_pk) -> List[PlayerStat]:
        pk_map = {"home_stats": home_pk, "away_stats": away_pk}
        player_db_list = []
        for k in player_data.keys():
            for ps in player_data[k]:
                stat = PlayerStat(
                    player_id=ps.get("player", "")["player_id"],
                    game_id=ps.get("game_id", ""),
                    team_abbr=pk_map[k],
                    minutes=ps.get("min", ""),
                    points=ps.get("pts", ""),
                    drebs=ps.get("dreb", ""),
                    orebs=ps.get("oreb", ""),
                    rebounds=ps.get("reb", ""),
                    assists=ps.get("ast", ""),
                    turnovers=ps.get("to", ""),
                    fgm=ps.get("fgm", ""),
                    fga=ps.get("fga", ""),
                    fg_per=ps.get("fg_per", ""),
                    ftm=ps.get("ftm", ""),
                    fta=ps.get("fta", ""),
                    ft_per=ps.get("ft_per", ""),
                    x3pm=ps.get("x3pm", ""),
                    x3pa=ps.get("x3pa", ""),
                    x3p_per=ps.get("x3p_per", ""),
                    steals=ps.get("stl", ""),
                    fouls=ps.get("pf", ""),
                    plus_minus=ps.get("plusminus", ""),
                )
                player_db_list.append(stat)
        return player_db_list

    @staticmethod
    def map_team_stats(team_data) -> List[TeamStat]:
        team_db_list = []
        for k in team_data.keys():
            team = team_data[k]
            team_stat = TeamStat(
                game_id=team.get("game_id", ""),
                team_abbr=team.get("team", {}).get("abbreviation", ""),
                home=True if (k == "home") else False,
                fgm=team.get("fgm", ""),
                fga=team.get("fga", ""),
                fg_per=team.get("fg_per", ""),
                x3pm=team.get("x3pm", ""),
                x3pa=team.get("x3pa", ""),
                x3p_per=team.get("x3p_per", ""),
                ftm=team.get("ftm", ""),
                fta=team.get("fta", ""),
                ft_per=team.get("ft_per", ""),
                oreb=team.get("oreb", ""),
                dreb=team.get("dreb", ""),
                reb=team.get("reb", ""),
                ast=team.get("ast", ""),
                stl=team.get("stl", ""),
                blk=team.get("blk", ""),
                to=team.get("to", ""),
                pts_off_to=team.get("pts_off_to", ""),
                fast_break_pts=team.get("fast_break_pts", ""),
                points_in_paint=team.get("points_in_paint", ""),
                pf=team.get("pf", ""),
                technical=team.get("technical", ""),
                flagrant=team.get("flagrant", ""),
                largest_lead=team.get("largest_lead", ""),
                pts=team.get("pts", ""),
            )
            team_db_list.append(team_stat)
        return team_db_list

    @staticmethod
    def map_players(player_data) -> List[Player]:
        players = []
        for k in player_data.keys():
            for p in player_data[k]:
                player = Player(
                    id=p.get("player", {}).get("player_id", ""),
                    first_name=p.get("player", {}).get("first_name", ""),
                    last_name=p.get("player", {}).get("last_name", ""),
                    position=p.get("player", {}).get("position", ""),
                )
                players.append(player)
        return players

    @staticmethod
    def map_teams(team_data) -> List[Team]:
        teams = []
        for k in team_data.keys():
            t = team_data[k]
            team = Team(
                location=t.get("team", {}).get("location", ""),
                name=t.get("team", {}).get("name", ""),
                abbr=t.get("team", {}).get("abbreviation", ""),
            )
            teams.append(team)
        return teams
