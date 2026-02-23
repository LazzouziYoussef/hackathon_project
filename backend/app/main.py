# from fastapi import FastAPI
# # from fastapi.middleware.cors import CORSMiddleware
# # from backend.app.api.v1.endpoints import forecast
# from backend.app.api import routes
# app = FastAPI(title="Sadaqa Tech Backend")

# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"], 
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )
# app.include_router(routes.router, prefix="/api")
# # Root route for health check
# @app.get("/")
# def read_root():
#     return {"status": "Sadaqa Tech Watchman Active", "mode": "Decision Support"}

from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.app.database import engine
from backend.app.api.endpoints import reccomend


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    print("app starting!!")
    
    yield

    await engine.dispose()

# ===== APP =====
app = FastAPI(
    title="Ramadan Traffic Predictor",
    description="ML-powered scaling recommendations for Ramadan traffic surges",
    version="1.0.0",
    lifespan=lifespan
)
 
app.include_router(reccomend.router,prefix="/api/recommand",tags=["recommendation"])


