import asyncio
import datetime as dt
import random

import discord
from discord.ext import commands

import config


class LilHalJr(commands.Bot):
    """
    Lil Hal Jr.
    """
    def __init__(self):
        """
        Initialize Lil Hal Jr. No command/prefix, all intents, case insensitive.
        """
        self.quiet_channels = set()
        super().__init__(command_prefix="^",
                         intents=discord.Intents.all(),
                         case_insensitive=True,
                         help_command=None)

    @property
    def dialogue(self) -> str:
        """ Returns Lil Hal Junior's famous catchphrase. """
        if not random.randint(0, 199):
            return "Oh."

        return random.choice(["Hmm.", "Yes.", "Interesting."])

    @staticmethod
    def random_time(first: int, last: int) -> dt.time:
        """
        Creates a random time between the given hours.
        :param first:
        :param last:
        :return:
        """
        return dt.time(random.randint(first, last - 1),
                       random.randint(0, 60),
                       random.randint(0, 60),
                       tzinfo=dt.timezone(dt.timedelta(hours=-8)))

    def is_referenced(self, message: discord.Message) -> bool:
        """
        Checks if Hal is mentioned/referenced in the given message.
        :param message:
        :return: True if Hal is pinged, or mentioned by name.
        """
        return self.user.mentioned_in(message) or "hal" in message.content.lower().split()

    async def be_quiet(self, message: discord.Message) -> int:
        """
        Reads a message and parses for a request to be quiet.
        :param message:
        :return: A value > 0 if Hal has been told to be quiet. This value is the "rudeness level".
        """
        # Not talking to Hal.
        if not self.is_referenced(message):
            return False

        # Check for keywords.
        original = message.content.lower()

        # Get rudeness level.
        for query, level in config.quiet_phrases.items():
            if query in original:
                return level
        else:
            return 0

    async def pause(self, low: int = 5, high: int = 20, multiplier: int = None) -> None:
        """ Pausing shortcut, using asyncio.sleep(). Pauses within the given range. """
        if multiplier is not None:
            high += round(high * multiplier / 4)

        await asyncio.sleep(random.randint(low, high) + random.random())

    async def speak_in(self, channel: discord.TextChannel, statement: str = None) -> None:
        """
        Hal speaks in a channel.
        :param channel:
        :param statement:
        :return:
        """
        # Safety, possible double safety.
        if channel.id in self.quiet_channels or not channel.can_send(discord.Message):
            return

        # Possible overwrite.
        message = self.dialogue if statement is None else statement

        # Send.
        await channel.trigger_typing()
        await self.pause(1, len(message) // 3)

        await channel.send(message)

    async def thumbs_up(self, message: discord.Message) -> None:
        """
        Reacts to the given message with an ice-cold thumbs up.
        :param message:
        :return:
        """
        high = max(2, len(message.content) // 6)
        await self.pause(1, high)
        await message.add_reaction('👍')

    async def wait_loop(self, message: discord.Message) -> None:
        """
        The main event. Waiting loop, eventually speaks if/when it times out.
        :param message:
        :return:
        """
        wait = random.randint(1, 4) if self.is_referenced(message) else None

        def check(channel: discord.TextChannel, *_) -> bool:
            """ Simple check. Return `True` extends the wait. """
            return channel == message.channel

        # This is the cycle of waiting that decides when he will acknowledge/participate in conversation.
        try:
            await self.wait_for('typing', check=check, timeout=wait or random.randint(9, 25) + random.random())
        except asyncio.TimeoutError:
            await self.speak_in(message.channel)

    async def on_ready(self):
        """
        Once connected, Lil Hal Junior sets his status to "online".
        """
        await self.change_presence(status=discord.Status.dnd)

    async def on_message(self, message: discord.Message):
        """
        Lil Hal Junior waits for a gap in conversation to say something
        :param message:
        """
        await self.process_commands(message)

        # If Hal has been muted in the channel, he will not say anything, nothing will happen.
        if message.channel.id in self.quiet_channels or message.author == self.user:
            return

        elif level := await self.be_quiet(message):
            await self.thumbs_up(message)

            self.quiet_channels.add(message.channel.id)
            await self.pause(2700, 4500, level)
            self.quiet_channels.discard(message.channel.id)

        # If the message isn't interesting enough, he will say nothing.
        elif len(message.content) < 10:
            return

        # The main event.
        else:
            await self.wait_loop(message)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        # Clear all silenced channels.
        for channel in guild.channels:
            self.quiet_channels.discard(channel.id)
