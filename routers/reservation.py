from fastapi import APIRouter, HTTPException
from db import reservations_collection  # pretpostavljamo da već postoji connection
from models.reservation import Reservation  # tvoj Pydantic model

router = APIRouter(prefix="/reservation", tags=["reservation"])

# ========================
# GET: rezervacije po datumu ili korisniku
# ========================
@router.get("/")
async def get_reservations(date: str = None, username: str = None):
    query = {}
    if date:
        query["date"] = date
    if username:
        query["username"] = username
    reservations = await reservations_collection.find(query).to_list(length=100)
    return reservations

# ========================
# POST: kreiranje nove rezervacije
# ========================
@router.post("/create")
async def create_reservation(reservation: Reservation):
    # Provera da li je mesto zauzeto na odabrani datum
    existing = await reservations_collection.find_one({
        "date": reservation.date,
        "seat_number": reservation.seat_number
    })
    if existing:
        raise HTTPException(status_code=400, detail="Mesto je već zauzeto za odabrani datum")
    
    await reservations_collection.insert_one(reservation.dict())
    return {"message": f"Mesto {reservation.seat_number} rezervisano za {reservation.date}"}

# ========================
# PUT: menja status rezervacije (approve/reject) - za admina
# ========================
@router.put("/{reservation_id}")
async def update_reservation_status(reservation_id: str, status: str):
    result = await reservations_collection.update_one(
        {"_id": reservation_id},
        {"$set": {"status": status}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Rezervacija nije pronađena")
    return {"message": f"Rezervacija {reservation_id} ažurirana sa statusom {status}"}