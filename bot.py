import asyncio
import logging
import random
import re

import discord
from discord.ext import commands

import config
import helpers

logger = logging.getLogger("lilhaljr")


class LilHalJr(commands.Bot):
    """
    Lil Hal Jr.
    """
    def __init__(self):
        """
        Initialize Lil Hal Jr. All intents, case-insensitive.
        """
        self.name_pattern = re.compile(r"\bhal\b", re.IGNORECASE)

        self.quiet_channels = set()
        super().__init__(command_prefix='^',
                         intents=discord.Intents.all(),
                         case_insensitive=True,
                         help_command=helpers.LilHalJrHelp(self))

    # ==================================== HELPER OPERATIONS ====================================
    @property
    def dialogue(self) -> str:
        """ Returns Lil Hal Junior's famous catchphrase. """
        if not random.randint(0, 199):
            return "Oh."

        return random.choice(["Hmm.", "Yes.", "Interesting."])

    # ==================================== HELPER OPERATIONS ====================================
    async def check_quiet_request(self, message: discord.Message) -> int:
        """
        Reads a message and parses for a request to be quiet.
        :param message: The message to review.
        :return: A value > 0 if Hal has been told to be quiet. This is the "rudeness level".
        """
        # Not talking to Hal.
        if not await self.is_referenced(message):
            return False

        original = message.content.lower()

        # Check for keywords/regex, get level.
        for query, level in config.quiet_phrases.items():
            if r"\b" in query and re.findall(query, message.content, re.I):
                return level

            elif query in original:
                return level

        else:
            return 0

    def emoji_confirmation(self, message: discord.Message, thumbs_up: bool = True) -> None:
        """
        Reacts to the given message with an ice-cold thumbs up. Or thumbs down.
        NOTE: Non-asynchronous. This creates an asyncio task, which will execute in parallel.
        :param message:
        :param thumbs_up: True for thumbs up, false for thumbs down.
        :return:
        """
        async def response():
            """ Pauses, responds to the message. """
            reaction = '👍' if thumbs_up else '👎'

            await self.pause(base_time=0)  # Tiny pause.
            await message.add_reaction(reaction)

        asyncio.create_task(response())

    async def is_referenced(self, message: discord.Message) -> bool:
        """
        Checks if Hal is mentioned/referenced in the given message.
        :param message:
        :return: True if Hal is pinged, or mentioned by name.
        """
        return self.user.mentioned_in(message) or self.name_pattern.findall(message.content)

    def mute_in(self, channel: discord.TextChannel, level: int = 2) -> None:
        """
        Creates an asyncio task to mute the given channel for a variable amount of time.
        :param channel: The channel to mute.
        :param level: The rudeness level.
        """
        async def mute_and_wait() -> None:
            """ Coroutine. Mutes for a variable amount of time."""
            self.quiet_channels.add(channel.id)
            await self.pause(2700, 4500, level)  # TODO: Add waiting loop for a "come back" keywords
            self.quiet_channels.discard(channel.id)

        asyncio.create_task(mute_and_wait())

    async def pause(self, low: int = 5, high: int = 20, multiplier: int = None, base_time: int = None) -> None:
        """ Pausing shortcut, using asyncio.sleep(). Pauses within the given range. """
        # TODO: Redesign, and documentation
        if base_time is None:
            # Apply multiplier -- work in progress.
            if multiplier is not None:
                high += round(high * multiplier / 4)

            # If low is less than high, as it should be.
            if low < high:
                base_time = random.randint(low, high)
            else:
                base_time = low

        await asyncio.sleep(base_time + random.random())

    async def speak_in(self, channel: discord.TextChannel, statement: str = None, **kwargs) -> None:
        """
        Hal speaks in a channel.
        :param channel:
        :param statement:
        :param kwargs: All keyword arguments are passed through `channel.send()`.
        :return:
        """
        # Safety, possible double safety.
        if channel.id in self.quiet_channels or not channel.can_send(discord.Message):
            return

        # Possible overwrite.
        message = self.dialogue if statement is None else statement

        # Send.
        await channel.trigger_typing()
        await self.pause(1, len(message) % 60 // 4)

        await channel.send(message, **kwargs)

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
            await self.wait_for("typing", check=check, timeout=wait or random.randint(5, 12) + random.random())
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
        # Check if he has been muted.
        elif message.channel.id in self.quiet_channels or message.author == self.user:
            return

        # Clean up content, altering the message object. Questionable!
        message.content = helpers.clean_string(message.content)

        if level := await self.check_quiet_request(message):
            # Confirm request, dispatch mute duration.
            self.emoji_confirmation(message)
            self.mute_in(message.channel, level)

        # If the message isn't interesting enough, say nothing.
        elif len(message.content.split()) < 3:
            return

        # The main event.
        else:
            await self.wait_loop(message)

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member | discord.User):
        """
        Alternative method to mute Hal in a server: reaction with the shushing emoji.
        :param reaction: The Discord reaction.
        :param user: The user reacting.
        """
        # Ignore if the reaction isn't on Hal's message.
        if reaction.message.author != self.user:
            return

        # Shushing reaction.
        if reaction.emoji == config.QUIET_EMOJI:
            self.mute_in(reaction.message.channel)
            logger.info(f"[{reaction.message.channel}] {user} muted Hal.")

    async def on_guild_remove(self, guild: discord.Guild):
        # Clear all silenced channels.
        for channel in guild.channels:
            self.quiet_channels.discard(channel.id)
