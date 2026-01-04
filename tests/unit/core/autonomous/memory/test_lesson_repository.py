"""
LessonRepository 테스트

교훈 저장소의 CRUD 기능을 테스트합니다.
"""

import pytest
from src.core.autonomous.memory.lesson_repository import LessonRepository


class TestLessonRepository:
    """LessonRepository 테스트"""

    @pytest.fixture
    def repository(self):
        """테스트용 인메모리 Repository"""
        repo = LessonRepository(db_path=":memory:")
        yield repo
        repo.close()

    def test_save_lesson(self, repository):
        """교훈 저장 테스트"""
        lesson_id = repository.save(
            content="사용자는 아침 알림을 선호함",
            context={"trigger": "morning_briefing", "reaction": "positive"},
            user_reaction="positive",
        )

        assert lesson_id is not None
        assert isinstance(lesson_id, str)

    def test_get_lesson(self, repository):
        """단일 교훈 조회 테스트"""
        lesson_id = repository.save(
            content="날씨 알림 후 긍정 반응",
            context={"trigger": "weather"},
            user_reaction="positive",
        )

        lesson = repository.get(lesson_id)

        assert lesson is not None
        assert lesson["content"] == "날씨 알림 후 긍정 반응"
        assert lesson["user_reaction"] == "positive"

    def test_get_all_lessons(self, repository):
        """전체 교훈 조회 테스트"""
        repository.save(content="교훈 1", context={}, user_reaction="positive")
        repository.save(content="교훈 2", context={}, user_reaction="negative")

        lessons = repository.get_all()

        assert len(lessons) == 2

    def test_get_recent_lessons(self, repository):
        """최근 N개 교훈 조회 테스트"""
        for i in range(10):
            repository.save(content=f"교훈 {i}", context={}, user_reaction="neutral")

        recent = repository.get_recent(limit=5)

        assert len(recent) == 5
        # 최신순으로 정렬되어야 함
        assert recent[0]["content"] == "교훈 9"

    def test_lesson_limit(self, repository):
        """교훈 최대 개수 제한 테스트 (50개)"""
        # 60개 저장
        for i in range(60):
            repository.save(content=f"교훈 {i}", context={}, user_reaction="neutral")

        # 50개만 유지되어야 함
        all_lessons = repository.get_all()
        assert len(all_lessons) <= 50

    def test_get_by_reaction(self, repository):
        """반응 유형별 교훈 조회 테스트"""
        repository.save(content="긍정 교훈", context={}, user_reaction="positive")
        repository.save(content="부정 교훈", context={}, user_reaction="negative")
        repository.save(content="긍정 교훈 2", context={}, user_reaction="positive")

        positive_lessons = repository.get_by_reaction("positive")

        assert len(positive_lessons) == 2

    def test_delete_lesson(self, repository):
        """교훈 삭제 테스트"""
        lesson_id = repository.save(content="삭제할 교훈", context={}, user_reaction="neutral")

        result = repository.delete(lesson_id)

        assert result is True
        assert repository.get(lesson_id) is None
