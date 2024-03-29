import asyncio
import logging
import random
import typing

import discord
from discord.ext import commands, tasks

from bot import LilHalJr, common
import config
import helpers

logger = logging.getLogger("lilhaljr")


class SocialCog(commands.Cog, name="Social"):
    """
    Hal will attempt to be a little more social with this cog.
    """

    def __init__(self, bot: LilHalJr):
        self.bot = bot

        self.bot_interaction_loop.start()

    # ==================================== HELPER OPERATIONS ====================================
    @staticmethod
    def __find_channel_by_keyword(guild: discord.Guild, keyword: str) -> discord.TextChannel | None:
        """
        Finds a channel in a given guild with a very simple keyword search.
        :param guild: Guild to search.
        :param keyword: Keyword to use.
        :return: Matching channel, if any. None otherwise.
        """
        for channel in guild.text_channels:
            if channel.can_send(discord.Message) and keyword.lower() in channel.name.lower():
                return channel

    async def find_quiet_channel(self, condition: typing.Callable[[discord.TextChannel], bool] = None) \
            -> discord.TextChannel:
        """
        Hal finds a quiet channel, with an optional additional condition.
        :param condition: A callable function that takes a text channel for input, and returns a bool
        :return: Suitable channel.
        """

        def name_check(ch: discord.TextChannel) -> bool:
            """ This ensures the given channel is appropriate to chat in. """
            return "intro" not in ch.name.lower() and "vent" not in ch.name.lower()

        def validate(ch: discord.TextChannel) -> bool:
            """ Tests the given channel. """
            test = condition(ch) if condition else True  # Condition can be None, be wary.
            return ch.can_send(discord.Message) and test and name_check(ch)

        # Get a list of candidate channels. Checks home guild first.
        home_guild = self.bot.get_guild(config.HOME_GUILD)
        secret_guild = self.bot.get_guild(config.SECRET_GUILD)
        channels = list(filter(validate, home_guild.text_channels + secret_guild.text_channels))

        def channel_check(ch: discord.TextChannel, *_) -> bool:
            """ Checks if the typing channel is in the list. """
            return ch in channels

        while len(channels) > 0:
            try:
                typing_result = await self.bot.wait_for("typing", check=channel_check, timeout=10)
                channels.remove(typing_result[0])

            except asyncio.TimeoutError:
                break

        if len(channels) >= 1:
            return channels[0]

    async def wait_until_quiet(self, channel: discord.TextChannel) -> None:
        """
        Waits for the given channel to quiet down, when no one is typing anymore. Returns when ready.
        :param channel: Channel to wait in.
        :return: No value. Just returns when ready.
        """
        # Loop until quiet.
        while True:
            try:
                wait = random.randint(9, 25) + random.random()
                await self.bot.wait_for("typing", check=lambda c, u, w: c == channel, timeout=wait)

            # Loop breaks, return.
            except asyncio.TimeoutError:
                break

    # ==================================== EVENTS ====================================
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """
        Hal says hello joining a guild.
        :param guild:
        """
        # Say hello
        channel = self.__find_channel_by_keyword(guild, "general")
        if channel is not None:
            asyncio.create_task(common.say_hello(channel))

        # Introduce self.
        channel = self.__find_channel_by_keyword(guild, "intro")
        if channel is not None:
            asyncio.create_task(common.introduce_self(channel))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """
        Hal says hello to a new person.
        :param member: Joining member.
        """
        # A place to save the channel.
        channel = []

        def check(m: discord.Message) -> bool:
            """ Checks that a message is from the new member. """
            result = m.author == member and m.guild == member.guild and "intro" not in m.channel.name.lower()

            # Save the channel.
            if result:
                channel.append(m.channel)

            return result

        # Wait for them to say something.
        try:
            await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:  # If they don't, no big deal.
            return

        # Grab the saved channel and say hello.
        channel = channel[0]
        await common.say_hello(channel)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        Certain social interactions on message.
        """
        if message.content.lower().startswith("%toast"):
            print("toast happening...")

            async def callback() -> None:
                """ A callback for the Join instance to fire."""
                await common.speak_in(message.channel, "%Toast")

            async def complete() -> None:
                """ A callback that returns when the Join can be deleted. """
                await self.bot.wait_for("message",
                                        check=lambda m: m.author.id == config.CRANEBOT_ID
                                        and m.channel == message.channel)

            # Create a custom event that
            helpers.Join.get(message.channel, callback, complete).call()

    # @commands.Cog.listener()
    # async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
    #     """ When a general command error occurs. """
    #     print(error, type(error))
    #
    #     if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
    #         common.emoji_confirmation(ctx.message, False)

    # ==================================== LOOPS ====================================
    @tasks.loop(hours=5)
    async def bot_interaction_loop(self):
        """ Every now and again, Hal will try to interact with other bots. """
        logger.info("Running bot interaction loop.")

        # List of possible interactions and their prefixes and commands.
        bot_info = [
            (config.CRANEBOT_ID, '%',
             ["pokemon", "beast", "catch", "explode", "meme", "tarot", "beef", "highfive", "pat", "dex",
              "bestiary", "randomfact", "cast"],
             [7, 7, 3, 7, 6, 5, 6, 4, 4, 1, 1, 6, 2]),
            (config.TOASTY_ID, ';', ["pokemon", "cat", "cow", "shrug", "lenny", "punch"])
        ]

        # Shuffle interactions.
        random.shuffle(bot_info)  # Commented out until there are more bots to interact with.

        for info in bot_info:
            result = await self.bot_command_interaction(*info)

            # If no interaction, or by random change, run the next interaction.
            if not result or not random.randint(0, 10):
                continue

            # Default is to break.
            break

        # Shake up the time between commands.
        next_time = helpers.random_time(6, 21)
        self.bot_interaction_loop.change_interval(time=next_time)
        logger.info(f"Bot interaction loop will run again at {next_time}...")

    @bot_interaction_loop.before_loop
    async def before_bot_loop(self):
        """ Simply waits until ready before doing anything. """
        await self.bot.wait_until_ready()

        logger.info("Starting bot interaction loop...")

    async def bot_command_interaction(self, bot_id: int, command_prefix: str,
                                      command_list: list[str], command_weights: list[int] = None) -> bool:
        """
        Attempts to interact with another bot through commands.
        :param bot_id: Discord user ID of the bot.
        :param command_prefix: The bot's prefix.
        :param command_list: List of the given bot's commands to pick from.
        :param command_weights: Command weights, optional.
        :return: True if an interaction is attempted. False if not.
        """

        def check_online(c: discord.TextChannel) -> bool:
            """ A check that the bot is in a channel and online. """
            bot = c.guild.get_member(bot_id)
            return bot is not None and bot.status != discord.Status.offline

        # Find a quiet channel that also passes the above test.
        channel = await self.find_quiet_channel(check_online)
        if channel is None:
            return False

        def msg_check(m: discord.Message) -> bool:
            """ For checking that the command yields a response. """
            return (m.author.id == bot_id or m.author.bot) and m.channel == channel

        # Use a couple commands, waiting for responses in between.
        coms = random.choices(command_list, k=random.randint(1, 3), weights=command_weights)

        for command in coms:
            command_usage = command_prefix + command.capitalize() + " "

            # Special command cases.
            if command == "explode":
                # Random chance of Toasty targeting, if applicable.
                if not random.randint(0, 5) and (toasty := channel.guild.get_member(config.TOASTY_ID)):
                    targets = [toasty]

                # Possible targets, anyone but self and Cranebot. Collect their mentions.
                else:
                    targets = [m.author async for m in channel.history(limit=3) if m.author.id not in
                               [config.CRANEBOT_ID, self.bot.user.id]]

                if len(targets) > 0:
                    command_usage += random.choice(targets).mention

            elif command == "punch":
                command_usage += channel.guild.get_member(config.TOASTY_ID).mention

            elif command == "tarot" and not random.randint(0, 150):
                command_usage += helpers.existential_question()

            elif command == "cast":
                command_usage += helpers.random_word()

            await self.wait_until_quiet(channel)
            await common.speak_in(channel, command_usage)

            # Wait for a response.
            try:
                await self.bot.wait_for("message", check=msg_check, timeout=random.randint(10, 25))

            # Be sad if there is none, return value indicating no response.
            except asyncio.TimeoutError:
                await common.speak_in(channel, helpers.disappointment())
                return False

        await common.speak_in(channel, helpers.thank_you())
        return True

    # ==================================== COMMANDS ====================================
    @commands.command(name="inquire", help="Ask Lil Hal Junior a question.", aliases=["inquiry", "ask"],
                      usage="[ Optional question ]")
    async def command_inquire(self, ctx: commands.Context, *, query: str):
        """
        Ask Lil Hal Junior a question, and Lil Hal Junior will respond in the most asinine way.
        :param ctx: Context.
        :param query: The user's question.
        """
        await common.speak_in(ctx.channel, helpers.inquire_answer(ctx.message))

    @commands.command(name="kiss", help="Bestow a kiss upon Lil Hal Junior.")
    async def command_kiss(self, ctx: commands.Context):
        """ Gives Lil Hal Junior a kiss, similar to Cranebot's %kiss. """
        await common.speak_in(ctx.channel, f"Oh, {helpers.thank_you().lower()}")

    @commands.command(name="scrabble", help="Draw Scrabble tiles.")
    async def command_scrabble(self, ctx: commands.Context, tiles: int = 7):
        """ Draws an amount of Scrabble tiles for the user to contemplate. """
        letters = helpers.Scrabble.single_draw(tiles)
        await common.speak_in(ctx.channel, " ".join(f"` {i} `" for i in letters))

    @command_scrabble.error
    async def command_scrabble_error(self, ctx: commands.Context, error: commands.CommandError):
        """ Error handling for Scrabble. """
        if isinstance(error, commands.CommandInvokeError) and isinstance(error.original, ValueError):
            common.emoji_confirmation(ctx.message, thumbs_up=False)
            await common.speak_in(ctx.channel, random.choice([
                "Not enough Scrabble tiles in the bag.",
                "There are only 98 tiles in the bag.",
                "I have only 98 Scrabble tiles."
            ]))


def setup(bot: LilHalJr) -> None:
    """
    Set up function for load_extension.
    :param bot: Expecting Lil Hal Jr.
    :return: No return value.
    """
    bot.add_cog(SocialCog(bot))
