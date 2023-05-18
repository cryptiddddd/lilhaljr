import discord
from discord.ext import commands


class HelpEmbed(discord.Embed):
    """
    Lil Hal Jr's help embed. This displays his dev-only commands separate from his public commands.
    """


class InfoEmbed(discord.Embed):
    """
    A small footer embed for debug/info messages to be sent in Discord.
    """
    def __init__(self, text: str):
        """
        Builds info footer with the given message.
        """
        super().__init__(type="rich", color=discord.Color.from_rgb(242, 164, 0))

        self.set_footer(text=text)
