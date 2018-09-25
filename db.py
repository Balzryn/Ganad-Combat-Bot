import os.path

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

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
    __tablename__ = 'users'

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
        return 'Attack: {} Defence: {} Magic: {} Wisdom: {} Speed: {} Health: {}'\
            .format(self.attack, self.defence, self.magic, self.wisdom, self.speed, self.health)

def openPeristent():
    return PeristentGanbot(mkEngine())

def openTestPeristent():
    return PeristentGanbot(mkTestEngine())

class DuplicateCharacterError(Exception):
    pass

class PeristentGanbot():
    '''
    Class representing an abstract interface to persistent storage.
    To SQLite, usually, but the caller is oblivious to this.
    '''

    def __init__(self, dbeng):
        self.getSession = sessionmaker(bind=dbeng)

    def storeCharacter(self, character: Character):
        # Persist to database
        session = self.getSession()

        try:
            session.add(character)
            session.commit()

        except IntegrityError as ie:
            if ie.args[0] == '(sqlite3.IntegrityError) UNIQUE constraint failed: users.name':
                raise DuplicateCharacterError()

            raise ie

    def getCharactersForUser(self, userId):
        return self.getSession().query(Character).filter_by(player=userId).all()
