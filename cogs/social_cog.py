import asyncio
import random
import typing

import discord
from discord.ext import commands, tasks

import config
from bot import LilHalJr


class SocialCog(commands.Cog, name="Social"):
    """
    Hal will attempt to be a little more social with this cog.
    """
    def __init__(self, bot: LilHalJr):
        self.bot = bot

        self.cranebot_loop.start()

    async def find_quiet_channel(self, condition: typing.Callable[[discord.TextChannel], bool] = None) \
            -> discord.TextChannel:
        """
        Hal finds a quiet channel, with an optional additional condition.
        :param condition: A callable function that takes a text channel for input, and returns a bool
        :return: Suitable channel.
        """
        # Check bot arena first.

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """
        Hal says hello joining a guild.
        :param guild:
        """
        # Search for a general chat with enabled permissions.
        for channel in guild.text_channels:
            if channel.can_send(discord.Message) and "general" in channel.name:
                break
        else:
            return

        # Send hello.
        await asyncio.sleep(random.randint(5, 20) + random.random())
        await self.speak_in(channel, "Hello.")

    @tasks.loop(hours=2.5)
    async def cranebot_loop(self):
        """ Every now and again, Hal will try to interact with Cranebot. """
        # Shake up the time between commands.
        await asyncio.sleep(random.randint(1800, 3600) + random.random())

        def check(c: discord.TextChannel) -> bool:
            """ Hal checks that Cranebot is here. """
            cranebot = c.guild.get_member(config.CRANEBOT_ID)
            return cranebot is not None and cranebot.status != discord.Status.offline

        # Find a quiet channel.
        channel = await self.find_quiet_channel(check)
        if channel is None:
            return

        # Commands to choose between, all which should work.
        coms = random.choices(["explode", "beast", "pokemon", "catch", "fish", "meme", "randomfact", "pat"],
                              k=random.randint(1, 3))

        # Use each, waiting in between.
        for command in coms:
            await self.bot.speak_in(channel, f"%{command}")

            # await asyncio.sleep(random.randint()) # need to be sure that hal doesn't come back in
            # in the middle of a conversation.


def setup(bot: LilHalJr) -> None:
    """
    Set up function for load_extension.
    :param bot: Expecting Lil Hal Jr.
    :return: No return value.
    """
    bot.add_cog(SocialCog(bot))
