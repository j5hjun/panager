"""
NotificationRepository 테스트

알림 이력 저장소의 CRUD 기능을 테스트합니다.
"""

import pytest
from src.core.autonomous.memory.notification_repository import NotificationRepository


class TestNotificationRepository:
    """NotificationRepository 테스트"""

    @pytest.fixture
    def repository(self):
        """테스트용 인메모리 Repository"""
        repo = NotificationRepository(db_path=":memory:")
        yield repo
        repo.close()

    def test_save_notification(self, repository):
        """알림 저장 테스트"""
        notification_id = repository.save(
            user_id="U12345",
            message="오늘 비가 올 예정입니다 ☔",
            notification_type="weather_alert",
        )

        assert notification_id is not None
        assert isinstance(notification_id, str)

    def test_get_notification(self, repository):
        """단일 알림 조회 테스트"""
        notification_id = repository.save(
            user_id="U12345",
            message="테스트 알림",
            notification_type="reminder",
        )

        notification = repository.get(notification_id)

        assert notification is not None
        assert notification["user_id"] == "U12345"
        assert notification["message"] == "테스트 알림"
        assert notification["notification_type"] == "reminder"

    def test_get_by_user(self, repository):
        """사용자별 알림 조회 테스트"""
        repository.save(user_id="U111", message="알림 1", notification_type="test")
        repository.save(user_id="U222", message="알림 2", notification_type="test")
        repository.save(user_id="U111", message="알림 3", notification_type="test")

        user_notifications = repository.get_by_user("U111")

        assert len(user_notifications) == 2

    def test_update_reaction(self, repository):
        """사용자 반응 업데이트 테스트"""
        notification_id = repository.save(
            user_id="U12345",
            message="알림",
            notification_type="test",
        )

        result = repository.update_reaction(notification_id, "positive")

        assert result is True
        notification = repository.get(notification_id)
        assert notification["user_reaction"] == "positive"
        assert notification["reaction_at"] is not None

    def test_get_today_count(self, repository):
        """오늘 알림 개수 조회 테스트"""
        # 오늘 알림 3개 저장
        for i in range(3):
            repository.save(
                user_id="U12345",
                message=f"알림 {i}",
                notification_type="test",
            )

        count = repository.get_today_count("U12345")

        assert count == 3

    def test_get_recent(self, repository):
        """최근 알림 조회 테스트"""
        for i in range(10):
            repository.save(
                user_id="U12345",
                message=f"알림 {i}",
                notification_type="test",
            )

        recent = repository.get_recent("U12345", limit=5)

        assert len(recent) == 5
        # 최신순
        assert recent[0]["message"] == "알림 9"

    def test_notification_limit(self, repository):
        """알림 최대 개수 제한 테스트 (100개)"""
        for i in range(120):
            repository.save(
                user_id="U12345",
                message=f"알림 {i}",
                notification_type="test",
            )

        all_notifications = repository.get_by_user("U12345")
        assert len(all_notifications) <= 100
