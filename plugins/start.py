# plugins/start.py
from pyrogram import Client, filters

@Client.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("I am alive and built from scratch! 🤖")
  
