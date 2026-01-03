from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time

class Segment(BaseModel):
    train_no: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
class TripOption(BaseModel):
    departure_time: str
    arrival_time: str
    total_minutes: int
    seat_type: str
    segments: List[Segment]

class TripRequest(BaseModel):
    date: date
    time: time
    origin: str
    destination: str
    seat_type: str   # "reserved" | "non_reserved"

class TripResponse(BaseModel):
    best_option: TripOption
    alternatives: List[TripOption]
