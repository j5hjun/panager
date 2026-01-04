"""
MemoryManager - 통합 메모리 관리자

모든 Repository를 통합 관리하고 사용자 컨텍스트를 제공합니다.
"""

import logging
from datetime import datetime
from typing import Any

from src.core.autonomous.memory.lesson_repository import LessonRepository
from src.core.autonomous.memory.notification_repository import NotificationRepository
from src.core.autonomous.memory.user_profile_repository import UserProfileRepository

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    통합 메모리 관리자

    교훈, 알림, 사용자 프로필을 통합 관리합니다.
    """

    def __init__(
        self,
        lesson_repo: LessonRepository | None = None,
        notification_repo: NotificationRepository | None = None,
        user_profile_repo: UserProfileRepository | None = None,
        db_path: str = "data/memory.db",
    ):
        """
        MemoryManager 초기화

        Args:
            lesson_repo: 교훈 저장소 (DI)
            notification_repo: 알림 저장소 (DI)
            user_profile_repo: 사용자 프로필 저장소 (DI)
            db_path: 기본 DB 경로
        """
        self.lesson_repo = lesson_repo or LessonRepository(db_path=db_path)
        self.notification_repo = notification_repo or NotificationRepository(db_path=db_path)
        self.user_profile_repo = user_profile_repo or UserProfileRepository(db_path=db_path)

        logger.info("MemoryManager 초기화 완료")

    def get_user_context(self, user_id: str) -> dict[str, Any]:
        """
        사용자 컨텍스트 조회

        Args:
            user_id: 사용자 ID

        Returns:
            사용자 컨텍스트 dict
        """
        # 프로필 가져오기 (없으면 생성)
        profile = self.user_profile_repo.get_or_create(user_id)

        # 최근 교훈
        lessons = self.lesson_repo.get_recent(limit=5)

        # 최근 알림
        notifications = self.notification_repo.get_recent(user_id, limit=5)

        return {
            "user_id": user_id,
            "profile": profile,
            "patterns": profile.get("patterns", {}),
            "preferences": profile.get("preferences", {}),
            "lessons": lessons,
            "notifications": notifications,
        }

    def update_user_activity(self, user_id: str) -> bool:
        """
        사용자 활동 업데이트

        Args:
            user_id: 사용자 ID

        Returns:
            성공 여부
        """
        # 프로필 없으면 생성
        self.user_profile_repo.get_or_create(user_id)

        # 마지막 활동 시간 업데이트
        return self.user_profile_repo.update_last_active(user_id)

    def record_notification(
        self,
        user_id: str,
        message: str,
        notification_type: str = "general",
    ) -> str:
        """
        알림 기록

        Args:
            user_id: 사용자 ID
            message: 알림 메시지
            notification_type: 알림 유형

        Returns:
            알림 ID
        """
        return self.notification_repo.save(
            user_id=user_id,
            message=message,
            notification_type=notification_type,
        )

    def record_lesson(
        self,
        content: str,
        context: dict[str, Any] | None = None,
        user_reaction: str = "neutral",
    ) -> str:
        """
        교훈 기록

        Args:
            content: 교훈 내용
            context: 맥락
            user_reaction: 사용자 반응

        Returns:
            교훈 ID
        """
        return self.lesson_repo.save(
            content=content,
            context=context,
            user_reaction=user_reaction,
        )

    def get_relevant_lessons(self, context: str | None = None) -> list[dict]:
        """
        관련 교훈 조회

        Args:
            context: 검색 맥락

        Returns:
            관련 교훈 목록
        """
        # TODO: 벡터 검색 구현
        return self.lesson_repo.get_recent(limit=5)

    def update_user_patterns(self, user_id: str, patterns: dict[str, Any]) -> bool:
        """
        사용자 패턴 업데이트

        Args:
            user_id: 사용자 ID
            patterns: 패턴 dict

        Returns:
            성공 여부
        """
        # 프로필 없으면 생성
        self.user_profile_repo.get_or_create(user_id)

        return self.user_profile_repo.update_patterns(user_id, patterns)

    def should_notify(self, user_id: str) -> bool:
        """
        알림 여부 판단

        Args:
            user_id: 사용자 ID

        Returns:
            알림해야 하면 True
        """
        profile = self.user_profile_repo.get(user_id)
        if not profile:
            return False

        patterns = profile.get("patterns", {})
        preferred_times = patterns.get("preferred_notification_times", [])

        if not preferred_times:
            # 선호 시간 없으면 기본 허용
            return True

        # 현재 시간이 선호 시간에 포함되는지 확인
        current_hour = datetime.now().strftime("%H:00")

        for preferred_time in preferred_times:
            # 시간 비교 (HH:00 형식으로 비교)
            pref_hour = preferred_time.split(":")[0] + ":00"
            if current_hour == pref_hour:
                return True

        return False

    def get_all_active_users(self) -> list[dict]:
        """
        모든 활성 사용자 조회

        Returns:
            사용자 프로필 목록
        """
        return self.user_profile_repo.get_all()

    def close(self) -> None:
        """리소스 정리"""
        self.lesson_repo.close()
        self.notification_repo.close()
        self.user_profile_repo.close()
