from fastapi import APIRouter, HTTPException, Cookie, Depends
from db import reservations_collection
from models.reservation import Reservation
from auth import verify_token
from bson import ObjectId

router = APIRouter(prefix="/reservation", tags=["reservation"])

async def get_current_user(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Token nedostaje")
    username = verify_token(access_token)
    if not username:
        raise HTTPException(status_code=401, detail="Neispravan ili istekao token")
    return username

@router.get("/")
async def get_reservations():
    try:
        reservations = await reservations_collection.find({}).to_list(length=100)
        for r in reservations:
            r["_id"] = str(r["_id"])
        return reservations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvatanju rezervacija: {str(e)}")

@router.post("/create")
async def create_reservation(
    reservation: Reservation,
    current_user: str = Depends(get_current_user)
):
    reservation.username = current_user

    existing = await reservations_collection.find_one({
        "date": reservation.date,
        "seat_number": reservation.seat_number,
        "status": {"$in": ["approved", "pending"]}
    })
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Mesto je već zauzeto (rezervacija je već u toku ili odobrena) za odabrani datum"
        )

    try:
        result = await reservations_collection.insert_one(reservation.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri kreiranju rezervacije: {str(e)}")

    return {
        "message": f"Mesto {reservation.seat_number} rezervisano za {reservation.date}",
        "id": str(result.inserted_id)
    }


@router.put("/{reservation_id}")
async def update_reservation_status(
    reservation_id: str,
    status: str
):
    allowed_statuses = {"approved", "rejected", "pending"}
    if status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Nevalidan status rezervacije")

    try:
        obj_id = ObjectId(reservation_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Neispravan ID rezervacije")

    reservation = await reservations_collection.find_one({"_id": obj_id})
    if not reservation:
        raise HTTPException(status_code=404, detail="Rezervacija nije pronađena")

    if status == "approved":
        existing = await reservations_collection.find_one({
            "date": reservation["date"],
            "seat_number": reservation["seat_number"],
            "status": "approved",
            "_id": {"$ne": obj_id}
        })
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Već postoji odobrena rezervacija za to mesto i datum"
            )

    try:
        result = await reservations_collection.update_one(
            {"_id": obj_id},
            {"$set": {"status": status}}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri ažuriranju rezervacije: {str(e)}")

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Rezervacija nije pronađena (tokom ažuriranja)")

    return {"message": f"Rezervacija je uspešno ažurirana sa statusom {status}"}