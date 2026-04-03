"""
Database Configuration
MongoDB connection using Motor (async driver).
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "cognify_db")

client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]

# Collections
quiz_sessions = db["quiz_sessions"]
user_performance = db["user_performance"]


async def connect_db():
    """Test database connection."""
    try:
        await client.admin.command("ping")
        print("✅ Connected to MongoDB successfully!")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")


async def close_db():
    """Close database connection."""
    client.close()