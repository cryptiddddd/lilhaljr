# Lil Hal Jr.

*It seems you have asked about DS's chat client auto-responder.*

This bot is a recreation of Lil Hal Jr. from Homestuck. It has three thrilling features:
- Responding to chat activity with a "Hmm."
- Engaging socially by answering "Yes."
- Interacting with and pondering natural conversations, contributing an observation. "Interesting."

He will also shut up for 15-75 minutes if told to.


---
### To run

Create a file called `.env` with a variable `DISCORD_TOKEN`, and set the value to your Discord bot token. 

Install packages specified in `requirements.txt` and run `lil_hal_jr.py`.


---
### Structure

- `lil_hal_jr.py.`: Driver file.
- `bot.py`: Bot structure.
- `config.py`: Configuration options.
- `cogs`: Extensions.
  - `dev_cog.py`: Adds owner-only commands.
  - `logging_cog.py`: Handles logging capabilities, toggleable from `config.py`.
  - `social_cog.py`: Hal Jr gets more socially adventurous.


---
### Feature Breakdown

In `bot.py`:
- The basic, classic, "Hmm" "Yes" and "Interesting" responses.
- A secret surprise response.
- Temporary mute ability, responding to key phrases set in `config.py`.

In `dev_cog.py`:
- Ping command.
- View mute channel command [via logger].
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


---
### Changelog

- 05-04-2023: Added commands.
- 05-05-2023: Added [to run](#to-run) guide section.
