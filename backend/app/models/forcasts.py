from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.app.database import Base
from datetime import datetime
import uuid

class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True),  nullable=False)
    forecast_time = Column(DateTime, nullable=False)
    metric_type = Column(String(50), nullable=False)
    predicted_value = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    model_version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    