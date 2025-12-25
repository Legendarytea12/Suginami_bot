# main.py

from core.config import BOT_TOKEN
from core.bot import SuginamiBot
import discord

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = SuginamiBot(intents=intents)

if __name__ == "__main__":
    bot.run(BOT_TOKEN)