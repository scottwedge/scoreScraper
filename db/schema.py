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
from sqlalchemy.orm import relationship
import os

USER = os.environ["dbName"]
PASSWORD = os.environ["dbPass"]

Base = declarative_base()


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    team_stat_id = Column(Integer, ForeignKey("team_stats.id"))
    team_stats = relationship(
        "TeamStat", back_populates="team_stats", cascade="save-update"
    )
    player_stat_id = Column(Integer, ForeignKey("player_stats.id"))
    player_stats = relationship(
        "PlayerStat", back_populates="player_stats", cascade="save-update"
    )


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    location = Column(String, nullable=False)
    name = Column(String, nullable=False)
    abbr = Column(String, nullable=False)
    game_stats_id = Column(Integer, ForeignKey("team_stats.id"))
    game_stats = relationship("TeamStat", back_populates="team_stats")
    player_stats_id = Column(Integer, ForeignKey("player_stats.id"))
    player_stats = relationship("PlayerStat", back_populates="player_stats")


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    height = Column(Integer)
    weight = Column(Integer)
    draft_yr = Column(Integer)
    draft_rd = Column(Integer)
    draft_pk = Column(Integer)
    stats_id = Column(Integer, ForeignKey("player_stats.id"))
    stats = relationship("PlayerStat", back_populates="player_stats")


class PlayerStat(Base):
    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    player = relationship("Player", back_populates="players", cascade="save-update")
    game_id = Column(Integer, ForeignKey("games.id"))
    game = relationship("Game", back_populates="games")
    team_id = Column(Integer, ForeignKey("teams.id"))
    team = relationship("Team", back_populates="teams")
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
    game = relationship("Game", back_populates="games")
    team_id = Column(Integer, ForeignKey("teams.id"))
    team = relationship("Team", back_populates="teams", cascade="save-update")
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


def main():
    engine = create_engine(
        f"postgresql://{USER}:{PASSWORD}@localhost:5432/nba_stats", echo=True
    )
    Base.metadata.create_all(engine)


main()
