from auth import require_and_refresh_token
from fastapi import APIRouter, HTTPException, Cookie, Body, Response
from db import seats_collection
from auth import verify_token
from typing import List
from auth import create_access_token 
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
async def get_all_seats(response: Response, access_token: str = Cookie(None)):
    require_and_refresh_token(response, access_token)
    try:
        seats = await seats_collection.find().to_list(length=1000)
        return [serialize_seat(seat) for seat in seats]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvatanju sedišta: {str(e)}")

@router.post("/")
async def create_seats(
    new_seats: List[dict] = Body(...),
    response: Response = None,
    access_token: str = Cookie(None)
):
    try:
        require_and_refresh_token(response, access_token)

        if not isinstance(new_seats, list) or not all(isinstance(seat, dict) for seat in new_seats):
            raise HTTPException(status_code=400, detail="Pogrešan format podataka za sedišta.")
        await seats_collection.delete_many({})
        result = await seats_collection.insert_many(new_seats)
        seats = await seats_collection.find().to_list(length=1000)
        return [serialize_seat(seat) for seat in seats]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri kreiranju sedišta: {str(e)}")