# backend/app/models/metrics.py
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from backend.app.core.database import Base

class Metrices(Base):
    __tablename__ = "metrics"

    time = Column(DateTime, primary_key=True, nullable=False)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    metric_type = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    tags = Column(JSONB)
    created_at = Column(DateTime)