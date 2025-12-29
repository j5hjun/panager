"""
Tool Plugins 테스트

WeatherTool, CalendarTool 플러그인을 검증합니다.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from src.core.entities.weather import WeatherData
from src.core.tools.base import BaseTool


class TestWeatherTool:
    """WeatherTool 플러그인 테스트"""

    def test_weather_tool_inherits_base_tool(self):
        """WeatherTool이 BaseTool을 상속하는지 확인"""
        from src.core.tools.plugins.weather import WeatherTool

        assert issubclass(WeatherTool, BaseTool)

    def test_weather_tool_has_correct_name(self):
        """WeatherTool의 name이 'weather'인지 확인"""
        from src.core.tools.plugins.weather import WeatherTool

        mock_service = MagicMock()
        tool = WeatherTool(weather_service=mock_service)

        assert tool.name == "weather"

    def test_weather_tool_has_description(self):
        """WeatherTool에 description이 있는지 확인"""
        from src.core.tools.plugins.weather import WeatherTool

        mock_service = MagicMock()
        tool = WeatherTool(weather_service=mock_service)

        assert tool.description is not None
        assert len(tool.description) > 0

    def test_weather_tool_get_tool_definitions_returns_list(self):
        """get_tool_definitions가 도구 정의 리스트를 반환"""
        from src.core.tools.plugins.weather import WeatherTool

        mock_service = MagicMock()
        tool = WeatherTool(weather_service=mock_service)

        definitions = tool.get_tool_definitions()

        assert isinstance(definitions, list)
        assert len(definitions) == 2  # get_current_weather, check_umbrella

        function_names = [d["function"]["name"] for d in definitions]
        assert "get_current_weather" in function_names
        assert "check_umbrella" in function_names

    @pytest.mark.asyncio
    async def test_weather_tool_execute_get_current_weather(self):
        """execute로 get_current_weather 호출"""
        from src.core.tools.plugins.weather import WeatherTool

        mock_weather_data = WeatherData(
            city="Seoul",
            temperature=20.0,
            feels_like=18.0,
            humidity=65,
            description="맑음",
            wind_speed=3.5,
            icon="01d",
        )

        mock_service = MagicMock()
        mock_service.get_weather_data = AsyncMock(return_value=mock_weather_data)

        tool = WeatherTool(weather_service=mock_service)
        result = await tool.execute(function_name="get_current_weather", city="Seoul")

        assert result["success"] is True
        assert result["data"]["city"] == "Seoul"
        assert result["data"]["temperature"] == 20.0
        mock_service.get_weather_data.assert_called_once_with("Seoul")

    @pytest.mark.asyncio
    async def test_weather_tool_execute_check_umbrella(self):
        """execute로 check_umbrella 호출"""
        from src.core.tools.plugins.weather import WeatherTool

        mock_service = MagicMock()
        mock_service.needs_umbrella = AsyncMock(
            return_value=(False, "Seoul는 맑아요. 우산은 필요 없을 것 같아요!")
        )

        tool = WeatherTool(weather_service=mock_service)
        result = await tool.execute(function_name="check_umbrella", city="Seoul")

        assert result["success"] is True
        assert result["needs_umbrella"] is False
        mock_service.needs_umbrella.assert_called_once_with("Seoul")

    @pytest.mark.asyncio
    async def test_weather_tool_execute_unknown_function_raises_error(self):
        """알 수 없는 함수 호출 시 ValueError 발생"""
        from src.core.tools.plugins.weather import WeatherTool

        mock_service = MagicMock()
        tool = WeatherTool(weather_service=mock_service)

        with pytest.raises(ValueError, match="알 수 없는 함수"):
            await tool.execute(function_name="unknown_function")


class TestCalendarTool:
    """CalendarTool 플러그인 테스트"""

    def test_calendar_tool_inherits_base_tool(self):
        """CalendarTool이 BaseTool을 상속하는지 확인"""
        from src.core.tools.plugins.calendar import CalendarTool

        assert issubclass(CalendarTool, BaseTool)

    def test_calendar_tool_has_correct_name(self):
        """CalendarTool의 name이 'calendar'인지 확인"""
        from src.core.tools.plugins.calendar import CalendarTool

        mock_service = MagicMock()
        tool = CalendarTool(calendar_service=mock_service)

        assert tool.name == "calendar"

    def test_calendar_tool_has_description(self):
        """CalendarTool에 description이 있는지 확인"""
        from src.core.tools.plugins.calendar import CalendarTool

        mock_service = MagicMock()
        tool = CalendarTool(calendar_service=mock_service)

        assert tool.description is not None
        assert len(tool.description) > 0

    def test_calendar_tool_get_tool_definitions_returns_list(self):
        """get_tool_definitions가 도구 정의 리스트를 반환"""
        from src.core.tools.plugins.calendar import CalendarTool

        mock_service = MagicMock()
        tool = CalendarTool(calendar_service=mock_service)

        definitions = tool.get_tool_definitions()

        assert isinstance(definitions, list)
        assert len(definitions) == 2  # get_schedule, add_schedule

        function_names = [d["function"]["name"] for d in definitions]
        assert "get_schedule" in function_names
        assert "add_schedule" in function_names

    @pytest.mark.asyncio
    async def test_calendar_tool_execute_get_schedule(self):
        """execute로 get_schedule 호출"""
        from src.core.tools.plugins.calendar import CalendarTool

        mock_service = MagicMock()
        mock_service.get_schedules_by_date.return_value = []
        mock_service.format_schedule_list.return_value = "일정이 없습니다."

        tool = CalendarTool(calendar_service=mock_service)
        result = await tool.execute(function_name="get_schedule", date="today")

        assert result["success"] is True
        assert result["count"] == 0
        mock_service.get_schedules_by_date.assert_called_once()

    @pytest.mark.asyncio
    async def test_calendar_tool_execute_add_schedule(self):
        """execute로 add_schedule 호출"""
        from src.core.tools.plugins.calendar import CalendarTool

        mock_service = MagicMock()
        mock_service.add_schedule.return_value = "schedule_123"

        tool = CalendarTool(calendar_service=mock_service)
        result = await tool.execute(
            function_name="add_schedule",
            title="팀 미팅",
            date="today",
            time="14:00",
            location="회의실 A",
        )

        assert result["success"] is True
        assert result["schedule_id"] == "schedule_123"
        mock_service.add_schedule.assert_called_once()

    @pytest.mark.asyncio
    async def test_calendar_tool_execute_unknown_function_raises_error(self):
        """알 수 없는 함수 호출 시 ValueError 발생"""
        from src.core.tools.plugins.calendar import CalendarTool

        mock_service = MagicMock()
        tool = CalendarTool(calendar_service=mock_service)

        with pytest.raises(ValueError, match="알 수 없는 함수"):
            await tool.execute(function_name="unknown_function")


class TestToolPluginsIntegration:
    """Tool Plugin 통합 테스트"""

    def test_plugins_can_be_registered_to_registry(self):
        """플러그인들을 Registry에 등록할 수 있음"""
        from src.core.tools.plugins.calendar import CalendarTool
        from src.core.tools.plugins.weather import WeatherTool
        from src.core.tools.registry import ToolRegistry

        registry = ToolRegistry()
        registry.clear()

        weather_service = MagicMock()
        calendar_service = MagicMock()

        weather_tool = WeatherTool(weather_service=weather_service)
        calendar_tool = CalendarTool(calendar_service=calendar_service)

        registry.register(weather_tool)
        registry.register(calendar_tool)

        assert "weather" in registry.list_tools()
        assert "calendar" in registry.list_tools()

    def test_registry_returns_all_tool_definitions_from_plugins(self):
        """Registry가 모든 플러그인의 도구 정의를 반환"""
        from src.core.tools.plugins.calendar import CalendarTool
        from src.core.tools.plugins.weather import WeatherTool
        from src.core.tools.registry import ToolRegistry

        registry = ToolRegistry()
        registry.clear()

        weather_service = MagicMock()
        calendar_service = MagicMock()

        registry.register(WeatherTool(weather_service=weather_service))
        registry.register(CalendarTool(calendar_service=calendar_service))

        all_definitions = registry.get_all_tool_definitions()

        # Weather: 2개, Calendar: 2개 = 총 4개
        assert len(all_definitions) == 4

        function_names = [d["function"]["name"] for d in all_definitions]
        assert "get_current_weather" in function_names
        assert "check_umbrella" in function_names
        assert "get_schedule" in function_names
        assert "add_schedule" in function_names
