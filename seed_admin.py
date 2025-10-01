import asyncio
from db import users_collection
import bcrypt

async def seed_admin():
    admin = {
        "username": "admin",
        "password": bcrypt.hashpw("Admin123!".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
        "role": "admin",
        "approved": True
    }
    existing = await users_collection.find_one({"username": admin["username"]})
    if not existing:
        await users_collection.insert_one(admin)
        print("Admin user created.")
    else:
        print("Admin user already exists.")

if __name__ == "__main__":
    asyncio.run(seed_admin())
