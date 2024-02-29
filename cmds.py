import discord
from discord import app_commands
from discord.ext import commands

class SteamBossCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.hybrid_command(name="hello_boss", description="Replies with hello. Used for testing!")
    async def hello_boss(self, ctx: commands.Context) -> None:
        await ctx.send("Hello BOSS!")
    
    @commands.hybrid_command(name="quiet_hello", description="Replies with hello, but the message is ephemeral. Used for testing!")
    async def quiet_hello(self, ctx: commands.Context) -> None:
        await ctx.send("Hello BOSS!", ephemeral=True)