import pytest
from unittest.mock import MagicMock, AsyncMock
from app.services.slack_service import SlackService

@pytest.mark.asyncio
async def test_send_message():
    # given
    mock_app = MagicMock()
    mock_app.client.chat_postMessage = AsyncMock(return_value={"ok": True})
    
    service = SlackService(mock_app)
    channel_id = "C12345"
    text = "Hello World"
    
    # when
    await service.send_message(channel_id=channel_id, text=text)

    # then
    mock_app.client.chat_postMessage.assert_awaited_once_with(
        channel=channel_id,
        text=text
    )

@pytest.mark.asyncio
async def test_send_dm():
    # given
    mock_app = MagicMock()
    mock_app.client.chat_postMessage = AsyncMock(return_value={"ok": True})
    
    service = SlackService(mock_app)
    user_id = "U12345"
    text = "Direct Message"
    
    # when
    await service.send_dm(user_id=user_id, text=text)

    # then
    mock_app.client.chat_postMessage.assert_awaited_once_with(
        channel=user_id,
        text=text
    )
