from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json

from app.schemas import TripRequest, TripResponse, TripOption, Segment
from app.algorithms.dijkstra import (
    build_by_origin,
    earliest_arrival_dijkstra,
    compress_segments,
    min_to_hhmm,
)

app = FastAPI(title="TRA Fastest Trip API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "timetable_connections_clean_20251223.json"

if not DATA_PATH.exists():
    raise RuntimeError("找不到 timetable_connections_clean_20251223.json")

CONNECTIONS = json.loads(DATA_PATH.read_text(encoding="utf-8"))

_BY_ORIGIN_CACHE = {}

def get_index(seat_type: str):
    if seat_type not in _BY_ORIGIN_CACHE:
        _BY_ORIGIN_CACHE[seat_type] = build_by_origin(CONNECTIONS, seat_type)
    return _BY_ORIGIN_CACHE[seat_type]

@app.post("/api/plan-trip", response_model=TripResponse)
def plan_trip(req: TripRequest):
    start_min = req.time.hour * 60 + req.time.minute
    by_origin = get_index(req.seat_type)

    arr_min, path = earliest_arrival_dijkstra(
        by_origin,
        req.origin,
        req.destination,
        start_min,
        transfer_buffer_min=8,
    )

    if arr_min is None:
        raise HTTPException(status_code=404, detail="找不到可到達路徑")

    merged = compress_segments(path)

    segments = [
        Segment(
            train_no=s["train_no"],
            origin=s["origin"],
            destination=s["destination"],
            departure_time=s["dep"],
            arrival_time=s["arr"],
            fare=s.get("fare"),
        )
        for s in merged
    ]

    best = TripOption(
        departure_time=min_to_hhmm(start_min),
        arrival_time=min_to_hhmm(arr_min),
        total_minutes=arr_min - start_min,
        seat_type=req.seat_type,
        segments=segments,
    )

    return TripResponse(best_option=best, alternatives=[])
