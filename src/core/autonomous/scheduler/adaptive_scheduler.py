"""
AdaptiveScheduler - 유동적 스케줄러

사용자 데이터 기반으로 자율 판단 루프를 트리거합니다.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from src.core.autonomous.memory.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


class AdaptiveScheduler:
    """
    유동적 스케줄러

    사용자 패턴에 따라 자율 판단 루프를 트리거합니다.
    - 사용자 없으면 비활성
    - 패턴 없으면 기본 시간(08:00, 12:00, 18:00)
    - 패턴 있으면 맞춤 시간
    """

    # 기본 알림 시간
    DEFAULT_TRIGGER_TIMES = ["08:00", "12:00", "18:00"]

    def __init__(self, memory_manager: MemoryManager):
        """
        AdaptiveScheduler 초기화

        Args:
            memory_manager: 메모리 관리자
        """
        self.memory_manager = memory_manager
        self._registered = False

        logger.info("AdaptiveScheduler 초기화 완료")

    def should_run_now(self) -> bool:
        """
        지금 자율 판단 루프를 실행해야 하는지 확인

        Returns:
            실행해야 하면 True
        """
        users = self.memory_manager.get_all_active_users()

        if not users:
            logger.debug("[Scheduler] 활성 사용자 없음, 실행 안 함")
            return False

        # 알림할 사용자가 있는지 확인
        users_to_notify = self.get_users_to_notify()

        return len(users_to_notify) > 0

    def get_users_to_notify(self) -> list[dict]:
        """
        알림할 사용자 목록 조회

        Returns:
            알림 대상 사용자 목록
        """
        users = self.memory_manager.get_all_active_users()
        result = []

        for user in users:
            user_id = user.get("user_id")
            if user_id and self.memory_manager.should_notify(user_id):
                result.append(user)

        return result

    def get_next_trigger_time(self, user_id: str) -> datetime | None:
        """
        다음 트리거 시간 계산

        Args:
            user_id: 사용자 ID

        Returns:
            다음 트리거 시간
        """
        try:
            profile = self.memory_manager.user_profile_repo.get(user_id)
        except AttributeError:
            profile = None

        if not profile:
            # 기본 시간 사용
            patterns = {}
        else:
            patterns = profile.get("patterns", {})

        return self.calculate_next_trigger(patterns)

    def calculate_next_trigger(self, patterns: dict[str, Any]) -> datetime:
        """
        패턴 기반 다음 트리거 시간 계산

        Args:
            patterns: 사용자 패턴

        Returns:
            다음 트리거 시간
        """
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        # 선호 시간 또는 기본 시간
        trigger_times = patterns.get("preferred_notification_times", self.DEFAULT_TRIGGER_TIMES)

        # 오늘 남은 트리거 시간 찾기
        for time_str in sorted(trigger_times):
            if time_str > current_time:
                hour, minute = map(int, time_str.split(":"))
                return now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # 오늘 남은 시간 없으면 내일 첫 번째 시간
        if trigger_times:
            first_time = sorted(trigger_times)[0]
            hour, minute = map(int, first_time.split(":"))
            tomorrow = now + timedelta(days=1)
            return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # 기본: 1시간 후
        return now + timedelta(hours=1)

    def is_quiet_hours(self, user_id: str, preferences: dict[str, Any]) -> bool:
        """
        방해 금지 시간인지 확인

        Args:
            user_id: 사용자 ID
            preferences: 사용자 선호도

        Returns:
            방해 금지 시간이면 True
        """
        quiet_hours = preferences.get("quiet_hours", {})
        start = quiet_hours.get("start")
        end = quiet_hours.get("end")

        if not start or not end:
            return False

        now = datetime.now()
        current_time = now.strftime("%H:%M")

        # 자정을 넘는 경우 처리 (예: 22:00 ~ 08:00)
        if start > end:
            return current_time >= start or current_time < end
        else:
            return start <= current_time < end

    def register_with(self, scheduler_service: Any) -> None:
        """
        기존 SchedulerService와 통합

        Args:
            scheduler_service: 스케줄러 서비스
        """
        if self._registered:
            logger.warning("[Scheduler] 이미 등록됨")
            return

        # 매시 정각에 체크
        scheduler_service.add_cron_job(
            name="adaptive_check",
            func=self._check_and_notify,
            hour="*",
            minute="0",
        )

        self._registered = True
        logger.info("[Scheduler] SchedulerService에 등록 완료")

    def _check_and_notify(self) -> None:
        """매시 정각 체크 (내부 사용)"""
        if self.should_run_now():
            logger.info("[Scheduler] 자율 판단 루프 트리거")
            # TODO: AutonomousRunner 실행

    def on_user_activity(self, user_id: str) -> bool:
        """
        사용자 활동 시 호출

        Args:
            user_id: 사용자 ID

        Returns:
            성공 여부
        """
        self.memory_manager.update_user_activity(user_id)
        logger.info(f"[Scheduler] 사용자 활동 업데이트: {user_id}")
        return True

    def get_status(self) -> dict[str, Any]:
        """
        스케줄러 상태 조회

        Returns:
            상태 dict
        """
        users = self.memory_manager.get_all_active_users()

        return {
            "registered": self._registered,
            "active_users": len(users),
            "users_to_notify": len(self.get_users_to_notify()),
            "should_run_now": self.should_run_now(),
        }
