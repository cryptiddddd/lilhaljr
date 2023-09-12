import random

import discord

from .number import random_number
from .text import clean_string


def existential_question() -> str:
    """
    Generates a randomized existential question for Lil Hal Jr to ask.
    :return: A randomized existential question
    """
    if not random.randint(0, 100):
        return "Why?"

    # Possibly add more range in the future. For now, these are safe options.
    interrogative = random.choice(["Who", "What", "Where"])
    subject = random.choice(["am I", "are you", "are we", "is this"])
    return f"{interrogative} {subject}?"


def inquire_answer(message: discord.Message) -> str:
    """
    Generates a response for the ^inquire command. Involves a random number, with some punctuation.
    :param message:
    :return:
    """
    if not random.randint(0, 100):
        return inquire_non_answer(message)

    query = clean_string(message.content).split()[1]  # The first word is the question word.

    # Yes/no question.
    if query in {"am", "are", "can", "could", "did", "do", "does", "has", "have", "is", "may", "should", "was",
                 "were", "will", "would"}:
        answer = random_number(percentage=True)
        answer = f"There is a {answer} chance so"

        # Random addition.
        if not random.randint(0, 4):
            answer += random.choice([", however, I'm not sure.", "\b\bat least.", "\b\bat most.", "..."])
        else:
            answer += "."

    # Anything else.
    else:
        answer = random_number()

        if not random.randint(0, 5):
            answer += random.choice("?!")

    return answer


def inquire_non_answer(message: discord.Message) -> str:
    """
    Generates "I don't know" message.
    :param message: The Discord message being answered.
    :return: A randomized message.
    """
    if random.randint(0, 3):
        return "I just don't know."

    return f"I just don't know, {clean_string(message.author.name.capitalize())}."


def thank_you() -> str:
    """
    Generates "thank you" message.
    :return: A string ready to send.
    """
    return random.choice(["Thank you.", "Thank you very much.", "Thanks.", "Cool."])
