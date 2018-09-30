import os.path

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Enum, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import IntegrityError

from difflib import SequenceMatcher

def mkEngine():
    eng = create_engine('sqlite:///ganbot.db', echo=True)

    print("Creating database if it doesn't exist.")
    Base.metadata.create_all(eng)

    return eng


def mkTestEngine():
    eng = create_engine('sqlite:///:memory:', echo=True)

    Base.metadata.create_all(eng)

    return eng


Base = declarative_base()


class Character(Base):
    """Type representing a character. It exists separately from battles."""


    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    player = Column(Integer, nullable=False)

    attack = Column(Integer, nullable=False)
    defence = Column(Integer, nullable=False)
    speed = Column(Integer, nullable=False)
    magic = Column(Integer, nullable=False)
    wisdom = Column(Integer, nullable=False)
    health = Column(Integer, nullable=False)

    def __repr__(self):
        return '{} ({})'.format(self.name, self.format_stats())

    def format_stats(self):
        return 'Attack: {} Defence: {} Magic: {} Wisdom: {} Speed: {} Health: {}' \
            .format(self.attack, self.defence, self.magic, self.wisdom, self.speed, self.health)


class Battle(Base):
    """Represents a single, ongoing battle."""

    __tablename__ = 'battles'

    id = Column(Integer, primary_key=True)

    channel_id = Column(Integer, unique=True)

    teamA = relationship("InBattleA", back_populates="battle")

    teamB = relationship("InBattleB", back_populates="battle")


class InBattleA(Base):
    """Represents a character being in a battle in team A with a certain amount of health remaining."""

    __tablename__ = 'in_battle_teamA'

    id = Column(Integer, primary_key=True)
    health_remaining = Column(Integer)

    character_id = Column(Integer, ForeignKey('characters.id'))
    battle_id = Column(Integer, ForeignKey('battles.id'))
    battle = relationship("Battle", back_populates="teamA")


class InBattleB(Base):
    """Represents a character being in a battle in team B with a certain amount of health remaining."""

    __tablename__ = 'in_battle_teamB'

    id = Column(Integer, primary_key=True)
    health_remaining = Column(Integer)

    character_id = Column(Integer, ForeignKey('characters.id'))
    battle_id = Column(Integer, ForeignKey('battles.id'))
    battle = relationship("Battle", back_populates="teamB")


distance_table = Table('battle_distances', Base.metadata,

                       Column('left_char_id',
                              Integer,
                              ForeignKey('battles.id')),

                       Column('distance', Integer),

                       Column('right_char_id',
                              Integer,
                              ForeignKey('battles.id'))
                       )


def openPeristent():
    return PersistentGanbot(mkEngine())


def openTestPeristent():
    return PersistentGanbot(mkTestEngine())


class DuplicateCharacterError(Exception):
    pass


class PersistentGanbot():
    '''
    Class representing an abstract interface to persistent storage.
    To SQLite, usually, but the caller is oblivious to this.
    '''

    def __init__(self, dbeng):
        self.getSession = sessionmaker(bind=dbeng)

    def __storeObject(self, obj: Base):

        # Persist to database
        session = self.getSession()

        try:
            session.add(obj)
            session.commit()
        except Exception as ex:
            session.rollback()
            raise ex


    def storeCharacter(self, character: Character):

        try:
            self.__storeObject(character)

        except IntegrityError as ie:
            if ie.args[0] == '(sqlite3.IntegrityError) UNIQUE constraint failed: users.name':
                raise DuplicateCharacterError()

            raise ie

    def fetch_characters_for_user(self, userId):
        return self.getSession().query(Character).filter_by(player=userId).all()

    def fetch_character_by_name(self, charName):
        return self.getSession().query(Character).filter_by(name=charName).one_or_none()

    def fetch_all_characters_by_name_like(self, pattern):
        return self.getSession().query(Character).filter(Character.name.like(pattern)).all()

    def search_character(self, queryName):

        chars = self.getSession().query(Character).all()

        def fuzzy_match(char: Character):
            return SequenceMatcher(None, char.name, queryName).ratio()


        return sorted(chars, key=fuzzy_match, reverse=True)

    def storeBattle(self, battle: Battle):
        self.__storeObject(battle)

