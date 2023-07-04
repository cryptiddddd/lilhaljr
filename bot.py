import asyncio
import logging
import random
import re

import discord
from discord.ext import commands, tasks

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

        self.quiet_channels = {}
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
        if not channel.can_send(discord.Message):
            return

        # Possible overwrite.
        message = self.dialogue if statement is None else statement

        # Send.
        await channel.trigger_typing()
        await self.pause(1, len(message) % 60 // 4)

        await channel.send(message, **kwargs)

    def clean_apprehension(self, modifier: int = 0) -> None:
        """
        Cleans up the quiet channel dictionary, removes any unmuted channels.
        """
        # Creating a list avoids runtime error.
        pop_channels = []

        for channel_id, value in self.quiet_channels.items():
            # Optional modifier
            if modifier:
                self.quiet_channels[channel_id] += modifier

            if value < 1:
                pop_channels.append(channel_id)

        for channel_id in pop_channels:
            self.quiet_channels.pop(channel_id)

    def update_apprehension(self, message: discord.Message) -> None:
        """
        Updates Hal's apprehension in a channel based on a message.
        :param message:
        :return:
        """
        # If channel is muted, check for unmuting keywords.
        if message.channel.id in self.quiet_channels.keys() and helpers.check_match(config.return_phrases, message):
            self.quiet_channels[message.channel.id] = 0

        # Check for muting keywords.
        # todo: maybe someday, this will hear All the shut up phrases, and add up their values.
        if mute_request := helpers.check_match(config.quiet_phrases.keys(), message):
            # Feedback.
            self.emoji_confirmation(message)

            # Get mute value, plus one for safety.
            mute_value = config.quiet_phrases[mute_request] + 1

            # Update quiet channels.
            try:
                self.quiet_channels[message.channel.id] += mute_value
            except KeyError:
                self.quiet_channels[message.channel.id] = mute_value

        self.clean_apprehension()

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
        # Don't respond to himself.
        if message.channel.last_message.author == self.user:
            return

        # Process commands. No response if a command was processed.
        await self.process_commands(message)

        # Check for muting/unmuting keywords.
        self.update_apprehension(message)

        # Check if muted.
        if message.channel.id in self.quiet_channels or message.author == self.user:
            return

        # Trigger waiting loop if message is long enough.
        elif len(message.content.split()) > 3:
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
            self.quiet_channels[reaction.message.channel.id] = 4  # this should actually add 4, but i'm not there yet.
            logger.info(f"[{reaction.message.channel}] {user} muted Hal.")

    async def on_guild_remove(self, guild: discord.Guild):
        # Clear all silenced channels.
        for channel in guild.channels:
            self.quiet_channels.pop(channel.id)

    # ==================================== TASKS ====================================
    @tasks.loop(minutes=15)
    async def apprehension_cooldown_loop(self) -> None:
        """
        Every fifteen minutes, Hal gets a little less apprehensive in each muted channel.
        """
        self.clean_apprehension(-1)

