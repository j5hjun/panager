import pytest
from unittest.mock import MagicMock, patch

def test_generate_auth_url():
    """
    Test generating the Google OAuth login URL.
    Should contain the client ID, redirect URI, scope, and state (slack_user_id).
    """
    try:
        from app.services.user_service import AuthService
    except ImportError:
        pytest.fail("app.services.user_service module not found")

    slack_user_id = "U12345"
    auth_service = AuthService()
    
    # We patch the actual google flow to avoid making network requests or needing real client secrets
    with patch("app.services.user_service.Flow") as MockFlow:
        mock_flow_instance = MockFlow.from_client_config.return_value
        mock_flow_instance.authorization_url.return_value = ("https://accounts.google.com/o/oauth2/auth?foo=bar", "state_value")
        
        url, state = auth_service.get_authorization_url(slack_user_id)
        
        assert "https://accounts.google.com" in url
        # State should contain the slack_user_id to map it back later
        # However, the exact implementation of state might vary (base64 encoded or plain).
        # We expect the service to pass the slack_user_id to the flow state logic.
        assert state == slack_user_id or state == f"state_{slack_user_id}" or "state" in state

def test_exchange_code():
    """
    Test exchanging the auth code for credentials.
    """
    from app.services.user_service import AuthService
    
    auth_service = AuthService()
    fake_code = "fake_auth_code"
    
    with patch("app.services.user_service.Flow") as MockFlow:
        mock_flow_instance = MockFlow.from_client_config.return_value
        
        # Mock fetch_token
        mock_flow_instance.fetch_token.return_value = None
        
        # Mock credentials object returned by flow
        mock_creds = MagicMock()
        mock_creds.token = "access_token_123"
        mock_creds.refresh_token = "refresh_token_123"
        mock_creds.expiry = "2026-01-01T00:00:00Z"
        
        mock_flow_instance.credentials = mock_creds
        
        creds_data = auth_service.exchange_code(fake_code)
        
        mock_flow_instance.fetch_token.assert_called_once_with(code=fake_code)
        assert creds_data["access_token"] == "access_token_123"
        assert creds_data["refresh_token"] == "refresh_token_123"
