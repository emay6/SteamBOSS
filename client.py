import steam_boss
import json

if __name__ == "__main__":
    BOT_TOKEN = ""
    with open("token.json") as f:
        info = json.load(f)
        BOT_TOKEN = info["token"]

    steam_boss.bot.run(BOT_TOKEN)