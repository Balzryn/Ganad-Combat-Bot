
import db
import discord
import itertools


idGen = itertools.count()

user_alice = discord.User(id=next(idGen))
user_bob = discord.User(id=next(idGen))
server = discord.Server(id=next(idGen))
channel_1 = discord.Channel(id=next(idGen), server=server)

mysta = dict(name='Mysta', attack=20, wisdom=60, defence=50, speed=40, magic=30, health=100, player=user_alice.id)
maasta = dict(name='Maasta', attack=20, wisdom=60, defence=50, speed=40, magic=30, health=100, player=user_alice.id)
danny = dict(name='Danny', attack=20, wisdom=60, defence=50, speed=40, magic=30, health=100, player=user_alice.id)
jonus = dict(name='Jonus', attack=20, wisdom=60, defence=50, speed=40, magic=30, health=100, player=user_alice.id)
dareko = dict(name='Dareko', attack=30, wisdom=20, defence=10, speed=10, magic=20, health=150, player=user_bob.id)

allChars = [mysta,danny,dareko,jonus,maasta]