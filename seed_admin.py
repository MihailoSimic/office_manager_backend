import asyncio
from db import users_collection, seats_collection
import bcrypt

def generate_seat_grid(rows=3, cols=3):
    seats = []
    seat_number = 1
    for row in range(1, rows + 1):
        for col in range(1, cols + 1):
            seats.append({
                "seat_number": seat_number,
                "row": row,
                "col": col,
                "enabled": True
            })
            seat_number += 1
    return seats

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

    seat_count = await seats_collection.count_documents({})
    if seat_count == 0:
        seats = generate_seat_grid(3, 3)
        await seats_collection.insert_many(seats)
        print("Default 3x3 seat layout created.")
    else:
        print("Seats already exist, skipping seat seeding.")

if __name__ == "__main__":
    asyncio.run(seed_admin())
