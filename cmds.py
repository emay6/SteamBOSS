import discord
from discord.ext import commands
from web_scraper import search_steam

class SteamBossCommands(commands.Cog):
    personalWL = {} # Stores by user id
    serverWL = {} # Stores by server id
    

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.hybrid_command(name="hello_boss", description="Replies with hello. Used for testing!")
    async def hello_boss(self, ctx: commands.Context) -> None:
        await ctx.send("Hello BOSS!")
    
    @commands.hybrid_command(name="quiet_hello", description="Replies with hello, but the message is ephemeral. Used for testing!")
    async def quiet_hello(self, ctx: commands.Context) -> None:
        await ctx.send("Hello BOSS!", ephemeral=True)

    @commands.hybrid_command(name="add_personal_wl", description="Adds a game to the user's wishlist.")
    async def add_personal_wl(self, ctx: commands.Context, game: str) -> None:
        search = search_steam(game, amount=1)
        game_embed = discord.Embed(color=discord.Color.green())
        message = ""

        if len(search) > 0:
            message = "The following game was successfully added to your wishlist."
            game_info = search[0]
            game_embed.title = game_info.title
            game_embed.description = game_info.description
            game_embed.set_image(url=game_info.header_url)
        else:
            game_embed.description = f"Could not find any game using your search of \"{game}\"."
        
        await ctx.send(content=message, embed=game_embed, ephemeral=True)
            

    @commands.hybrid_command(name="add_server_wl", description="Adds a game to the server-wide wishlist.")
    async def add_server_wl(self, ctx: commands.Context, game: str) -> None:
        search = search_steam(game, amount=1)
        game_embed = discord.Embed(color=discord.Color.green())
        message = ""

        if len(search) > 0:
            message = "The following game was successfully added to the server wishlist."
            game_info = search[0]
            game_embed.title = game_info.title
            game_embed.description = game_info.description
            game_embed.set_image(url=game_info.header_url)
            id = ctx.guild.id
            self.serverWL[id].append(game_info)
            
        else:
            game_embed.description = f"Could not find any game using your search of \"{game}\"."
        
        await ctx.send(content=message, embed=game_embed, ephemeral=True if message == "" else False)
    
    @commands.hybrid_command(name="print_server_wl", description="Prints the server-wide wishlist.")
    async def print_server_wl(self, ctx: commands.Context) -> None:
        id = ctx.message.guild.id
        list = self.serverWL[id]
        if(len(list) > 0):
            await ctx.send("Server Wishlist:")
            for game in list:
                ctx.send(content = game.title)
        else:
            await ctx.send("Server Wishlist is currently empty.")
