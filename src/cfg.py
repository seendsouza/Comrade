# version of the bot
VERSION = "3.1 [Build June 30 v1]" 

# set to True if you are testing the bot in a development environment, False otherwise
DEVELOPMENT_MODE = False 

# change depending on host location.
LOCAL_TIMEZONE = 'Canada/Eastern' 

# the thing you type at the beginning of a command
BOT_PREFIX = "$c " 

# default status of the bot
DEFAULT_STATUS = "[{}] Mechanizing Communism".format(BOT_PREFIX) 

# amount of daily member counts everyone starts with
DEFAULT_DAILY_COUNT = 2 

# max number of active polymorph models (affects RAM)
RAM_LIMIT = 10 

# number of messages to be stored per user in buffer for moderation (affects RAM)
MSG_BUFFER_LIMIT = 10 

# default channel to load for Polymorph cache
DEFAULT_CACHE_LOAD = 419214713755402262 

# main colour for server; used in embeds
THEME_COLOUR = (215, 52, 42)

# colour for daily member (RGB)
DAILY_MEMBER_COLOUR = (241, 196, 15) 

# enforces recency for daily members, in days. Set to -1 to disable. TODO
DAILY_MEMBER_STALENESS = 30

# time to vote for ZA HANDO, in seconds
ZA_HANDO_VOTE_DURATION = 120 

# time to vote for Vault post, in seconds
VAULT_VOTE_DURATION = 180 