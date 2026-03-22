from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import pandas as pd
import json
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

async def insert_Metric(db: AsyncSession, tenant_id, metrics: list):
    query = text("""
        INSERT INTO metrics(time, tenant_id,metric_type,value,tags)
        values(:time,:tenant_id,:metric_type,:value,:tags)
    """)
    for metric in metrics:
        time = metric["time"]
        if hasattr(time,'tzinfo') and time.tzinfo is not None:
            time = time.replace(tzinfo=None)
        tags = metric.get("tags")
        if tags is not None:
            tags = json.dumps(tags)

        await db.execute(query,{
            "time" : time,
            "metric_type" : metric["metric_type"],
            "tenant_id": tenant_id,
            "value" : metric["value"],
            "tags" : tags
        })
    await db.commit()



