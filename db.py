import os.path

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

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
    # health = Column(Integer)

    def __repr__(self):
       return '{} ({})'.format(self.name, self.format_stats())

    def format_stats(self):
        return 'Attack: {} Defence: {} Magic: {} Wisdom: {} Speed: {}'\
            .format(self.attack, self.defence, self.magic, self.wisdom, self.speed)