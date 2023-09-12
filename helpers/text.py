import re
import typing

import discord


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


def check_match(matches: typing.Iterable[str], message: discord.Message, require: str = "hal") -> str:
    """
    Checks for matches in a message. Flexible between regex and non-regex tests.
    :param matches: List of matches as strings [words/regex].
    :param message: Discord message searching for a match.
    :param require: Additional string required to match. This is not included in the returned string.
        Default is "Hal".
    :return: Matched text. Empty string if none.
    """
    original = clean_string(message.content.lower())

    if require is not None and require not in original.split():
        return ""

    # Check for keywords/regex, get level.
    for query in matches:
        if r"\b" in query and re.findall(query, message.content, re.I):
            return query

        elif query in original:
            return query

    return ""
