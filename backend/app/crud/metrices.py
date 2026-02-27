from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import pandas as pd

async def get_metrices_as_df( db: AsyncSession,
    tenant_id: str,
    metric_type: str,
    start: str,
    end: str) -> pd.DataFrame:

    query = text(""" 
            SELECT time,value
            FROM metrics
            WHERE tenant_id = :tenant_id
            AND metric_type = :metric_type
            AND time BETWEEN :start AND :end
            ORDER BY time ASC    
         """)

    result = await db.execute(query,{
       "tenant_id": tenant_id,
        "metric_type": metric_type,
        "start": datetime.strptime(start,"%Y-%m-%d"),
        "end": datetime.strptime(end,"%Y-%m-%d")
        })

    rows = result.fetchall()
    df = pd.DataFrame(rows,columns=["time","value"])

    df["time"] = pd.to_datetime(df["time"])
    df["time"] = df["time"].dt.tz_localize(None)
    df = df.set_index("time")
    df.index = pd.DatetimeIndex(df.index)

    return df


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