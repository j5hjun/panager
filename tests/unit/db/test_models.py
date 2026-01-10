import pytest
from datetime import datetime, timezone

def test_user_model_structure():
    """
    Test that the User model exists and has the required fields.
    """
    try:
        from app.db.models import User
        
        # Test instantiation
        user = User(slack_id="U12345", email="test@example.com")
        assert user.slack_id == "U12345"
        assert user.email == "test@example.com"
        
        # created_at should be handled by default or init (if configured)
        # But we'll at least check the attribute exists if we were to verify columns
        # For now, just class existence and basic init is enough for RED
        
    except ImportError:
        pytest.fail("app.db.models.User not found")

def test_google_credentials_model_structure():
    """
    Test that GoogleCredentials model exists and has fields.
    """
    try:
        from app.db.models import GoogleCredentials
        
        creds = GoogleCredentials(
            user_id="U12345",
            access_token="acc_token",
            refresh_token="ref_token",
            expires_at=datetime.now(timezone.utc)
        )
        assert creds.user_id == "U12345"
        assert creds.access_token == "acc_token"
    except ImportError:
        pytest.fail("app.db.models.GoogleCredentials not found")

def test_sync_state_model_structure():
    """
    Test that SyncState model exists and has fields.
    """
    try:
        from app.db.models import SyncState
        
        sync = SyncState(
            user_id="U12345",
            resource_id="res_123",
            sync_token="sync_token_123"
        )
        assert sync.user_id == "U12345"
        assert sync.resource_id == "res_123"
    except ImportError:
        pytest.fail("app.db.models.SyncState not found")
