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
<<<<<<< HEAD
<<<<<<< HEAD
from backend.app.api.endpoints import reccomend,metrics,predictions
import backend.app.models
=======
from backend.app.api.endpoints import reccomend,metrics
>>>>>>> origin/FrontEndZaid
=======
from backend.app.api.endpoints import reccomend,metrics,predictions
import backend.app.models
>>>>>>> 9cf69d5f1e4ccdbfee7f17db2f02c18605d1b063


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    print("app starting!!")
    
    yield

    await engine.dispose()


app = FastAPI(
    title="Ramadan Traffic Predictor",
    description="ML-powered scaling recommendations for Ramadan traffic surges",
    version="1.0.0",
    lifespan=lifespan
)
 
app.include_router(reccomend.router,prefix="/api/v1",tags=["recommendation"])
app.include_router(metrics.router,prefix="/api/v1",tags=["insert_metric"])
<<<<<<< HEAD
<<<<<<< HEAD
app.include_router(predictions.router,prefix="/api/v1",tags=["predictions"])
=======

>>>>>>> origin/FrontEndZaid
=======
app.include_router(predictions.router,prefix="/api/v1",tags=["predictions"])
>>>>>>> 9cf69d5f1e4ccdbfee7f17db2f02c18605d1b063
