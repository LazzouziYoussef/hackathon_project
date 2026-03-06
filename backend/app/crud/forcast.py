from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from backend.app.models.forcasts import Forecast
from datetime import datetime
from uuid import UUID


async def insert_forecast(db: AsyncSession, tenant_id: UUID, forecasts: list):
    if not forecasts:
        return
    
    for f in forecasts:
        
        forecast_time = f["forecast_time"]
        if hasattr(forecast_time, 'tzinfo') and forecast_time.tzinfo is not None:
            forecast_time = forecast_time.replace(tzinfo=None)

        forecast = Forecast(
            tenant_id=tenant_id,
            forecast_time=forecast_time,
            metric_type=f["metric_type"],
            predicted_value=f["predicted_value"],
            confidence=f["confidence"],
            model_version=f.get("model_version", "v1.0")
        )
        db.add(forecast)
    await db.commit()


async def get_forecasts(db: AsyncSession, tenant_id: UUID):
    result = await db.execute(
        select(Forecast)
        .where(Forecast.tenant_id == tenant_id)
        .order_by(Forecast.forecast_time.asc())
    )
    return result.scalars().all()


async def get_upcoming_forecasts(db: AsyncSession, tenant_id: UUID):
    result = await db.execute(
        select(Forecast)
        .where(
            Forecast.tenant_id == tenant_id,
        )
        .order_by(Forecast.forecast_time.asc())
    )
    rows = result.scalars().all()

    return [
        {
            "id": str(row.id),
            "tenant_id": str(row.tenant_id),
            "forecast_time": row.forecast_time.isoformat(),
            "metric_type": row.metric_type,
            "predicted_value": row.predicted_value,
            "confidence": row.confidence,
            "model_version": row.model_version,
            "created_at": row.created_at.isoformat() if row.created_at else None
        }
        for row in rows
    ]


async def delete_old_forecasts(db: AsyncSession, tenant_id: UUID):
    await db.execute(
        delete(Forecast)
        .where(
            Forecast.tenant_id == tenant_id,
            Forecast.forecast_time < datetime.utcnow()
        )
    )
    await db.commit()