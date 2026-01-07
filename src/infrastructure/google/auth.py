"""Google OAuth 토큰 관리 유틸리티"""
from typing import Optional
from datetime import datetime, timezone
from aiogoogle.auth.creds import UserCreds, ClientCreds

from src.config.settings import Settings
from src.domain.models.token import Token
from src.domain.ports.token_repo import TokenRepository


class GoogleAuthManager:
    """Google OAuth 토큰 관리자"""
    
    def __init__(
        self, 
        token_repo: TokenRepository,
        settings: Optional[Settings] = None
    ):
        self.token_repo = token_repo
        self.settings = settings or Settings()
        self._client_creds = None
    
    @property
    def client_creds(self) -> ClientCreds:
        """Google OAuth Client 자격 증명"""
        if not self._client_creds:
            self._client_creds = ClientCreds(
                client_id=self.settings.google_client_id,
                client_secret=self.settings.google_client_secret,
                scopes=[
                    'https://www.googleapis.com/auth/calendar.readonly',
                    'https://www.googleapis.com/auth/calendar.events',
                ],
                redirect_uri=self.settings.google_redirect_uri
            )
        return self._client_creds

    async def get_user_creds(self, slack_id: str) -> Optional[UserCreds]:
        """
        사용자의 Google OAuth 자격 증명을 조회합니다.
        
        Args:
            slack_id: Slack 사용자 ID
            
        Returns:
            UserCreds 객체 또는 None
        """
        token = await self.token_repo.get_by_user_id(slack_id)
        
        if not token:
            return None
        
        # 토큰 만료 확인
        if token.is_expired():
            # 토큰 갱신 시도
            refreshed = await self.refresh_token(slack_id, token)
            if not refreshed:
                return None
            token = refreshed
        
        return UserCreds(
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            expires_at=token.expires_at.isoformat() if token.expires_at else None
        )

    async def refresh_token(self, slack_id: str, token: Token) -> Optional[Token]:
        """
        만료된 토큰을 갱신합니다.
        
        Args:
            slack_id: Slack 사용자 ID
            token: 현재 토큰
            
        Returns:
            갱신된 Token 또는 None
        """
        if not token.refresh_token:
            return None
        
        try:
            from aiogoogle import Aiogoogle
            
            user_creds = UserCreds(
                access_token=token.access_token,
                refresh_token=token.refresh_token,
                expires_at=token.expires_at.isoformat() if token.expires_at else None
            )
            
            async with Aiogoogle(
                client_creds=self.client_creds,
                user_creds=user_creds
            ) as aiogoogle:
                # 토큰 갱신
                new_creds = await aiogoogle.oauth2.refresh(
                    user_creds=user_creds,
                    client_creds=self.client_creds
                )
                
                # 새 토큰 저장
                new_token = Token(
                    user_slack_id=slack_id,
                    access_token=new_creds.access_token,
                    refresh_token=new_creds.refresh_token or token.refresh_token,
                    expires_at=datetime.fromisoformat(new_creds.expires_at) if new_creds.expires_at else None
                )
                
                await self.token_repo.save(new_token)
                return new_token
                
        except Exception as e:
            print(f"Token refresh failed: {e}")
            return None

    async def save_token_from_auth_response(
        self, 
        slack_id: str, 
        auth_response: dict
    ) -> Token:
        """
        OAuth 인증 응답에서 토큰을 저장합니다.
        
        Args:
            slack_id: Slack 사용자 ID
            auth_response: OAuth 인증 응답
            
        Returns:
            저장된 Token
        """
        expires_at = None
        if 'expires_at' in auth_response:
            expires_at = datetime.fromisoformat(auth_response['expires_at'])
        elif 'expires_in' in auth_response:
            expires_at = datetime.now(timezone.utc) + \
                         __import__('datetime').timedelta(seconds=auth_response['expires_in'])
        
        token = Token(
            user_slack_id=slack_id,
            access_token=auth_response.get('access_token', ''),
            refresh_token=auth_response.get('refresh_token', ''),
            expires_at=expires_at or datetime.now(timezone.utc)
        )
        
        await self.token_repo.save(token)
        return token

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        OAuth 인증 URL을 생성합니다.
        
        Args:
            state: CSRF 방지용 상태 값
            
        Returns:
            인증 URL
        """
        from aiogoogle.auth.utils import create_secret
        
        state = state or create_secret()
        
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": self.settings.google_client_id,
            "redirect_uri": self.settings.google_redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.client_creds.scopes),
            "access_type": "offline",
            "prompt": "consent",
            "state": state
        }
        
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{base_url}?{query}"

    async def exchange_code(self, code: str) -> Optional[dict]:
        """
        인증 코드를 액세스 토큰으로 교환합니다.
        
        Args:
            code: 인증 코드
            
        Returns:
            토큰 정보 Dictionary 또는 None
        """
        try:
            from aiogoogle import Aiogoogle
            
            async with Aiogoogle(client_creds=self.client_creds) as aiogoogle:
                token_response = await aiogoogle.oauth2.build_user_creds(
                    grant=code,
                    client_creds=self.client_creds
                )
                return token_response
        except Exception as e:
            print(f"Token exchange failed: {e}")
            return None
