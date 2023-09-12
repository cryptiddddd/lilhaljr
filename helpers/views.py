import discord
from discord.ext import commands

import config

COLOR = discord.Color.from_rgb(242, 164, 0)


class HelpEmbed(discord.Embed):
    """
    Base for Lil Hal Jr.'s help. Contains message for blank information field, and sets Hal's color.
    """
    blank_message = "No information provided."

    def __init__(self, title: str, description: str):
        """
        Creates template embed with the given title and description.
        :param title: Embed title.
        :param description: Embed description.
        """
        super().__init__(type="rich", color=COLOR, title=title, description=description)
        self.set_author(name="Lil Hal Jr.")


class HelpCommandEmbed(HelpEmbed):
    """
    Lil Hal Jr's command help embed.
    """
    def __init__(self, command: commands.Command):
        """
        Creates a help embed for a single command.
        :param command: Queried command.
        """
        # Create description text.
        description = f"`^{command.qualified_name.capitalize()}"
        description += f" {command.usage}" if command.usage else ""  # Example/template usage.
        description += "`\n\n"  # Close example.

        description += command.help if command.help else self.blank_message

        if len(command.aliases) > 0:
            aliases = ", ".join([f"`{alias}`" for alias in command.aliases])
            description += f"\n\nAliases: {aliases}."

        # Init.
        super().__init__(title=command.qualified_name.capitalize(),
                         description=description)


class HelpCogEmbed(HelpEmbed):
    """
    Lil Hal Jr's cog help embed.
    """
    def __init__(self, cog: commands.Cog):
        """
        Creates a help embed based off a single cog.
        :param cog: Command cog.
        """
        super().__init__(title=cog.qualified_name,
                         description=cog.description if cog.description else self.blank_message)

        cog_commands = cog.get_commands()
        for command in cog_commands:
            self.add_field(name=f"`^{command.qualified_name.capitalize()}`",
                           value=command.description if command.description else self.blank_message,
                           inline=False)

        self.set_footer(text=f"{len(cog_commands)} commands.")


class InfoEmbed(discord.Embed):
    """
    A small footer embed for quick debug/info messages to be sent in Discord.
    """
    def __init__(self, text: str):
        """
        Builds info footer with the given message.
        """
        super().__init__(type="rich", color=COLOR)

        self.set_footer(text=text)


class PhrasesEmbed(discord.Embed):
    """
    A more complex embed for debug/dev messages to be sent in Discord.
    """
    def __init__(self):
        """
        Builds an info embed with the given fields of information.
        """
        super().__init__(type="rich", color=COLOR, description=f"Silencing emoji: {config.QUIET_EMOJI}")

        for label, phrases in [
            ("Silencing phrases", config.quiet_phrases),
            ("Returning phrases", config.return_phrases)
        ]:
            value = "\n".join(phrases)
            self.add_field(name=label + ":", value=value, inline=True)
