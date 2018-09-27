import asyncio
import discord
import shlex

import db

DISCORD_BOT_TOKEN = 'NDk0MTg4OTI4Mzk2NDI3MjY5.Dov52Q.YlOZ6ZcTeWzhxsa4PAzBE7h4cTs'
PREFIX = '--'
HELP = '''
Ganbot has the following commands:

`$PREFIX$create_character`
    Start the character creation process.

`$PREFIX$list_characters`
    List all of your characters. (Other players' characters aren't listed.)

`$PREFIX$help`
    Display this message.
'''.replace('$PREFIX$', PREFIX)


def run_ganbot(client, persistent):
    awaiting_answer = {}

    @client.event
    async def on_ready():
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')

    def await_answer(in_response_to: discord.Message):

        fut = asyncio.Future()

        awaiting_answer[(in_response_to.channel.id, in_response_to.author.id)] = fut

        return fut

    async def await_nonnegative_int(message):
        attack = None
        while not isinstance(attack, int) or attack < 0:
            response = await await_answer(message)

            try:
                attack = int(response)
            except ValueError:
                await client.send_message(message.channel, "Please enter a non-negative integer.")

        return attack

    @client.event
    async def on_message(message):

        # Try so we can respond with a message to the user if something goes wrong
        try:

            # The bot should ignore its' own messages.
            if message.author.id == client.user.id:
                return

            # Check if the bot is waiting for a message for this user in this channel
            awaiting = awaiting_answer.pop((message.channel.id, message.author.id), None)

            # Yes! Go send the answer into that coroutine.
            if awaiting is not None:
                awaiting.set_result(message.content)
                return

            # Ignore anythong that doesn't start with the prefix.
            if not message.content.startswith(PREFIX):
                return

            print('Got command: ' + message.content)

            # Slice off the prefix, then split the command into individual words.
            # Words surrounded by "quotes" are left as one, wit the quotes stripped off.
            tokens = shlex.split(message.content[len(PREFIX):])

            # Whoops... We got the prefix, then nothing!
            if tokens == []:
                await client.send_message(message.channel, 'No command provided.\n' + HELP)
                return

            # User wants to create a character!
            if tokens[0] == 'create_character':

                await create_character(message)

            elif tokens[0] == 'list_characters':
                await list_characters(message)

            elif tokens[0] == 'help':
                await client.send_message(message.channel, HELP)

            else:
                await client.send_message(message.channel, 'Unrecognized command.\n' + HELP)

        except Exception as ex:
            await client.send_message(message.channel,
                                      'Something went wrong. Go blame Bal and Civ (gently).\n' + str(ex))

            raise ex

    async def list_characters(message):
        characters = persistent.getCharactersForUser(message.author.id)

        if characters:
            msg = 'Off the top of my head, I remember you had these characters:\n' + \
                  '\n'.join(map(lambda x: '- ' + str(x),
                                characters))
        else:
            msg = 'You have no characters. Go make one!'
        await client.send_message(message.channel, msg)

    async def create_character(message):
        # Go through a series of prompts to define the character.

        # Name
        await client.send_message(message.channel,
                                  "Awoo! A new character! What are you gonna call them?")
        name = await await_answer(message)
        # Attack
        await client.send_message(message.channel,
                                  "How strong is their attack? (Integer)")
        attack = await await_nonnegative_int(message)
        # Defence
        await client.send_message(message.channel,
                                  "How strong is their defence? (Integer)")
        defence = await await_nonnegative_int(message)
        # Magic
        await client.send_message(message.channel,
                                  "How strong is their magic? (Integer)")
        magic = await await_nonnegative_int(message)
        # Speed
        await client.send_message(message.channel,
                                  "How fast are they? (Integer)")
        speed = await await_nonnegative_int(message)
        # Wisdom
        await client.send_message(message.channel,
                                  "How wise are they? (Integer)")
        wisdom = await await_nonnegative_int(message)
        # Health
        await client.send_message(message.channel,
                                  "How much much health do they have? (Integer)")
        health = await await_nonnegative_int(message)
        # Done! Package it up.
        character = db.Character(name=name,
                                 player=message.author.id,
                                 attack=attack,
                                 defence=defence,
                                 magic=magic,
                                 wisdom=wisdom,
                                 speed=speed,
                                 health=health)

        # Persist to database
        try:
            persistent.storeCharacter(character)

            # Notify user that char has been created.
            feedback = 'Say hello to {}! ({})'.format(character.name, character.format_stats())

            await client.send_message(message.channel, feedback)

        except db.DuplicateCharacterError:
            errmsg = 'A character with the name {} already exists!'.format(character.name)
            await client.send_message(message.channel, errmsg)

    client.run(DISCORD_BOT_TOKEN)


if __name__ == '__main__':
    print('Starting Ganbot. Let the games begin!')

    client = discord.Client()

    persistent = db.openPeristent()

    run_ganbot(client, persistent)
