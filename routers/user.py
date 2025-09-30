
from fastapi import APIRouter, HTTPException, Cookie, Response
from db import users_collection
from models.user import User
from bson import ObjectId
from auth import create_access_token, verify_token
import bcrypt

router = APIRouter(prefix="/user", tags=["user"])

def user_without_id(user_dict):
    user_copy = user_dict.copy()
    if "_id" in user_copy:
        user_copy["_id"] = str(user_copy["_id"])
    return user_copy

@router.get("")
async def get_users(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Token nedostaje")
    
    username = verify_token(access_token)
    if not username:
        raise HTTPException(status_code=401, detail="Neispravan ili istekao token")
    users = []
    async for user in users_collection.find():
        users.append(user_without_id(user))
    return {"users": users}

@router.put("/{user_id}")
async def update_user(user_id: str, updated_user: User, access_token: str = Cookie(None)):
    try:
        if not access_token:
            raise HTTPException(status_code=401, detail="Token nedostaje")
        
        username = verify_token(access_token)
        if not username:
            raise HTTPException(status_code=401, detail="Neispravan ili istekao token")
        
        try:
            oid = ObjectId(user_id)
        except:
            raise HTTPException(status_code=400, detail="Neispravan ID")

        new_data = updated_user.dict(exclude_none=True)
        if "_id" in new_data:
            del new_data["_id"]

        if "password" in new_data and new_data["password"]:
            new_data["password"] = bcrypt.hashpw(new_data["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        result = await users_collection.replace_one(
            {"_id": oid},
            new_data
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=400, detail="Korisnik nije pronađen")

        updated_user_db = await users_collection.find_one({"_id": oid})
        return {
            "message": "Korisnik uspešno ažuriran",
            "user": user_without_id(updated_user_db)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}")
async def delete_user(user_id: str, access_token: str = Cookie(None)):
    try:
        if not access_token:
            raise HTTPException(status_code=401, detail="Token nedostaje")
        
        username = verify_token(access_token)
        if not username:
            raise HTTPException(status_code=401, detail="Neispravan ili istekao token")
        
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Nevažeći ID korisnika")

        result = await users_collection.delete_one({"_id": ObjectId(user_id)})

        if result.deleted_count == 0:
            return {"message": "Korisnik već ne postoji ili je već obrisan"}

        return {"message": "Korisnik uspešno obrisan"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register")
async def register(user: User, response: Response):
    existing_user = await users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Korisnik već postoji")

    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    user_dict = user.dict()
    user_dict["password"] = hashed_password.decode('utf-8')

    await users_collection.insert_one(user_dict)
    user_data = user_without_id(user_dict)

    token = create_access_token({"sub": user.username})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/"
    )
    return {"message": "Korisnik uspešno registrovan", "user": user_data}

@router.post("/login")
async def login(data: User, response: Response):
    user_in_db = await users_collection.find_one({"username": data.username})
    if user_in_db:
        hashed_pw = user_in_db.get("password", "")
        if bcrypt.checkpw(data.password.encode('utf-8'), hashed_pw.encode('utf-8')):
            token = create_access_token({"sub": user_in_db["username"]})
            response.set_cookie(
                key="access_token",
                value=token,
                httponly=True,
                samesite="lax",
                secure=False,
                path="/"
            )
            return {"user": user_without_id(user_in_db)}
    raise HTTPException(status_code=401, detail="Neispravno korisničko ime ili lozinka")

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        samesite="lax",
        secure=False
    )
    return {"message": "Uspešno ste se odjavili"}
    
@router.get("/checkToken")
async def check_token(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Token nedostaje")

    username = verify_token(access_token)
    if not username:
        raise HTTPException(status_code=401, detail="Neispravan ili istekao token")

    user = await users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=401, detail="Korisnik ne postoji")

    return {
        "message": "Token je validan",
        "username": username,
        "role": user.get("role", "user")
    }