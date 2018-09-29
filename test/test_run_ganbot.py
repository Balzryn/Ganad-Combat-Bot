from unittest import TestCase

import bot
import db
import discord
import asyncio
import asyncio.queues as aqueue
import itertools
from timeout_decorator import timeout

idGen = itertools.count()

user_alice = discord.User(id=next(idGen))
user_bob = discord.User(id=next(idGen))
server = discord.Server(id=next(idGen))
channel_1 = discord.Channel(id=next(idGen), server=server)


class TestClient():
    def __init__(self, test_routine):
        self.user = discord.User(id=1337)
        self.test_routine = test_routine

        self.received_messages = {}

    def event(self, handle):

        if 'on_ready' == handle.__name__:
            self.on_ready = handle
        elif 'on_message' == handle.__name__:
            self.on_message = handle

    def send_message(self, channel: discord.Channel, msg):
        print('Bot says: "{}" in channel {} '.format(msg, channel.id))

        return self.received_messages.setdefault(channel.id, aqueue.Queue()).put(msg)

    def wait_for_bot_message(self, channel: discord.Channel):

        return self.received_messages.setdefault(channel.id, aqueue.Queue()).get()

    def has_message_on_channel(self, channel: discord.Channel):

        try:
            return self.received_messages[channel].qsize() >= 1
        except KeyError:
            return False




    def test_message(self, content, channel, user=user_alice):

        print('Sent mock message: "{}" in channel {} as user {}'.format(content, channel_1.id, user.id))

        message = discord.Message(content=content,
                                  author={'id': user.id},
                                  channel=channel,
                                  reactions=[])

        return asyncio.ensure_future(self.on_message(message))


    def run(self, token):

        loop = asyncio.get_event_loop()
        # Blocking call which returns when the hello_world() coroutine is done
        loop.run_until_complete(self.test_routine(self))
        # loop.close()


class TestRun_ganbot(TestCase):

    def test_run_ganbot_ignored_messages(self):

        async def runCoroutine(client):

            # Should not respond to non-prefixed commands
            client.test_message("The quick brown fox jumps over the lazy dog.", channel_1)
            await asyncio.sleep(1)
            self.assertFalse(client.has_message_on_channel(channel_1))

            client.test_message("create_character", channel_1)
            await asyncio.sleep(1)
            self.assertFalse(client.has_message_on_channel(channel_1))

        bot.run_ganbot(TestClient(runCoroutine), db.openTestPeristent())

    @timeout(1)
    def test_ganbot_help(self):

        async def runCoroutine(client):

            # Should respond with help message for help command
            client.test_message("--help", channel_1)
            self.assertTrue(bot.HELP in await client.wait_for_bot_message(channel_1))

            # Display help on bad or misspelled commands
            client.test_message("--crate_char", channel_1)
            self.assertTrue(bot.HELP in await client.wait_for_bot_message(channel_1))

            # Empty command should trigger help
            client.test_message("--", channel_1)
            self.assertTrue(bot.HELP in await client.wait_for_bot_message(channel_1))

        bot.run_ganbot(TestClient(runCoroutine), db.openTestPeristent())

    @timeout(1)
    def test_run_ganbot_charcreation(self):

        test_peristent = db.openTestPeristent()

        async def runCoroutine(client):

            name = 'Alisson'

            skills = {
                'attack': 9,
                'defence': 10,
                'magic': 7,
                'speed': 20,
                'health': 100,
                'wisdom': 20
            }

            client.test_message("--create_character", channel_1)

            self.assertIn('call them', await client.wait_for_bot_message(channel_1))

            client.test_message(name, channel_1)

            last_msg = await client.wait_for_bot_message(channel_1)

            print('Skills.')

            while 'hello to' not in last_msg:

                found = False

                for key, val in skills.items():

                    # print('{} in "{}"'.format(key, last_msg))
                    if key in last_msg:
                        client.test_message(str(val), channel_1)

                        last_msg = await client.wait_for_bot_message(channel_1)
                        found = True
                        break

                if not found:
                    self.fail('Bot asked for unknown skill. Known skills are {}'.format(skills.keys()))



            print('Done. Checking creation.')

            chars = test_peristent.getCharactersForUser(user_alice.id)

            filtered = [c for c in chars if c.name == name]

            self.assertNotEquals(filtered, [])

            resultingChar = filtered[0]

            for skill, skillStat in skills.items():
                self.assertEquals(getattr(resultingChar, skill), skillStat)

        bot.run_ganbot(TestClient(runCoroutine), test_peristent)
