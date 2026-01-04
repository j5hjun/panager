"""
MemoryManager 테스트

통합 메모리 관리자를 테스트합니다.
"""

import pytest
from src.core.autonomous.memory.lesson_repository import LessonRepository
from src.core.autonomous.memory.memory_manager import MemoryManager
from src.core.autonomous.memory.notification_repository import NotificationRepository
from src.core.autonomous.memory.user_profile_repository import UserProfileRepository


class TestMemoryManager:
    """MemoryManager 테스트"""

    @pytest.fixture
    def manager(self):
        """테스트용 메모리 관리자"""
        lesson_repo = LessonRepository(db_path=":memory:")
        notification_repo = NotificationRepository(db_path=":memory:")
        user_profile_repo = UserProfileRepository(db_path=":memory:")

        mgr = MemoryManager(
            lesson_repo=lesson_repo,
            notification_repo=notification_repo,
            user_profile_repo=user_profile_repo,
        )
        yield mgr

        lesson_repo.close()
        notification_repo.close()
        user_profile_repo.close()

    def test_get_user_context(self, manager):
        """사용자 컨텍스트 조회"""
        # 사용자 생성
        manager.user_profile_repo.create("U12345")

        context = manager.get_user_context("U12345")

        assert context is not None
        assert "user_id" in context
        assert "patterns" in context
        assert "lessons" in context

    def test_get_user_context_new_user(self, manager):
        """새 사용자 컨텍스트 (자동 생성)"""
        context = manager.get_user_context("NEW_USER")

        assert context is not None
        assert context["user_id"] == "NEW_USER"

    def test_update_user_activity(self, manager):
        """사용자 활동 업데이트"""
        result = manager.update_user_activity("U12345")

        assert result is True
        profile = manager.user_profile_repo.get("U12345")
        assert profile is not None

    def test_record_notification(self, manager):
        """알림 기록"""
        notification_id = manager.record_notification(
            user_id="U12345",
            message="테스트 알림",
            notification_type="weather",
        )

        assert notification_id is not None
        notification = manager.notification_repo.get(notification_id)
        assert notification["message"] == "테스트 알림"

    def test_record_lesson(self, manager):
        """교훈 기록"""
        lesson_id = manager.record_lesson(
            content="아침에 알림하면 안됨",
            context={"time": "07:00"},
            user_reaction="negative",
        )

        assert lesson_id is not None
        lessons = manager.lesson_repo.get_all()
        assert len(lessons) == 1

    def test_get_relevant_lessons(self, manager):
        """관련 교훈 조회"""
        # 교훈 추가
        for i in range(5):
            manager.record_lesson(
                content=f"교훈 {i}",
                context={},
                user_reaction="negative",
            )

        lessons = manager.get_relevant_lessons()

        assert len(lessons) <= 5

    def test_update_user_patterns(self, manager):
        """사용자 패턴 업데이트"""
        patterns = {
            "wake_up_time": "07:00",
            "commute_time": "08:30",
        }

        result = manager.update_user_patterns("U12345", patterns)

        assert result is True
        profile = manager.user_profile_repo.get("U12345")
        assert profile["patterns"]["wake_up_time"] == "07:00"

    def test_should_notify(self, manager):
        """알림 여부 판단"""
        # 사용자 생성 및 패턴 설정
        manager.user_profile_repo.create("U12345")
        manager.user_profile_repo.update_patterns(
            "U12345",
            {"preferred_notification_times": ["08:00", "12:00"]},
        )

        # 현재 시간에 따라 결과 달라짐
        result = manager.should_notify("U12345")

        assert isinstance(result, bool)

    def test_get_all_active_users(self, manager):
        """활성 사용자 목록 조회"""
        manager.user_profile_repo.create("U111")
        manager.user_profile_repo.create("U222")

        users = manager.get_all_active_users()

        assert len(users) == 2
