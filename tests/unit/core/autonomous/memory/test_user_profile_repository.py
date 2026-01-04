"""
UserProfileRepository 테스트

사용자 프로필 저장소의 CRUD 기능을 테스트합니다.
"""

import pytest
from src.core.autonomous.memory.user_profile_repository import UserProfileRepository


class TestUserProfileRepository:
    """UserProfileRepository 테스트"""

    @pytest.fixture
    def repository(self):
        """테스트용 인메모리 Repository"""
        repo = UserProfileRepository(db_path=":memory:")
        yield repo
        repo.close()

    def test_create_profile(self, repository):
        """프로필 생성 테스트"""
        result = repository.create("U12345")

        assert result is True
        profile = repository.get("U12345")
        assert profile is not None
        assert profile["user_id"] == "U12345"

    def test_get_profile(self, repository):
        """프로필 조회 테스트"""
        repository.create("U12345")

        profile = repository.get("U12345")

        assert profile is not None
        assert profile["user_id"] == "U12345"
        assert "first_seen_at" in profile
        assert "last_active_at" in profile

    def test_get_nonexistent_profile(self, repository):
        """존재하지 않는 프로필 조회 테스트"""
        profile = repository.get("U99999")

        assert profile is None

    def test_update_last_active(self, repository):
        """마지막 활동 시간 업데이트 테스트"""
        repository.create("U12345")

        result = repository.update_last_active("U12345")

        assert result is True
        profile = repository.get("U12345")
        assert profile["last_active_at"] is not None

    def test_update_preferences(self, repository):
        """선호도 업데이트 테스트"""
        repository.create("U12345")
        preferences = {
            "quiet_hours": {"start": "22:00", "end": "08:00"},
            "notification_frequency": "low",
        }

        result = repository.update_preferences("U12345", preferences)

        assert result is True
        profile = repository.get("U12345")
        assert profile["preferences"]["quiet_hours"]["start"] == "22:00"
        assert profile["preferences"]["notification_frequency"] == "low"

    def test_update_patterns(self, repository):
        """패턴 업데이트 테스트"""
        repository.create("U12345")
        patterns = {
            "wake_up_time": "07:00",
            "commute_time": "08:30",
            "preferred_notification_times": ["08:00", "12:00", "18:00"],
        }

        result = repository.update_patterns("U12345", patterns)

        assert result is True
        profile = repository.get("U12345")
        assert profile["patterns"]["wake_up_time"] == "07:00"
        assert profile["patterns"]["commute_time"] == "08:30"

    def test_get_or_create(self, repository):
        """없으면 생성, 있으면 조회 테스트"""
        # 처음 호출 - 생성
        profile1 = repository.get_or_create("U12345")
        assert profile1 is not None

        # 두 번째 호출 - 기존 조회
        profile2 = repository.get_or_create("U12345")
        assert profile2["first_seen_at"] == profile1["first_seen_at"]

    def test_delete_profile(self, repository):
        """프로필 삭제 테스트"""
        repository.create("U12345")

        result = repository.delete("U12345")

        assert result is True
        assert repository.get("U12345") is None

    def test_get_all_profiles(self, repository):
        """모든 프로필 조회 테스트"""
        repository.create("U111")
        repository.create("U222")
        repository.create("U333")

        profiles = repository.get_all()

        assert len(profiles) == 3
