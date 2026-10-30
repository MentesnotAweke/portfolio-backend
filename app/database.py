import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def connect_to_mongo():
    """Connect to MongoDB on startup"""
    print("Connecting to MongoDB...")
    db_instance.client = AsyncIOMotorClient(MONGO_URI)
    # "portfolio_db" is the name of the database we will use
    db_instance.db = db_instance.client.get_database("portfolio_db")
    print("Connected to MongoDB successfully!")

async def close_mongo_connection():
    """Close MongoDB connection on shutdown"""
    print("Closing MongoDB connection...")
    if db_instance.client:
        db_instance.client.close()
    print("MongoDB connection closed.")

def get_database():
    """Dependency to get the database instance"""
    return db_instance.db