from fastapi import APIRouter
from db import seats_collection  # pretpostavljamo da već postoji connection
def serialize_seat(seat):
    """
    Pretvara MongoDB dokument u JSON-serializable dict.
    ObjectId _id se konvertuje u string.
    """
    return {
        "id": str(seat["_id"]),
        "seat_number": seat["seat_number"],
        "row": seat["row"],
        "col": seat["col"]
    }
router = APIRouter(prefix="/seat", tags=["seat"])


@router.get("/")
async def get_all_seats():
    seats = await seats_collection.find().to_list(length=100)
    return [serialize_seat(seat) for seat in seats]