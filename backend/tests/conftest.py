import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.config import settings
from app.database import Base, get_db

DATABASE_URL = settings.DATABASE_URL


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the event loop for the session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_engine():
    engine = create_async_engine(DATABASE_URL, echo=False, future=True)
    # create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
async def async_session_factory(async_engine):
    return async_sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture(scope="function")
async def db_session(async_session_factory):
    """Return an async DB session, rollback changes after test."""
    async with async_session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="module")
def client(async_engine):
    """
    Create TestClient and override get_db dependency to use the test async session.
    Because TestClient runs in a separate thread, we provide a sync wrapper that yields
    an AsyncSession via dependency that creates a new async session per-request.
    """
    from app.database import get_db as real_get_db
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.database import engine as real_engine

    # override get_db to use our async_engine sessions
    async def override_get_db():
        async_session_maker = async_sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c
