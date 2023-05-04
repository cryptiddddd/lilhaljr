import os

from dotenv import load_dotenv
load_dotenv()

from bot import LilHalJr
import cogs
import config


# Initialize.
lil_hal = LilHalJr()

if __name__ == "__main__":
    # Load implemented cogs.
    for i in cogs.implemented:
        lil_hal.load_extension(f"cogs.{i}")

    # Conditional logging.
    if config.LOGGING:
        lil_hal.load_extension("cogs.logging_cog")

    # Run!
    lil_hal.run(os.getenv("DISCORD_TOKEN"))
