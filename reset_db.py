import pymongo
from config import MONGO_URI

# Connect
client = pymongo.MongoClient(MONGO_URI)
db = client["AnimeNewsBot"]

# Delete the history collection
db.news_history.drop()

print("✅ Database history cleared! The bot will now repost everything.")
