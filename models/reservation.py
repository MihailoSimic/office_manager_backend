from pydantic import BaseModel

class Reservation(BaseModel):
    username: str
    date: str  # YYYY-MM-DD
    seat_number: int
    status: str = "pending"  # kasnije može biti approved/rejected