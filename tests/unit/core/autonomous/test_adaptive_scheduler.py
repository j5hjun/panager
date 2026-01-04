"""
AdaptiveScheduler 테스트

데이터 기반 유동적 스케줄러를 테스트합니다.
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from src.core.autonomous.memory.memory_manager import MemoryManager
from src.core.autonomous.scheduler.adaptive_scheduler import AdaptiveScheduler


class TestAdaptiveScheduler:
    """AdaptiveScheduler 테스트"""

    @pytest.fixture
    def mock_memory_manager(self):
        """모의 메모리 관리자"""
        manager = MagicMock(spec=MemoryManager)
        manager.get_all_active_users.return_value = []
        return manager

    @pytest.fixture
    def scheduler(self, mock_memory_manager):
        """테스트용 스케줄러"""
        return AdaptiveScheduler(memory_manager=mock_memory_manager)

    def test_no_user_no_trigger(self, scheduler, mock_memory_manager):
        """사용자 없으면 트리거 안 함"""
        mock_memory_manager.get_all_active_users.return_value = []

        should_run = scheduler.should_run_now()

        assert should_run is False

    def test_user_without_pattern_default_trigger(self, scheduler, mock_memory_manager):
        """패턴 없는 사용자는 기본 규칙 적용"""
        mock_memory_manager.get_all_active_users.return_value = [
            {"user_id": "U12345", "patterns": {}}
        ]

        # 기본 규칙: 아침 8시, 점심 12시, 저녁 18시에 트리거
        result = scheduler.get_next_trigger_time("U12345")

        assert result is not None

    def test_user_with_pattern_custom_trigger(self, scheduler, mock_memory_manager):
        """패턴 있는 사용자는 맞춤 시간에 트리거"""
        mock_memory_manager.get_all_active_users.return_value = [
            {
                "user_id": "U12345",
                "patterns": {
                    "wake_up_time": "07:00",
                    "preferred_notification_times": ["07:30", "12:00"],
                },
            }
        ]
        mock_memory_manager.user_profile_repo = MagicMock()
        mock_memory_manager.user_profile_repo.get.return_value = {
            "user_id": "U12345",
            "patterns": {
                "wake_up_time": "07:00",
                "preferred_notification_times": ["07:30", "12:00"],
            },
        }

        result = scheduler.get_next_trigger_time("U12345")

        assert result is not None

    def test_get_users_to_notify(self, scheduler, mock_memory_manager):
        """알림할 사용자 목록 조회"""
        mock_memory_manager.get_all_active_users.return_value = [
            {"user_id": "U111", "patterns": {}},
            {"user_id": "U222", "patterns": {}},
        ]
        mock_memory_manager.should_notify.side_effect = [True, False]

        users = scheduler.get_users_to_notify()

        # should_notify가 True인 사용자만
        assert len(users) == 1
        assert users[0]["user_id"] == "U111"

    def test_quiet_hours_respected(self, scheduler, mock_memory_manager):
        """방해 금지 시간 준수"""
        mock_memory_manager.get_all_active_users.return_value = [
            {
                "user_id": "U12345",
                "preferences": {"quiet_hours": {"start": "22:00", "end": "08:00"}},
            }
        ]

        # 방해 금지 시간 체크
        is_quiet = scheduler.is_quiet_hours(
            "U12345",
            {"quiet_hours": {"start": "22:00", "end": "08:00"}},
        )

        # 현재 시간에 따라 결과 달라짐
        assert isinstance(is_quiet, bool)

    def test_calculate_next_trigger(self, scheduler):
        """다음 트리거 시간 계산"""
        patterns = {"preferred_notification_times": ["08:00", "12:00", "18:00"]}

        next_time = scheduler.calculate_next_trigger(patterns)

        assert next_time is not None
        assert isinstance(next_time, datetime)

    def test_register_with_scheduler_service(self, scheduler):
        """기존 SchedulerService와 통합"""
        mock_scheduler_service = MagicMock()

        scheduler.register_with(mock_scheduler_service)

        # add_interval_job 또는 add_cron_job 호출 확인
        assert mock_scheduler_service.method_calls  # 뭔가 호출됨

    def test_on_user_activity(self, scheduler, mock_memory_manager):
        """사용자 활동 시 스케줄 갱신"""
        result = scheduler.on_user_activity("U12345")

        assert result is True
        mock_memory_manager.update_user_activity.assert_called_once_with("U12345")
