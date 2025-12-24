# main.py

from core.config import BOT_TOKEN
from core.bot import SuginamiBot
import discord

intents = discord.Intents.default()
bot = SuginamiBot(command_prefix="!", intents=intents)

bot.run(BOT_TOKEN)