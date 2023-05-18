import logging

import discord
from discord.ext import commands

import helpers
from bot import LilHalJr
import config


logger = logging.getLogger("lilhaljr")


class DevCog(commands.Cog, name="Dev"):
    """
    Dev cog holds a secret interface for the developer and the developer only.
    """
    def __init__(self, bot: LilHalJr):
        """
        Initializes cog, connects to Hal.
        :param bot: Expected Lil Hal Jr.
        """
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        """
        Commands only work for the developer.
        :param ctx:
        :return: True if allowed.
        """
        return await self.bot.is_owner(ctx.author)

    @commands.command(name="channels", help="View currently muted channels.")
    async def command_channels(self, ctx: commands.Context):
        """
        Hal logs quiet channels, reacts with a thumbs up.
        """
        # self.bot.thumbs_up(ctx.message)

        channels = [self.bot.get_channel(i) for i in self.bot.quiet_channels]

        if len(channels) > 0:
            message = "Quiet channels are: " + ", ".join([ch.name for ch in channels])
        else:
            message = "No quiet channels."

        embed = helpers.InfoEmbed(message)

        await self.bot.speak_in(ctx.channel, embed=embed)

    @commands.command(name="goodnight", help="Deactivates Lil Hal Jr safely.")
    async def command_good_night(self, ctx: commands.Context):
        """
        Disconnects and closes Lil Hal Jr safely.
        :param ctx:
        """
        self.bot.thumbs_up(ctx.message)

        await self.bot.pause(1, 2)
        await self.bot.change_presence(status=discord.Status.offline)

        await self.bot.close()
        quit(0)

    @commands.command(name="keyword", usage="[ Rude level ] [ New phrase ]", help="Add a new phrase to quiet Hal.")
    async def command_add_keyword(self, ctx: commands.Context, rude_level: int, *, new_phrase: str):
        """
        Allows the developer to add a key phrase to tell Hal to be quiet.
        :param ctx:
        :param rude_level: The level of rudeness of the phrase.
        :param new_phrase: A phrase to add to `quiet_keywords`.
        """
        config.quiet_phrases[new_phrase.lower()] = rude_level
        # self.bot.thumbs_up(ctx.message)

        embed = helpers.InfoEmbed(f"Quiet key phrases: {config.quiet_phrases}")

        await self.bot.speak_in(ctx.channel, embed=embed)

    @commands.command(name="ping", help="Checks Hal's response.")
    async def command_ping(self, ctx: commands.Context):
        """
        Pings to test Hal's response.
        :param ctx:
        """
        self.bot.thumbs_up(ctx.message)


def setup(bot: LilHalJr) -> None:
    """
    Set up function for load_extension.
    :param bot: Expecting Lil Hal Jr.
    :return: No return value.
    """
    bot.add_cog(DevCog(bot))
