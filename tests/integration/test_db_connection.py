import pytest
from sqlalchemy import text
from src.infrastructure.db import get_db

@pytest.mark.asyncio
async def test_database_connection():
    """DB 연결이 정상적으로 이루어지는지 테스트"""
    async for session in get_db():
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1
