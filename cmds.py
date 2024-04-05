import asyncio
import discord
import os
import json
from discord.ext import commands
from web_scraper import search_steam, get_game_reviews, get_game_info

USER_WL_SAVE_PATH = "data/wl_user_info.json"
SERVER_WL_SAVE_PATH = "data/wl_server_info.json"

personalWL = {} # Stores by user id
serverWL = {} # Stores by server id
PagepersonalWL = {} #Stores by user id, pages
PageserverWL = {} #Stores by server id, pages

# TODO: Saves wishlist data into files
def save_wishlists():
    if not os.path.exists("data"):
        os.makedirs("data")

    data = {}
    with open(USER_WL_SAVE_PATH, "w", encoding="utf-8") as user_wl, open(SERVER_WL_SAVE_PATH, "w", encoding="utf-8") as server_wl:
        json.dump(personalWL, user_wl)
        json.dump(serverWL, server_wl)
        json.dump(PagepersonalWL, user_wl)
        json.dump(PageserverWL,server_wl)

# TODO: Checks if there's pre-existing data, load it if so
def init_wishlists():
    try:
        with open(USER_WL_SAVE_PATH, "r+", encoding="utf-8") as user_wl, open(SERVER_WL_SAVE_PATH, "r+", encoding="utf-8") as server_wl:
            personalWL = json.load(user_wl)
            serverWL = json.load(server_wl)
            PagepersonalWL = json.load(user_wl)
            PageserverWL = json.load(server_wl)
    except FileNotFoundError:
        pass

class SteamBossCommands(commands.GroupCog, name="wishlist"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        #init_wishlists()
    
    # @commands.hybrid_command(name="hello_boss", description="Replies with hello. Used for testing!")
    # async def hello_boss(self, ctx: commands.Context) -> None:
    #    await ctx.send("Hello BOSS!")
    
    # @commands.hybrid_command(name="quiet_hello", description="Replies with hello, but the message is ephemeral. Used for testing!")
    # async def quiet_hello(self, ctx: commands.Context) -> None:
    #    await ctx.send("Hello BOSS!", ephemeral=True)

    @commands.hybrid_command(name="add", description="Adds a game to the user's personal wishlist.")
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
            userID = ctx.author.id
            if(userID not in personalWL):
                personalWL[userID] = []
            if (userID not in PagepersonalWL):
                PagepersonalWL[userID]=[]
            personalWL[userID].append(game_info)
            PagepersonalWL[userID].append(game_embed);
        else:
            game_embed.description = f"Could not find any game using your search of \"{game}\"."
        
        await ctx.send(content=message, embed=game_embed, ephemeral=True)
            
    @commands.hybrid_command(name="print", description="Prints the user's personal wishlist.")
    async def print_personal_wl(self, ctx: commands.Context) -> None:
        userID = ctx.author.id
        if userID not in personalWL or len(personalWL[userID]) == 0:
            message = ctx.author.mention + "'s Wishlist is currently empty."
            await ctx.send(content = message)
        else:
            buttons = [u"\u23EA", u"\u25C0",u"\u25B6",u"\u23E9"]
            current_page = 0
            msg = await ctx.send(embed=PagepersonalWL[userID][current_page])
            
            for button in buttons:
                await msg.add_reaction(button)
            
            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons, timeout=60.0)
                except asyncio.TimeoutError:
                    return print("PageTimeoutError")

                else:
                    reaction_num=0
                    previous_page = current_page
                    if reaction.emoji == buttons[0]:
                        current_page = 0
                        reaction_num=0
                        
                    elif reaction.emoji == buttons[1]:
                        reaction_num=1
                        if current_page > 0:
                            current_page -= 1
                            
                    elif reaction.emoji == buttons[2]:
                        reaction_num=2
                        if current_page < len(PagepersonalWL[userID])-1:
                            current_page += 1

                    elif reaction.emoji == buttons[3]:
                        current_page = len(PagepersonalWL[userID])-1
                        reaction_num=3
                        
                    if current_page != previous_page:
                        await msg.edit(embed=PagepersonalWL[userID][current_page])
                        
                    elif current_page==len(PagepersonalWL[userID])-1 and current_page!=0:
                        await ctx.send(content = "You have reached the end of your wishlist.")
                        
                    elif current_page==0:
                        await ctx.send(content = "You are at the beginning of your wishlist.")
                        
                    await msg.remove_reaction(buttons[reaction_num], ctx.author)

    @commands.hybrid_command(name="delete", description="Deletes a game from the user's personal wishlist.")
    async def delete_personal_wl(self, ctx: commands.Context, game: str) -> None:
        userID = ctx.author.id
        if userID not in personalWL:
            await ctx.send(content = "Error: " + ctx.author.mention + "'s Wishlist is currently empty.", ephemeral = True)
        else:
            search = search_steam(game, amount=1)
            game_info = search[0]
            game_embed = discord.Embed(color=discord.Color.green())
            game_embed.title = game_info.title
            game_embed.description = game_info.description
            game_embed.set_image(url=game_info.header_url)
            list = personalWL[userID]
            if game_info not in list:
                await ctx.send(content = "Error: " + game_info.title + " is not in " + ctx.author.mention + "'s Wishlist.", ephemeral = True)
            else:
                list.remove(game_info)
                PagepersonalWL[userID].remove(game_embed)
                await ctx.send(content = game_info.title + " was successfully removed from " + ctx.author.mention + "'s Wishlist.", ephemeral = True)
            
    @commands.hybrid_command(name="add_server", description="Adds a game to the server-wide wishlist.")
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
            if serverID not in serverWL:
                serverWL[serverID] = []
            if (serverID not in PageserverWL):
                PageserverWL[serverID] = []
            serverWL[serverID].append(game_info)
            PageserverWL[serverID].append(game_embed)
            
        else:
            game_embed.description = f"Could not find any game using your search of \"{game}\"."
        
        await ctx.send(content=message, embed=game_embed, ephemeral=True if message == "" else False)
    
    @commands.hybrid_command(name="print_server", description="Prints the server-wide wishlist.")
    async def print_server_wl(self, ctx: commands.Context) -> None:
        serverID = ctx.message.guild.id
        if serverID not in serverWL or len(serverWL[serverID]) == 0:
            await ctx.send("Server Wishlist is currently empty.")
        else:
            buttons = [u"\u23EA", u"\u25C0",u"\u25B6",u"\u23E9"]
            current_page = 0
            msg = await ctx.send(embed=PageserverWL[serverID][current_page])
            
            for button in buttons:
                await msg.add_reaction(button)
            
            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons, timeout=60.0)
                except asyncio.TimeoutError:
                    return print("PageTimeoutError")

                else:
                    reaction_num=0
                    previous_page = current_page
                    if reaction.emoji == buttons[0]:
                        current_page = 0
                        reaction_num=0
                        
                    elif reaction.emoji == buttons[1]:
                        reaction_num=1
                        if current_page > 0:
                            current_page -= 1
                            
                    elif reaction.emoji == buttons[2]:
                        reaction_num=2
                        if current_page < len(PageserverWL[serverID])-1:
                            current_page += 1

                    elif reaction.emoji == buttons[3]:
                        current_page = len(PageserverWL[serverID])-1
                        reaction_num=3
                        
                    if current_page != previous_page:
                        await msg.edit(embed=PageserverWL[serverID][current_page])
                        
                    elif current_page==len(PageserverWL[serverID])-1 and current_page!=0:
                        await ctx.send(content = "You have reached the end of your wishlist.")
                        
                    elif current_page==0:
                        await ctx.send(content = "You are at the beginning of your wishlist.")
                        
                    await msg.remove_reaction(buttons[reaction_num], ctx.author)

    @commands.hybrid_command(name="delete_server", description="Deletes a game from the server-wide wishlist.")
    async def delete_server_wl(self, ctx: commands.Context, game: str) -> None:
        serverID = ctx.message.guild.id
        if serverID not in serverWL:
            await ctx.send("Error: Server Wishlist is currently empty.")
        else:
            search = search_steam(game, amount=1)
            game_info = search[0]
            game_embed = discord.Embed(color=discord.Color.green())
            game_embed.title = game_info.title
            game_embed.description = game_info.description
            game_embed.set_image(url=game_info.header_url)
            list = serverWL[serverID]
            if game_info not in list:
                await ctx.send("Error: " + game_info.title + " is not in Server Wishlist.")
            else:
                list.remove(game_info)
                PageserverWL[serverID].remove(game_embed)
                await ctx.send(game_info.title + " was successfully removed from Server Wishlist.")

    @commands.hybrid_command(name="reviews", description="View the top reviews for a given game.")
    async def get_game_reviews(self, ctx: commands.Context, game: str, view_positive: bool = None) -> None:
        pages = []
        if game.isnumeric():
            game = get_game_info(game)
        else:
            game = search_steam(game, amount=1)[0]
        reviews = get_game_reviews(game.id, view_positive)

        for review in reviews:
            embed = discord.Embed()
            embed.color = discord.Color.teal() if review.recommended else discord.Color.red()
            embed.title = "Review by " + review.author
            embed.description = review.content
            embed.add_field(name=review.hours_on_record, value="")
            embed.url = review.review_url
            embed.set_thumbnail(url=game.header_url)
            embed.set_author(name=review.date_posted, icon_url=review.rec_url)

            pages.append(embed)
        
        # TODO: Implement actual page functionality
        for page in pages:
            await ctx.send(embed=page, ephemeral=True)
      
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