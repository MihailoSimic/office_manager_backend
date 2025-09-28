from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import router-a
from routers import user, reservation, seat

app = FastAPI()

# ========================
# CORS middleware
# ========================
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# Registracija router-a
# ========================
app.include_router(user.router)
app.include_router(reservation.router)
app.include_router(seat.router)

@app.get("/")
async def root():
    return {"message": "Backend radi! FastAPI + MongoDB + router setup"}