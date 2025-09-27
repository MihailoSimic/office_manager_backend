from fastapi import APIRouter, HTTPException, Cookie
from db import seats_collection
from auth import verify_token

router = APIRouter(prefix="/seat", tags=["seat"])

def serialize_seat(seat):
    return {
        "id": str(seat["_id"]),
        "seat_number": seat["seat_number"],
        "row": seat["row"],
        "col": seat["col"]
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