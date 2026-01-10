import pytest
from datetime import datetime, timedelta, timezone

from src.domain.models.user import User
from src.domain.models.token import Token
from src.domain.models.event import CalendarEvent

# 구현체 Import (아직 존재하지 않음)
from src.infrastructure.persistence.user_repo import SqlAlchemyUserRepository
from src.infrastructure.persistence.token_repo import SqlAlchemyTokenRepository
from src.infrastructure.persistence.event_repo import SqlAlchemyEventRepository
from src.infrastructure.db import get_db
from sqlalchemy import text

async def cleanup_db():
    # 간단한 Cleanup: 테스트 전후로 데이터 삭제 (TRUNCATE)
    async for session in get_db():
        await session.execute(text("TRUNCATE TABLE users, tokens, events RESTART IDENTITY CASCADE"))
        await session.commit()

@pytest.mark.asyncio
async def test_user_flow():
    await cleanup_db()
    async for session in get_db():
        repo = SqlAlchemyUserRepository(session)
        
        user = User(slack_id="U_TEST_001", name="Tester", is_active=True)
        saved = await repo.save(user)
        
        assert saved.id is not None
        
        found = await repo.get_by_slack_id("U_TEST_001")
        assert found is not None
        assert found.slack_id == "U_TEST_001"

@pytest.mark.asyncio
async def test_token_flow():
    await cleanup_db()
    async for session in get_db():
        # 사전 조건: 유저 존재
        user_repo = SqlAlchemyUserRepository(session)
        user = await user_repo.save(User(slack_id="U_TOKEN_TEST", name="TokenOwner"))
        
        token_repo = SqlAlchemyTokenRepository(session)
        
        now = datetime.now(timezone.utc)
        token = Token(
            user_slack_id=user.slack_id,
            access_token="access_123",
            refresh_token="refresh_123",
            expires_at=now + timedelta(hours=1)
        )
        
        saved_token = await token_repo.save(token)
        assert saved_token is not None
        
        found_token = await token_repo.get_by_user_id(user.slack_id)
        assert found_token is not None
        assert found_token.access_token == "access_123"
        
        await token_repo.delete(user.slack_id)
        found_after_delete = await token_repo.get_by_user_id(user.slack_id)
        assert found_after_delete is None

@pytest.mark.asyncio
async def test_event_flow():
    await cleanup_db()
    async for session in get_db():
        # 사전 조건: 유저 존재
        user_repo = SqlAlchemyUserRepository(session)
        user = await user_repo.save(User(slack_id="U_EVENT_TEST", name="EventOwner"))
        
        event_repo = SqlAlchemyEventRepository(session)
        
        now = datetime.now(timezone.utc)
        event = CalendarEvent(
            id="evt_001",
            summary="Test Event",
            start_time=now + timedelta(minutes=10), # 확실한 미래
            end_time=now + timedelta(hours=1),
            status="confirmed"
        )
        saved_event = await event_repo.save(event, user_id=user.id)
        assert saved_event.id == "evt_001"
        
        # 날짜 범위로 조회
        events = await event_repo.get_by_range(
            slack_id=user.slack_id,
            start=now - timedelta(hours=1),
            end=now + timedelta(hours=2)
        )
        assert len(events) == 1
        assert events[0].summary == "Test Event"
        
        # Upcoming
        upcoming = await event_repo.get_upcoming_events(user.slack_id)
        assert len(upcoming) == 1
