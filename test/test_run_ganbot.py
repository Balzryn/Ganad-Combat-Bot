from unittest import TestCase

import bot
import db
import discord
import asyncio
import itertools

idGen = itertools.count()

user_alice = discord.User(id=next(idGen))
user_bob = discord.User(id=next(idGen))
server = discord.Server(id=next(idGen))
channel_1 = discord.Channel(id=next(idGen), server=server)

class TestClient():
    received_messages = {}

    def __init__(self, test_routine):
        self.user = discord.User(id=1337)
        self.test_routine = test_routine

    def event(self, handle):

        if 'on_ready' == handle.__name__:
            self.on_ready = handle
        elif 'on_message' == handle.__name__:
            self.on_message = handle

    async def send_message(self, channel: discord.Channel, msg):
        self.received_messages.setdefault(channel, []).append(msg)

    async def test_message(self, content, user=user_alice):

        self.received_messages = {}

        await self.on_message(discord.Message(
            content=content,
            author={'id': user.id},
            channel=channel_1,
            reactions=[]
        ))

        return self.received_messages


    def run(self, token):

        loop = asyncio.get_event_loop()
        # Blocking call which returns when the hello_world() coroutine is done
        loop.run_until_complete(self.test_routine(self))
        loop.close()

class TestRun_ganbot(TestCase):

    def test_run_ganbot(self):

        async def runCoroutine(client):

            # Should not respond to non-prefixed commands
            received_messages = await client.test_message("The quick brown fox jumps over the lazy dog.")
            self.assertEquals({}, received_messages)

            received_messages = await client.test_message("create_character")
            self.assertEquals({}, received_messages)

            # Should respond with help message for help command
            received_messages = await client.test_message("--help")
            self.assertTrue(bot.HELP in received_messages[channel_1][0])

            # Display help on bad or misspelled commands
            received_messages = await client.test_message("--crate_char")
            self.assertTrue(bot.HELP in received_messages[channel_1][0])

            # Empty command should trigger help
            received_messages = await client.test_message("--")
            self.assertTrue(bot.HELP in received_messages[channel_1][0])

        bot.run_ganbot(TestClient(runCoroutine), db.openTestPeristent())
