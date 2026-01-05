# tra-fastapi-planner

本專題為「**台鐵最快到達路線規劃系統**」，使用 **FastAPI + Dijkstra 演算法**，  
根據使用者輸入的出發時間、起點與終點，計算 **最早可到達的搭車路徑**。

本系統為前後端分離架構，後端專注於路線計算與 API 服務，前端僅需透過 REST API 即可取得結果。

## 功能

- 使用真實台鐵時刻資料（手動抓，TDX 目前使用上有困難）
- 依出發時間計算「最早到達」路線
- 支援多次轉乘
- 支援對號 / 非對號座位分類（目前只有非對號，因為手抓太累）
- FastAPI + Swagger API 文件
- 演算法與 API 分離（易於維護＆擴充）

---

## 系統架構

```
Frontend (Web / App)
        │
        ▼
 FastAPI Backend
        │
        ├─ Dijkstra 演算法
        │
        └─ 台鐵時刻表資料（JSON）
```

---

## 專案結構

```
tra-fastapi-planner/
├─frontend/
│  ├─ app.js
│  ├─index.html
│  └─styles.css
├─ app/
│  ├─ main.py
│  ├─ schemas.py
│  └─ algorithms/
│     └─ dijkstra.py
├─ data/
│  ├─ timetable_connections_clean_20251223.json
│  └─ stations_clean_20251223.json
├─ README.md
└─ requirements.txt
```
 
## 檔案說明

```
main.py ─ FastAPI 主程式（API 入口）
└─ 收到前端請求
   ├─ 解析輸入（起點/終點/時間/座位類型）
   ├─ 呼叫 dijkstra.py 的演算法計算路線
   └─ 把結果包成 TripResponse 回傳給前端

schemas.py ─ API 資料格式定義（Request/Response 規格）
└─ 用 Pydantic 定義「前端送來的 JSON 長什麼樣」與「後端回傳 JSON 長什麼樣」
   ├─ TripRequest：使用者輸入（date、time、origin、destination、seat_type）
   ├─ TripResponse：回傳（best_option、alternatives）
   ├─ TripOption：一個方案（總時間、到達時間、segments）
   └─ Segment：一段車程（車次、起訖站、出發/到達時間）

dijkstra.py ─ 實現 Dijkstra 演算法
└─ 負責算出最早到達路線

timetable_connections_clean_20251223.json ─ 離線版時刻表資料（演算法的輸入）
└─ 每一筆代表「站 → 站」的一段行程
   └─ train_no / origin / destination / dep / arr / seat_type / train_type

stations_clean_20251223.json - 車站的資料（西部）

requirements.txt ─ Python 套件清單

README.md - 專案的使用說明書
```

## API 使用說明

### 啟動後端服務

進入虛擬環境：
```
source .venv/bin/activate
```

啟動 FastAPI Web API 伺服器
```bash
uvicorn app.main:app --reload
```

Swagger API 文件：
```
http://127.0.0.1:8000/docs
```

### POST /api/plan-trip

#### Request Body
```json
{
  "date": "2025-12-23",
  "time": "08:00:00",
  "origin": "基隆",
  "destination": "嘉義",
  "seat_type": "non_reserved"
}
```
