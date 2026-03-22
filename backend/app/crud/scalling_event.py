from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import pandas as pd
from uuid import UUID

async def insert_scaling_event(db: AsyncSession, event: dict):
    query = text("""
        INSERT INTO scaling_events 
            (id, tenant_id, event_type, current_replicas, recommended_replicas,
             confidence, reason, cost_impact_usd, status)
        VALUES 
            (gen_random_uuid(), :tenant_id, :event_type, :current_replicas,
             :recommended_replicas, :confidence, :reason, :cost_impact_usd, 'pending')
        RETURNING id
    """)
    result = await db.execute(query, event)
    await db.commit()
    return result.scalar()       

async def get_scalling_event(db:AsyncSession, tenant_id:UUID ):
    query = text("""
            SELECT * FROM scaling_events where tenant_id = :tenant_id
            ORDER BY created_at DESC
            LIMIT 50  
    """)
    result = await db.execute(query,{"tenant_id": tenant_id})
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]
    