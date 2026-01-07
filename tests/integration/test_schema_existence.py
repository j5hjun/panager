import pytest
from sqlalchemy import text
from src.infrastructure.db import get_db

@pytest.mark.asyncio
async def test_schema_tables_exist():
    """주요 테이블들이 DB에 존재하는지 확인"""
    required_tables = {"users", "tokens", "events"}
    
    async for session in get_db():
        # Postgres에서 테이블 목록 조회
        result = await session.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        ))
        existing_tables = {row[0] for row in result.fetchall()}
        
        # 모든 필수 테이블이 존재해야 함
        missing = required_tables - existing_tables
        assert not missing, f"Missing tables: {missing}"
