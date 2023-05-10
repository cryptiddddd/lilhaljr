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
        Initialize Lil Hal Jr. All intents, case insensitive.
        """
        self.quiet_channels = set()
        super().__init__(command_prefix="^",
                         intents=discord.Intents.all(),
                         case_insensitive=True,
                         help_command=None)

    # ==================================== HELPER OPERATIONS ====================================
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
        :param first: The earliest hour.
        :param last: The latest hour.
        :return: A randomized datetime.time object.
        """
        return dt.time(random.randint(first, last - 1),
                       random.randint(0, 59),
                       random.randint(0, 59),
                       tzinfo=dt.timezone(dt.timedelta(hours=-8)))

    # ==================================== HELPER OPERATIONS ====================================
    async def be_quiet(self, message: discord.Message) -> int:
        """
        Reads a message and parses for a request to be quiet.
        :param message: The message to review.
        :return: A value > 0 if Hal has been told to be quiet. This value is the "rudeness level".
        """
        # Not talking to Hal.
        if not await self.is_referenced(message):
            return False

        # Check for keywords.
        original = message.content.lower()

        # Get rudeness level.
        for query, level in config.quiet_phrases.items():
            if query in original:
                return level
        else:
            return 0

    @staticmethod
    def clean_string(text: str) -> str:
        """
        Cleans a string of all punctuation, returns it lowercase.
        :param text: Input text.
        :return: Output text.
        """
        new_text = ""
        for i in text.lower():
            # Save letters, numbers, and spaces.
            if i.isalnum() or i.isspace():
                new_text += i

        return new_text

    async def is_referenced(self, message: discord.Message) -> bool:
        """
        Checks if Hal is mentioned/referenced in the given message.
        :param message:
        :return: True if Hal is pinged, or mentioned by name.
        """
        return self.user.mentioned_in(message) or "hal" in message.content.split() \
            or self.user in [m.author async for m in message.channel.history(limit=2)]

    async def pause(self, low: int = 5, high: int = 20, multiplier: int = None) -> None:
        """ Pausing shortcut, using asyncio.sleep(). Pauses within the given range. """
        if multiplier is not None:
            high += round(high * multiplier / 4)

        if low >= high:
            base_time = low
        else:
            base_time = random.randint(low, high)

        await asyncio.sleep(base_time + random.random())

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
        await self.pause(1, len(message) // 4)

        await channel.send(message)

    async def thumbs_up(self, message: discord.Message, up: bool = True) -> None:
        """
        Reacts to the given message with an ice-cold thumbs up.
        :param message:
        :param up: True for thumbs up, false for thumbs down.
        :return:
        """
        reaction = '👍' if up else '👎'

        high = max(2, len(message.content) // 6)
        await self.pause(1, high)
        await message.add_reaction(reaction)

    async def wait_loop(self, message: discord.Message) -> None:
        """
        The main event. Waiting loop, eventually speaks if/when it times out.
        :param message:
        :return:
        """
        wait = random.randint(1, 4) if await self.is_referenced(message) else None

        def check(channel: discord.TextChannel, *_) -> bool:
            """ Simple check. Return `True` extends the wait. """
            return channel == message.channel

        # This is the cycle of waiting that decides when he will acknowledge/participate in conversation.
        try:
            await self.wait_for('typing', check=check, timeout=wait or random.randint(9, 25) + random.random())
        except asyncio.TimeoutError:
            await self.speak_in(message.channel)

    # ==================================== EVENTS ====================================
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
        # Process commands. No response if a command was processed.
        await self.process_commands(message)
        if message.channel.last_message.author == self.user:
            return

        # Clean up content, altering the message object. Questionable!
        message.content = self.clean_string(message.content)

        # Check if he has been muted.
        if message.channel.id in self.quiet_channels or message.author == self.user:
            return

        elif level := await self.be_quiet(message):
            await self.thumbs_up(message)

            # Be quiet, but only for so long. 
            self.quiet_channels.add(message.channel.id)
            await self.pause(2700, 4500, level)
            self.quiet_channels.discard(message.channel.id)

        # If the message isn't interesting enough, say nothing.
        elif len(message.content) < 10:
            return

        # The main event.
        else:
            await self.wait_loop(message)

    async def on_guild_remove(self, guild: discord.Guild):
        # Clear all silenced channels.
        for channel in guild.channels:
            self.quiet_channels.discard(channel.id)
