from fastapi import APIRouter, HTTPException, Cookie, Body
from db import seats_collection
from auth import verify_token
from typing import List

router = APIRouter(prefix="/seat", tags=["seat"])

def serialize_seat(seat):
    return {
        "id": str(seat["_id"]),
        "seat_number": seat["seat_number"],
        "row": seat["row"],
        "col": seat["col"],
        "enabled": seat.get("enabled", True)  # dodato polje enabled
    }

@router.get("/")
async def get_all_seats(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Token nedostaje")
    
    username = verify_token(access_token)
    if not username:
        raise HTTPException(status_code=401, detail="Neispravan ili istekao token")
    
    seats = await seats_collection.find().to_list(length=100)
    return [serialize_seat(seat) for seat in seats]

# POST ruta koja briše sva sedišta i ubacuje nova
@router.post("/")
async def create_seats(
    new_seats: List[dict] = Body(...),
    access_token: str = Cookie(None)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Token nedostaje")
    
    username = verify_token(access_token)
    if not username:
        raise HTTPException(status_code=401, detail="Neispravan ili istekao token")
    
    # Obriši sva postojeća sedišta
    await seats_collection.delete_many({})
    
    # Ubaci nova sedišta
    result = await seats_collection.insert_many(new_seats)
    
    # Dohvati nova sedišta da ih vrati FE
    seats = await seats_collection.find().to_list(length=100)
    return [serialize_seat(seat) for seat in seats]