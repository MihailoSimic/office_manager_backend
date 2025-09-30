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
        "enabled": seat.get("enabled", True)
    }

@router.get("/")
async def get_all_seats(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Token nedostaje")
    username = verify_token(access_token)
    if not username:
        raise HTTPException(status_code=401, detail="Neispravan ili istekao token")
    try:
        seats = await seats_collection.find().to_list(length=100)
        return [serialize_seat(seat) for seat in seats]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvatanju sedišta: {str(e)}")

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

    # Validacija unosa
    if not isinstance(new_seats, list) or not all(isinstance(seat, dict) for seat in new_seats):
        raise HTTPException(status_code=400, detail="Pogrešan format podataka za sedišta.")

    try:
        await seats_collection.delete_many({})
        result = await seats_collection.insert_many(new_seats)
        seats = await seats_collection.find().to_list(length=100)
        return [serialize_seat(seat) for seat in seats]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri kreiranju sedišta: {str(e)}")