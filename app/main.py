from fastapi import FastAPI, HTTPException
from datetime import datetime

from app.mock_data import MOCK_STATIONS, MOCK_TRAINS
from app.schemas import TripRequest, TripResponse, TripOption, Segment

app = FastAPI(title="TRA Fastest Trip API")

# 1) 你原本的測試首頁
@app.get("/")
def root():
    return {"message": "Hello, FastAPI"}

# 2) 車站清單（mock）
@app.get("/api/stations")
def stations():
    return MOCK_STATIONS

# 3) 路線規劃（mock + 最快到）
@app.post("/api/plan-trip", response_model=TripResponse)
def plan_trip(req: TripRequest):
    # A. 先挑出「起點/終點/座位類型」都符合的班次
    candidates = [
        t for t in MOCK_TRAINS
        if t["origin"] == req.origin
        and t["destination"] == req.destination
        and t["seat_type"] == req.seat_type
    ]
    if not candidates:
        raise HTTPException(status_code=404, detail="找不到符合條件的班次（mock）")

    # B. 再挑出「出發時間 >= 使用者輸入時間」的班次
    date_str = req.date.isoformat()                       # 例如 "2025-12-12"
    min_dt = datetime.fromisoformat(f"{date_str}T{req.time.strftime('%H:%M')}")

    def to_dt(hhmm: str):
        # 把 "08:10" 變成 datetime，才能比較大小
        return datetime.fromisoformat(f"{date_str}T{hhmm}")

    candidates = [t for t in candidates if to_dt(t["dep"]) >= min_dt]
    if not candidates:
        raise HTTPException(status_code=404, detail="該時間之後沒有班次（mock）")

    # C. 依「到達時間最早」排序（最早到 = 最快抵達）
    candidates.sort(key=lambda t: t["arr"])

    # D. 把一筆班次資料轉成 API 規格（TripOption）
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
    alts = [to_option(x) for x in candidates[1:3]]   # 取最多兩個備選

    return TripResponse(best_option=best, alternatives=alts)
