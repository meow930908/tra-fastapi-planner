from fastapi import FastAPI
from app.mock_data import MOCK_STATIONS

app = FastAPI(title="TRA Fastest Trip API")

@app.get("/")
def root():
    return {"message": "Hello, FastAPI"}

@app.get("/api/stations")
def stations():
    return MOCK_STATIONS
