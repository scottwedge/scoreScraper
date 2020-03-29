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
import os
from datetime import date


USER = os.environ["dbName"]
PASSWORD = os.environ["dbPass"]

Base = declarative_base()


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    regular_season = Column(Boolean)
    home_wins = Column(Integer)
    home_losses = Column(Integer)
    away_wins = Column(Integer)
    away_losses = Column(Integer)
    over_under = Column(Integer)
    spread = Column(String)
    team_stats = relationship("TeamStat", back_populates="game", cascade="save-update")
    player_stats = relationship(
        "PlayerStat", back_populates="game", cascade="save-update"
    )


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    location = Column(String, nullable=False)
    name = Column(String, nullable=False)
    abbr = Column(String, nullable=False)
    game_stats = relationship("TeamStat", back_populates="team")
    player_stats = relationship("PlayerStat")


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
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
    team_id = Column(Integer, ForeignKey("teams.id"))
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


class TeamStat(Base):
    __tablename__ = "team_stats"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    game = relationship("Game", back_populates="team_stats")
    team_id = Column(Integer, ForeignKey("teams.id"))
    team = relationship("Team", back_populates="game_stats", cascade="save-update")
    home = Column(Boolean)
    points = Column(Integer)
    drebs = Column(Integer)
    orebs = Column(Integer)
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


class nbaDB:
    def __init__(self, user, password):
        self.engine = create_engine(
            f"postgresql://{USER}:{PASSWORD}@localhost:5432/nba_stats", echo=True
        )
        Sess = sessionmaker(bind=self.engine)
        self.session = Sess()

    def map_game(self, data: dict):
        pass

    def commit_game(self):
        pass
