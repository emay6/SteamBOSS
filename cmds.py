import asyncio
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
            
      
    @commands.hybrid_command(name="page_test", description="used for testing pages only!")
    async def page_help(self, ctx):
        page1 = discord.Embed(title="Bot Test 1",description="Use the buttons to see if this stuff works.", colour=discord.Colour.dark_blue())
        page2 = discord.Embed(title="Bot Test 2",description="Page 2 test", colour=discord.Colour.green())
        page3 = discord.Embed(title="Bot Test 3",description="Page 3 test", colour=discord.Colour.red())
        
        self.pages = [page1,page2,page3]
        
        buttons = [u"\u23EA", u"\u25C0",u"\u25B6",u"\u23E9"]
        current_page = 0
        msg = await ctx.send(embed=self.pages[current_page])
        
        for button in buttons:
            await msg.add_reaction(button)
        
        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons, timeout=60.0)

            except asyncio.TimeoutError:
                return print("test")

            else:
                reaction_num=0
                previous_page = current_page
                if reaction.emoji == buttons[0]:
                    current_page = 0
                    reaction_num=0
                    
                elif reaction.emoji == buttons[1]:
                    if current_page > 0:
                        current_page -= 1
                        reaction_num=1
                        
                elif reaction.emoji == buttons[2]:
                    if current_page < len(self.pages)-1:
                        current_page += 1
                        reaction_num=2

                elif reaction.emoji == buttons[3]:
                    current_page = len(self.pages)-1
                    reaction_num=3
                    
                if current_page != previous_page:
                    await msg.edit(embed=self.pages[current_page])
                    
                await msg.remove_reaction(buttons[reaction_num], ctx.author)