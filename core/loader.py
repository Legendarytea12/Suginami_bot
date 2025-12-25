# core/loader.py


import os
import logging
from pathlib import Path
from typing import List, Optional
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


class CogsLoader:
    
    def __init__(self, bot: commands.Bot, cogs_directory: str = "cogs"):
        self.bot = bot
        self.cogs_dir = Path(cogs_directory)
        self.loaded_cogs: List[str] = []
    
    def _get_cog_files(self) -> List[Path]:
        cog_files = []

        if not self.cogs_dir.exists():
            logger.warning(f"Cogs directory '{self.cogs_dir}' does not exist.")
            return cog_files
            
        for root, dirs, files in os.walk(self.cogs_dir):
            dirs[:] = [d for d in dirs if not d.startswith('_')]

            for file in files:
                if file.endswith(".py") and not file.startswith("_"):
                    full_path = Path(root) / file
                    cog_files.append(full_path.resolve())
                    
        return cog_files

    def _path_to_module(self, file_path: Path) -> str:
        try:
            relative_path = file_path.relative_to(Path.cwd())
        except ValueError:
            relative_path = file_path
        module_path = str(relative_path.with_suffix('')).replace(os.sep, '.')
        return module_path

    async def load_cog(self, cog_path: str) -> bool:
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
        try:
            await self.bot.unload_extension(cog_path)
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
        try:
            await self.bot.reload_extension(cog_path)
            logger.info(f"Cog reloaded: {cog_path}")
            return True
        except commands.ExtensionNotLoaded:
            logger.info(f"Cog {cog_path} not loaded, loading...")
            return await self.load_cog(cog_path)
        except Exception as e:
            logger.error(f"Error reloading {cog_path}: {e}", exc_info=True)
            return False
    
    async def load_all_cogs(self) -> dict:
        results = {
            'success': [],
            'failed': [],
            'total': 0
        }
        
        cog_files = self._get_cog_files()
        results['total'] = len(cog_files)
        
        logger.info(f"Found {len(cog_files)} cog files")
        
        for file_path in cog_files:
            module_path = self._path_to_module(file_path)
            
            if await self.load_cog(module_path):
                results['success'].append(module_path)
            else:
                results['failed'].append(module_path)
        
        logger.info(f"Load finished: {len(results['success'])}/{results['total']} successfully loaded")
        return results
    
    async def reload_all_cogs(self) -> dict:
        results = {
            'success': [],
            'failed': [],
            'total': len(self.loaded_cogs)
        }
        
        cogs_to_reload = self.loaded_cogs.copy()

        for cog_path in cogs_to_reload:
            if await self.reload_cog(cog_path):
                results['success'].append(cog_path)
            else:
                results['failed'].append(cog_path)

        logger.info(f"Reload finished: {len(results['success'])}/{results['total']} successfully reloaded")
        return results
    
    def get_loaded_cogs(self) -> List[str]:
        return self.loaded_cogs.copy()


async def setup_loader(bot: commands.Bot, cogs_dir: str = "cogs") -> CogsLoader:
    loader = CogsLoader(bot, cogs_dir)
    await loader.load_all_cogs()
    return loader