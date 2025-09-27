from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorClient

# ========================
# Konektovanje na MongoDB
# ========================
MONGO_DETAILS = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_DETAILS)
db = client["office_manager"]

# ========================
# Kolekcije
# ========================
users_collection = db["users"]
seats_collection = db["seats"]
reservations_collection = db["reservations"]

# ========================
# Opcioni helper (ako zatreba)
# ========================
async def fetch_all(collection):
    return await collection.find().to_list(length=100)