# main.py
# Main entry point for the Suginami Discord bot

from core.config import BOT_TOKEN
from core.bot import SuginamiBot
import discord

# Configure Discord intents
# Intents define what events the bot can receive from Discord
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content
intents.members = True  # Required to access member information

# Create bot instance with configured intents
bot = SuginamiBot(intents=intents)

# Run the bot when script is executed directly
if __name__ == "__main__":
    bot.run(BOT_TOKEN)