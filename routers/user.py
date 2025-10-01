
from fastapi import APIRouter, HTTPException, Cookie, Response
from db import users_collection
from models.user import User
from bson import ObjectId
from auth import create_access_token, verify_token, require_and_refresh_token
import bcrypt
import re

router = APIRouter(prefix="/user", tags=["user"])

def user_without_id(user_dict):
    user_copy = user_dict.copy()
    if "_id" in user_copy:
        user_copy["_id"] = str(user_copy["_id"])
    return user_copy

@router.get("")
async def get_users(response: Response, access_token: str = Cookie(None)):
    require_and_refresh_token(response, access_token)
    try:
        users = []
        async for user in users_collection.find():
            users.append(user_without_id(user))
        return {"users": users}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvatanju korisnika: {str(e)}")

@router.put("/{user_id}")
async def update_user(user_id: str, updated_user: User, response: Response, access_token: str = Cookie(None)):
    try:
        require_and_refresh_token(response, access_token)
        try:
            oid = ObjectId(user_id)
        except:
            raise HTTPException(status_code=400, detail="Neispravan ID")

        new_data = updated_user.dict(exclude_none=True)
        if "_id" in new_data:
            del new_data["_id"]

        if "password" in new_data:
            pw = new_data["password"]
            if pw == "":
                raise HTTPException(status_code=400, detail="Lozinka ne sme biti prazna.")
            if isinstance(pw, str) and pw.startswith("$2"):
                pass
            elif isinstance(pw, str):
                new_data["password"] = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            else:
                del new_data["password"]

        try:
            result = await users_collection.replace_one(
                {"_id": oid},
                new_data
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Greška pri ažuriranju korisnika: {str(e)}")

        if result.matched_count == 0:
            raise HTTPException(status_code=400, detail="Korisnik nije pronađen")

        try:
            updated_user_db = await users_collection.find_one({"_id": oid})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Greška pri dohvatanju ažuriranog korisnika: {str(e)}")
        return {
            "message": "Korisnik uspešno ažuriran",
            "user": user_without_id(updated_user_db)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}")
async def delete_user(user_id: str, response: Response, access_token: str = Cookie(None)):
    try:
        require_and_refresh_token(response, access_token)
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Nevažeći ID korisnika")

        result = await users_collection.delete_one({"_id": ObjectId(user_id)})

        if result.deleted_count == 0:
            return {"message": "Korisnik već ne postoji ili je već obrisan"}

        return {"message": "Korisnik uspešno obrisan"}
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register")
async def register(user: User, response: Response):
    try:
        existing_user = await users_collection.find_one({"username": user.username})
        if existing_user:
            raise HTTPException(status_code=400, detail="Korisnik već postoji")

        password_regex = r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=[\]{};\':"\\|,.<>/?]).{5,}$'
        if not re.match(password_regex, user.password):
            raise HTTPException(status_code=400, detail="Lozinka mora imati bar 5 karaktera, jedno veliko slovo, jedan broj i jedan specijalan znak.")

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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri registraciji: {str(e)}")

@router.post("/login")
async def login(data: User, response: Response):
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri loginu: {str(e)}")

@router.post("/logout")
async def logout(response: Response):
    try:
        response.delete_cookie(
            key="access_token",
            path="/",
            httponly=True,
            samesite="lax",
            secure=False
        )
        return {"message": "Uspešno ste se odjavili"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri odjavi: {str(e)}")
    
@router.get("/checkToken")
async def check_token(response: Response, access_token: str = Cookie(None)):
    try:
        user = await users_collection.find_one({"username": require_and_refresh_token(response,access_token)})
        if not user:
            raise HTTPException(status_code=401, detail="Korisnik ne postoji")

        return {
            "message": "Token je validan",
            "username": user["username"],
            "role": user.get("role", "user")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri proveri tokena: {str(e)}")