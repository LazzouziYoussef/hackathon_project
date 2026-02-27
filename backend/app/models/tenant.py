from sqlalchemy import column, String , Boolean, DateTime,PrimaryKeyConstraint,Nullable,UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.app.database import Base
import uuid

class Tenant(Base):
    __tablename__ = "tenants"

    id = column(UUID(as_uuid=True), PrimaryKeyConstraint=True,default= uuid.uuid4)
    name = column(String(255), Nullable=False)
    api_key_hash = column(String(255), Nullable=False, UniqueConstraint=True)
    created_day = column(DateTime)
    is_active = column(Boolean, default=True)

    user = relationship("User",back_populates=tenant)
    metrics = relationship("Metrices",back_populates=tenant)

    