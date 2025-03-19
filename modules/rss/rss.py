import asyncio
import feedparser
from bot import app, format_post, STICKER_ID  # Import key elements directly

async def fetch_and_send_news(app: Client, db, global_settings_collection, urls):
    config = global_settings_collection.find_one({"_id": "config"})
    if not config or "news_channel" not in config:
        return

    news_channel = "@" + config["news_channel"]

    for url in urls:
        feed = await asyncio.to_thread(feedparser.parse, url)
        entries = list(feed.entries)[::-1]  # Reverse order to send newest last

        for entry in entries:
            entry_id = entry.get('id', entry.get('link'))

            if not db.sent_news.find_one({"entry_id": entry_id}):
                news_item = {
                    "title": entry.title,
                    "summary": entry.get("summary", ""),
                    "link": entry.link,
                    "date": entry.get("published", "Unknown Date"),
                    "studio": entry.get("source", {}).get("title", "Unknown Studio"),
                    "category": "Anime Release" if "anime" in entry.title.lower() else "Industry News"
                }

                msg, sticker_id = format_post(news_item, STICKER_ID)
                thumbnail_url = entry.media_thumbnail[0]['url'] if 'media_thumbnail' in entry else None

                try:
                    await asyncio.sleep(5)  # Reduced delay for faster updates
                    if thumbnail_url:
                        await app.send_photo(chat_id=news_channel, photo=thumbnail_url, caption=msg)
                    else:
                        await app.send_message(chat_id=news_channel, text=msg)

                    await app.send_sticker(chat_id=news_channel, sticker=sticker_id)

                    db.sent_news.insert_one({"entry_id": entry_id, "title": entry.title, "link": entry.link})
                    print(f"✅ Sent news: {entry.title}")
                except Exception as e:
                    print(f"❌ Error sending news message: {entry.title}")
                    print(f"➡️ Details: {e}")

async def news_feed_loop(app: Client, db, global_settings_collection, urls):
    while True:
        await fetch_and_send_news(app, db, global_settings_collection, urls)
        await asyncio.sleep(30)  # Increased delay for better interval control
