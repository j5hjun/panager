"""Phase 3 RED: Slack Adapter 테스트"""
import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_slack_adapter_implements_port():
    """SlackAdapter가 MessengerPort를 구현하는지 확인"""
    from src.infrastructure.slack.slack_adapter import SlackAdapter
    from src.domain.ports.messenger_port import MessengerPort
    
    assert issubclass(SlackAdapter, MessengerPort)


@pytest.mark.asyncio
async def test_send_message_calls_slack_api():
    """send_message가 Slack API를 호출하는지 확인"""
    from src.infrastructure.slack.slack_adapter import SlackAdapter
    
    with patch('src.infrastructure.slack.slack_adapter.AsyncWebClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.chat_postMessage = AsyncMock(return_value={'ok': True})
        mock_client_class.return_value = mock_client
        
        adapter = SlackAdapter(bot_token="xoxb-test-token")
        result = await adapter.send_message(user_id="U12345", text="Hello!")
        
        assert result is True
        mock_client.chat_postMessage.assert_called_once()
