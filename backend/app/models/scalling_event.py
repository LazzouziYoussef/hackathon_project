# backend/app/models/scaling_event.py
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from backend.app.core.database import Base
import uuid

class ScalingEvent(Base):
    __tablename__ = "scaling_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(50), nullable=False)
    current_replicas = Column(Integer, nullable=False)
    recommended_replicas = Column(Integer, nullable=False)
    cost_impact_usd = Column(Float)
    confidence = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    reason = Column(Text, nullable=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    executed_at = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)