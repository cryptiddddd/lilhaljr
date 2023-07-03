import random

import discord

from .number import random_number
from .text import clean_string


def inquire_non_answer(message: discord.Message) -> str:
    """
    Generates "I don't know" message.
    :param message: The Discord message being answered.
    :return: A randomized message.
    """
    if random.randint(0, 3):
        return "I just don't know."

    return f"I just don't know, {message.author.name}."


def inquire_answer(message: discord.Message) -> str:
    """
    Generates a response for the ^inquire command. Involves a random number, with some punctuation.
    :param message:
    :return:
    """
    if not random.randint(0, 200):
        return inquire_non_answer(message)

    query = clean_string(message.content).split()[0]  # The first word is the question word.

    # Yes/no question.
    if query in {"am", "are", "can", "could", "did", "do", "does", "has", "have", "is", "may", "should", "was",
                 "were", "will", "would"}:
        answer = random_number(percentage=True)
        answer = f"There is a {answer} chance so"

        # Random addition.
        if not random.randint(0, 4):
            answer += random.choice([", but I'm not sure.", " at least.", " at most.", "..."])
        else:
            answer += "."

    # Anything else.
    else:
        answer = random_number()

        if not random.randint(0, 5):
            answer += random.choice("?!")

    return answer