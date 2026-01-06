"""
사용자 알림 설정

사용자별 알림 설정을 관리합니다.
P-011 Phase 6: SQLite 영속화 (UserProfileRepository 재사용)
"""

import logging
from dataclasses import dataclass
from typing import Any

from src.core.autonomous.memory.user_profile_repository import UserProfileRepository

logger = logging.getLogger(__name__)


@dataclass
class UserAlertSettings:
    """
    사용자별 알림 설정

    각 사용자의 알림 선호도를 저장합니다.
    """

    user_id: str
    channel_id: str = ""  # 알림을 받을 채널 (비어있으면 DM)
    city: str = "Seoul"  # 날씨 조회할 도시
    weather_alert_enabled: bool = True  # 날씨 알림 활성화
    timezone: str = "Asia/Seoul"

    def to_dict(self) -> dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "user_id": self.user_id,
            "channel_id": self.channel_id,
            "city": self.city,
            "weather_alert_enabled": self.weather_alert_enabled,
            "timezone": self.timezone,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserAlertSettings":
        """딕셔너리에서 생성"""
        return cls(
            user_id=data.get("user_id", ""),
            channel_id=data.get("channel_id", ""),
            city=data.get("city", "Seoul"),
            weather_alert_enabled=data.get("weather_alert_enabled", True),
            timezone=data.get("timezone", "Asia/Seoul"),
        )


class UserSettingsManager:
    """
    사용자 설정 관리자

    사용자별 알림 설정을 저장하고 조회합니다.
    P-011: SQLite 기반 영속화 (UserProfileRepository preferences 활용)
    """

    def __init__(
        self,
        default_city: str = "Seoul",
        default_channel: str = "",
        repository: UserProfileRepository | None = None,
        db_path: str = "data/memory.db",
    ):
        """
        UserSettingsManager 초기화

        Args:
            default_city: 기본 도시
            default_channel: 기본 채널 ID
            repository: UserProfileRepository (DI용)
            db_path: DB 경로 (repository가 없을 때 사용)
        """
        self._repository = repository or UserProfileRepository(db_path=db_path)
        self.default_city = default_city
        self.default_channel = default_channel
        self._cache: dict[str, UserAlertSettings] = {}  # DB 조회 캐시

        logger.info(f"UserSettingsManager 초기화 (default_city={default_city})")

    def get_settings(self, user_id: str) -> UserAlertSettings:
        """
        사용자 설정 조회

        Args:
            user_id: 사용자 ID

        Returns:
            사용자 설정 (없으면 기본값으로 생성)
        """
        # 캐시 확인
        if user_id in self._cache:
            return self._cache[user_id]

        # DB에서 조회
        profile = self._repository.get_or_create(user_id)
        preferences = profile.get("preferences", {})

        if preferences:
            settings = UserAlertSettings.from_dict(
                {
                    "user_id": user_id,
                    **preferences,
                }
            )
        else:
            # 기본 설정 생성
            settings = UserAlertSettings(
                user_id=user_id,
                channel_id=self.default_channel,
                city=self.default_city,
            )
            # DB에 저장
            self._save_settings(settings)

        self._cache[user_id] = settings
        return settings

    def _save_settings(self, settings: UserAlertSettings) -> None:
        """설정을 DB에 저장"""
        preferences = settings.to_dict()
        preferences.pop("user_id", None)  # user_id는 별도 컬럼
        self._repository.update_preferences(settings.user_id, preferences)

    def update_settings(self, user_id: str, **kwargs: Any) -> UserAlertSettings:
        """
        사용자 설정 업데이트

        Args:
            user_id: 사용자 ID
            **kwargs: 업데이트할 설정 값들

        Returns:
            업데이트된 설정
        """
        settings = self.get_settings(user_id)

        for key, value in kwargs.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

        # DB에 저장
        self._save_settings(settings)

        # 캐시 갱신
        self._cache[user_id] = settings

        logger.info(f"설정 업데이트: {user_id} - {kwargs}")
        return settings

    def set_city(self, user_id: str, city: str) -> UserAlertSettings:
        """사용자 도시 설정"""
        return self.update_settings(user_id, city=city)



    def list_all_settings(self) -> list[UserAlertSettings]:
        """모든 사용자 설정 조회"""
        all_profiles = self._repository.get_all()
        return [self.get_settings(profile["user_id"]) for profile in all_profiles]

    def close(self) -> None:
        """리소스 정리"""
        self._repository.close()
