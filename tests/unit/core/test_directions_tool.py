"""
길찾기 도구 플러그인 테스트

DirectionsTool 클래스를 검증합니다.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from src.core.entities.directions import DirectionsData
from src.core.tools.base import BaseTool


class TestDirectionsTool:
    """DirectionsTool 테스트"""

    def test_directions_tool_inherits_base_tool(self):
        """BaseTool을 상속하는지 확인"""
        from src.core.tools.plugins.directions import DirectionsTool

        assert issubclass(DirectionsTool, BaseTool)

    def test_directions_tool_has_correct_name(self):
        """name 속성이 올바른지 확인"""
        from src.core.tools.plugins.directions import DirectionsTool

        mock_service = MagicMock()
        tool = DirectionsTool(directions_service=mock_service)

        assert tool.name == "directions"

    def test_directions_tool_has_description(self):
        """description 속성이 있는지 확인"""
        from src.core.tools.plugins.directions import DirectionsTool

        mock_service = MagicMock()
        tool = DirectionsTool(directions_service=mock_service)

        assert "길찾기" in tool.description

    def test_directions_tool_get_tool_definitions(self):
        """get_tool_definitions가 올바른 정의를 반환"""
        from src.core.tools.plugins.directions import DirectionsTool

        mock_service = MagicMock()
        tool = DirectionsTool(directions_service=mock_service)

        definitions = tool.get_tool_definitions()

        assert isinstance(definitions, list)
        assert len(definitions) == 2  # get_directions, calculate_departure

        # get_directions 확인
        get_dirs = next(d for d in definitions if d["function"]["name"] == "get_directions")
        assert get_dirs["type"] == "function"
        assert "origin" in get_dirs["function"]["parameters"]["properties"]
        assert "destination" in get_dirs["function"]["parameters"]["properties"]

        # calculate_departure 확인
        calc_dep = next(d for d in definitions if d["function"]["name"] == "calculate_departure")
        assert "arrival_time" in calc_dep["function"]["parameters"]["properties"]
        assert "duration_minutes" in calc_dep["function"]["parameters"]["properties"]

    @pytest.mark.asyncio
    async def test_directions_tool_execute_get_directions(self):
        """get_directions 실행"""
        from src.core.tools.plugins.directions import DirectionsTool

        mock_service = MagicMock()
        mock_data = DirectionsData(
            origin="창동역",
            destination="강남역",
            duration_minutes=45,
            distance_meters=15000,
            fare=1500,
            transfer_count=1,
            departure_time=None,
            arrival_time=None,
            steps=[],
        )
        mock_service.get_directions = AsyncMock(return_value=mock_data)

        tool = DirectionsTool(directions_service=mock_service)
        result = await tool.execute(
            function_name="get_directions",
            origin="창동역",
            destination="강남역",
        )

        assert result["success"] is True
        assert "창동역" in result["message"]
        assert result["data"]["duration_minutes"] == 45

    @pytest.mark.asyncio
    async def test_directions_tool_execute_calculate_departure(self):
        """calculate_departure 실행"""
        from datetime import datetime

        from src.core.tools.plugins.directions import DirectionsTool

        mock_service = MagicMock()
        mock_service.calculate_departure_time.return_value = datetime(2025, 1, 15, 12, 15)

        tool = DirectionsTool(directions_service=mock_service)
        result = await tool.execute(
            function_name="calculate_departure",
            arrival_time="13:00",
            duration_minutes=45,
        )

        assert result["success"] is True
        assert "12:15" in result["message"]

    @pytest.mark.asyncio
    async def test_directions_tool_execute_unknown_function(self):
        """알 수 없는 함수 호출 시 에러"""
        from src.core.tools.plugins.directions import DirectionsTool

        mock_service = MagicMock()
        tool = DirectionsTool(directions_service=mock_service)

        with pytest.raises(ValueError, match="알 수 없는 함수"):
            await tool.execute(function_name="unknown_function")
