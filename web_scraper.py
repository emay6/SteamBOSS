import requests
import sys
import json
from typing import List
from bs4 import BeautifulSoup
from steam_game import SteamGame, save_game, load_game, SAVE_PATH

STEAM_URL = "https://store.steampowered.com"
STEAM_CDN_URL = "https://cdn.akamai.steamstatic.com"

def request_steam(url: str) -> requests.Response:
    """Function to help request a page from Steam."""
    req = requests.get(url)
    if (req.status_code != 200):
        raise requests.HTTPError("An error occurred while attempting to access Steam. HTTP error code: " + req.status_code)
    
    return req

def get_game_info(game_id: str) -> SteamGame:
    """Returns a information about the game found on the store page of the game with the given id.

    The returns only the information of the base version of the game (the first price on the page).

    i.e. Will not return information about special editions, deluxe editions, etc."""
    if (not game_id.isdigit()):
        raise ValueError("Game IDs may only consist of digits.")
    
    # Checks if game already exists in saved games to save time
    try:
        with open(SAVE_PATH, "r+", encoding="utf-8") as f:
            games = json.load(f)
            if game_id in games:
                return load_game(games[game_id])
    except FileNotFoundError:
        pass
    
    page_request = request_steam(STEAM_URL + "/app/" + game_id)
    
    # Checks if the id provided was a valid game (i.e. check if a valid game page was recieved)
    page = BeautifulSoup(page_request.content, features="html.parser")
    if (not "game_bg" in page.body["class"]):
        raise ValueError(f"No game with ID '{game_id}' was found.")
    
    # Initialize information for game
    game_info = SteamGame()
    game_info.id = game_id
    game_info.title = page.find(id="appHubAppName").text
    game_info.header_url = STEAM_CDN_URL + "/steam/apps/" + game_id + "/header.jpg"

    desc = page.find(class_="game_description_snippet")
    if desc is not None:
        game_info.description = desc.text.strip()

    price = page.find(class_="discount_original_price")
    # Ignores bundle discounts
    if (price is not None) and (price.parent.find_previous_sibling(class_="bundle_base_discount") is None):
        game_info.price = price.text
        game_info.discount_price = page.find(class_="discount_final_price").text
        # Formats the discount amount properly
        discount_amount = float(page.find(class_="game_purchase_discount")["data-discount"])
        game_info.discount_amount = round(discount_amount / 100, 2)
        game_info.is_discounted = True
    else:
        game_info.price = page.find(class_="game_purchase_price").text.strip()

    save_game(game_info)
    return game_info

def get_games_info(game_ids: List[str]) -> List[SteamGame]:
    """Returns a dictionary of info for the given list of game ids. Keyed by game id."""
    games = []
    for id in game_ids:
        games.append(get_game_info(id))
    
    return games

def search_steam(search_query: str, amount: int = 10) -> List[SteamGame]:
    """Queries Steam's search with the given string, returning the first "amount" results. Currently only supports games."""
    page_request = request_steam(STEAM_URL + "/search/?term=" + search_query + "&category1=998")

    page = BeautifulSoup(page_request.content, features="html.parser")

    # Grab search results
    seen = []
    results = []
    i = 1
    search_rows = page.find_all(class_="search_result_row")
    for game in search_rows:
        # Only get a certain amount of results
        if i > amount:
            break
        # The game's id, ignoring things like special editions, duplicates, etc.
        game_id = game["data-ds-appid"].split(",")[0]
        if game_id not in seen:
            seen.append(game_id)
            results.append(get_game_info(game_id))
        
        i += 1
    
    return results

# Testing code
if __name__ == "__main__":
    print("--TESTING WEB_SCRAPER.PY--")
    if len(sys.argv) == 1:
        test_game_ids = ["1621310", "2594920", "2778580", "1164050"] # regular game, f2p game, dlc, game on sale
        game_infos = get_games_info(test_game_ids)
        for game in game_infos:
            print("-----------------------")
            print(game)
    elif len(sys.argv) == 2:
        games = search_steam(sys.argv[1])
        for game in games:
            print("-----------------------")
            print(game)
