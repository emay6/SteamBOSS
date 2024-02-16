import discord
import json

class SteamBOSS(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}")

    async def on_message(self, msg):
        print(f"Message from {msg.author}: {msg.content}")

intents = discord.Intents.default()
intents.message_content = True
BOT_TOKEN = ""
with open("token.json") as f:
    info = json.load(f)
    BOT_TOKEN = info["token"]

client = SteamBOSS(intents=intents)
client.run(BOT_TOKEN)