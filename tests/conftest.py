import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.config import settings
from app.db.models import Base
from app.db.session import get_db

# DB URL
DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create engine for the session"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    # Init tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Get a new DB session for a test"""
    # Create sessionmaker bound to the engine
    TestingSessionLocal = sessionmaker(
        bind=db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Client with DB override"""
    app.dependency_overrides[get_db] = lambda: session
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    app.dependency_overrides.clear()
