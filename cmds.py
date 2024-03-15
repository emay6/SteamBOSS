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
            serverID = ctx.message.guild.id
            if serverID not in self.serverWL:
                self.serverWL[serverID] = []
            self.serverWL[serverID].append(game_info)
            
        else:
            game_embed.description = f"Could not find any game using your search of \"{game}\"."
        
        await ctx.send(content=message, embed=game_embed, ephemeral=True if message == "" else False)
    
    @commands.hybrid_command(name="print_server_wl", description="Prints the server-wide wishlist.")
    async def print_server_wl(self, ctx: commands.Context) -> None:
        serverID = ctx.message.guild.id
        if serverID not in self.serverWL:
            await ctx.send("Server Wishlist is currently empty.")
        else:
            list = self.serverWL[serverID]
            message = "Server Wishlist:\n"
            if(len(list) > 0):
                for game in list:
                    message += (game.title + "\n")
            await ctx.send(content = message)

    @commands.hybrid_command(name="delete_server_wl", description="Deletes a game from the server-wide wishlist.")
    async def delete_server_wl(self, ctx: commands.Context, game: str) -> None:
        serverID = ctx.message.guild.id
        if serverID not in self.serverWL:
            await ctx.send("Error: Server Wishlist is currently empty.")
        else:
            search = search_steam(game, amount=1)
            game_info = search[0]
            list = self.serverWL[serverID]
            if game_info not in list:
                await ctx.send("Error: " + game_info.title + " is not in Server Wishlist.")
            else:
                list.remove(game_info)
                await ctx.send(game_info.title + " was successfully removed from Server Wishlist.")
            
