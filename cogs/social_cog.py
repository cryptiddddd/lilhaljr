import asyncio
import logging
import random
import typing

import discord
from discord.ext import commands, tasks

import config
from bot import LilHalJr


logger = logging.getLogger("lilhaljr")


class SocialCog(commands.Cog, name="Social"):
    """
    Hal will attempt to be a little more social with this cog.
    """
    def __init__(self, bot: LilHalJr):
        self.bot = bot

        self.bot_interaction_loop.start()

    @staticmethod
    def __find_channel_by_keyword(guild: discord.Guild, keyword: str) -> discord.TextChannel | None:
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
        def validate(ch: discord.TextChannel) -> bool:
            """ Tests the given channel. """
            test = condition(ch) if condition else True  # Condition can be None, be wary.
            return ch.can_send(discord.Message) and test

        # Get a list of candidate channels. Checks home guild first.
        home_guild = self.bot.get_guild(config.HOME_GUILD)
        channels = list(filter(validate, home_guild.text_channels))

        def channel_check(ch: discord.TextChannel, *_) -> bool:
            """ Checks if the typing channel is in the list. """
            return ch in channels

        while len(channels) > 0:
            try:
                typing_result = await self.bot.wait_for("typing", check=channel_check, timeout=10)
                print(typing_result)
                channels.remove(typing_result[0])

            except asyncio.TimeoutError:
                break

        if len(channels) >= 1:
            return channels[0]

        # # Else, surf through all guilds.
        # for guild in self.bot.guilds:
        #     if guild == home_guild:
        #         continue
        #
        #     # Test channels, return first match.
        #     for channel in guild.text_channels:
        #         if await validate(channel):
        #             return channel

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
        await self.bot.pause(5, 10)
        await self.bot.speak_in(channel, "Hello.")

    async def wait_until_quiet(self, channel: discord.TextChannel) -> None:
        """
        Waits for the given channel to quiet down, when no one is typing anymore. Returns when ready.
        :param channel: Channel to wait in.
        :return: No value. Just returns when ready.
        """
        # Loop until quiet.
        while True:
            try:
                wait = random.randint(9, 25) + random.random()
                await self.bot.wait_for('typing', check=lambda c, u, w: c == channel, timeout=wait)

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
        channel = self.__find_channel_by_keyword(guild, "general")
        if channel is not None:
            await self.say_hello(channel)

        # Introduce self.
        channel = self.__find_channel_by_keyword(guild, "intro")
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
        channel = channel[0]

        # Safeguard.
        if "intro" not in channel.name.lower():
            await self.say_hello(channel)

    @tasks.loop(hours=5)
    async def bot_interaction_loop(self):
        """ Every now and again, Hal will try to interact with Cranebot. """
        logger.info("Running bot interaction loop.")

        cranebot_commands = ["pokemon", "beast", "catch", "explode", "meme", "songrec", "highfive", "pat"]
        cranebot_result = await self.bot_command_interaction(config.CRANEBOT_ID, '%', cranebot_commands)

        # Backup plan:
        if not cranebot_result and not random.randint(0, 99):
            await self.bot_command_interaction(config.TOASTY_ID, ';', ["pokemon", "cat", "cow", "shrug", "lenny"])

        # Shake up the time between commands.
        next_time = self.bot.random_time(6, 21)
        self.bot_interaction_loop.change_interval(time=next_time)
        logger.info(f"Bot interaction loop will run again at {next_time}...")

    @bot_interaction_loop.before_loop
    async def before_bot_loop(self):
        """ Simply waits until ready before doing anything. """
        await self.bot.wait_until_ready()

        logger.info("Starting bot interaction loop...")

    async def bot_command_interaction(self, bot_id: int, command_prefix: str, command_list: list[str]) -> bool:
        """
        Attempts to interact with another bot through commands.
        :param bot_id: Discord user ID of the bot.
        :param command_prefix: The bot's prefix.
        :param command_list: List of the given bot's commands to pick from.
        :return: True if an interaction is attempted. False if not.
        """
        def check(c: discord.TextChannel) -> bool:
            """ A check that the bot is in a channel and online. """
            bot = c.guild.get_member(bot_id)
            return bot is not None and bot.status != discord.Status.offline

        # Find a quiet channel.
        channel = await self.find_quiet_channel(check)
        if channel is None:
            return False

        # Use a couple commands, waiting in between.
        coms = random.choices(command_list, k=random.randint(1, 3))

        for command in coms:
            await self.wait_until_quiet(channel)
            await self.bot.speak_in(channel, f"{command_prefix}{command.capitalize()}")

        return True


def setup(bot: LilHalJr) -> None:
    """
    Set up function for load_extension.
    :param bot: Expecting Lil Hal Jr.
    :return: No return value.
    """
    bot.add_cog(SocialCog(bot))
