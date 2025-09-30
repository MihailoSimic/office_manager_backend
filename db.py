import os
from motor.motor_asyncio import AsyncIOMotorClient

# ========================
# Konektovanje na MongoDB
# ========================
# Ako je u Dockeru, koristi MONGO_URI iz env; ako nije, fallback na lokalni MongoDB
MONGO_DETAILS = os.getenv("MONGO_URI", "mongodb://localhost:27017/office_manager")

client = AsyncIOMotorClient(MONGO_DETAILS)

# Ako koristiš MONGO_URI sa bazom u URI, get_default_database() radi automatski
# Inače možeš eksplicitno:
db = client.get_default_database()  # ili client["office_manager"]

# ========================
# Kolekcije
# ========================
users_collection = db["users"]
seats_collection = db["seats"]
reservations_collection = db["reservations"]

# ========================
# Helper funkcije
# ========================
async def fetch_all(collection, limit=100):
    """Vrati do 100 dokumenata iz kolekcije (ili koliko limit kaže)"""
    return await collection.find().to_list(length=limit)