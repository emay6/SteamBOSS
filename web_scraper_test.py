import unittest
from web_scraper import *

# Game ids to test
# Change as needed based on Steam discounts
normal_game_ids = ["730", "1245620", "646570"]
discounted_game_ids = ["470220", "814380"]

class WebScraperTest(unittest.TestCase):
    def test_request_steam(self):
        # query steam and check if we get a valid response
        self.assertIsInstance(request_steam(STEAM_URL), requests.Response)
        self.assertIsInstance(request_steam(STEAM_CDN_URL), requests.Response)
        self.assertIsInstance(request_steam(STEAM_COMM_URL), requests.Response)

        # should fail
        with self.assertRaises(requests.ConnectionError):
            request_steam("https://invalid_url.here")
        
        with self.assertRaises(requests.HTTPError):
            request_steam(STEAM_CDN_URL + "/invalid_url")

    def test_game_info(self):
        normal_games = get_games_info(normal_game_ids)
        discounted_games = get_games_info(discounted_game_ids)

        test_normal_games = []
        test_discounted_games = []

        # Normal games
        for game_id in normal_game_ids:
            game = get_game_info(game_id)
            test_normal_games.append(game)

            self.assertEqual(game.id, game_id)
            self.assertNotEqual(game.description, "")
            self.assertNotEqual(game.price, "")
            self.assertNotEqual(game.title, "")
            self.assertEqual(game.is_discounted, False)
            self.assertEqual(game.discount_price, "N/A")
        
        # Discounted games
        for game_id in discounted_game_ids:
            game = get_game_info(game_id)
            test_discounted_games.append(game)

            self.assertEqual(game.id, game_id)
            self.assertNotEqual(game.description, "")
            self.assertNotEqual(game.price, "")
            self.assertNotEqual(game.title, "")
            self.assertEqual(game.is_discounted, True)
            self.assertNotEqual(game.discount_price, "N/A")
        
        # Invalid games
        with self.assertRaises(ValueError):
            get_game_info("2")
            get_game_info("not_a_game")
            get_game_info("...")
            get_game_info("91919191")
        
        self.assertEqual(normal_games, test_normal_games)
        self.assertEqual(discounted_games, test_discounted_games)

    def test_search_steam(self):
        # Standard searches
        game_1 = search_steam("Elden Ring", amount=1)[0]
        self.assertEqual(game_1.title, "ELDEN RING")

        game_2 = search_steam("Hollow Knight", amount=1)[0]
        self.assertEqual(game_2.title, "Hollow Knight")

        game_3 = search_steam("Sekiro", amount=1)[0]
        self.assertEqual(game_3.title, "Sekiro™: Shadows Die Twice - GOTY Edition")

        game_4 = search_steam("ror2", amount=1)[0]
        self.assertEqual(game_4.title, "Risk of Rain 2")

        # Invalid searches (no results)
        self.assertEqual(search_steam("fjwijaflkjaa"), [])
        self.assertEqual(search_steam("-=-=[]\[\][,,]"), [])

    def test_game_reviews(self):
        # Check if reviews are gotten normally
        for game_id in normal_game_ids:
            reviews = get_game_reviews(game_id)
            pos_reviews = get_game_reviews(game_id, positive=True)
            neg_reviews = get_game_reviews(game_id, positive=False)

            # Reviews are grabbed properly 
            self.assertNotEqual(reviews, [])
            self.assertNotEqual(pos_reviews, [])
            self.assertNotEqual(neg_reviews, [])

            # Reviews are checked for valid data
            for review in reviews:
                self.assertNotEqual(review.author, "N/A")
                self.assertNotEqual(review.content, "N/A")
                self.assertNotEqual(review.date_posted, "N/A")
                self.assertNotEqual(review.hours_on_record, "N/A")
                self.assertNotEqual(review.rec_url, "")

            # Only positive reviews gotten successfully
            for review in pos_reviews:
                self.assertEqual(review.recommended, True)
                self.assertEqual(review.rec_url, THUMBS_UP_URL)
            
            # Only negative reviews gotten successfully
            for review in neg_reviews:
                self.assertEqual(review.recommended, False)
                self.assertEqual(review.rec_url, THUMBS_DOWN_URL)

if __name__ == "__main__":
    unittest.main()