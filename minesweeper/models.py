from enum import unique, Enum

from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey, DateTime, PickleType)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


@unique
class CellState(Enum):
    empty = 1
    mine = 2


@unique
class PlayerAction(Enum):
    click = 1
    flag = 2


class Game(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)
    board_state = Column(PickleType)


class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    name = Column(Text)


class PlayerAction(Base):
    __tablename__ = 'player_actions'
    id = Column('rowid', Integer, primary_key=True)  # implicit id
    game_id = Column(Integer, ForeignKey('games.id'))
    player_id = Column(Integer, ForeignKey('players.id'))
    action = Column(Text)
    timestamp = Column(DateTime)
