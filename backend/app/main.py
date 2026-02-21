from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.v1.endpoints import forecast

app = FastAPI(title="Sadaqa Tech Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route for health check
@app.get("/")
def read_root():
    return {"status": "Sadaqa Tech Watchman Active", "mode": "Decision Support"}

app.include_router(forecast.router, prefix="/api/v1")