"""
iCloud CalDAV 서비스

iCloud 캘린더 연동을 위한 CalDAV 클라이언트입니다.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

import caldav

logger = logging.getLogger(__name__)

# iCloud CalDAV 서버 URL
ICLOUD_CALDAV_URL = "https://caldav.icloud.com"


class ICloudService:
    """
    iCloud CalDAV 서비스

    iCloud 캘린더에 접근하기 위한 CalDAV 클라이언트입니다.
    """

    def __init__(self, token_repository: Any):
        """
        ICloudService 초기화

        Args:
            token_repository: TokenRepository 인스턴스
        """
        self.token_repository = token_repository

    def validate_credentials(self, username: str, app_password: str) -> bool:
        """
        iCloud 자격증명 검증

        CalDAV 서버에 연결하여 자격증명이 유효한지 확인합니다.

        Args:
            username: Apple ID (이메일)
            app_password: 앱 전용 암호

        Returns:
            자격증명 유효 여부
        """
        try:
            client = caldav.DAVClient(
                url=ICLOUD_CALDAV_URL,
                username=username,
                password=app_password,
            )
            principal = client.principal()
            calendars = principal.calendars()

            logger.info(f"iCloud 연결 성공: {username} ({len(calendars)}개 캘린더)")
            return True

        except Exception as e:
            logger.error(f"iCloud 연결 실패: {username} - {e}")
            return False

    def save_credentials(
        self,
        user_id: str,
        username: str,
        app_password: str,
    ) -> None:
        """
        iCloud 자격증명 저장

        앱 암호를 암호화하여 토큰 저장소에 저장합니다.
        username과 password를 "|" 구분자로 결합하여 저장합니다.

        Args:
            user_id: 사용자 ID
            username: Apple ID
            app_password: 앱 전용 암호
        """
        # username과 password를 결합하여 저장
        combined = f"{username}|{app_password}"
        self.token_repository.save_token(
            user_id=user_id,
            provider="icloud",
            access_token=combined,
            refresh_token=None,
            expires_at=datetime.now() + timedelta(days=365 * 10),
        )
        logger.info(f"iCloud 자격증명 저장: {user_id}")

    def get_credentials(self, user_id: str) -> dict | None:
        """
        저장된 iCloud 자격증명 조회

        Args:
            user_id: 사용자 ID

        Returns:
            자격증명 (username, app_password) 또는 None
        """
        token = self.token_repository.get_token(user_id, "icloud")
        if not token:
            return None

        # "|" 구분자로 분리
        combined = token.get("access_token", "")
        if "|" not in combined:
            return None

        username, app_password = combined.split("|", 1)
        return {
            "username": username,
            "app_password": app_password,
        }

    def list_calendars(self, user_id: str) -> list[str]:
        """
        사용자의 iCloud 캘린더 목록 조회

        Args:
            user_id: 사용자 ID

        Returns:
            캘린더 이름 목록
        """
        creds = self.get_credentials(user_id)
        if not creds:
            logger.warning(f"iCloud 자격증명 없음: {user_id}")
            return []

        try:
            client = caldav.DAVClient(
                url=ICLOUD_CALDAV_URL,
                username=creds["username"],
                password=creds["app_password"],
            )
            principal = client.principal()
            calendars = principal.calendars()

            return [cal.name for cal in calendars]

        except Exception as e:
            logger.error(f"캘린더 목록 조회 실패: {user_id} - {e}")
            return []

    def get_client(self, user_id: str) -> caldav.DAVClient | None:
        """
        CalDAV 클라이언트 생성

        Args:
            user_id: 사용자 ID

        Returns:
            DAVClient 인스턴스 또는 None
        """
        creds = self.get_credentials(user_id)
        if not creds:
            return None

        return caldav.DAVClient(
            url=ICLOUD_CALDAV_URL,
            username=creds["username"],
            password=creds["app_password"],
        )
