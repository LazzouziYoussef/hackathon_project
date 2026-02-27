from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from backend.app.core.config import settings



engine = create_async_engine(settings.DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine,class_=AsyncSession ,expire_on_commit=False)

