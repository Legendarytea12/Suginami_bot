# core/config.py

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if BOT_TOKEN is None:
    raise ValueError("BOT_TOKEN is not set in the environment variables.")
elif BOT_TOKEN is not None:
    print("BOT_TOKEN loaded successfully.")