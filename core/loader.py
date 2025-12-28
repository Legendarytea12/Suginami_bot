# core/loader.py
# Module for loading, unloading, and reloading Discord bot extensions (cogs)
# Supports parallel loading for better performance

import os
import logging
import asyncio
from pathlib import Path
from typing import List, Optional, Tuple
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


class CogsLoader:
    # Manages loading, unloading, and reloading of bot extensions (cogs)
    # Supports parallel operations for improved performance
    
    def __init__(self, bot: commands.Bot, cogs_directory: str = "cogs"):
        # Initialize the CogsLoader
        # Args:
        #     bot: The Discord bot instance
        #     cogs_directory: Directory path where cogs are located (default: "cogs")
        self.bot = bot
        self.cogs_dir = Path(cogs_directory)
        self.loaded_cogs: List[str] = []  # List of loaded cog module paths
    
    def _get_cog_files(self) -> List[Path]:
        # Recursively find all Python files in the cogs directory
        # Ignores files and directories starting with '_' (like __init__.py, __pycache__)
        # Returns:
        #     List of Path objects pointing to cog files
        cog_files = []

        # Check if cogs directory exists
        if not self.cogs_dir.exists():
            logger.warning(f"Cogs directory '{self.cogs_dir}' does not exist.")
            return cog_files
        
        # Walk through the directory tree
        for root, dirs, files in os.walk(self.cogs_dir):
            # Skip directories starting with '_' (like __pycache__)
            dirs[:] = [d for d in dirs if not d.startswith('_')]

            # Find all Python files that don't start with '_'
            for file in files:
                if file.endswith(".py") and not file.startswith("_"):
                    full_path = Path(root) / file
                    cog_files.append(full_path.resolve())  # Use absolute path
                    
        return cog_files

    def _path_to_module(self, file_path: Path) -> str:
        # Convert a file path to a Python module path
        # Example: cogs/cog_admin/admin.py -> cogs.cog_admin.admin
        # Args:
        #     file_path: Path to the Python file
        # Returns:
        #     Module path as a string (e.g., "cogs.cog_admin.admin")
        try:
            # Get relative path from current working directory
            relative_path = file_path.relative_to(Path.cwd())
        except ValueError:
            # If path is not relative to cwd, use the path as-is
            relative_path = file_path
        # Convert path separators to dots and remove .py extension
        module_path = str(relative_path.with_suffix('')).replace(os.sep, '.')
        return module_path

    async def load_cog(self, cog_path: str) -> bool:
        # Load a single cog by its module path
        # Args:
        #     cog_path: Module path of the cog (e.g., "cogs.cog_admin.admin")
        # Returns:
        #     True if loaded successfully, False otherwise
        try:
            await self.bot.load_extension(cog_path)
            self.loaded_cogs.append(cog_path)
            logger.info(f"Cog loaded: {cog_path}")
            return True
        except commands.ExtensionAlreadyLoaded:
            logger.warning(f"Cog {cog_path} already loaded")
            return False
        except commands.ExtensionNotFound:
            logger.error(f"Cog {cog_path} not found")
            return False
        except commands.NoEntryPointError:
            logger.error(f"In {cog_path} missing setup() function")
            return False
        except Exception as e:
            logger.error(f"Error loading {cog_path}: {e}", exc_info=True)
            return False
    
    async def unload_cog(self, cog_path: str) -> bool:
        # Unload a single cog by its module path
        # Args:
        #     cog_path: Module path of the cog to unload
        # Returns:
        #     True if unloaded successfully, False otherwise
        try:
            await self.bot.unload_extension(cog_path)
            # Remove from loaded_cogs list if present
            if cog_path in self.loaded_cogs:
                self.loaded_cogs.remove(cog_path)
            logger.info(f"Cog unloaded: {cog_path}")
            return True
        except commands.ExtensionNotLoaded:
            logger.warning(f"Cog {cog_path} not loaded")
            return False
        except Exception as e:
            logger.error(f"Error unloading {cog_path}: {e}", exc_info=True)
            return False
    
    async def reload_cog(self, cog_path: str) -> bool:
        # Reload a single cog by its module path
        # If the cog is not loaded, it will be loaded instead
        # Args:
        #     cog_path: Module path of the cog to reload
        # Returns:
        #     True if reloaded/loaded successfully, False otherwise
        try:
            await self.bot.reload_extension(cog_path)
            logger.info(f"Cog reloaded: {cog_path}")
            return True
        except commands.ExtensionNotLoaded:
            # If not loaded, try loading it
            logger.info(f"Cog {cog_path} not loaded, loading...")
            return await self.load_cog(cog_path)
        except Exception as e:
            logger.error(f"Error reloading {cog_path}: {e}", exc_info=True)
            return False
    
    async def load_all_cogs(self) -> dict:
        # Load all cogs found in the cogs directory in parallel
        # This improves startup time when there are many cogs
        # Returns:
        #     Dictionary with keys:
        #         - 'success': List of successfully loaded cog paths
        #         - 'failed': List of failed cog paths
        #         - 'total': Total number of cog files found
        results = {
            'success': [],
            'failed': [],
            'total': 0
        }
        
        # Find all cog files
        cog_files = self._get_cog_files()
        results['total'] = len(cog_files)
        
        logger.info(f"Found {len(cog_files)} cog files")
        
        # Return early if no cogs found
        if not cog_files:
            return results
        
        # Helper function to load a single cog
        async def load_single_cog(file_path: Path) -> Tuple[str, bool]:
            # Load a single cog and return its path and success status
            module_path = self._path_to_module(file_path)
            success = await self.load_cog(module_path)
            return (module_path, success)
        
        # Create tasks for all cogs and load them in parallel
        # return_exceptions=True ensures one failure doesn't stop others
        tasks = [load_single_cog(file_path) for file_path in cog_files]
        load_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and categorize into success/failed
        for result in load_results:
            if isinstance(result, Exception):
                logger.error(f"Unexpected error during parallel loading: {result}", exc_info=result)
                continue
            
            module_path, success = result
            if success:
                results['success'].append(module_path)
            else:
                results['failed'].append(module_path)
        
        logger.info(f"Load finished: {len(results['success'])}/{results['total']} successfully loaded")
        return results
    
    async def reload_all_cogs(self) -> dict:
        # Reload all currently loaded cogs in parallel
        # This enables hot reloading without restarting the bot
        # Returns:
        #     Dictionary with keys:
        #         - 'success': List of successfully reloaded cog paths
        #         - 'failed': List of failed cog paths
        #         - 'total': Total number of cogs that were reloaded
        results = {
            'success': [],
            'failed': [],
            'total': len(self.loaded_cogs)
        }
        
        # Create a copy of loaded cogs list to avoid modification during iteration
        cogs_to_reload = self.loaded_cogs.copy()
        
        if not cogs_to_reload:
            logger.info("No cogs to reload")
            return results

        # Helper function to reload a single cog
        async def reload_single_cog(cog_path: str) -> Tuple[str, bool]:
            # Reload a single cog and return its path and success status
            success = await self.reload_cog(cog_path)
            return (cog_path, success)
        
        # Create tasks for all cogs and reload them in parallel
        # return_exceptions=True ensures one failure doesn't stop others
        tasks = [reload_single_cog(cog_path) for cog_path in cogs_to_reload]
        reload_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and categorize into success/failed
        for result in reload_results:
            if isinstance(result, Exception):
                logger.error(f"Unexpected error during parallel reload: {result}", exc_info=result)
                continue
            
            cog_path, success = result
            if success:
                results['success'].append(cog_path)
            else:
                results['failed'].append(cog_path)

        logger.info(f"Reload finished: {len(results['success'])}/{results['total']} successfully reloaded")
        return results
    
    def get_loaded_cogs(self) -> List[str]:
        # Get a copy of the list of loaded cog module paths
        # Returns:
        #     List of loaded cog module paths
        return self.loaded_cogs.copy()


async def setup_loader(bot: commands.Bot, cogs_dir: str = "cogs") -> CogsLoader:
    # Factory function to create and initialize a CogsLoader
    # Automatically loads all cogs from the specified directory
    # Args:
    #     bot: The Discord bot instance
    #     cogs_dir: Directory path where cogs are located (default: "cogs")
    # Returns:
    #     Initialized CogsLoader instance with all cogs loaded
    loader = CogsLoader(bot, cogs_dir)
    await loader.load_all_cogs()  # Load all cogs in parallel
    return loader