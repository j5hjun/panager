"""Phase 3 RED: NotificationService 테스트"""
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_send_welcome_message():
    """환영 메시지 전송 테스트"""
    from src.application.services.notification_service import NotificationService
    
    # Mock Adapter
    mock_messenger = AsyncMock()
    mock_messenger.send_message = AsyncMock(return_value=True)
    
    service = NotificationService(mock_messenger)
    
    success = await service.send_welcome_message(slack_id="U12345", name="Test User")
    
    assert success is True
    # 텍스트 또는 블록 메시지 호출 검증
    # 여기서는 단순화를 위해 send_message 호출 여부 확인 (구현에 따라 수정)
    assert mock_messenger.send_message.called or mock_messenger.send_block_message.called

@pytest.mark.asyncio
async def test_send_event_reminder():
    """일정 리마인더 전송 테스트"""
    from src.application.services.notification_service import NotificationService
    from src.domain.models.event import CalendarEvent
    from datetime import datetime, timezone
    
    mock_messenger = AsyncMock()
    mock_messenger.send_block_message = AsyncMock(return_value=True)
    
    service = NotificationService(mock_messenger)
    
    event = CalendarEvent(
        id="evt_1",
        summary="Meeting",
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc)
    )
    
    success = await service.send_event_reminder(slack_id="U12345", event=event)
    
    assert success is True
    mock_messenger.send_block_message.assert_called_once()
    args = mock_messenger.send_block_message.call_args
    # call_args could be positional or keyword
    if 'user_id' in args.kwargs:
        assert args.kwargs['user_id'] == "U12345"
    else:
        assert args.args[0] == "U12345"
