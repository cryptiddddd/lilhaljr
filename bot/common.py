import asyncio
import random

import discord

import helpers

# ====================== VARS
muted_channels = {}


# ====================== SYNCHRONOUS FUNCTIONS
def emoji_confirmation(message: discord.Message, thumbs_up: bool = True) -> None:
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

        await pause(base_time=0)  # Tiny pause.
        await message.add_reaction(reaction)

    asyncio.create_task(response())


# ====================== ASYNC ROUTINES
async def pause(low: int = 5, high: int = 20, multiplier: int = None, base_time: int = None) -> None:
    """ Pausing shortcut, using asyncio.sleep(). Pauses within the given range. """
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


async def speak_in(channel: discord.TextChannel, message: str = None, **kwargs) -> discord.Message | None:
    """
    Hal speaks in a channel.
    :param channel: Channel to speak in.
    :param message: The content to send. Optional: if None, replaced by hmm/yes/interesting.
    :param kwargs: All keyword arguments are passed through `channel.send()`.
    :return:
    """
    # Safety, possible double safety.
    if not channel.can_send(discord.Message):
        return

    # Generate dialogue.
    if message is None:
        message = helpers.basic()

    # Send.
    await channel.trigger_typing()
    await pause(0, (len(message) % 80) // 5)

    return await channel.send(message, **kwargs)


async def introduce_self(channel: discord.TextChannel) -> None:
    """
    Hal sends an introduction to the given channel.
    :param channel: Expected introduction channel.
    :return: No return value
    """
    await pause(20, 25)
    intro = "Hal\nHe/It\nI can quiet down when you tell me."

    await speak_in(channel, intro)


async def say_hello(channel: discord.TextChannel) -> None:
    """
    Hal says hello.
    :param channel: Channel in which to say hello.
    :return: No return value
    """
    await pause(5, 10)
    await speak_in(channel, "Hello.")
