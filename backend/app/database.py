"""
Подключение к PostgreSQL
"""
import greenlet
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, async_scoped_session
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from app.config import settings

# Создание async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True if settings.ENVIRONMENT == "development" else False,
    future=True
)

# Создание async session factory
async_session = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async_scoped_session = async_scoped_session(
    async_session,
    scopefunc=greenlet.getcurrent,
)

# Base класс для моделей
Base = declarative_base()


# Dependency для получения сессии БД
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения async сессии базы данных
    
    Yields:
        AsyncSession: Async сессия SQLAlchemy
    """
    async with async_scoped_session() as session:
        try:
            yield session
        finally:
            await session.close()
