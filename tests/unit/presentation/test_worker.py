"""Phase 3 RED: Worker Logic Test"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.mark.asyncio
async def test_worker_handle_dm_login_request():
    """'로그인' 메시지 수신 시 처리 테스트"""
    # Patch get_db
    with patch("src.worker.get_db") as mock_get_db:
        # Mock Session
        mock_session = AsyncMock()
        async def dependency_override():
            yield mock_session
        mock_get_db.side_effect = dependency_override

        from src.worker import handle_slack_event
        
        # Mock Container & Services
        mock_container = MagicMock()
        mock_auth_service = MagicMock()
        
        # auth_service.generate_auth_url
        mock_auth_service.generate_auth_url.return_value = "http://auth.url"
        
        # notification_service.send_message
        mock_noti_service = AsyncMock()
        mock_noti_service.send_message.return_value = True
        
        mock_container.get_auth_service.return_value = mock_auth_service
        mock_container.get_notification_service.return_value = mock_noti_service
        
        # Mock Context
        ctx = {
            'container': mock_container,
            'job_try': 1
        }
        
        # Event Data (DM Message)
        event_data = {
            "type": "message",
            "user": "U12345",
            "text": "로그인 하고 싶어",
            "channel": "D12345"
        }
        
        await handle_slack_event(ctx, event_data)
        
        # 1. Auth Service 호출 확인
        mock_auth_service.generate_auth_url.assert_called_with("U12345")
        
        # 2. Notification Service 호출 확인 (링크 전송)
        mock_noti_service.send_message.assert_called_once()
        args = mock_noti_service.send_message.call_args
        # 텍스트 검증 (키워드/위치 인자 모두 고려)
        sent_text = args.kwargs.get('text') or args.args[1]
        assert "http://auth.url" in sent_text

@pytest.mark.asyncio
async def test_worker_handle_unknown_message():
    """알 수 없는 메시지 처리 테스트"""
    with patch("src.worker.get_db") as mock_get_db:
        mock_session = AsyncMock()
        async def dependency_override():
            yield mock_session
        mock_get_db.side_effect = dependency_override

        from src.worker import handle_slack_event
        
        mock_container = MagicMock()
        mock_noti_service = AsyncMock()
        mock_container.get_notification_service.return_value = mock_noti_service
        
        ctx = {'container': mock_container}
        event_data = {
            "type": "message",
            "user": "U12345",
            "text": "블라블라",
            "channel": "D12345"
        }
        
        await handle_slack_event(ctx, event_data)
        
        # 1. Auth Service 호출 안 함 (container.get_auth_service가 호출되었을 수는 있음)
        
        # 2. Notification Service로 "이해하지 못했습니다" 전송
        mock_noti_service.send_message.assert_called_once()
        args = mock_noti_service.send_message.call_args
        sent_text = args.kwargs.get('text') or args.args[1]
        assert "아직 배우는 중입니다" in sent_text
