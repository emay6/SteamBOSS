from dataclasses import dataclass, asdict
from typing import List
from discord import Embed
import json
import os

SAVE_PATH = "data/game_info.json"

@dataclass
class SteamReview:
    """
    author: The username of the user who left the review
    date_posted: The date the review was psoted
    hours_on_record: The number of hours the user has on the game in total
    content: The content of the review
    recommended: True if the game was recommended by the user, False otherwise
    rec_url: URL to the thumbs up/thumbs down icon for the review depending on its recommended state
    """
    author: str = "N/A"
    date_posted: str = "N/A"
    hours_on_record: str = "N/A"
    content: str = "N/A"
    recommended: bool = False
    review_url: str = ""
    rec_url: str = ""

    def __str__(self) -> str:
        return f"Username: {self.author}\nDate Posted: {self.date_posted}\nHours on Record: {self.hours_on_record}\nContent: {self.content}\nRecommended?: {self.recommended}"

@dataclass
class SteamGame:
    """ 
    id: Steam ID of the game as a string
    title: The title of the game
    price: The original price of the game as a string
    is_discounted: True if the game is on sale, False otherwise
    discount_amount: The amount of the discount as a percentage ranging from 0 to 1, inclusive
    discount_price: The current price of the game, if its on sale
    header_url: The url to the header image of the game
    """
    id: str = "N/A"
    title: str = "N/A"
    description: str = "N/A"
    price: str = "N/A"
    is_discounted: bool = False
    discount_amount: float = 0
    discount_price: str = "N/A"
    header_url: str = ""
    game_url: str = ""

    def __str__(self) -> str:
        return f"Game ID: {self.id}\nGame Title: {self.title}\nGame Description: {self.description}\nGame Price: {self.price}\nIs Discounted?: {self.is_discounted}\nDiscount Amount: {self.discount_amount}\nDiscount Price: {self.discount_price}"

def save_game(game: SteamGame) -> None:
    """Saves or updates the game's info in the set location (currently set to be a JSON file)."""
    if not os.path.exists("data"):
        os.makedirs("data")

    with open(SAVE_PATH, "a+", encoding="utf-8") as f:
        # Return to beginning of file
        f.seek(0)
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            # Create a new dictionary upon error or if file is empty
            data = dict()
        finally:
            f.truncate(0)
            data[game.id] = asdict(game)
            json.dump(data, f)

def load_game(obj: dict) -> SteamGame:
    """Returns a SteamGame object given a dictionary."""
    return SteamGame(**obj)