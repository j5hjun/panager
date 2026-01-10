from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from google_auth_oauthlib.flow import Flow

from app.core.config import settings
from app.db.models import User, GoogleCredentials
from app.core.security import encrypt_token


class AuthService:
    SCOPES = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events",
    ]

    def _get_flow(self, state: str = None) -> Flow:
        """
        Create a Google OAuth Flow instance from client config.
        """
        client_config = {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
            }
        }

        flow = Flow.from_client_config(
            client_config=client_config, scopes=self.SCOPES, state=state
        )
        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
        return flow

    def get_authorization_url(self, slack_user_id: str) -> tuple[str, str]:
        """
        Generate the authorization URL for the user.
        """
        flow = self._get_flow(state=slack_user_id)
        authorization_url, state = flow.authorization_url(
            access_type="offline", include_granted_scopes="true", prompt="consent"
        )
        return authorization_url, state

    def exchange_code(self, code: str) -> dict[str, Any]:
        """
        Exchange the auth code for credentials (tokens).
        """
        flow = self._get_flow()
        flow.fetch_token(code=code)

        credentials = flow.credentials

        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
            "expiry": credentials.expiry,
        }


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_slack_id(self, slack_id: str) -> User | None:
        stmt = select(User).where(User.slack_id == slack_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_or_update_user(self, slack_id: str, email: str = None) -> User:
        user = await self.get_user_by_slack_id(slack_id)
        if not user:
            user = User(slack_id=slack_id, email=email)
            self.session.add(user)
        else:
            if email:
                user.email = email
        return user

    async def save_credentials(
        self, slack_id: str, token_data: dict[str, Any]
    ) -> GoogleCredentials:
        # First ensure user exists (though typically called after create_user)
        _ = await self.create_or_update_user(slack_id)

        # Encrypt refresh token
        refresh_token = token_data.get("refresh_token")
        encrypted_refresh_token = (
            encrypt_token(refresh_token) if refresh_token else None
        )

        # Check if credentials exist
        # Assuming 1:1 for MVP, but model has 1:Many. Let's just append new one or update latest.
        # For MVP simple logic: Create new entry or replace?
        # Let's delete old ones or just add new one.
        # Better: Check if one exists for this user and update it.

        stmt = select(GoogleCredentials).where(GoogleCredentials.user_id == slack_id)
        result = await self.session.execute(stmt)
        creds = result.scalars().first()

        if not creds:
            creds = GoogleCredentials(user_id=slack_id)
            self.session.add(creds)

        creds.access_token = token_data["access_token"]
        if encrypted_refresh_token:
            creds.refresh_token = encrypted_refresh_token

        # expiry might be datetime or None
        if token_data.get("expiry"):
            creds.expires_at = token_data["expiry"]

        return creds
