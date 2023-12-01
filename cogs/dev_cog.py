import logging

import discord
from discord.ext import commands

import helpers
from bot import LilHalJr, common


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
        """ Hal sends a list of muted channels. """
        channels = [self.bot.get_channel(i) for i in common.muted_channels]

        if len(channels) > 0:
            message = "Muted channels are: \n" + \
                      "\n".join([f"{ch.name} : {common.muted_channels[ch.id]}" for ch in channels])
        else:
            message = "No muted channels."

        embed = helpers.InfoEmbed(message)

        await common.speak_in(ctx.channel, embed=embed)

    @commands.command(name="check", help="Checks Lil Hal Jr's key phrases for reference.")
    async def command_check(self, ctx: commands.Context):
        """
        Sends an embed with information on Lil Hal Jr's silencing configuration.
        :param ctx:
        """
        # Send the phrases information embed.
        await common.speak_in(ctx.channel, embed=helpers.PhrasesEmbed())

    @commands.command(name="goodnight", help="Deactivates Lil Hal Jr safely.")
    async def command_good_night(self, ctx: commands.Context):
        """
        Disconnects and closes Lil Hal Jr safely.
        :param ctx:
        """
        # Response.
        common.emoji_confirmation(ctx.message)

        # Go offline.
        await common.pause(1, 2)
        await self.bot.change_presence(status=discord.Status.offline)

        # Close bot and quit program.
        await self.bot.close()
        quit(0)

    @commands.command(name="ping", help="Checks Hal's response time.")
    async def command_ping(self, ctx: commands.Context):
        """
        Pings to test Hal's response.
        :param ctx:
        """
        common.emoji_confirmation(ctx.message)


def setup(bot: LilHalJr) -> None:
    """
    Set up function for load_extension.
    :param bot: Expecting Lil Hal Jr.
    :return: No return value.
    """
    bot.add_cog(DevCog(bot))
