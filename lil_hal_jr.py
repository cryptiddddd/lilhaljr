import os

from dotenv import load_dotenv
load_dotenv()

import cogs
from bot import LilHalJr


# Initialize.
lil_hal = LilHalJr()

# Load implemented cogs.
for i in cogs.implemented:
    lil_hal.load_extension(f"cogs.{i}")


if __name__ == "__main__":
    # Run.
    lil_hal.run(os.getenv("DISCORD_TOKEN"))
