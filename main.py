# main.py
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

class Bot(Client):
    def __init__(self):
        super().__init__(
            "MyAnimeBot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="plugins")  # Automatically loads files from /plugins
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        print(f"🔥 Bot Started as {me.username}")

    async def stop(self, *args):
        await super().stop()
        print("Bot Stopped.")

if __name__ == "__main__":
    app = Bot()
    app.run()
  
