import asyncio
import logging
import feedparser
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Import Config
from config import API_ID, API_HASH, BOT_TOKEN, NEWS_FEED_URLS, CHANNEL_ID, OWNER_ID

# Import Our Custom Tools
from duck.database import db
from duck.utils.ai_helper import ai_editor
from duck.utils.image_gen import image_generator
from duck.utils.graph_helper import graph_maker
from duck.utils.text_styler import styler

# --- Setup Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Initialize Bot ---
app = Client(
    "AnimeNewsBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins") # Loads /plugins folder automatically
)

# --- The Core Logic: RSS Checker ---
async def check_feeds():
    """Main loop that checks RSS feeds periodically."""
    logger.info("🔄 RSS Checker Started...")
    
    while True:
        for url in NEWS_FEED_URLS:
            try:
                # Parse the Feed
                feed = feedparser.parse(url)
                
                for entry in feed.entries[:3]:  # Check top 3 latest posts
                    link = entry.link
                    title = entry.title
                    summary = getattr(entry, "summary", "No summary available.")
                    
                    # 1. Check Database (Skip if already posted)
                    if await db.is_posted(link):
                        continue
                    
                    logger.info(f"🆕 New Post Found: {title}")
                    
                    # 2. Generate Assets (The Magic Happens Here)
                    
                    # A. Generate Hype Caption (AI)
                    caption_text = await ai_editor.generate_hype_caption(title, summary)
                    
                    # B. Create Instant View Page (Telegraph)
                    # We pass the full content if available, else summary
                    content = getattr(entry, "content", [{"value": summary}])[0]["value"]
                    telegraph_url = graph_maker.create_page(title, content)
                    
                    # C. Generate Custom Thumbnail (Image Gen)
                    # Try to find an image in the RSS entry
                    image_url = None
                    if "media_content" in entry:
                        image_url = entry.media_content[0]["url"]
                    elif "links" in entry:
                         for l in entry.links:
                             if "image" in l.type:
                                 image_url = l.href
                                 break
                    
                    # If we found an image URL, process it
                    photo_file = None
                    if image_url:
                        photo_file = await image_generator.create_thumbnail(image_url, title)

                    # 3. Construct the Message
                    separator = styler.get_separator()
                    bullet = styler.get_random_bullet()
                    
                    final_caption = (
                        f"{bullet} {caption_text}\n\n"
                        f"{separator}\n"
                        f"📣 ᴊᴏɪɴ @YourChannelUsername" 
                    )
                    
                    # Create Button
                    buttons = InlineKeyboardMarkup([
                        [InlineKeyboardButton(styler.convert("READ FULL ARTICLE", "small_caps"), url=telegraph_url or link)]
                    ])

                    # 4. Send to Channel
                    try:
                        if photo_file:
                            await app.send_photo(CHANNEL_ID, photo_file, caption=final_caption, reply_markup=buttons)
                        else:
                            # Fallback if no image found
                            await app.send_message(CHANNEL_ID, final_caption, reply_markup=buttons)
                            
                        # 5. Save to Database
                        await db.add_post(link, title)
                        logger.info(f"✅ Posted: {title}")
                        
                        # Wait a bit between posts to avoid flood limits
                        await asyncio.sleep(5)
                        
                    except Exception as e:
                        logger.error(f"Failed to send message: {e}")

            except Exception as e:
                logger.error(f"Error parsing feed {url}: {e}")
        
        # Wait 5 minutes before checking again
        logger.info("💤 Sleeping for 5 minutes...")
        await asyncio.sleep(300)

# --- Admin Commands ---

@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats(client, message):
    users = await db.get_total_users()
    await message.reply_text(f"📊 **Bot Stats**\n\n👤 Users: {users}\n✅ System Online")

@app.on_message(filters.command("force") & filters.user(OWNER_ID))
async def force_check(client, message):
    await message.reply_text("🔄 Forcing Feed Check...")
    # This just creates a background task to check immediately
    asyncio.create_task(check_feeds())

# --- Entry Point ---
async def main():
    await app.start()
    print("🔥 Bot is Online!")
    
    # Start the RSS Loop in background
    asyncio.create_task(check_feeds())
    
    # Keep bot running
    await idle()
    await app.stop()

if __name__ == "__main__":
    app.run(main())
    
