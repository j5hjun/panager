"""
Tool Base Class 테스트

BaseTool 추상 클래스의 인터페이스를 검증합니다.
"""

from abc import ABC
from typing import Any

import pytest


class TestBaseTool:
    """BaseTool 추상 클래스 테스트"""

    def test_base_tool_is_abstract_class(self):
        """BaseTool이 ABC를 상속하는지 확인"""
        from src.core.tools.base import BaseTool

        assert issubclass(BaseTool, ABC)

    def test_base_tool_cannot_be_instantiated(self):
        """BaseTool을 직접 인스턴스화할 수 없음"""
        from src.core.tools.base import BaseTool

        with pytest.raises(TypeError):
            BaseTool()  # type: ignore

    def test_base_tool_has_required_abstract_methods(self):
        """BaseTool이 필수 추상 메서드를 정의하는지 확인"""
        from src.core.tools.base import BaseTool

        # 추상 메서드 확인
        abstract_methods = getattr(BaseTool, "__abstractmethods__", set())
        assert "execute" in abstract_methods
        assert "get_tool_definitions" in abstract_methods

    def test_base_tool_has_name_property(self):
        """BaseTool이 name 속성을 가지는지 확인"""
        from src.core.tools.base import BaseTool

        abstract_methods = getattr(BaseTool, "__abstractmethods__", set())
        assert "name" in abstract_methods

    def test_base_tool_has_description_property(self):
        """BaseTool이 description 속성을 가지는지 확인"""
        from src.core.tools.base import BaseTool

        abstract_methods = getattr(BaseTool, "__abstractmethods__", set())
        assert "description" in abstract_methods


class TestConcreteToolImplementation:
    """BaseTool을 상속한 구체 클래스 테스트"""

    def test_concrete_tool_can_be_instantiated(self):
        """BaseTool을 상속한 클래스는 인스턴스화 가능"""
        from src.core.tools.base import BaseTool

        class MockTool(BaseTool):
            @property
            def name(self) -> str:
                return "mock_tool"

            @property
            def description(self) -> str:
                return "테스트용 모의 도구"

            async def execute(self, function_name: str, **kwargs: Any) -> Any:
                return {"result": "success"}

            def get_tool_definitions(self) -> list[dict[str, Any]]:
                return [
                    {
                        "type": "function",
                        "function": {
                            "name": self.name,
                            "description": self.description,
                            "parameters": {"type": "object", "properties": {}},
                        },
                    }
                ]

        tool = MockTool()
        assert tool.name == "mock_tool"
        assert tool.description == "테스트용 모의 도구"

    @pytest.mark.asyncio
    async def test_concrete_tool_execute_returns_result(self):
        """execute 메서드가 결과를 반환"""
        from src.core.tools.base import BaseTool

        class MockTool(BaseTool):
            @property
            def name(self) -> str:
                return "mock_tool"

            @property
            def description(self) -> str:
                return "테스트용 모의 도구"

            async def execute(self, function_name: str, **kwargs: Any) -> Any:
                return {"city": kwargs.get("city", "Seoul"), "temp": 20}

            def get_tool_definitions(self) -> list[dict[str, Any]]:
                return []

        tool = MockTool()
        result = await tool.execute(function_name="test", city="Busan")
        assert result == {"city": "Busan", "temp": 20}

    def test_concrete_tool_get_tool_definitions_returns_list(self):
        """get_tool_definitions가 도구 정의 리스트를 반환"""
        from src.core.tools.base import BaseTool

        class MockTool(BaseTool):
            @property
            def name(self) -> str:
                return "mock_tool"

            @property
            def description(self) -> str:
                return "테스트용 모의 도구"

            async def execute(self, function_name: str, **kwargs: Any) -> Any:
                return {}

            def get_tool_definitions(self) -> list[dict[str, Any]]:
                return [
                    {
                        "type": "function",
                        "function": {
                            "name": self.name,
                            "description": self.description,
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "검색어"}
                                },
                                "required": ["query"],
                            },
                        },
                    }
                ]

        tool = MockTool()
        definitions = tool.get_tool_definitions()

        assert isinstance(definitions, list)
        assert len(definitions) == 1
        assert definitions[0]["type"] == "function"
        assert definitions[0]["function"]["name"] == "mock_tool"
