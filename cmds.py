import discord
from discord import app_commands
from discord.ext import commands

class SteamBossCommands(commands.Cog):
    personalWL = {}
    serverWL = []
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.hybrid_command(name="hello_boss", description="Replies with hello. Used for testing!")
    async def hello_boss(self, ctx: commands.Context) -> None:
        await ctx.send("Hello BOSS!")
    
    @commands.hybrid_command(name="quiet_hello", description="Replies with hello, but the message is ephemeral. Used for testing!")
    async def quiet_hello(self, ctx: commands.Context) -> None:
        await ctx.send("Hello BOSS!", ephemeral=True)

    @commands.hybrid_command(name="add_personal_wl", description="Adds a game to the user's wishlist.")
    async def add_personal_wl(self, ctx: commands.Context, game) -> None:
        await ctx.send(game, "added to personal wishlist!")

    @commands.hybrid_command(name="add_server_wl", description="Adds a game to the server-wide wishlist.")
    async def add_server_wl(self, ctx: commands.Context, game: str) -> None:
        self.serverWL.append(game)
        await ctx.send(game, "added to server wishlist!")
    
    @commands.hybrid_command(name="print_server_wl", description="Prints the server-wide wishlist.")
    async def print_server_wl(self, ctx: commands.Context) -> None:
        await ctx.send("Server Wishlist:")