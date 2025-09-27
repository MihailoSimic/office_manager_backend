from fastapi import APIRouter, HTTPException
from db import users_collection
from models.user import User  # importujemo jednostavan User model

router = APIRouter(prefix="/user", tags=["user"])

# ========================
# Ruta za registraciju korisnika
# ========================
@router.post("/register")
async def register(user: User):
    existing_user = await users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Korisnik već postoji")
    
    await users_collection.insert_one(user.dict())
    return {"message": "Korisnik uspešno registrovan", "user": user}

# ========================
# Ruta za login
# ========================
@router.post("/login")
async def login(data: User):
    user_in_db = await users_collection.find_one({"username": data.username})
    if user_in_db and user_in_db["password"] == data.password:
        return {"username": user_in_db["username"], "role": user_in_db.get("role", "user")}
    
    raise HTTPException(status_code=401, detail="Neispravno korisničko ime ili lozinka")

# ========================
# Ruta za dohvat informacija o korisniku
# ========================
@router.get("/me")
async def me(username: str):
    user_in_db = await users_collection.find_one({"username": username})
    if not user_in_db:
        raise HTTPException(status_code=404, detail="Korisnik ne postoji")
    return {"username": user_in_db["username"], "role": user_in_db.get("role", "user")}