import os
import asyncio
from dotenv import load_dotenv
import datetime as dt

import discord
from discord.ext import commands

from random import random, randint, choice

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# this could just be a client, i do not know if it needs to be a bot, but ok!
#   having owner-only commands could be a good idea for manually muting hal from an entire server, etc
lil_hal_junior = commands.Bot(command_prefix=None, intents=discord.Intents.all(), case_insensitive=True)

RESPONSES = ["Hmm.", "Yes.", "Interesting."]
SHUT_UP_QUERIES = ["hush", "shut up", "be quiet", "go away"]
quiet_channels = []


def timestamp() -> str:
    return dt.datetime.now().strftime('[%m/%d/%Y | %H:%M:%S]')


# ------------------------------ EVENTS ------------------------------ #
@lil_hal_junior.event
async def on_ready():
    """
    Once connected, Lil Hal Junior sets his status to "online". The console prints a list of connected servers.
    """
    await lil_hal_junior.change_presence(status=discord.Status.online)

    stamp = timestamp()
    message = f"{stamp} {lil_hal_junior.user.name} has connected to:"
    whitespace = " " * (len(stamp) + 1)
    connect = "\n" + whitespace + " " * 6
    print(message, connect.join([""] + [g.name for g in lil_hal_junior.guilds]))


@lil_hal_junior.event
async def on_guild_join(guild: discord.Guild):
    print(f"{timestamp()} {lil_hal_junior.user.name} has joined {guild.name}!")


@lil_hal_junior.event
async def on_guild_remove(guild: discord.Guild):
    print(f"{timestamp()} {lil_hal_junior.user.name} has left {guild.name}!")


@lil_hal_junior.event
async def on_message(message: discord.Message):
    """
    On receiving a message, Lil Hal Junior decides whether to respond. If he is mentioned in a message, he will respond
    sooner rather than later. After a randomized moment of time without receiving a message, he sends one of three
    responses.
    :param message:
    :return:
    """
    # If Hal has been muted in the channel, he will not say anything, nothing will happen.
    if message.channel.id in quiet_channels:
        return

    # If Hal is referenced and told to shut up, he will give a stoic thumbs up, and cease chatter for about 58 minutes.
    if "hal" in message.content.lower().split():
        for cue in SHUT_UP_QUERIES:
            if cue in message.content.lower():
                await message.add_reaction('👍')
                quiet_channels.append(message.channel.id)

                await asyncio.sleep(3600 + randint(-900, 900))

                quiet_channels.remove(message.channel.id)
                return

    # If it is Hal talking, or if the message isn't interesting enough, he will say nothing.
    if message.author == lil_hal_junior.user or len(message.content) < 10:
        return

    # If Hal is mentioned, with more than just a ping, he will wait a moment before responding.
    elif lil_hal_junior.user.mentioned_in(message):
        if message.content.strip() == f"<@!{lil_hal_junior.user.id}>":
            return

        await asyncio.sleep(randint(1, 4))
        await message.channel.send(choice(RESPONSES))
        return

    def check(m):
        return m.channel == message.channel

    # This is the cycle of waiting that decides when he will acknowledge/participate in conversation.
    try:
        await lil_hal_junior.wait_for('message', check=check, timeout=randint(13, 25) + random())
    except asyncio.TimeoutError:
        await message.channel.send(choice(RESPONSES))


# ------------------------------ RUN ------------------------------ #
lil_hal_junior.run(TOKEN)
