import random

import config


def is_safe_letters(letters: list[str]) -> bool:
    """
    Ensures that the chosen letters are appropriate.
    :param letters: A list of unsorted letters.
    :return: True if appropriate, false if inappropriate.
    """
    total = "".join(letters).lower()

    # Loop check.
    for word in config.bad_words:
        if word in total:
            return False

    # Passed
    return True


class Scrabble:
    """
    Acts as a bag of Scrabble tiles.
    """
    LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
               'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    COUNTS = [9, 2, 2, 4, 12, 2, 3, 2, 9, 1, 1, 4, 2, 6, 8, 2, 1, 6, 4, 6, 4, 2, 2, 1, 2, 1]

    @classmethod
    def single_draw(cls, n: int = 7):
        """
        One single draw of tiles from a Scrabble bag. This classmethod saves time and memory as it serves the same
        function as the class, without constructing a Scrabble object.
        :param n: How many tiles to draw. Default is 7, the amount one draws in a real game of Scrabble.
        """
        # Draw sample.
        letters = random.sample(cls.LETTERS, counts=cls.COUNTS, k=n)

        # Check.
        if not is_safe_letters(letters):
            return cls.single_draw(n)
        else:
            return letters

    def __init__(self):
        """ Prepares a bag of Scrabble tiles. Only initialize a Scrabble object if you intend for consistent use. """
        self.contents = []

        for letter, weight in zip(self.LETTERS, self.COUNTS):
            self.contents += [letter for _ in range(weight)]

        # TODO... I don't have a use for this yet, but here's where I'd put it all.


if __name__ == "__main__":
    Scrabble.single_draw()
