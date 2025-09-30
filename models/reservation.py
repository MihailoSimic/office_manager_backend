from pydantic import BaseModel

class Reservation(BaseModel):
    username: str
    date: str
    seat_number: int
    status: str = "pending"