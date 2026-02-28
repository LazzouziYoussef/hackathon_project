from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel,field_validator
from datetime import datetime
from uuid import UUID
from typing import List
from backend.app.database import SessionLocal
from backend.app.crud.metrices import insert_Metric
from backend.app.api.endpoints.reccomend import get_db_for_tennant

router = APIRouter()

class Metric_item(BaseModel):
    metric_type : str
    value : float
    time : datetime
    tags : dict | None = None

    @field_validator("time")
    @classmethod
    def strip_timezone(cls,v:datetime):
        if v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v   

class Metrics_list(BaseModel):
    metrics : List[Metric_item]

@router.post("/metrics")
async def metric_submit(payload : Metrics_list, tenant_id : UUID, db : AsyncSession = Depends(get_db_for_tennant)):
    if len(payload.metrics) > 1000 :
        return {"error" :"full expand"}
    await insert_Metric(db , tenant_id ,[m.model_dump()  for m in payload.metrics])
    return {"inserted", len([payload.metrics])}

