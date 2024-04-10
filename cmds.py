import asyncio
import discord
import os
import json
import datetime
from typing import List
from discord.ext import commands, tasks
from steam_game import SteamGame
from web_scraper import search_steam, get_game_reviews, get_game_info

# util classes

class PageMessage:
    prev_page: int
    curr_page: int
    id: int
    user: discord.User
    page_list: List[discord.Embed]
    ctx: commands.Context
    bot: commands.Bot

    def __init__(self, page_list: List[discord.Embed], ctx: commands.Context, bot: commands.Bot, user: discord.User):
        self.prev_page = 0
        self.curr_page = 0
        self.id = 0

        self.user = user
        self.page_list = page_list
        self.ctx = ctx
        self.bot = bot
    
    def check(self, reaction, user):
        return user == self.user and reaction.emoji in BUTTONS and reaction.message.id == self.id
    
    async def init_pages(self, ephemeral: bool = False) -> None:
        """
        Sets up pages using the provided page list.
        """
        msg = await self.ctx.send(embed=self.page_list[self.curr_page], ephemeral=ephemeral)
        self.id = msg.id
        
        for button in BUTTONS:
            await msg.add_reaction(button)
        
        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check=self.check, timeout=60.0)
            except asyncio.TimeoutError:
                return print("PageTimeoutError")

            else:
                reaction_num = 0
                self.prev_page = self.curr_page
                if reaction.emoji == BUTTONS[0]:
                    self.curr_page = 0
                    reaction_num = 0
                    
                elif reaction.emoji == BUTTONS[1]:
                    reaction_num = 1
                    if self.curr_page > 0:
                        self.curr_page -= 1
                        
                elif reaction.emoji == BUTTONS[2]:
                    reaction_num = 2
                    if self.curr_page < len(self.page_list) - 1:
                        self.curr_page += 1

                elif reaction.emoji == BUTTONS[3]:
                    self.curr_page = len(self.page_list) - 1
                    reaction_num = 3
                    
                if self.curr_page != self.prev_page:
                    await msg.edit(embed=self.page_list[self.curr_page])
                    
                elif self.curr_page == len(self.page_list) - 1 and self.curr_page != 0:
                    await self.ctx.send(content="You have reached the end of the list.", ephemeral=True)
                    
                elif self.curr_page == 0:
                    await self.ctx.send(content="You are at the beginning of the list.", ephemeral=True)
                    
                await msg.remove_reaction(BUTTONS[reaction_num], self.user)

# constants 

USER_WL_SAVE_PATH = "data/wl_user_info.json"
SERVER_WL_SAVE_PATH = "data/wl_server_info.json"
BUTTONS = [u"\u23EA", u"\u25C0",u"\u25B6",u"\u23E9"]

# global variables

personalWL = {} # Stores by user id
memberList = {} # Stores member objects for personal wishlist notifications
serverWL = {} # Stores by server id
PagepersonalWL = {} # Stores by user id, pages
PageserverWL = {} # Stores by server id, pages
notiChannel = {} # stores the channel that server wishlist notifications are given on
discord.AllowedMentions.all = True

# Misc functions

def get_page_list(games: List[SteamGame]) -> List[discord.Embed]:
    """
    Returns a list of the corresponding embeds for the given games
    """
    pages = []
    for game in games:
        pages.append(game_pages[game.id])
    
    return pages

def create_embed(color: discord.Color, msg: str):
    return discord.Embed(color=color, description=msg)

def create_embed(game: SteamGame):
    game_embed = discord.Embed(color=discord.Color.green())
    game_embed.title = game.title
    game_embed.description = game.description
    game_embed.url = game.game_url
    game_embed.set_image(url=game.header_url)
    game_embed.add_field(name="Price:", value=f"~~{game.price}~~ {game.discount_price} ({int(game.discount_amount * 100)}%)" if game.is_discounted else game.price)

    return game_embed

# Functions for persistent data

# TODO: Saves wishlist data into files
def save_wishlists():
    if not os.path.exists("data"):
        os.makedirs("data")

    data = {}
    with open(USER_WL_SAVE_PATH, "w", encoding="utf-8") as user_wl, open(SERVER_WL_SAVE_PATH, "w", encoding="utf-8") as server_wl:
        json.dump(personal_wishlists, user_wl)
        json.dump(server_wishlists, server_wl)
        # json.dump(personal_wishlist_pages, user_wl)
        # json.dump(server_wishlist_pages,server_wl)
        # json.dump(PersonalDiscountFilterL,user_wl)
        # json.dump(ServerDiscountFilterL,server_wl)
        # PersonalDiscountFilterL[user_wl]=0
        # ServerDiscountFilterL[server_wl]=0

# TODO: Checks if there's pre-existing data, load it if so
def init_wishlists():
    try:
        with open(USER_WL_SAVE_PATH, "r+", encoding="utf-8") as user_wl, open(SERVER_WL_SAVE_PATH, "r+", encoding="utf-8") as server_wl:
            personalWL = json.load(user_wl)
            serverWL = json.load(server_wl)
            PagepersonalWL = json.load(user_wl)
            PageserverWL = json.load(server_wl)
            # PersonalDiscountFilterL = json.load(user_wl)
            # ServerDiscountFilterL = json.load(server_wl)
    except FileNotFoundError:
        pass

class SteamBossCommands(commands.GroupCog, name="wishlist"):
    #function that runs every __  minutes to list discounted games
    @tasks.loop(minutes = 15)
    async def serverDiscUpdate(self):
        for server_id in server_wishlists:
            message = "\n@everyone\n"
            for game in server_wishlists[server_id]:
                message += "**SALE ALERT**\n"
                if(game.is_discounted):
                    channel = self.bot.get_channel(server_noti_channels[server_id])
                    message += game.title+" is currently on sale!\n"
                    await channel.send(content=message, embed=game_pages[game.id])

    @tasks.loop(minutes = 15)
    async def personalDiscUpdate(self):
        for user_id in personal_wishlists:
            for game in personal_wishlists[user_id]:
                member = member_list[user_id]
                channel = await member.create_dm()
                if(game.is_discounted):
                    message = "**SALE ALERT**\n"
                    message += game.title + " is currently on sale!\n"
                    await channel.send(content=message, embed=game_pages[game.id])            

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.serverDiscUpdate.start()
        self.personalDiscUpdate.start()
        #init_wishlists()

    @commands.hybrid_command(name="set_noti_channel", description="Sets the channel for Steam BOSS to notify you in to the calling channel.")
    async def set_noti_channel(self, ctx: commands.Context):
        server_id = ctx.message.guild.id
        server_noti_channels[server_id] = ctx.channel.id
        
        await ctx.send(content="Notification channel set.", ephemeral=True)

    #@commands.hybrid_command(name="set_personal_discount_filter", description="Sets a discount filter for personal wishlist.")
    #async def set_discount_personal(self, ctx: commands.Context, discountamount: float) -> None:
    #    userID = ctx.author.id
    #    if (discountamount<0 or discountamount>100):
    #        message = "Invalid Discount Filter Amount, please put in a number from 0 to 100!"
    #        await ctx.send(content = message)
    #        return
    #    TrueDiscountAmount = discountamount/100
    #    PersonalDiscountFilterL[userID]=TrueDiscountAmount
    #    message = "Successfully set Discount Filter for Personal Wishlist to ",discountamount,"."
    #    await ctx.send(content = message)
    #commented command to set a discount filter to adding to personal wishlist

    @commands.hybrid_command(name="add", description="Adds a game to the user's personal wishlist.")
    async def add_personal_wl(self, ctx: commands.Context, game: str) -> None:
        user_id = ctx.author.id
        search = search_steam(game, amount=1)
        message = ""

        if len(search) > 0:
            game_info = search[0]
        #    if (game_info.discount_amount<PersonalDiscountFilterL[userID]):
        #        message = "Game does not meet the set Discount Filter so it has not been added."
        #        await ctx.send(content = message)
        #        return
        #If we want to filter adding to wishlist by discount, ask later
            
            message = "The following game was successfully added to your wishlist."
            game_embed = create_embed(game_info)

            if(user_id not in personal_wishlists):
                personal_wishlists[user_id] = []
                member = ctx.author
                member_list[user_id] = member
            if (game_info.id not in game_pages):
                game_pages[game_info.id] = game_embed
            
            personal_wishlists[user_id].append(game_info)
        else:
            game_embed = create_embed(f"Could not find any game using your search of \"{game}\".")
        
        await ctx.send(content=message, embed=game_embed, view=self.get_reviews_view(game_info.id), ephemeral=True)
            
    @commands.hybrid_command(name="print", description="Prints the user's personal wishlist.")
    async def print_personal_wl(self, ctx: commands.Context) -> None:
        user_id = ctx.author.id
        if user_id not in personal_wishlists or len(personal_wishlists[user_id]) == 0:
            message = "Your wishlist is currently empty."
            await ctx.send(content=message, ephemeral=True)
        else:
            pages = get_page_list(personal_wishlists[user_id])
            page = PageMessage(get_page_list(personal_wishlists[user_id]), ctx, self.bot, ctx.author)
            await page.init_pages()

    @commands.hybrid_command(name="delete", description="Deletes a game from the user's personal wishlist.")
    async def delete_personal_wl(self, ctx: commands.Context, game: str) -> None:
        userID = ctx.author.id
        if userID not in personal_wishlists:
            await ctx.send(content = "Error: " + ctx.author.mention + "'s wishlist is currently empty.", ephemeral = True)
        else:
            search = search_steam(game, amount=1)
            game_info = search[0]

            list = personal_wishlists[userID]
            if game_info not in list:
                await ctx.send(content = "Error: " + game_info.title + " is not in " + ctx.author.mention + "'s wishlist.", ephemeral = True)
            else:
                list.remove(game_info)
                await ctx.send(content = game_info.title + " was successfully removed from " + ctx.author.mention + "'s wishlist.", ephemeral = True)
            
    @commands.hybrid_command(name="add_server", description="Adds a game to the server-wide wishlist.")
    async def add_server_wl(self, ctx: commands.Context, game: str) -> None:
        server_id = ctx.message.guild.id
        search = search_steam(game, amount=1)
        game_embed = discord.Embed(color=discord.Color.green())
        message = ""

        if len(search) > 0:
            message = "The following game was successfully added to the server wishlist."
            game_info = search[0]
            game_embed = create_embed(game_info)

            if server_id not in server_wishlists:
                server_wishlists[server_id] = []
            if (game_info.id not in game_pages):
                game_pages[game_info.id] = game_embed
            server_wishlists[server_id].append(game_info)
            
        else:
            game_embed = create_embed(f"Could not find any game using your search of \"{game}\".")
        
        await ctx.send(content=message, embed=game_embed, ephemeral=True if message == "" else False)
    
    @commands.hybrid_command(name="print_server", description="Prints the server-wide wishlist.")
    async def print_server_wl(self, ctx: commands.Context) -> None:
        server_id = ctx.message.guild.id
        if server_id not in server_wishlists or len(server_wishlists[server_id]) == 0:
            await ctx.send("Server wishlist is currently empty.")
        else:
            page = PageMessage(get_page_list(server_wishlists[server_id]), ctx, self.bot, ctx.author)
            await page.init_pages()

    @commands.hybrid_command(name="delete_server", description="Deletes a game from the server-wide wishlist.")
    async def delete_server_wl(self, ctx: commands.Context, game: str) -> None:
        server_id = ctx.message.guild.id
        if server_id not in server_wishlists:
            await ctx.send("Error: Server wishlist is currently empty.")
        else:
            search = search_steam(game, amount=1)
            game_info = search[0]

            list = server_wishlists[server_id]
            if game_info not in list:
                await ctx.send("Error: " + game_info.title + " is not in the server wishlist.")
            else:
                list.remove(game_info)
                await ctx.send(game_info.title + " was successfully removed from the server wishlist.")

    @commands.hybrid_command(name="reviews", description="View the top reviews for a given game.")
    async def get_game_reviews(self, ctx: commands.Context, game: str, view_positive: bool = None) -> None:
        page = PageMessage(self.get_review_pages(game, view_positive), ctx, self.bot, ctx.author)
        await page.init_pages()
    
    # Utility functions
    
    def get_review_pages(self, game: str, view_positive: bool = None) -> List[discord.Embed]:
        review_pages = []
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
            embed.set_author(name="Date Posted: " + review.date_posted, icon_url=review.rec_url)

            review_pages.append(embed)
        
        return review_pages

    def get_reviews_view(self, game_id: str) -> discord.ui.View:
        view = discord.ui.View()

        reviews_button = discord.ui.Button(label="Top Reviews", custom_id=game_id, emoji="📒", style=discord.ButtonStyle.primary)
        reviews_button.callback = self.reviews
        view.add_item(reviews_button)

        return view

    # Button callbacks

    async def reviews(self, interaction: discord.Interaction):
        await interaction.response.defer()

        msg = await interaction.original_response()
        ctx = await self.bot.get_context(msg)

        pages = PageMessage(self.get_review_pages(interaction.data["custom_id"]), ctx, self.bot, interaction.user)
        await pages.init_pages()
    
        