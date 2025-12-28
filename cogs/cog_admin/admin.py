# cogs/cog_admin/admin.py
# Admin cog providing commands for managing bot extensions (cogs)
# Allows loading, unloading, and reloading cogs without restarting the bot

import discord
from discord.ext import commands
from core.loader import CogsLoader


class AdminCog(commands.Cog):
    # Admin cog for managing bot extensions
    # Provides commands for loading, unloading, and reloading cogs
    # All commands require administrator permissions
    
    def __init__(self, bot: commands.Bot):
        # Initialize the AdminCog
        # Args:
        #     bot: The Discord bot instance
        self.bot = bot

    def _get_loader(self) -> CogsLoader:
        # Get the CogsLoader instance from the bot
        # Returns None if loader is not available
        # Returns:
        #     CogsLoader instance or None
        if hasattr(self.bot, 'loader') and self.bot.loader:
            return self.bot.loader
        return None

    @commands.command(name='loaded_cogs', help='Display list of loaded cogs')
    @commands.has_permissions(administrator=True)
    async def loaded_cogs(self, ctx: commands.Context):
        # Display a list of all currently loaded cogs
        # Shows both cog names and their module paths
        # Args:
        #     ctx: Command context
        embed = discord.Embed(
            title="Loaded Cogs",
            description="Here is the list of currently loaded cogs:",
            color=discord.Color.blue()
        )
        loader = self._get_loader()
        if loader:
            # Get module paths from loader
            loaded = loader.get_loaded_cogs()
            # Get cog class names
            cogs = [cog for cog in self.bot.cogs.keys()]
            embed.add_field(name="Cog Names", value=", ".join(cogs) if cogs else "None", inline=False)
            embed.add_field(name="Module Paths", value="\n".join(loaded) if loaded else "None", inline=False)
        else:
            # Fallback if loader is not available
            cogs = [cog for cog in self.bot.cogs.keys()]
            embed.add_field(name="Loaded Cogs", value=", ".join(cogs) if cogs else "None", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='unload_cog', help='Unload a specified cog by module path (e.g., cogs.cog_admin.admin)')    
    @commands.has_permissions(administrator=True)
    async def unload_cog(self, ctx: commands.Context, cog_path: str):
        # Unload a cog by its module path
        # Example: !unload_cog cogs.cog_admin.admin
        # Args:
        #     ctx: Command context
        #     cog_path: Module path of the cog to unload
        loader = self._get_loader()
        if loader:
            # Use loader for consistent behavior
            success = await loader.unload_cog(cog_path)
            if success:
                await ctx.send(f"✅ Unloaded cog: `{cog_path}`")
            else:
                await ctx.send(f"❌ Failed to unload cog: `{cog_path}`")
        else:
            # Fallback to direct bot method if loader unavailable
            try:
                await self.bot.unload_extension(cog_path)
                await ctx.send(f"✅ Unloaded cog: `{cog_path}`")
            except Exception as e:
                await ctx.send(f"❌ Failed to unload cog `{cog_path}`: {e}")

    @commands.command(name='load_cog', help='Load a specified cog by module path (e.g., cogs.cog_admin.admin)')
    @commands.has_permissions(administrator=True)
    async def load_cog(self, ctx: commands.Context, cog_path: str):
        # Load a cog by its module path
        # Example: !load_cog cogs.cog_admin.admin
        # Args:
        #     ctx: Command context
        #     cog_path: Module path of the cog to load
        loader = self._get_loader()
        if loader:
            # Use loader for consistent behavior
            success = await loader.load_cog(cog_path)
            if success:
                await ctx.send(f"✅ Loaded cog: `{cog_path}`")
            else:
                await ctx.send(f"❌ Failed to load cog: `{cog_path}`")
        else:
            # Fallback to direct bot method if loader unavailable
            try:
                await self.bot.load_extension(cog_path)
                await ctx.send(f"✅ Loaded cog: `{cog_path}`")
            except Exception as e:
                await ctx.send(f"❌ Failed to load cog `{cog_path}`: {e}")

    @commands.command(name='reload_cog', help='Reload a specified cog by module path (e.g., cogs.cog_admin.admin)')
    @commands.has_permissions(administrator=True)
    async def reload_cog(self, ctx: commands.Context, cog_path: str):
        # Reload a cog by its module path (hot reload)
        # This allows updating cog code without restarting the bot
        # Example: !reload_cog cogs.cog_admin.admin
        # Args:
        #     ctx: Command context
        #     cog_path: Module path of the cog to reload
        loader = self._get_loader()
        if loader:
            # Use loader for consistent behavior
            success = await loader.reload_cog(cog_path)
            if success:
                await ctx.send(f"✅ Reloaded cog: `{cog_path}`")
            else:
                await ctx.send(f"❌ Failed to reload cog: `{cog_path}`")
        else:
            # Fallback to direct bot method if loader unavailable
            try:
                await self.bot.reload_extension(cog_path)
                await ctx.send(f"✅ Reloaded cog: `{cog_path}`")
            except Exception as e:
                await ctx.send(f"❌ Failed to reload cog `{cog_path}`: {e}")

    @commands.command(name='reload_all_cogs', help='Reload all loaded cogs in parallel (hot reload)')
    @commands.has_permissions(administrator=True)
    async def reload_all_cogs(self, ctx: commands.Context):
        # Reload all currently loaded cogs in parallel
        # This is useful for hot reloading all extensions after making changes
        # All cogs are reloaded simultaneously for better performance
        # Args:
        #     ctx: Command context
        loader = self._get_loader()
        if not loader:
            await ctx.send("❌ Loader not available")
            return
        
        await ctx.send("🔄 Reloading all cogs in parallel...")
        
        # Reload all cogs in parallel
        results = await loader.reload_all_cogs()
        
        # Create embed with results
        embed = discord.Embed(
            title="Reload All Cogs",
            color=discord.Color.gold()
        )
        
        # Show successfully reloaded cogs (limit to 10 for display)
        if results['success']:
            embed.add_field(
                name=f"✅ Successfully reloaded ({len(results['success'])})",
                value="\n".join(results['success'][:10]) + ("..." if len(results['success']) > 10 else ""),
                inline=False
            )
        
        # Show failed reloads (limit to 10 for display)
        if results['failed']:
            embed.add_field(
                name=f"❌ Failed to reload ({len(results['failed'])})",
                value="\n".join(results['failed'][:10]) + ("..." if len(results['failed']) > 10 else ""),
                inline=False
            )
        
        embed.set_footer(text=f"Total: {results['total']} cogs")
        await ctx.send(embed=embed)
            
    @commands.command(name='help_admin', help='Display admin commands help')
    @commands.has_permissions(administrator=True)
    async def help_admin(self, ctx: commands.Context):
        # Display help information for all admin commands
        # Args:
        #     ctx: Command context
        embed = discord.Embed(
            title="Admin Commands Help",
            description="List of available admin commands:",
            color=discord.Color.green()
        )
        embed.add_field(name="!loaded_cogs", value="Display list of loaded cogs", inline=False)
        embed.add_field(name="!unload_cog <module_path>", value="Unload a specified cog (e.g., cogs.cog_admin.admin)", inline=False)
        embed.add_field(name="!load_cog <module_path>", value="Load a specified cog (e.g., cogs.cog_admin.admin)", inline=False)
        embed.add_field(name="!reload_cog <module_path>", value="Reload a specified cog (e.g., cogs.cog_admin.admin)", inline=False)
        embed.add_field(name="!reload_all_cogs", value="🔄 Reload all cogs in parallel (hot reload)", inline=False)
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    # Setup function called by discord.py when loading this cog
    # This is required for all cogs
    # Args:
    #     bot: The Discord bot instance
    await bot.add_cog(AdminCog(bot))