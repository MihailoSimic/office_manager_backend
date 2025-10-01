import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DETAILS = os.getenv("MONGO_URI", "mongodb://localhost:27017/office_manager")

client = AsyncIOMotorClient(MONGO_DETAILS)

db = client.get_default_database()

users_collection = db["users"]
seats_collection = db["seats"]
reservations_collection = db["reservations"]
