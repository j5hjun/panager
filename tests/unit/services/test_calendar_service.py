from unittest.mock import AsyncMock, Mock, patch
import pytest
from app.services.calendar_service import CalendarService
from app.db.models import GoogleCredentials


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def calendar_service(mock_session):
    return CalendarService(mock_session)


@pytest.mark.asyncio
async def test_watch_events(calendar_service, mock_session):
    """
    Test that watch_events requests Google API to watch resources.
    """
    # given
    slack_id = "U12345"
    mock_creds = Mock(spec=GoogleCredentials)
    mock_creds.access_token = "fake_access_token"
    mock_creds.refresh_token = "fake_refresh_token"

    # Mock UserService resolving credentials
    # We need to mock the internal call or method.
    # CalendarService usually needs access to credentials.
    # Let's assume CalendarService uses UserService or queries directly?
    # In Phase 4, CalendarService was simple. We need to upgrade it.

    # Mocking the session execute to return credentials
    mock_result = Mock()
    mock_result.scalars.return_value.first.return_value = mock_creds
    mock_session.execute.return_value = mock_result

    # Mock google_auth_oauthlib and googleapiclient
    with patch("app.services.calendar_service.build") as mock_build, patch(
        "app.services.calendar_service.decrypt_token"
    ) as mock_decrypt:
        mock_decrypt.return_value = "decrypted_refresh_token"

        mock_service = Mock()
        mock_events = Mock()
        mock_watch = Mock()

        mock_build.return_value = mock_service
        mock_service.events.return_value = mock_events
        mock_events.watch.return_value = mock_watch
        mock_watch.execute.return_value = {
            "kind": "api#channel",
            "id": "new-resource-id",
            "resourceId": "resource-id-from-google",
            "resourceUri": "https://...",
        }

        # when
        result = await calendar_service.watch_events(slack_id)

        # then
        assert result is True
        # Verify watch was called with correct parameters
        mock_events.watch.assert_called()
        call_args = mock_events.watch.call_args[1]
        assert call_args["calendarId"] == "primary"
        assert call_args["body"]["type"] == "web_hook"
        # Verification of public URL is important in prod, but mocked here.
