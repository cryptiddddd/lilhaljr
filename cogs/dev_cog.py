import discord
from discord.ext import commands

from bot import LilHalJr
import config


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

    @commands.command(name="goodnight")
    async def command_good_night(self, ctx: commands.Context):
        """
        Disconnects and closes Lil Hal Jr safely.
        :param ctx:
        """
        await self.bot.thumbs_up(ctx.message)

        await self.bot.pause(1, 2)
        await self.bot.change_presence(status=discord.Status.offline)

        await self.bot.close()
        quit(0)

    @commands.command(name="keyword")
    async def command_add_keyword(self, ctx: commands.Context, *, new_phrase: str):
        """
        Allows the developer to add a key phrase to tell Hal to be quiet.
        :param ctx:
        :param new_phrase: A phrase to add to `quiet_keywords`.
        """
        config.quiet_phrases.append(new_phrase.lower())
        await self.bot.thumbs_up(ctx.message)

    @commands.command(name="ping")
    async def command_ping(self, ctx: commands.Context):
        """
        Pings to test Hal's response.
        :param ctx:
        """
        await self.bot.thumbs_up(ctx.message)


def setup(bot: LilHalJr) -> None:
    """
    Set up function for load_extension.
    :param bot: Expecting Lil Hal Jr.
    :return: No return value.
    """
    bot.add_cog(DevCog(bot))
