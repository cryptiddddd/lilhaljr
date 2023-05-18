import datetime as dt
import random


def random_number(percentage: bool = False) -> str:
    """
    Creates a random number for Hal to spit out. Returns it as a string.
    :param percentage: If the number should be a [real] percentage, or not.
    :return: Written string of a number or percentage.
    """

    def flat_numbers(number: str) -> int:
        """ Converts a string into an int, regardless of decimal presence. """
        return round(float(number)) if "." in number else int(number)

    def add_decimal(number: str, position: int = None) -> str:
        """ Adds a decimal at the given position. """
        # No space for a decimal
        if len(number) == 1:
            return number

        elif position is None:
            position = random.randint(0, len(number))

        return number[:position] + "." + number[position:]

    # Decide length.
    length = random.sample([0, 1, 2, 3, 4, 5], k=1, counts=[1, 10, 22, 15, 5, 2])[0]

    # Get digits.
    if length == 0:
        digits = "0"
    else:
        digits = "".join([str(random.randint(0, 9)) for _ in range(length)])

    # Add decimal.
    if percentage:
        digits = add_decimal(digits, 2)

    elif not random.randint(0, 3):
        digits = add_decimal(digits)

    # Final checks
    while not digits == "0" and digits.startswith("0") and not digits.startswith("0."):
        digits = digits[1:]

    if digits.startswith("."):
        digits = f"0{digits}"
    elif digits.endswith("."):
        digits = digits[:-1]

    if percentage:
        digits += "%"

    # If not percentage, possibly turn to hex or binary.
    elif not random.randint(0, 3):
        modify = random.sample([hex, bin, oct], k=1, counts=[5, 5, 1])[0]
        digits = modify(flat_numbers(digits))

    return digits


def random_time(first: int, last: int) -> dt.time:
    """
    Creates a random time between the given hours.
    :param first: The earliest hour.
    :param last: The latest hour.
    :return: A randomized `datetime.time` object.
    """
    return dt.time(random.randint(first, last - 1),
                   random.randint(0, 59),
                   random.randint(0, 59),
                   tzinfo=dt.timezone(dt.timedelta(hours=-8)))
