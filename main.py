# main.py
import asyncio
import logging
import feedparser
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from urllib.parse import urlparse

# Import Config & Tools
from config import API_ID, API_HASH, BOT_TOKEN, NEWS_FEED_URLS, CHANNEL_ID, OWNER_ID
from duck.database import db
from duck.utils.ai_helper import ai_editor
from duck.utils.image_gen import image_generator
from duck.utils.graph_helper import graph_maker
from duck.utils.text_styler import styler
from duck.utils.scraper import scraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Client("AnimeNewsBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, plugins=dict(root="plugins"))

def get_source_name(url):
    """Extracts 'Crunchyroll' from 'https://crunchyroll.com/...'"""
    domain = urlparse(url).netloc
    name = domain.replace("www.", "").split('.')[0]
    return name.capitalize()

async def check_feeds():
    logger.info("🔄 RSS Checker Started...")
    while True:
        for url in NEWS_FEED_URLS:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:3]:
                    link = entry.link
                    # Extract Source Name (e.g., "Crunchyroll")
                    source_name = get_source_name(link)
                    
                    if await db.is_posted(link):
                        continue
                    
                    logger.info(f"Processing: {entry.title}")

                    # 1. Scrape Content
                    scraped = scraper.scrape(link)
                    if not scraped: continue

                    full_text = scraped['text']
                    image_url = scraped['image']
                    
                    # 2. AI Processing (Parallel for speed)
                    # We generate Caption AND Telegraph HTML simultaneously
                    caption_task = ai_editor.generate_hype_caption(entry.title, getattr(entry, "summary", ""), source_name)
                    html_task = ai_editor.format_article_html(entry.title, full_text, image_url)
                    
                    caption_text, formatted_html = await asyncio.gather(caption_task, html_task)

                    # 3. Create Telegraph Page
                    telegraph_url = graph_maker.create_page(entry.title, formatted_html)

                    # 4. Generate Thumbnail
                    photo_file = None
                    if image_url:
                        photo_file = await image_generator.create_thumbnail(image_url, entry.title)

                    # 5. Build Final Message
                    bullet = styler.get_random_bullet()
                    separator = styler.get_separator()
                    
                    # Custom Watermark & Source
                    footer = (
                        f"{separator}\n"
                        f"🗞 **Source:** {source_name}\n"
                        f"💎 **DOT NeWZ Network**"
                    )

                    final_caption = f"{bullet} {caption_text}\n\n{footer}"
                    
                    # Styled Button
                    btn_text = styler.convert("READ FULL ARTICLE", "small_caps")
                    buttons = InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"⌲ {btn_text}", url=telegraph_url or link)]
                    ])

                    # 6. Send
                    try:
                        if photo_file:
                            await app.send_photo(CHANNEL_ID, photo_file, caption=final_caption, reply_markup=buttons)
                        else:
                            await app.send_message(CHANNEL_ID, final_caption, reply_markup=buttons)
                        
                        await db.add_post(link, entry.title)
                        await asyncio.sleep(5)
                    except Exception as e:
                        logger.error(f"Send Error: {e}")

            except Exception as e:
                logger.error(f"Feed Error: {e}")
        
        await asyncio.sleep(300)

async def main():
    await app.start()
    asyncio.create_task(check_feeds())
    await idle()
    await app.stop()

if __name__ == "__main__":
    app.run(main())
    
