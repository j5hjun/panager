"""
Observe 노드 테스트
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core.autonomous.nodes.observe import (
    _schedule_to_dict,
    observe_node,
    observe_node_async,
)
from src.core.autonomous.state import AgentState, create_initial_state


class TestObserveNode:
    """Observe 노드 기본 테스트"""

    def test_observe_node_updates_time(self):
        """시간 정보가 업데이트되어야 함"""
        state = create_initial_state()
        result = observe_node(state)

        assert result["current_time"] is not None
        assert result["time_period"] in ["morning", "afternoon", "evening", "night"]
        assert isinstance(result["is_quiet_hours"], bool)

    def test_observe_node_preserves_existing_state(self):
        """기존 상태가 보존되어야 함"""
        state = create_initial_state()
        state["today_notification_count"] = 5

        result = observe_node(state)

        assert result["today_notification_count"] == 5

    def test_time_period_morning(self):
        """오전 시간대 테스트"""
        from src.core.autonomous.state import get_time_period

        morning = datetime(2026, 1, 4, 8, 0, 0)
        assert get_time_period(morning) == "morning"

    def test_time_period_afternoon(self):
        """오후 시간대 테스트"""
        from src.core.autonomous.state import get_time_period

        afternoon = datetime(2026, 1, 4, 14, 0, 0)
        assert get_time_period(afternoon) == "afternoon"

    def test_time_period_evening(self):
        """저녁 시간대 테스트"""
        from src.core.autonomous.state import get_time_period

        evening = datetime(2026, 1, 4, 19, 0, 0)
        assert get_time_period(evening) == "evening"

    def test_time_period_night(self):
        """밤 시간대 테스트"""
        from src.core.autonomous.state import get_time_period

        night = datetime(2026, 1, 4, 23, 0, 0)
        assert get_time_period(night) == "night"

    def test_quiet_hours_true(self):
        """방해 금지 시간 테스트"""
        from src.core.autonomous.state import is_quiet_hours

        quiet = datetime(2026, 1, 4, 2, 0, 0)
        assert is_quiet_hours(quiet) is True

    def test_quiet_hours_false(self):
        """방해 금지 시간 아닌 경우 테스트"""
        from src.core.autonomous.state import is_quiet_hours

        not_quiet = datetime(2026, 1, 4, 12, 0, 0)
        assert is_quiet_hours(not_quiet) is False


class TestObserveNodeAsync:
    """Observe 노드 비동기 테스트"""

    @pytest.mark.asyncio
    async def test_observe_node_async_without_services(self):
        """서비스 없이도 기본 정보 수집"""
        state = create_initial_state()
        result = await observe_node_async(state)

        assert result["current_time"] is not None
        assert result["weather"] is None
        assert result["today_schedules"] == []

    @pytest.mark.asyncio
    async def test_observe_node_async_with_weather_service(self):
        """날씨 서비스 연동 테스트"""
        state = create_initial_state()

        # Mock 날씨 서비스
        mock_weather = AsyncMock()
        mock_weather.get_current_weather.return_value = {
            "city": "Seoul",
            "temp": 15.0,
            "description": "맑음",
        }
        mock_weather.needs_umbrella.return_value = (False, "우산 필요 없음")

        result = await observe_node_async(state, weather_service=mock_weather)

        assert result["weather"] is not None
        assert result["weather"]["city"] == "Seoul"
        assert result["needs_umbrella"] is False

    @pytest.mark.asyncio
    async def test_observe_node_async_with_calendar_service(self):
        """일정 서비스 연동 테스트"""
        state = create_initial_state()

        # Mock 일정
        mock_schedule = MagicMock()
        mock_schedule.id = "test-123"
        mock_schedule.title = "테스트 미팅"
        mock_schedule.start_time = datetime(2099, 1, 4, 15, 0, 0)  # 미래 시간
        mock_schedule.end_time = datetime(2099, 1, 4, 16, 0, 0)
        mock_schedule.location = "회의실"
        mock_schedule.description = ""

        # Mock 캘린더 서비스
        mock_calendar = MagicMock()
        mock_calendar.get_today_schedules.return_value = [mock_schedule]

        result = await observe_node_async(state, calendar_service=mock_calendar)

        assert len(result["today_schedules"]) == 1
        assert result["today_schedules"][0]["title"] == "테스트 미팅"

    @pytest.mark.asyncio
    async def test_observe_node_handles_service_errors(self):
        """서비스 에러 핸들링 테스트"""
        state = create_initial_state()

        # 에러 발생하는 Mock 서비스
        mock_weather = AsyncMock()
        mock_weather.get_current_weather.side_effect = Exception("API Error")

        result = await observe_node_async(state, weather_service=mock_weather)

        # 에러가 발생해도 기본 상태는 반환되어야 함
        assert result["current_time"] is not None
        assert result["weather"] is None


class TestScheduleToDict:
    """일정 변환 테스트"""

    def test_schedule_to_dict(self):
        """Schedule 객체를 dict로 변환"""
        mock_schedule = MagicMock()
        mock_schedule.id = "test-123"
        mock_schedule.title = "테스트"
        mock_schedule.start_time = datetime(2026, 1, 4, 10, 0, 0)
        mock_schedule.end_time = None
        mock_schedule.location = ""
        mock_schedule.description = ""

        result = _schedule_to_dict(mock_schedule)

        assert result["id"] == "test-123"
        assert result["title"] == "테스트"
        assert result["end_time"] is None
