from fastapi import FastAPI

app = FastAPI(title="TRA Fastest Trip API")

@app.get("/")
def root():
    return {"message": "Hello, FastAPI"}

