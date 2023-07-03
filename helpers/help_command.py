from discord.ext import commands

import config

from .views import HelpCogEmbed, HelpCommandEmbed


class LilHalJrHelp(commands.HelpCommand):
    """
    Lil Hal Jr's help command.
    """
    def __init__(self, bot, **options):
        """
        Initializes and connects Lil Hal Jr directly.
        :param bot: Expects Lil Hal Jr.
        :param options: Arbitrary options.
        """
        super().__init__(**options)
        self.bot = bot

    async def command_callback(self, ctx: commands.Context, *, command: str = None) -> None:
        """
        Callback for the help command. Enforces case-insensitivity.
        :param ctx: Command context.
        :param command: Command query
        :return: No return value.
        """
        # Conditional correction
        if command is not None:
            command = command.lower()

        if command in ["dev", "social", "logging"]:
            command = command.capitalize()

        # Carry on.
        await super().command_callback(ctx, command=command)

    async def command_not_found(self, command_name: str) -> None:
        """ Handles missing command. """
        self.bot.emoji_confirmation(self.context.message, thumbs_up=False)

    async def send_cog_help(self, cog: commands.Cog) -> None:
        """
        Sends help for a specific cog.
        :param cog:
        :return:
        """
        channel = self.get_destination()
        embed = HelpCogEmbed(cog)

        await self.bot.speak_in(channel, embed=embed)

    async def send_command_help(self, command: commands.Command) -> None:
        """
        Sends help for a command.
        :param command: Queried command.
        :return: No return value.
        """
        channel = self.get_destination()
        embed = HelpCommandEmbed(command)

        await self.bot.speak_in(channel, embed=embed)

    async def send_bot_help(self, *_ignore) -> None:
        """
        Sends default bot help message, set in config.py.
        :param _ignore: Ignores any arguments.
        :return: No return value.
        """
        channel = self.get_destination()
        await self.bot.speak_in(channel, config.HELP_MESSAGE)
