"""
OAuth 서비스

Google/iCloud OAuth 인증 흐름을 처리합니다.
"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urlencode

import requests

from src.core.auth.token_repository import TokenRepository

logger = logging.getLogger(__name__)


class OAuthService:
    """
    OAuth 인증 서비스

    Google/iCloud OAuth 인증 흐름을 처리합니다.
    """

    # Google OAuth 엔드포인트
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_REVOKE_URL = "https://oauth2.googleapis.com/revoke"

    # 기본 스코프
    DEFAULT_GOOGLE_SCOPES = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events",
    ]

    def __init__(
        self,
        token_repository: TokenRepository,
        google_client_id: str,
        google_client_secret: str,
        redirect_uri: str,
        state_secret: str | None = None,
    ):
        """
        OAuthService 초기화

        Args:
            token_repository: 토큰 저장소
            google_client_id: Google OAuth 클라이언트 ID
            google_client_secret: Google OAuth 클라이언트 시크릿
            redirect_uri: OAuth 콜백 URI
            state_secret: state 암호화 키
        """
        self.token_repository = token_repository
        self.google_client_id = google_client_id
        self.google_client_secret = google_client_secret
        self.redirect_uri = redirect_uri
        self.state_secret = state_secret or secrets.token_hex(16)

        # state 저장소 (user_id -> state 매핑)
        self._pending_states: dict[str, dict] = {}

        logger.info("OAuthService 초기화")

    def generate_auth_url(
        self,
        provider: str,
        user_id: str,
        scopes: list[str] | None = None,
    ) -> tuple[str, str]:
        """
        OAuth 인증 URL 생성

        Args:
            provider: 제공자 (google, icloud)
            user_id: Slack 사용자 ID
            scopes: 요청할 스코프

        Returns:
            (인증 URL, state)
        """
        if provider == "google":
            return self._generate_google_auth_url(user_id, scopes)
        else:
            raise ValueError(f"지원하지 않는 제공자: {provider}")

    def _generate_google_auth_url(
        self,
        user_id: str,
        scopes: list[str] | None = None,
    ) -> tuple[str, str]:
        """Google 인증 URL 생성"""
        # state 생성 (user_id 포함)
        state = self._create_state(user_id, "google")

        # 스코프 설정
        scope_list = scopes or self.DEFAULT_GOOGLE_SCOPES
        scope_str = " ".join(scope_list)

        # URL 파라미터
        params = {
            "client_id": self.google_client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": scope_str,
            "access_type": "offline",  # refresh_token 받기 위해
            "prompt": "consent",  # 항상 동의 화면 표시 (refresh_token 보장)
            "state": state,
        }

        url = f"{self.GOOGLE_AUTH_URL}?{urlencode(params)}"
        return url, state

    def _create_state(self, user_id: str, provider: str) -> str:
        """state 토큰 생성 (user_id 포함)"""
        # 랜덤 토큰 생성
        random_token = secrets.token_urlsafe(16)

        # 데이터 저장
        state_data = {
            "user_id": user_id,
            "provider": provider,
            "created_at": datetime.now().isoformat(),
        }
        self._pending_states[random_token] = state_data

        # state는 단순 랜덤 토큰으로 반환
        return random_token

    def decode_state(self, state: str) -> str | None:
        """
        state에서 user_id 추출

        Args:
            state: state 토큰

        Returns:
            user_id 또는 None
        """
        state_data = self._pending_states.get(state)
        if not state_data:
            return None

        # 5분 이상 된 state는 무효
        created_at = datetime.fromisoformat(state_data["created_at"])
        if datetime.now() - created_at > timedelta(minutes=10):
            del self._pending_states[state]
            return None

        return state_data["user_id"]

    def get_state_data(self, state: str) -> dict | None:
        """state 전체 데이터 조회"""
        return self._pending_states.get(state)

    def exchange_code(
        self,
        provider: str,
        code: str,
        state: str,
    ) -> dict[str, Any]:
        """
        인증 코드를 토큰으로 교환

        Args:
            provider: 제공자
            code: 인증 코드
            state: state 토큰

        Returns:
            토큰 정보
        """
        # state 검증 및 user_id 추출
        state_data = self.get_state_data(state)
        if not state_data:
            raise ValueError("Invalid or expired state")

        user_id = state_data["user_id"]

        if provider == "google":
            result = self._exchange_google_code(code)
        else:
            raise ValueError(f"지원하지 않는 제공자: {provider}")

        # 토큰 저장
        expires_at = None
        if "expires_in" in result:
            expires_at = datetime.now() + timedelta(seconds=result["expires_in"])

        self.token_repository.save_token(
            user_id=user_id,
            provider=provider,
            access_token=result["access_token"],
            refresh_token=result.get("refresh_token"),
            expires_at=expires_at,
        )

        # state 정리
        if state in self._pending_states:
            del self._pending_states[state]

        logger.info(f"토큰 교환 완료: {user_id}/{provider}")
        return result

    def _exchange_google_code(self, code: str) -> dict[str, Any]:
        """Google 인증 코드를 토큰으로 교환"""
        data = {
            "client_id": self.google_client_id,
            "client_secret": self.google_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }

        response = requests.post(self.GOOGLE_TOKEN_URL, data=data)

        if response.status_code != 200:
            logger.error(f"Google 토큰 교환 실패: {response.text}")
            raise RuntimeError(f"토큰 교환 실패: {response.status_code}")

        return response.json()

    def refresh_token(self, user_id: str, provider: str) -> dict[str, Any]:
        """
        토큰 갱신

        Args:
            user_id: 사용자 ID
            provider: 제공자

        Returns:
            새 토큰 정보
        """
        # 기존 토큰 조회
        token = self.token_repository.get_token(user_id, provider)
        if not token:
            raise ValueError(f"토큰 없음: {user_id}/{provider}")

        if not token.get("refresh_token"):
            raise ValueError("refresh_token 없음")

        if provider == "google":
            result = self._refresh_google_token(token["refresh_token"])
        else:
            raise ValueError(f"지원하지 않는 제공자: {provider}")

        # 토큰 업데이트
        expires_at = None
        if "expires_in" in result:
            expires_at = datetime.now() + timedelta(seconds=result["expires_in"])

        self.token_repository.save_token(
            user_id=user_id,
            provider=provider,
            access_token=result["access_token"],
            refresh_token=token["refresh_token"],  # refresh_token은 유지
            expires_at=expires_at,
        )

        logger.info(f"토큰 갱신 완료: {user_id}/{provider}")
        return result

    def _refresh_google_token(self, refresh_token: str) -> dict[str, Any]:
        """Google 토큰 갱신"""
        data = {
            "client_id": self.google_client_id,
            "client_secret": self.google_client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        response = requests.post(self.GOOGLE_TOKEN_URL, data=data)

        if response.status_code != 200:
            logger.error(f"Google 토큰 갱신 실패: {response.text}")
            raise RuntimeError(f"토큰 갱신 실패: {response.status_code}")

        return response.json()

    def revoke_token(self, user_id: str, provider: str) -> bool:
        """
        토큰 해지

        Args:
            user_id: 사용자 ID
            provider: 제공자

        Returns:
            성공 여부
        """
        # 기존 토큰 조회
        token = self.token_repository.get_token(user_id, provider)
        if not token:
            return False

        if provider == "google":
            self._revoke_google_token(token["access_token"])

        # DB에서 삭제
        self.token_repository.delete_token(user_id, provider)

        logger.info(f"토큰 해지 완료: {user_id}/{provider}")
        return True

    def _revoke_google_token(self, access_token: str) -> None:
        """Google 토큰 해지"""
        params = {"token": access_token}
        response = requests.post(self.GOOGLE_REVOKE_URL, params=params)

        if response.status_code not in (200, 204):
            logger.warning(f"Google 토큰 해지 실패 (무시): {response.text}")

    def get_token(self, user_id: str, provider: str) -> dict[str, Any] | None:
        """토큰 조회"""
        return self.token_repository.get_token(user_id, provider)
