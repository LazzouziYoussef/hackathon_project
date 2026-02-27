from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.app.database import SessionLocal
from typing import AsyncGenerator

async def get_db(tenant_id: str) -> AsyncGenerator[AsyncSession,None]:
    async with SessionLocal() as session:

        await session.execute(text("Set app.current_tenant_id =:tid"),{"tid":tenant_id})

        try:
            yield session   
        finally:
            await session.close()    