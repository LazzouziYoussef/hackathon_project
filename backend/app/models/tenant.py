from sqlalchemy import Column, String , Boolean, DateTime,PrimaryKeyConstraint,Nullable,UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.app.database import Base
import uuid

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), PrimaryKeyConstraint=True,default= uuid.uuid4)
    name = Column(String(255), Nullable=False)
    api_key_hash = Column(String(255), Nullable=False, UniqueConstraint=True)
    created_day = Column(DateTime)
    is_active = Column(Boolean, default=True)

    user = relationship("User",back_populates=tenant)
    metrics = relationship("Metrices",back_populates=tenant)
    forcats = relationship("Forcasts",back_populates=tenant)

    