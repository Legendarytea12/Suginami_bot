# core/bot.py

import discord
from discord.ext import commands
import logging
from core.loader import setup_loader, CogsLoader

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Main Bot Class
class SuginamiBot(commands.Bot):
    
    def __init__(self, intents: discord.Intents = None):
        if intents is None:
            intents = discord.Intents.default()
            intents.message_content = True
            intents.members = True
        
        super().__init__(
            command_prefix='/',
            intents=intents,
            help_command=None
        )
        
        self.loader: CogsLoader = None
        
    async def setup_hook(self):
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("🚀 Starting Suginami...")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Initializing loader and loading all cogs
        logger.info("📦 Loading extensions...")
        self.loader = await setup_loader(self, cogs_dir="cogs")
        
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("✅ Bot is ready!")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    async def on_ready(self):
        logger.info(f'👤 Bot: {self.user} (ID: {self.user.id})')
        logger.info(f'🌐 Servers: {len(self.guilds)}')
        logger.info(f'📦 Loaded extensions: {len(self.loader.loaded_cogs)}')
        logger.info(f'🏓 Latency: {round(self.latency * 1000)}ms')
        logger.info('─' * 50)
        
        # Установка статуса бота (опционально)
        await self.change_presence(
            activity=discord.Game(name="!help | Suginami Bot"),
            status=discord.Status.online
        )
    
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have the required permissions to use this command!")
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
            return
        
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument: {error}")
            return

        # Log unexpected errors
        logger.error(f"Error in command {ctx.command}: {error}", exc_info=error)
        await ctx.send("❌ An unexpected error occurred while executing the command.")
    
    async def close(self):
        logger.info("Stopping the bot...")
        await super().close()
        logger.info("Bot stopped")