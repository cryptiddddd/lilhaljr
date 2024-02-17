"""
    A class for joining in a specific interaction, filtered by channel to prevent repeats.
"""
from __future__ import annotations

import asyncio
import random
import typing

import discord


CURRENT_DIR: dict[int, Join] = {}


class Join:
    @classmethod
    def get(cls, channel: discord.TextChannel, *args, **kwargs) -> Join:
        """
        Fetches/creates a Join for the given channel.
        :param channel: The given channel.
        :return: An instance of Join.
        """
        # Create new if it doesn't exist.
        if channel.id not in CURRENT_DIR.keys():
            CURRENT_DIR[channel.id] = cls(channel, *args, **kwargs)
            asyncio.create_task(CURRENT_DIR[channel.id].await_and_terminate())  # Begin process.

        # Increase call count and return
        return CURRENT_DIR[channel.id]

    def __init__(self, channel: discord.TextChannel,
                 callback: typing.Callable,
                 end_on: typing.Callable[[], typing.Coroutine]):
        """
        Initializes a Join event
        :param callback: A callable function to be triggered.
        :param end_on: A coroutine that will return when the instance can be removed.
        """
        self.channel_id = channel.id
        self.__callback = callback
        self.__end_on = end_on

        # Init variables
        self.__calls = 0  # Counts how many times an event was triggered.
        self.performed = False  # Tracks if the callback has been triggered yet.
        self.__awaiting_termination = False

    def call(self) -> None:
        """
        Triggers a call to the given event. The callback will have a chance of firing.
        """
        self.__calls += 1

        if not self.performed and random.random() < (self.__calls / 3):
            asyncio.create_task(self.__callback())
            self.performed = True

    async def await_and_terminate(self) -> None:
        """
        Awaits the given end_on coroutine and terminates the instance.
        """
        if self.__awaiting_termination:
            return

        # Set flag, await, and pop.
        self.__awaiting_termination = True
        await self.__end_on()
        CURRENT_DIR.pop(self.channel_id)
