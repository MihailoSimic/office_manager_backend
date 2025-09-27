# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import router-a
from routers import user
from routers import reservation
from routers import seat

# ========================
# FastAPI app
# ========================
app = FastAPI()

# ========================
# CORS middleware (za React frontend)
# ========================
origins = ["http://localhost:5173"]  # tvoj frontend

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

# ========================
# Test ruta (opciono)
# ========================
@app.get("/")
async def root():
    return {"message": "Backend radi! FastAPI + MongoDB + router setup"}