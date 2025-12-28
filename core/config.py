# core/config.py
# Configuration module for loading environment variables

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get bot token from environment variables
# The token is required for the bot to connect to Discord
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Validate that BOT_TOKEN is set
if BOT_TOKEN is None:
    raise ValueError("BOT_TOKEN is not set in the environment variables.")
elif BOT_TOKEN is not None:
    print("BOT_TOKEN loaded successfully.")