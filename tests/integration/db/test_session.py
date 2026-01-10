import pytest
from sqlalchemy import text
from app.db.session import get_db


@pytest.mark.asyncio
async def test_database_connection():
    """
    Test that the async database session can connect and execute a query.
    This test verifies:
    1. app.db.session module exists (Verification of Task 2.3 structure)
    2. get_db works as an async generator
    3. The session can execute a real SQL query against the database
    """
    try:
        async for session in get_db():
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
            break  # We only need one session from the generator
    except ImportError:
        pytest.fail("app.db.session or get_db not found")
    except Exception as e:
        pytest.fail(f"Database connection failed: {str(e)}")
