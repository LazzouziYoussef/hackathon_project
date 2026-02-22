from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from backend.app.api.v1.endpoints import forecast
from backend.app.api import routes
app = FastAPI(title="Sadaqa Tech Backend")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], 
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
app.include_router(routes.router, prefix="/api")
# Root route for health check
@app.get("/")
def read_root():
    return {"status": "Sadaqa Tech Watchman Active", "mode": "Decision Support"}

