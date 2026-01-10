import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_redirect(client: AsyncClient):
    """
    Test GET /api/v1/auth/google/login
    Should redirect to Google OAuth URL.
    """
    response = await client.get(
        "/api/v1/auth/google/login", params={"slack_user_id": "U12345"}
    )

    # Needs to be implemented
    # 307 Temporary Redirect is common for FastAPI redirects, or 302
    assert response.status_code in [302, 307]

    location = response.headers["location"]
    assert "accounts.google.com" in location
    assert "client_id=" in location
    assert "redirect_uri=" in location
    assert "state=U12345" in location


@pytest.mark.asyncio
async def test_auth_callback(client: AsyncClient):
    """
    Test GET /api/v1/auth/google/callback
    Should exchange code and redirect to success page/message (or return 200 JSON).
    """
    # We mock the service layer in the actual implementation test,
    # but for integration test RED phase, we just assert the endpoint exists.
    # Since we can't easily mock the google callback seamlessly in integration without some work,
    # we expect 500 or 400 if code is invalid, NOT 404.

    response = await client.get(
        "/api/v1/auth/google/callback", params={"code": "fake_code", "state": "U12345"}
    )
    assert response.status_code != 404
