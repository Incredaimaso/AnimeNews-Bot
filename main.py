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
from duck.utils.uploader import catbox

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Client("AnimeNewsBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, plugins=dict(root="plugins"))

def get_source_name(url):
    try:
        domain = urlparse(url).netloc
        return domain.replace("www.", "").split('.')[0].capitalize()
    except:
        return "Anime News"

async def check_feeds():
    logger.info("🔄 RSS Checker Started...")
    while True:
        for url in NEWS_FEED_URLS:
            try:
                feed = feedparser.parse(url)
                if not feed.entries:
                    continue

                for entry in feed.entries[:3]:
                    link = entry.link
                    title = entry.title
                    
                    # 1. Check Database (Skip if already posted)
                    if await db.is_posted(link):
                        continue
                    
                    logger.info(f"🆕 Processing: {title}")
                    source_name = get_source_name(link)

                    # 2. Scrape Content
                    scraped = scraper.scrape(link)
                    
                    if scraped:
                        full_text = scraped['text']
                        original_image_url = scraped['image']
                        logger.info("✅ Scraped successfully")
                    else:
                        logger.warning(f"⚠️ Scraping failed/skipped for {link}. Using RSS Fallback.")
                        full_text = getattr(entry, "summary", "Read full article for details.")
                        
                        # ROBUST IMAGE EXTRACTION (Fixes the 'url' crash)
                        original_image_url = None
                        try:
                            if "media_content" in entry and entry.media_content:
                                original_image_url = entry.media_content[0].get("url")
                            elif "links" in entry:
                                for l in entry.links:
                                    if l.get("type", "").startswith("image"):
                                        original_image_url = l.get("href")
                                        break
                        except Exception as e:
                            logger.error(f"Image Extraction Error: {e}")

                    # 3. Upload to Catbox (Only if we have an image)
                    catbox_url = None
                    if original_image_url:
                        catbox_url = await catbox.upload_from_url(original_image_url)
                    
                    # Fallback for Telegraph
                    final_image_url = catbox_url if catbox_url else original_image_url
                    
                    # 4. AI Processing
                    # Safely handle missing image in AI prompt
                    caption_task = ai_editor.generate_hype_caption(title, getattr(entry, "summary", ""), source_name)
                    html_task = ai_editor.format_article_html(title, full_text, final_image_url or "https://telegra.ph/file/placeholder.jpg")
                    
                    caption_text, formatted_html = await asyncio.gather(caption_task, html_task)

                    # 5. Create Telegraph Page
                    telegraph_url = graph_maker.create_page(title, formatted_html)

                    # 6. Generate Thumbnail (If possible)
                    photo_file = None
                    if original_image_url:
                        try:
                            photo_file = await image_generator.create_thumbnail(original_image_url, title)
                        except Exception as e:
                            logger.error(f"Thumbnail Gen Error: {e}")

                    # 7. Build Message
                    bullet = styler.get_random_bullet()
                    separator = styler.get_separator()
                    
                    footer = (
                        f"{separator}\n"
                        f"🗞 **Source:** {source_name}\n"
                        f"💎 **DOT NeWZ Network**"
                    )

                    final_caption = f"{bullet} {caption_text}\n\n{footer}"
                    
                    btn_text = styler.convert("READ FULL ARTICLE", "small_caps")
                    buttons = InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"⌲ {btn_text}", url=telegraph_url or link)]
                    ])

                    # 8. Send & SAVE (Critical Step)
                    try:
                        if photo_file:
                            await app.send_photo(CHANNEL_ID, photo_file, caption=final_caption, reply_markup=buttons)
                        else:
                            # Fallback if no image exists at all
                            await app.send_message(CHANNEL_ID, final_caption, reply_markup=buttons, disable_web_page_preview=False)
                        
                        logger.info(f"🚀 Posted: {title}")
                        
                    except Exception as e:
                        logger.error(f"Telegram Send Error: {e}")
                    
                    # ALWAYS save to DB to prevent loops, even if sending failed partly
                    await db.add_post(link, title)
                    await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Feed Loop Error for {url}: {e}")
        
        logger.info("💤 Sleeping for 60 seconds...")
        await asyncio.sleep(60)

async def main():
    await app.start()
    print("🔥 DOT NeWZ Bot is Online!")
    asyncio.create_task(check_feeds())
    await idle()
    await app.stop()

if __name__ == "__main__":
    app.run(main())
                    
