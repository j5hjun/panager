import pytest
from unittest.mock import MagicMock, patch

def test_send_message():
    """
    Test sending a message via SlackService.
    Should call the underlying Slack client's chat_postMessage.
    """
    try:
        from app.services.slack_service import SlackService
    except ImportError:
        pytest.fail("app.services.slack_service module not found")

    mock_app = MagicMock()
    service = SlackService(app=mock_app)
    
    channel_id = "C12345"
    text = "Hello, World!"
    
    service.send_message(channel_id=channel_id, text=text)
    
    # Check if chat_postMessage was called with correct arguments
    mock_app.client.chat_postMessage.assert_called_once_with(
        channel=channel_id,
        text=text
    )

def test_send_dm():
    """
    Test helper method for sending DM.
    """
    from app.services.slack_service import SlackService
    
    mock_app = MagicMock()
    service = SlackService(app=mock_app)
    
    user_id = "U12345"
    text = "Direct Message"
    
    service.send_dm(user_id=user_id, text=text)
    
    mock_app.client.chat_postMessage.assert_called_once_with(
        channel=user_id, # In Slack, channel_id can be user_id for DM
        text=text
    )
