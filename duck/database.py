import motor.motor_asyncio
import logging
from config import MONGO_URI

# Configure Logger
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        # 1. Connect to MongoDB
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
            self.db = self.client["AnimeNewsBot"]
            
            # Collections (Tables)
            self.news_col = self.db["news_history"]  # Stores posted links
            self.users_col = self.db["users"]        # Stores bot users
            
            logger.info("✅ Database Connected Successfully")
        except Exception as e:
            logger.error(f"❌ Database Connection Failed: {e}")

    # --- News Logic ---
    async def is_posted(self, link):
        """Checks if a link has already been posted."""
        doc = await self.news_col.find_one({"link": link})
        return True if doc else False

    async def add_post(self, link, title):
        """Saves a link to history so we don't post it again."""
        await self.news_col.insert_one({
            "link": link,
            "title": title
        })

    # --- User Logic ---
    async def add_user(self, user_id, name):
        """Adds a user to the database if they don't exist."""
        if not await self.users_col.find_one({"user_id": user_id}):
            await self.users_col.insert_one({
                "user_id": user_id,
                "name": name
            })

    async def get_total_users(self):
        """Returns the count of total users."""
        return await self.users_col.count_documents({})

# Create a single instance to be used in main.py
db = Database()

