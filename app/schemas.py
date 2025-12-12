from datetime import date, time
from typing import List, Literal
from pydantic import BaseModel

SeatType = Literal["reserved", "non_reserved"]

class TripRequest(BaseModel):
    date: date
    time: time
    origin: str
    destination: str
    seat_type: SeatType

class Segment(BaseModel):
    train_no: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    fare: int | None = None

class TripOption(BaseModel):
    departure_time: str
    arrival_time: str
    total_minutes: int
    seat_type: SeatType
    segments: List[Segment]

class TripResponse(BaseModel):
    best_option: TripOption
    alternatives: List[TripOption] = []
