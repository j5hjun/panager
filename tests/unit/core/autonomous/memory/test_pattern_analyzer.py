"""
PatternAnalyzer 테스트

대화/일정에서 사용자 패턴을 추출하는 기능을 테스트합니다.
"""

import pytest
from src.core.autonomous.memory.pattern_analyzer import PatternAnalyzer


class TestPatternAnalyzer:
    """PatternAnalyzer 테스트"""

    @pytest.fixture
    def analyzer(self):
        """테스트용 분석기"""
        return PatternAnalyzer()

    def test_extract_wake_up_time_from_schedule(self, analyzer):
        """일정에서 기상 시간 추출"""
        schedules = [
            {"title": "출근", "start_time": "2026-01-04T08:30:00"},
            {"title": "아침 회의", "start_time": "2026-01-04T09:00:00"},
        ]

        patterns = analyzer.extract_patterns_from_schedules(schedules)

        # 출근 시간 30분 전 기상 추정
        assert "wake_up_time" in patterns or "commute_time" in patterns

    def test_extract_commute_time(self, analyzer):
        """출근 시간 추출"""
        schedules = [
            {"title": "출근", "start_time": "2026-01-04T08:30:00"},
            {"title": "출근", "start_time": "2026-01-05T08:30:00"},
            {"title": "출근", "start_time": "2026-01-06T08:45:00"},
        ]

        patterns = analyzer.extract_patterns_from_schedules(schedules)

        assert "commute_time" in patterns
        # 평균 출근 시간
        assert patterns["commute_time"] in ["08:30", "08:35", "08:45"]

    def test_extract_preferences_from_messages(self, analyzer):
        """대화에서 선호도 추출"""
        messages = [
            "날씨 알려줘",
            "오늘 날씨 어때?",
            "비 올까?",
            "일정 추가해줘",
        ]

        preferences = analyzer.extract_preferences_from_messages(messages)

        assert "interests" in preferences
        assert "날씨" in preferences["interests"]

    def test_extract_quiet_hours(self, analyzer):
        """방해 금지 시간 추출"""
        messages = [
            {"text": "밤에 알림 그만해", "timestamp": "2026-01-04T23:30:00"},
            {"text": "새벽에 알림 금지", "timestamp": "2026-01-05T01:00:00"},
        ]

        preferences = analyzer.extract_quiet_hours(messages)

        assert "quiet_hours" in preferences
        assert preferences["quiet_hours"]["start"] is not None

    def test_analyze_notification_feedback(self, analyzer):
        """알림 피드백 분석"""
        notifications = [
            {"sent_at": "08:00", "user_reaction": "positive"},
            {"sent_at": "07:00", "user_reaction": "negative"},
            {"sent_at": "12:00", "user_reaction": "positive"},
            {"sent_at": "22:00", "user_reaction": "negative"},
        ]

        preferences = analyzer.analyze_notification_feedback(notifications)

        assert "preferred_notification_times" in preferences
        assert "08:00" in preferences["preferred_notification_times"]

    def test_merge_patterns(self, analyzer):
        """패턴 병합"""
        existing = {
            "wake_up_time": "07:00",
            "interests": ["날씨"],
        }
        new = {
            "commute_time": "08:30",
            "interests": ["일정"],
        }

        merged = analyzer.merge_patterns(existing, new)

        assert merged["wake_up_time"] == "07:00"
        assert merged["commute_time"] == "08:30"
        assert "날씨" in merged["interests"]
        assert "일정" in merged["interests"]
