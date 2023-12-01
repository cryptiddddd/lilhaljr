# IDs for Hal to recognize.
CRANEBOT_ID = 943551083467391006
TOASTY_ID = 208946659361554432

SECRET_GUILD = 567541770943070236
HOME_GUILD = 944731867570143264

# Help message
HELP_MESSAGE = "It seems you have asked about Crane's parody-auto-responder Discord bot. " \
               "This is an application designed to simulate the ice-cold and magnetic conversational styling of " \
               "Lil Hal Jr. The algorithms are guaranteed to be in ongoing development, and wonky from time to time. " \
               "Use `^inquire` with any query, and Lil Hal Jr. will pull a statistical analysis straight out of his " \
               "ass, just for you."

# Each phrase is configured in lowercase, and mapped to its rudeness level, 1-5. Or 6...
# Working on regex support...
quiet_phrases = {
    "quiet down": 1,
    r"\bs+h+\b": 1,
    r"\bs*h+u+s+h+": 1,
    "be quiet": 2,
    "zip it": 3,
    "stop talking": 3,
    "put a sock in it": 4,
    "go away": 4,
    "shut up": 5,
    "fuck off": 6,
    "drop dead": 6
}

return_phrases = [
    "come back",
    "i didnt mean it",
    "i didnt mean that",
    "you can talk"
]

QUIET_EMOJI = "🤫"


bad_words = [
    "kike",
    "cripple",
    "retard",
    "nigg",
    "chink"
]
