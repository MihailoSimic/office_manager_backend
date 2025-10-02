from fastapi import APIRouter, HTTPException, Cookie, Depends, Response
from db import reservations_collection
from models.reservation import Reservation
from auth import verify_token, require_and_refresh_token
from bson import ObjectId
from auth import create_access_token
from datetime import datetime, date
router = APIRouter(prefix="/reservation", tags=["reservation"])

async def get_current_user(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Token nedostaje")
    username = verify_token(access_token)
    if not username:
        raise HTTPException(status_code=401, detail="Neispravan ili istekao token")
    return username

@router.get("/")
async def get_reservations(response: Response, access_token: str = Cookie(None)):
    try:
        require_and_refresh_token(response, access_token)
        reservations = await reservations_collection.find({}).to_list(length=1000)
        for r in reservations:
            r["_id"] = str(r["_id"])
        return reservations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvatanju rezervacija: {str(e)}")
@router.get("/my")
async def get_my_reservations(
    response: Response,
    access_token: str = Cookie(None),
    current_user: str = Depends(get_current_user)
):
    try:
        require_and_refresh_token(response, access_token)
        reservations = await reservations_collection.find({"username": current_user}).to_list(length=1000)
        for r in reservations:
            r["_id"] = str(r["_id"])
        return reservations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvatanju rezervacija korisnika: {str(e)}")

@router.post("/create")
async def create_reservation(
    response: Response,
    reservation: Reservation,
    access_token: str = Cookie(None),
    current_user: str = Depends(get_current_user)
):
    try:
        require_and_refresh_token(response, access_token)
        reservation.username = current_user

        try:
            res_date = datetime.strptime(reservation.date, "%Y-%m-%d").date()
        except Exception:
            raise HTTPException(status_code=400, detail="Neispravan format datuma. Očekivan format je YYYY-MM-DD.")
        if res_date < date.today():
            raise HTTPException(status_code=400, detail="Nije moguće napraviti rezervaciju za datum u prošlosti.")

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

        result = await reservations_collection.insert_one(reservation.dict())
        return {
            "message": f"Mesto {reservation.seat_number} rezervisano za {reservation.date}",
            "id": str(result.inserted_id)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri kreiranju rezervacije: {str(e)}")


@router.put("/{reservation_id}")
async def update_reservation_status(
    response: Response,
    reservation_id: str,
    status: str,
    access_token: str = Cookie(None)
):
    try:
        require_and_refresh_token(response, access_token)
        allowed_statuses = {"approved", "rejected", "pending"}
        if status not in allowed_statuses:
            raise HTTPException(status_code=400, detail="Nevalidan status rezervacije")

        if not ObjectId.is_valid(reservation_id):
            raise HTTPException(status_code=400, detail="Neispravan ID rezervacije")
        obj_id = ObjectId(reservation_id)

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

        result = await reservations_collection.update_one(
            {"_id": obj_id},
            {"$set": {"status": status}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Rezervacija nije pronađena (tokom ažuriranja)")

        return {"message": f"Rezervacija je uspešno ažurirana sa statusom {status}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri ažuriranju rezervacije: {str(e)}")

@router.delete("/{reservation_id}")
async def delete_reservation(
    reservation_id: str,
    response: Response,
    current_user: str = Depends(get_current_user),
    access_token: str = Cookie(None)
):
    require_and_refresh_token(response, access_token)
    try:
        obj_id = ObjectId(reservation_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Neispravan ID rezervacije")

    reservation = await reservations_collection.find_one({"_id": obj_id})
    if not reservation:
        raise HTTPException(status_code=404, detail="Rezervacija nije pronađena")

    if reservation.get("username") != current_user:
        if current_user != "admin":
            raise HTTPException(status_code=403, detail="Nemate pravo da obrišete ovu rezervaciju")

    try:
        result = await reservations_collection.delete_one({"_id": obj_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri otkazivanju rezervacije: {str(e)}")

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Rezervacija nije pronađena (tokom otkazivanja)")

    return {"message": "Rezervacija je uspešno obrisana."}