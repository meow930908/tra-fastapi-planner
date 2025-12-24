from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
from pathlib import Path

from app.schemas import TripRequest, TripResponse, TripOption, Segment

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def load_json(filename: str):
    path = DATA_DIR / filename
    return json.loads(path.read_text(encoding="utf-8"))

app = FastAPI(title="TRA Fastest Trip API")

# ✅ 前後端分離必備：先允許前端跨網域呼叫（開發期用 * 最省事）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 之後可改成你的前端網址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello, FastAPI"}

@app.get("/api/stations")
def stations():
    return load_json("stations.json")

@app.post("/api/plan-trip", response_model=TripResponse)
def plan_trip(req: TripRequest):
    trains = load_json("timetable.json")

    # 1) 起迄站 + seat_type 過濾
    candidates = [
        t for t in trains
        if t["origin"] == req.origin
        and t["destination"] == req.destination
        and t["seat_type"] == req.seat_type
    ]
    if not candidates:
        raise HTTPException(status_code=404, detail="找不到符合條件的班次（離線資料）")

    # 2) 出發時間 >= 使用者輸入時間
    date_str = req.date.isoformat()
    min_dt = datetime.fromisoformat(f"{date_str}T{req.time.strftime('%H:%M')}")

    def to_dt(hhmm: str):
        return datetime.fromisoformat(f"{date_str}T{hhmm}")

    candidates = [t for t in candidates if to_dt(t["dep"]) >= min_dt]
    if not candidates:
        raise HTTPException(status_code=404, detail="該時間之後沒有班次（離線資料）")

    # 3) 依到達時間最早排序（最早到 = 最快）
    candidates.sort(key=lambda t: t["arr"])

    def minutes(dep: str, arr: str) -> int:
        return int((to_dt(arr) - to_dt(dep)).total_seconds() // 60)

    def to_option(t):
        seg = Segment(
            train_no=t["train_no"],
            origin=t["origin"],
            destination=t["destination"],
            departure_time=t["dep"],
            arrival_time=t["arr"],
            fare=t.get("fare"),
        )
        return TripOption(
            departure_time=t["dep"],
            arrival_time=t["arr"],
            total_minutes=minutes(t["dep"], t["arr"]),
            seat_type=t["seat_type"],
            segments=[seg],
        )

    best = to_option(candidates[0])
    alts = [to_option(x) for x in candidates[1:3]]
    return TripResponse(best_option=best, alternatives=alts)
