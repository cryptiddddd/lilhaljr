# Lil Hal Jr.

*It seems you have asked about DS's chat client auto-responder.*

![python badge](https://img.shields.io/badge/python-3.11-fed142?logo=python&style=for-the-badge&labelColor=3776AB&logoColor=fff)
![pycord badge](https://img.shields.io/badge/pycord-2.4.1-d6d6d6?logo=discord&style=for-the-badge&labelColor=6c76e6&logoColor=d6d6d6)

[![signature](https://img.shields.io/badge/crane%20did%20this-support%20hal-ccc?style=for-the-badge&logo=ko-fi)](https://ko-fi.com/wormboy3)


This is a recreation of Lil Hal Jr. from Homestuck as a Discord bot. It has three thrilling features:
- Responding to chat activity with a "Hmm."
- Socially engaging with answers like "Yes."
- Interacting with and pondering natural conversations, contributing an observation. "Interesting."

He will also shut up for 15-75 minutes if told to.


---
## To run

Create a `.env` file in the root folder and insert Discord bot token like so:

```
DISCORD_TOKEN=token-goes-here
```

Install packages specified in `requirements.txt`.

```commandline
# Windows commandline
pip install -r requirements.txt
```


---
### Structure

- `lil_hal_jr.py.`: Driver file.
- `bot.py`: Bot structure.
- `config.py`: Configuration options.
- `cogs`: Extensions.
  - `dev_cog.py`: Adds owner-only commands.
  - `logging_cog.py`: Handles logging capabilities. Note: also initializes the logger from Python builtin `logging`.
  - `social_cog.py`: Events and reactions that adventure beyong "Hmm", "Yes", and "Interesting".


---
### Feature Breakdown

In `bot.py`:
- The basic, classic, "Hmm" "Yes" and "Interesting" responses.
- A secret surprise response.
- Temporary mute ability, responding to key phrases set in `config.py`, or an emoji, also configurable in `config.py` (in-progress, stable for default emojis).

In `dev_cog.py`:
- Ping command.
- View mute channel command (prints only to logger).
- Add a key phrase for muting.
- Shutdown command.

In `logging_cog.py`:
- Basic logging on most events.

In `social_cog.py`:
- Attempted greetings when joining a server.
  - If there is an obvious intro channel, it sends its own introduction.
  - If there is an obvious general channel, it sends a hello.
- Greets new members to the server.
- Attempts to engage with Cranebot's commands.
- `^inquire` command, allowing users to ask questions with vague and asinine responses.


---
### Changelog

- 05-04-2023: Added commands.
- 05-05-2023: Added [to run](#to-run) guide section.
- 05-10-2023: Added fun badges and refined introduction and "to run" section. Project made public.
- 05-11-2023: Added note for shushing emoji.
