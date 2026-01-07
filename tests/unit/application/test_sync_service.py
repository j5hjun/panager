"""Phase 2 RED: CalendarSyncService 테스트"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta

from src.domain.models.event import CalendarEvent

@pytest.mark.asyncio
async def test_sync_user_calendar_success():
    """캘린더 동기화 성공 케이스"""
    from src.application.services.sync_service import CalendarSyncService
    
    mock_calendar_adapter = AsyncMock()
    mock_event_repo = AsyncMock()
    mock_user_repo = AsyncMock()
    
    # Mock User
    mock_user_repo.get_by_slack_id.return_value = MagicMock(id=1, slack_id="U12345")
    
    # Mock Events from Google
    events = [
        CalendarEvent(
            id="evt_1",
            summary="Meeting",
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc) + timedelta(hours=1),
            status="confirmed"
        )
    ]
    mock_calendar_adapter.get_events.return_value = events
    
    service = CalendarSyncService(mock_calendar_adapter, mock_event_repo, mock_user_repo)
    
    count = await service.sync_user_calendar(slack_id="U12345")
    
    assert count == 1
    mock_calendar_adapter.get_events.assert_called_once()
    mock_event_repo.save.assert_called_once()
    
    # save(event, user_id) 순서임
    saved_event = mock_event_repo.save.call_args[0][0] 
    saved_user_id = mock_event_repo.save.call_args[0][1]
    
    assert saved_event.id == "evt_1"
    assert saved_user_id == 1

@pytest.mark.asyncio
async def test_sync_user_calendar_no_events():
    """이벤트가 없는 경우"""
    from src.application.services.sync_service import CalendarSyncService
    
    mock_calendar_adapter = AsyncMock()
    mock_calendar_adapter.get_events.return_value = []
    mock_event_repo = AsyncMock()
    mock_user_repo = AsyncMock()
    mock_user_repo.get_by_slack_id.return_value = MagicMock(id=1, slack_id="U12345")
    
    service = CalendarSyncService(mock_calendar_adapter, mock_event_repo, mock_user_repo)
    
    count = await service.sync_user_calendar(slack_id="U12345")
    
    assert count == 0
    mock_calendar_adapter.get_events.assert_called_once()
    mock_event_repo.save.assert_not_called()
