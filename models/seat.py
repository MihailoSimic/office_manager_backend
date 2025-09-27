from pydantic import BaseModel

class Seat(BaseModel):
    seat_number: int
    row: int
    col: int