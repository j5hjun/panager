"""
메모리 시스템 통합 테스트

P-011 메모리 시스템의 전체 흐름을 테스트합니다.
"""

import pytest
from src.core.autonomous.memory.lesson_repository import LessonRepository
from src.core.autonomous.memory.memory_manager import MemoryManager
from src.core.autonomous.memory.notification_repository import NotificationRepository
from src.core.autonomous.memory.pattern_analyzer import PatternAnalyzer
from src.core.autonomous.memory.user_profile_repository import UserProfileRepository


class TestMemorySystemIntegration:
    """메모리 시스템 통합 테스트"""

    @pytest.fixture
    def memory_manager(self):
        """통합 테스트용 메모리 관리자"""
        lesson_repo = LessonRepository(db_path=":memory:")
        notification_repo = NotificationRepository(db_path=":memory:")
        user_profile_repo = UserProfileRepository(db_path=":memory:")

        manager = MemoryManager(
            lesson_repo=lesson_repo,
            notification_repo=notification_repo,
            user_profile_repo=user_profile_repo,
        )
        yield manager

        manager.close()

    def test_full_user_lifecycle(self, memory_manager):
        """사용자 전체 라이프사이클 테스트"""
        user_id = "U_TEST_001"

        # 1. 사용자 활동 기록 (처음 대화)
        memory_manager.update_user_activity(user_id)

        # 2. 프로필 생성 확인
        context = memory_manager.get_user_context(user_id)
        assert context["user_id"] == user_id
        assert context["profile"] is not None

        # 3. 알림 기록
        notification_id = memory_manager.record_notification(
            user_id=user_id,
            message="오늘 비가 올 예정입니다!",
            notification_type="weather",
        )
        assert notification_id is not None

        # 4. 교훈 기록
        lesson_id = memory_manager.record_lesson(
            content="아침 7시 전에는 알림하지 않기",
            context={"time": "06:30"},
            user_reaction="negative",
        )
        assert lesson_id is not None

        # 5. 패턴 업데이트
        patterns = {
            "wake_up_time": "07:00",
            "preferred_notification_times": ["08:00", "12:00"],
        }
        memory_manager.update_user_patterns(user_id, patterns)

        # 6. 업데이트 확인
        updated_context = memory_manager.get_user_context(user_id)
        assert updated_context["patterns"]["wake_up_time"] == "07:00"

    def test_pattern_analyzer_to_profile(self, memory_manager):
        """패턴 분석기 → 프로필 저장 흐름"""
        user_id = "U_TEST_002"
        analyzer = PatternAnalyzer()

        # 1. 일정에서 패턴 추출
        schedules = [
            {"title": "출근", "start_time": "2026-01-04T08:30:00"},
            {"title": "점심 미팅", "start_time": "2026-01-04T12:00:00"},
        ]
        patterns = analyzer.extract_patterns_from_schedules(schedules)

        # 2. 대화에서 선호도 추출
        messages = ["오늘 날씨 어때?", "일정 추가해줘"]
        preferences = analyzer.extract_preferences_from_messages(messages)

        # 3. 패턴 병합
        merged = analyzer.merge_patterns(patterns, preferences)

        # 4. 프로필에 저장
        memory_manager.update_user_patterns(user_id, merged)

        # 5. 확인
        context = memory_manager.get_user_context(user_id)
        assert "commute_time" in context["patterns"] or "interests" in context["patterns"]

    def test_lesson_retrieval(self, memory_manager):
        """교훈 저장 및 조회"""
        # 1. 여러 교훈 저장
        for i in range(10):
            memory_manager.record_lesson(
                content=f"교훈 {i}: 중요한 내용",
                context={"index": i},
                user_reaction="negative" if i % 2 == 0 else "neutral",
            )

        # 2. 관련 교훈 조회
        lessons = memory_manager.get_relevant_lessons()

        # 3. 최근 5개 반환 확인
        assert len(lessons) <= 5
        assert all("content" in lesson for lesson in lessons)
