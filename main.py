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
    try:
        domain = urlparse(url).netloc
        name = domain.replace("www.", "").split('.')[0]
        return name.capitalize()
    except:
        return "Anime News"

async def check_feeds():
    logger.info("🔄 RSS Checker Started...")
    while True:
        for url in NEWS_FEED_URLS:
            try:
                feed = feedparser.parse(url)
                
                # Check top 3 entries
                for entry in feed.entries[:3]:
                    link = entry.link
                    title = entry.title
                    source_name = get_source_name(link)
                    
                    # 1. Check Database (Skip if already posted)
                    if await db.is_posted(link):
                        continue
                    
                    logger.info(f"🆕 Processing: {title}")

                    # 2. Scrape Content (With Fallback Logic)
                    scraped = scraper.scrape(link)
                    
                    full_text = ""
                    image_url = None
                    use_fallback = False

                    if scraped and scraped.get('text'):
                        # ✅ Scrape Successful
                        full_text = scraped['text']
                        image_url = scraped['image']
                        logger.info(f"✅ Scraped successfully from {source_name}")
                    else:
                        # ⚠️ Scrape Failed - ENABLE FALLBACK MODE
                        use_fallback = True
                        logger.warning(f"⚠️ Scraping failed for {link}. Using RSS Fallback.")
                        
                        # Use RSS Summary as text
                        full_text = getattr(entry, "summary", "Click the link below to read the full story.")
                        
                        # Try to find image in RSS metadata
                        if "media_content" in entry:
                            image_url = entry.media_content[0]["url"]
                        elif "links" in entry:
                             for l in entry.links:
                                 if "image" in l.type:
                                     image_url = l.href
                                     break

                    # 3. AI Processing
                    # If fallback is active, we tell AI to keep it simple
                    
                    # Parallel tasks: Generate Hype Caption AND Telegraph Page
                    caption_task = ai_editor.generate_hype_caption(title, getattr(entry, "summary", ""), source_name)
                    
                    # For Telegraph: If fallback, we use summary; if scraped, we use full text
                    html_task = ai_editor.format_article_html(title, full_text, image_url)
                    
                    caption_text, formatted_html = await asyncio.gather(caption_task, html_task)

                    # 4. Create Telegraph Page
                    telegraph_url = graph_maker.create_page(title, formatted_html)

                    # 5. Generate Thumbnail (If image exists)
                    photo_file = None
                    if image_url:
                        try:
                            # Add watermark to the image
                            photo_file = await image_generator.create_thumbnail(image_url, title)
                        except Exception as e:
                            logger.error(f"Thumbnail Generation Failed: {e}")

                    # 6. Build Final Message
                    bullet = styler.get_random_bullet()
                    separator = styler.get_separator()
                    
                    # Footer with Watermark Text
                    footer = (
                        f"{separator}\n"
                        f"🗞 **Source:** {source_name}\n"
                        f"💎 **DOT NeWZ Network**"
                    )

                    final_caption = f"{bullet} {caption_text}\n\n{footer}"
                    
                    # Read More Button
                    btn_text = styler.convert("READ FULL ARTICLE", "small_caps")
                    # If Telegraph failed, link directly to source
                    final_link = telegraph_url if telegraph_url else link
                    
                    buttons = InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"⌲ {btn_text}", url=final_link)]
                    ])

                    # 7. Send to Channel
                    try:
                        if photo_file:
                            await app.send_photo(CHANNEL_ID, photo_file, caption=final_caption, reply_markup=buttons)
                        else:
                            # If no image found at all, send text only
                            await app.send_message(CHANNEL_ID, final_caption, reply_markup=buttons)
                        
                        # Mark as posted
                        await db.add_post(link, title)
                        logger.info(f"🚀 Posted: {title}")
                        
                        # Rate limit to avoid flood
                        await asyncio.sleep(8)
                        
                    except Exception as e:
                        logger.error(f"❌ Send Error: {e}")

            except Exception as e:
                logger.error(f"❌ Feed Error for {url}: {e}")
        
        # Wait 5 minutes before next check
        logger.info("💤 Sleeping for 5 minutes...")
        await asyncio.sleep(300)

async def main():
    await app.start()
    print("🔥 DOT NeWZ Bot is Online!")
    
    # Run the feed checker in the background
    asyncio.create_task(check_feeds())
    
    await idle()
    await app.stop()

if __name__ == "__main__":
    app.run(main())
    
