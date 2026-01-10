import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_calendar_webhook_valid(client: AsyncClient):
    """
    Test POST /api/v1/webhook/google/calendar
    Valid request from Google.
    """
    headers = {
        "X-Goog-Channel-ID": "test-channel-id",
        "X-Goog-Resource-ID": "test-resource-id",
        "X-Goog-Resource-State": "exists", # or 'sync'
        "X-Goog-Message-Number": "1",
        "X-Goog-Resource-URI": "https://www.googleapis.com/calendar/v3/calendars/..."
    }
    
    # We might need to mock the service that handles the sync to avoid actual processing
    # But for RED phase, we just check routing.
    response = await client.post("/api/v1/webhook/google/calendar", headers=headers)
    
    # Validation logic isn't implemented yet, so if route is missing -> 404
    # If implemented but fails internal logic -> 500
    # We want to eventually see 200 or 202
    assert response.status_code in [200, 202]

@pytest.mark.asyncio
async def test_calendar_webhook_missing_headers(client: AsyncClient):
    """
    Test POST /api/v1/webhook/google/calendar
    Missing required headers should fail.
    """
    response = await client.post("/api/v1/webhook/google/calendar", headers={})
    # Should probably be 400 Bad Request
    assert response.status_code == 400
