import asyncio
import datetime as dt
import random
import typing

import discord
from discord.ext import commands, tasks

import config
from bot import LilHalJr


if config.LOGGING:
    import logging
    logger = logging.getLogger("lilhaljr")


class SocialCog(commands.Cog, name="Social"):
    """
    Hal will attempt to be a little more social with this cog.
    """
    def __init__(self, bot: LilHalJr):
        self.bot = bot

        self.cranebot_loop.start()

    @staticmethod
    async def __find_channel_by_keyword(guild: discord.Guild, keyword: str) -> discord.TextChannel | None:
        """
        Finds a channel in a given guild with a very simple keyword search.
        :param guild: Guild to search.
        :param keyword: Keyword to use.
        :return: Matching channel, if any. None otherwise.
        """
        for channel in guild.text_channels:
            if channel.can_send(discord.Message) and keyword.lower() in channel.name.lower():
                return channel

    async def find_quiet_channel(self, condition: typing.Callable[[discord.TextChannel], bool] = None) \
            -> discord.TextChannel:
        """
        Hal finds a quiet channel, with an optional additional condition.
        :param condition: A callable function that takes a text channel for input, and returns a bool
        :return: Suitable channel.
        """
        async def test_for_quiet(ch: discord.TextChannel) -> bool:
            """ Tests that the given channel is quiet. """
            try:
                # Wait for someone to type in the same channel
                self.bot.wait_for("typing", check=lambda c: c == ch, timeout=30)

            except asyncio.TimeoutError:
                return False

            else:
                return True

        async def tests(ch: discord.TextChannel) -> bool:
            """ Tests the given channel. """
            return ch.can_send(discord.Message) and condition(ch) and await test_for_quiet(ch)

        # Check bot arena first.
        home_guild = self.bot.get_guild(config.HOME_GUILD)
        for channel in home_guild.text_channels:
            if await tests(channel):
                return channel

        # Else, surf through all guilds.
        for guild in self.bot.guilds:
            if guild == home_guild:
                continue

            # Test channels, return first match.
            for channel in guild.text_channels:
                if await tests(channel):
                    return channel

    async def introduce_to(self, channel: discord.TextChannel) -> None:
        """
        Hal sends an introduction to the given channel.
        :param channel: Expected introduction channel.
        :return: No return value
        """
        await self.bot.pause(20, 25)
        intro = "Hal\nHe/It\nI can quiet down when you tell me."

        await self.bot.speak_in(channel, intro)

    async def say_hello(self, channel: discord.TextChannel) -> None:
        """
        Hal says hello.
        :param channel: Channel in which to say hello.
        :return: No return value
        """
        await self.bot.pause(5, 15)
        await self.bot.speak_in(channel, "Hello.")

    async def wait_until_quiet(self, channel: discord.TextChannel) -> None:
        """
        Waits for the given channel to quiet down, when no one is typing anymore. Returns when ready.
        :param channel: Channel to wait in.
        :return: No value. Just returns when ready.
        """
        def check(ch: discord.TextChannel, *_) -> bool:
            """ Simple check. Return `True` extends the wait. """
            return ch == channel

        # Loop until quiet.
        while True:
            try:
                await self.bot.wait_for('typing', check=check, timeout=random.randint(9, 25) + random.random())

            # Loop breaks, return.
            except asyncio.TimeoutError:
                break

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """
        Hal says hello joining a guild.
        :param guild:
        """
        # Say hello
        channel = await self.__find_channel_by_keyword(guild, "general")
        if channel is not None:
            await self.say_hello(channel)

        # Introduce self.
        channel = await self.__find_channel_by_keyword(guild, "intro")
        if channel is not None:
            await self.introduce_to(channel)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """
        Hal says hello to a new person.
        :param member: Joining member.
        """
        # A place to save the channel.
        channel = []

        def check(m: discord.Message) -> bool:
            """ Checks that a message is from the new member. """
            result = m.author == member and m.guild == member.guild

            if result:
                channel.append(m.channel)

            return result

        # Wait for them to say something.
        try:
            await self.bot.wait_for("message", check=check, timeout=3600)
        except asyncio.TimeoutError:  # If they don't, no big deal.
            return

        # Grab the registered channel.
        await self.say_hello(channel[0])

    @tasks.loop(time=dt.time(7, 2, tzinfo=dt.timezone(dt.timedelta(hours=-8))))
    async def cranebot_loop(self):
        """ Every now and again, Hal will try to interact with Cranebot. """
        if config.LOGGING:
            logger.info("Running Cranebot interaction loop.")

        def check(c: discord.TextChannel) -> bool:
            """ Hal checks that Cranebot is here. """
            cranebot = c.guild.get_member(config.CRANEBOT_ID)
            return cranebot is not None and cranebot.status != discord.Status.offline

        # Find a quiet channel.
        channel = await self.find_quiet_channel(check)
        if channel is None:
            return

        # Commands to choose between, all which should work.
        coms = random.choices(["pokemon", "beast", "catch", "explode", "meme", "songrec", "highfive", "pa"],
                              k=random.randint(1, 3))

        # Use each, waiting in between.
        for command in coms:
            await self.wait_until_quiet(channel)
            await self.bot.speak_in(channel, f";{command}")

        # Shake up the time between commands.
        hours = round(random.randint(1, 3) + random.random(), 3)
        self.cranebot_loop.change_interval(hours=hours)

    @cranebot_loop.before_loop
    async def before_cranebot_loop(self):
        """ Simply waits until ready before doing anything."""
        await self.bot.wait_until_ready()

        if config.LOGGING:
            logger.info("Starting Cranebot interaction loop...")


def setup(bot: LilHalJr) -> None:
    """
    Set up function for load_extension.
    :param bot: Expecting Lil Hal Jr.
    :return: No return value.
    """
    bot.add_cog(SocialCog(bot))
