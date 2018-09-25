import asyncio
import discord
import shlex
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

import db

DISCORD_BOT_TOKEN = 'NDk0MTg4OTI4Mzk2NDI3MjY5.Dov52Q.YlOZ6ZcTeWzhxsa4PAzBE7h4cTs'
PREFIX = '--'

client = discord.Client()

eng = db.mkEngine()
getSession = sessionmaker(bind=eng)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):

    try:


        if not message.content.startswith(PREFIX):
            return

        print('Got command: ' + message.content)

        tokens = shlex.split(message.content[len(PREFIX):])

        if tokens == []:
            await client.send_message(message.channel, 'No command provided.')
            # TODO Show some kind of help message
            return

        if tokens[0] == 'create_character':
            # await client.send_message(message.channel, 'Woo! creating a character is fun!')

            name = tokens[1]

            character = db.Character(name=name,
                                     player=message.author.id,
                                     attack=5,
                                     defence=5,
                                     magic=5,
                                     wisdom=5,
                                     speed=5)

            try:
                session = getSession()
                session.add(character)
                session.commit()

                feedback = 'Say hello to {}! ({})'.format(character.name, character.format_stats())

                await client.send_message(message.channel, feedback)

            except IntegrityError as ie:
                x = ie.args[0]

                if x == '(sqlite3.IntegrityError) UNIQUE constraint failed: users.name':
                    errmsg = 'A character with the name {} already exists!'.format(character.name)
                    await client.send_message(message.channel,
                                              errmsg)

                session.rollback()

        elif tokens[0] == 'list_characters':
            session = getSession()

            characters = session.query(db.Character).filter_by(player=message.author.id).all()

            if characters:
                msg = 'Off the top of my head, I remember you had these characters:\n' +\
                      '\n'.join(map(lambda x: '- ' + str(x),
                                    characters))
            else:
                msg = 'You have no characters. Go make one!'

            await client.send_message(message.channel, msg)


        else:
            await client.send_message(message.channel, 'Unrecognized command.')
            # TODO Show help as well

    except Exception as ex:
        await client.send_message(message.channel,
                                  'Something went wrong. Go blame Bal and Civ (gently).\n' + str(ex))

        raise ex

    # if message.content.startswith('!test'):
    #     counter = 0
    #     tmp = await client.send_message(message.channel, 'Calculating messages...')
    #     async for log in client.logs_from(message.channel, limit=100):
    #         if log.author == message.author:
    #             counter += 1
    #
    #     await client.edit_message(tmp, 'You have {} messages.'.format(counter))
    # elif message.content.startswith('!sleep'):
    #     await asyncio.sleep(5)
    #     await client.send_message(message.channel, 'Done sleeping')

if __name__ == '__main__':
    print('Starting Ganbot. Let the games begin!')
    client.run(DISCORD_BOT_TOKEN)