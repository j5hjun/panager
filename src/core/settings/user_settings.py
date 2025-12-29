"""
사용자 알림 설정

사용자별 알림 설정을 관리합니다.
"""

import logging
from dataclasses import dataclass
from typing import Any

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
    morning_briefing_enabled: bool = True  # 아침 브리핑 활성화
    morning_briefing_hour: int = 8  # 아침 브리핑 시간
    morning_briefing_minute: int = 0
    weather_alert_enabled: bool = True  # 날씨 알림 활성화
    timezone: str = "Asia/Seoul"

    def to_dict(self) -> dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "user_id": self.user_id,
            "channel_id": self.channel_id,
            "city": self.city,
            "morning_briefing_enabled": self.morning_briefing_enabled,
            "morning_briefing_hour": self.morning_briefing_hour,
            "morning_briefing_minute": self.morning_briefing_minute,
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
            morning_briefing_enabled=data.get("morning_briefing_enabled", True),
            morning_briefing_hour=data.get("morning_briefing_hour", 8),
            morning_briefing_minute=data.get("morning_briefing_minute", 0),
            weather_alert_enabled=data.get("weather_alert_enabled", True),
            timezone=data.get("timezone", "Asia/Seoul"),
        )


class UserSettingsManager:
    """
    사용자 설정 관리자

    사용자별 알림 설정을 저장하고 조회합니다.
    현재는 메모리에 저장하며, 추후 DB로 전환 가능합니다.
    """

    def __init__(self, default_city: str = "Seoul", default_channel: str = ""):
        """
        UserSettingsManager 초기화

        Args:
            default_city: 기본 도시
            default_channel: 기본 채널 ID
        """
        self._settings: dict[str, UserAlertSettings] = {}
        self.default_city = default_city
        self.default_channel = default_channel

        logger.info(f"UserSettingsManager 초기화 (default_city={default_city})")

    def get_settings(self, user_id: str) -> UserAlertSettings:
        """
        사용자 설정 조회

        Args:
            user_id: 사용자 ID

        Returns:
            사용자 설정 (없으면 기본값으로 생성)
        """
        if user_id not in self._settings:
            self._settings[user_id] = UserAlertSettings(
                user_id=user_id,
                channel_id=self.default_channel,
                city=self.default_city,
            )
        return self._settings[user_id]

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

        logger.info(f"설정 업데이트: {user_id} - {kwargs}")
        return settings

    def set_city(self, user_id: str, city: str) -> UserAlertSettings:
        """사용자 도시 설정"""
        return self.update_settings(user_id, city=city)

    def set_morning_briefing(
        self, user_id: str, enabled: bool, hour: int = 8, minute: int = 0
    ) -> UserAlertSettings:
        """아침 브리핑 설정"""
        return self.update_settings(
            user_id,
            morning_briefing_enabled=enabled,
            morning_briefing_hour=hour,
            morning_briefing_minute=minute,
        )

    def get_all_users_with_morning_briefing(self) -> list[UserAlertSettings]:
        """아침 브리핑이 활성화된 모든 사용자 조회"""
        return [s for s in self._settings.values() if s.morning_briefing_enabled]

    def list_all_settings(self) -> list[UserAlertSettings]:
        """모든 사용자 설정 조회"""
        return list(self._settings.values())
