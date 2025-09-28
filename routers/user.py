from fastapi import APIRouter, HTTPException, Cookie, Response
from db import users_collection
from models.user import User
from auth import create_access_token, verify_token

router = APIRouter(prefix="/user", tags=["user"])

# ========================
# Helper funkcija za uklanjanje lozinke i _id konverziju
# ========================
def user_without_password(user_dict):
    user_copy = user_dict.copy()
    user_copy.pop("password", None)
    if "_id" in user_copy:
        user_copy["_id"] = str(user_copy["_id"])
    return user_copy

# ========================
# Registracija korisnika
# ========================
@router.post("/register")
async def register(user: User):
    existing_user = await users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Korisnik već postoji")
    
    await users_collection.insert_one(user.dict())
    user_data = user_without_password(user.dict())
    return {"message": "Korisnik uspešno registrovan", "user": user_data}

# ========================
# Login sa JWT tokenom u HttpOnly cookie
# ========================
@router.post("/login")
async def login(data: User, response: Response):
    user_in_db = await users_collection.find_one({"username": data.username})
    if user_in_db and user_in_db["password"] == data.password:
        token = create_access_token({"sub": user_in_db["username"]})
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            samesite="strict"
        )
        user_data = user_without_password(user_in_db)
        return {"user": user_data}
    
    raise HTTPException(status_code=401, detail="Neispravno korisničko ime ili lozinka")

@router.get("")
async def get_users(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Token nedostaje")
    
    username = verify_token(access_token)
    if not username:
        raise HTTPException(status_code=401, detail="Neispravan ili istekao token")
    users = []
    async for user in users_collection.find():
        users.append(user_without_password(user))
    return {"users": users}

# ========================
# Dohvat informacija o korisniku (zaštićena ruta)
# ========================
@router.get("/me")
async def me(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Token nedostaje")
    
    username = verify_token(access_token)
    if not username:
        raise HTTPException(status_code=401, detail="Neispravan ili istekao token")

    user_in_db = await users_collection.find_one({"username": username})
    if not user_in_db:
        raise HTTPException(status_code=404, detail="Korisnik ne postoji")
    
    user_data = user_without_password(user_in_db)
    return {"user": user_data}

# ========================
# Logout (uklanjanje cookie)
# ========================
@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Uspešno ste se odjavili"}