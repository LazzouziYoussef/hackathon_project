from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.app.database import SessionLocal
from backend.app.services.ml_services import MLservice
from backend.app.crud.scalling_event import get_scalling_event
from uuid import UUID

router = APIRouter()

async def get_db_for_tennant(tenant_id: str):
    async with SessionLocal() as session:
        await session.execute( text(f"SET app.current_tenant_id = '{tenant_id}'"))
        yield session

@router.get("/reccomend/{tenant_id}")
async def get_recommandtion(tenant_id:UUID, db : AsyncSession = Depends(get_db_for_tennant)):
    ml_services = MLservice(db=db)
    data = await ml_services.sync_and_predict(tenant_id)

    history = await get_scalling_event(db,tenant_id)
    print("history ",history)
    print("data:",data)
    return {"tenant_id": tenant_id, "recommendation": data,"history": history}
        
