from backend.app.api.endpoints.reccomend import get_db_for_tennant
from backend.app.crud.forcast import get_upcoming_forecasts
from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID


router = APIRouter()

@router.get("/predictions/{tennant_id}")
async def get_predictions(tennant_id : UUID, db : AsyncSession = Depends(get_db_for_tennant)):
    forecasts = await get_upcoming_forecasts(db,tennant_id)
    return {"tennant_id": tennant_id, "preddictions":forecasts}    