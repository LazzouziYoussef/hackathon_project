# from fastapi import APIRouter
# import numpy as np
# import pandas as pd
# from datetime import datetime
# from backend.app.services.ml_services import MLservice
# from backend.app.api.core.engine import brain

# router = APIRouter()

# ml_services = MLservice()

# @router.get("/patten-summary")
# def get_pattern_summary():
#     return ml_services.get_pattern()

# @router.get("/day_factor")
# def get_day_factor():
#     factor = ml_services.get_day_adjustement()
#     return {"ramadan_day": day, "adjustement_factor" : factor}

# @router.get("/predict")
# def get_prediction(dt :datetime):
#     prediction = ml_services.predict(dt)
#     return {"datetime": dt, "predicted_trafic": prediction}

# @router.get("/recommand/{tenant_id}")
# async def get_recommandtion(tenant_id:str):
#     data = await brain.sync_and_predict(tenant_id)
    
#     return {"tenant_id": tenant_id, "recommendation": data}
