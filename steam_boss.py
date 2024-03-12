import discord
from cmds import SteamBossCommands
from discord.ext import commands

from typing import Literal, Optional

intents = discord.Intents.default()
intents.message_content = True   

bot = commands.Bot(command_prefix="!", intents=intents)

# List of servers for the sync command, used for testing
valid_servers = [discord.Object(id=464462171703869440), discord.Object(id=1208158746300383302)]

# Events
    
@bot.event
async def on_ready():
    await setup()
    print(f"Logged on as {bot.user}")

# Syncs commands with Discord - DISABLE for production build
# !sync - syncs all global commands with Discord (CURRENTLY NOT IMPLEMENTED)
# !sync * - syncs all global commands to the test servers (useful for testing)
# !sync ^ - clears all commands in the current server
@bot.command()
@commands.guild_only()
async def sync(ctx: commands.Context, spec: Optional[Literal["*", "^"]] = None) -> None:
    synced = []
    
    if spec == "*":
        for server in valid_servers:
            try:
                ctx.bot.tree.clear_commands(guild=server)
                ctx.bot.tree.copy_global_to(guild=server)
                synced = await ctx.bot.tree.sync(guild=server)
            except discord.HTTPException:
                pass
    elif spec == "^":
        ctx.bot.tree.clear_commands(guild=ctx.guild)
        await ctx.bot.tree.sync(guild=ctx.guild)
        synced = []
    else:
        # currently clears all global commands - can change later
        ctx.bot.tree.clear_commands(guild=None)
        synced = await ctx.bot.tree.sync(guild=None)

    await ctx.send(f"Synced {len(synced)} commands {'globally.' if spec is None else 'to the test servers.'}")
    return

# Extra bot setup
async def setup() -> None:
    await bot.add_cog(SteamBossCommands(bot))