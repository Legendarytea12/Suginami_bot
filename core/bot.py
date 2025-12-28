# core/bot.py
# Main bot class that extends discord.py commands.Bot

import discord
from discord.ext import commands
import logging
from core.loader import setup_loader, CogsLoader

# Configure logging to write to both file and console
# Logs are saved to bot.log file with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),  # File handler
        logging.StreamHandler()  # Console handler
    ]
)

logger = logging.getLogger(__name__)

# Main Bot Class
# Extends discord.py commands.Bot to add custom functionality
class SuginamiBot(commands.Bot):
    
    def __init__(self, intents: discord.Intents = None):
        # Initialize the bot with default intents if none provided
        # Args:
        #     intents: Discord intents object. If None, uses default intents with
        #              message_content and members enabled.
        # Set up default intents if none provided
        if intents is None:
            intents = discord.Intents.default()
            intents.message_content = True  # Required to read message content
            intents.members = True  # Required to access member information
        
        # Initialize parent Bot class with command prefix '!'
        super().__init__(
            command_prefix='!',  # Commands start with '!'
            intents=intents,
            help_command=None  # Disable default help command (can be customized)
        )
        
        # CogsLoader instance for managing extensions
        # Will be initialized in setup_hook
        self.loader: CogsLoader = None
        
    async def setup_hook(self):
        # Called when the bot is starting up, before it connects to Discord
        # This is where we initialize the loader and load all cogs
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("🚀 Starting Suginami...")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Initialize loader and load all cogs from the 'cogs' directory
        # This happens in parallel for better performance
        logger.info("📦 Loading extensions...")
        self.loader = await setup_loader(self, cogs_dir="cogs")
        
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("✅ Bot is ready!")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    async def on_ready(self):
        # Called when the bot has successfully connected to Discord
        # Logs bot information and sets the bot's presence status
        # Log bot information
        logger.info(f'👤 Bot: {self.user} (ID: {self.user.id})')
        logger.info(f'🌐 Servers: {len(self.guilds)}')
        logger.info(f'📦 Loaded extensions: {len(self.loader.loaded_cogs)}')
        logger.info(f'🏓 Latency: {round(self.latency * 1000)}ms')
        logger.info('─' * 50)
        
        # Set bot's presence status (what shows under the bot's name)
        await self.change_presence(
            activity=discord.Game(name="!help | Suginami Bot"),
            status=discord.Status.online
        )
    
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        # Global error handler for command errors
        # Handles common errors and provides user-friendly messages
        # Args:
        #     ctx: Command context
        #     error: The error that occurred
        # Ignore unknown commands (user typed something that isn't a command)
        if isinstance(error, commands.CommandNotFound):
            return
        
        # Handle missing permissions
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have the required permissions to use this command!")
            return
        
        # Handle missing required arguments
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
            return
        
        # Handle invalid arguments
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument: {error}")
            return

        # Log unexpected errors for debugging
        logger.error(f"Error in command {ctx.command}: {error}", exc_info=error)
        await ctx.send("❌ An unexpected error occurred while executing the command.")
    
    async def close(self):
        # Called when the bot is shutting down
        # Ensures proper cleanup of resources
        logger.info("Stopping the bot...")
        await super().close()
        logger.info("Bot stopped")