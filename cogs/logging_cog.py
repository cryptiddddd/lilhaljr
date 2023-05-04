import logging

import discord
from discord.ext import commands

from bot import LilHalJr


logger = logging.getLogger("lilhaljr")

logger.setLevel(logging.DEBUG)

form = logging.Formatter(fmt="[%(asctime)s] %(levelname)s :: %(message)s",
                         datefmt="%m/%d/%Y | %H:%M:%S")

console_handler = logging.StreamHandler()
console_handler.setFormatter(form)

logger.addHandler(console_handler)


class LogCog(commands.Cog, name="Logs"):
    """
    This cog manages all logging stuff, ergo it is not mandatory.
    """
    def __init__(self, bot: LilHalJr):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Prints connected guilds and loaded cogs.
        """
        message = f"{self.bot.user.name} has connected to: "
        message += ", ".join([guild.name for guild in self.bot.guilds]) + ". "
        message += "With cogs: "
        message += ", ".join([cog for cog in self.bot.cogs.keys()]) + "."

        logger.info(message)

    @commands.Cog.listener()
    async def on_connect(self):
        logger.info("Connected.")

    @commands.Cog.listener()
    async def on_disconnect(self):
        logger.info("Disconnected.")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        logger.info(f"{self.bot.user.name} joined `{guild.name}`.")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        logger.info(f"{self.bot.user.name} left `{guild.name}`.")

        # Clear all silenced channels.
        for channel in guild.channels:
            self.bot.quiet_channels.discard(channel.id)

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        """ Reports command use. """
        logger.info(f"{ctx.author} used {self.bot.command_prefix}{ctx.command.name} in {ctx.channel}.")

    @commands.Cog.listener()
    async def on_error(self, event_method: str, *args, **kwargs):
        """ Attempts to log an error. """
        logger.error(f"on `{event_method}`: `{args}` and `{kwargs}`")


def setup(bot: LilHalJr) -> None:
    """
    Set up function for load_extension.
    :param bot: Expecting Lil Hal Jr.
    :return: No return value.
    """
    bot.add_cog(LogCog(bot))