from fastapi import Response, HTTPException
from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "tajni_kljuc"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None
    
def require_and_refresh_token(response: Response, access_token: str):
    if not access_token:
        raise HTTPException(status_code=401, detail="Token nedostaje")
    username = verify_token(access_token)
    if not username:
        raise HTTPException(status_code=401, detail="Neispravan ili istekao token")
    new_token = create_access_token({"sub": username})
    response.set_cookie(
        key="access_token",
        value=new_token,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/"
    )
    return username
