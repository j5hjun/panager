"""
Tool Registry 테스트

ToolRegistry 클래스의 도구 등록/조회/해제 기능을 검증합니다.
"""

from typing import Any

import pytest


class TestToolRegistry:
    """ToolRegistry 클래스 테스트"""

    def test_registry_is_singleton(self):
        """ToolRegistry가 싱글톤 패턴을 따르는지 확인"""
        from src.core.tools.registry import ToolRegistry

        registry1 = ToolRegistry()
        registry2 = ToolRegistry()

        assert registry1 is registry2

    def test_registry_register_tool(self):
        """도구를 등록할 수 있음"""
        from src.core.tools.base import BaseTool
        from src.core.tools.registry import ToolRegistry

        class MockTool(BaseTool):
            @property
            def name(self) -> str:
                return "test_register_tool"

            @property
            def description(self) -> str:
                return "등록 테스트용 도구"

            async def execute(self, function_name: str, **kwargs: Any) -> Any:
                return {}

            def get_tool_definitions(self) -> list[dict[str, Any]]:
                return []

        registry = ToolRegistry()
        registry.clear()  # 테스트 전 초기화

        tool = MockTool()
        registry.register(tool)

        assert "test_register_tool" in registry.list_tools()

    def test_registry_get_tool(self):
        """등록된 도구를 이름으로 조회할 수 있음"""
        from src.core.tools.base import BaseTool
        from src.core.tools.registry import ToolRegistry

        class MockTool(BaseTool):
            @property
            def name(self) -> str:
                return "test_get_tool"

            @property
            def description(self) -> str:
                return "조회 테스트용 도구"

            async def execute(self, function_name: str, **kwargs: Any) -> Any:
                return {"status": "ok"}

            def get_tool_definitions(self) -> list[dict[str, Any]]:
                return []

        registry = ToolRegistry()
        registry.clear()

        tool = MockTool()
        registry.register(tool)

        retrieved = registry.get("test_get_tool")
        assert retrieved is tool
        assert retrieved.name == "test_get_tool"

    def test_registry_get_nonexistent_tool_returns_none(self):
        """존재하지 않는 도구 조회 시 None 반환"""
        from src.core.tools.registry import ToolRegistry

        registry = ToolRegistry()
        registry.clear()

        result = registry.get("nonexistent_tool")
        assert result is None

    def test_registry_list_tools(self):
        """등록된 모든 도구 이름을 조회할 수 있음"""
        from src.core.tools.base import BaseTool
        from src.core.tools.registry import ToolRegistry

        class MockToolA(BaseTool):
            @property
            def name(self) -> str:
                return "tool_a"

            @property
            def description(self) -> str:
                return "도구 A"

            async def execute(self, function_name: str, **kwargs: Any) -> Any:
                return {}

            def get_tool_definitions(self) -> list[dict[str, Any]]:
                return []

        class MockToolB(BaseTool):
            @property
            def name(self) -> str:
                return "tool_b"

            @property
            def description(self) -> str:
                return "도구 B"

            async def execute(self, function_name: str, **kwargs: Any) -> Any:
                return {}

            def get_tool_definitions(self) -> list[dict[str, Any]]:
                return []

        registry = ToolRegistry()
        registry.clear()

        registry.register(MockToolA())
        registry.register(MockToolB())

        tool_names = registry.list_tools()
        assert "tool_a" in tool_names
        assert "tool_b" in tool_names
        assert len(tool_names) == 2

    def test_registry_unregister_tool(self):
        """도구를 해제할 수 있음"""
        from src.core.tools.base import BaseTool
        from src.core.tools.registry import ToolRegistry

        class MockTool(BaseTool):
            @property
            def name(self) -> str:
                return "tool_to_unregister"

            @property
            def description(self) -> str:
                return "해제 테스트용 도구"

            async def execute(self, function_name: str, **kwargs: Any) -> Any:
                return {}

            def get_tool_definitions(self) -> list[dict[str, Any]]:
                return []

        registry = ToolRegistry()
        registry.clear()

        tool = MockTool()
        registry.register(tool)
        assert "tool_to_unregister" in registry.list_tools()

        registry.unregister("tool_to_unregister")
        assert "tool_to_unregister" not in registry.list_tools()

    def test_registry_duplicate_registration_raises_error(self):
        """동일한 이름의 도구 중복 등록 시 에러 발생"""
        from src.core.tools.base import BaseTool
        from src.core.tools.registry import ToolRegistry

        class MockToolA(BaseTool):
            @property
            def name(self) -> str:
                return "duplicate_tool"

            @property
            def description(self) -> str:
                return "첫 번째 도구"

            async def execute(self, function_name: str, **kwargs: Any) -> Any:
                return {}

            def get_tool_definitions(self) -> list[dict[str, Any]]:
                return []

        class MockToolB(BaseTool):
            @property
            def name(self) -> str:
                return "duplicate_tool"

            @property
            def description(self) -> str:
                return "두 번째 도구 (중복)"

            async def execute(self, function_name: str, **kwargs: Any) -> Any:
                return {}

            def get_tool_definitions(self) -> list[dict[str, Any]]:
                return []

        registry = ToolRegistry()
        registry.clear()

        registry.register(MockToolA())

        with pytest.raises(ValueError, match="이미 등록된 도구"):
            registry.register(MockToolB())

    def test_registry_get_all_tool_definitions(self):
        """모든 도구의 LLM Tool 정의를 한 번에 조회"""
        from src.core.tools.base import BaseTool
        from src.core.tools.registry import ToolRegistry

        class MockToolA(BaseTool):
            @property
            def name(self) -> str:
                return "def_tool_a"

            @property
            def description(self) -> str:
                return "정의 테스트 도구 A"

            async def execute(self, function_name: str, **kwargs: Any) -> Any:
                return {}

            def get_tool_definitions(self) -> list[dict[str, Any]]:
                return [
                    {
                        "type": "function",
                        "function": {
                            "name": "def_tool_a",
                            "description": self.description,
                            "parameters": {"type": "object", "properties": {}},
                        },
                    }
                ]

        class MockToolB(BaseTool):
            @property
            def name(self) -> str:
                return "def_tool_b"

            @property
            def description(self) -> str:
                return "정의 테스트 도구 B"

            async def execute(self, function_name: str, **kwargs: Any) -> Any:
                return {}

            def get_tool_definitions(self) -> list[dict[str, Any]]:
                return [
                    {
                        "type": "function",
                        "function": {
                            "name": "def_tool_b_func1",
                            "description": "B의 기능 1",
                            "parameters": {"type": "object", "properties": {}},
                        },
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "def_tool_b_func2",
                            "description": "B의 기능 2",
                            "parameters": {"type": "object", "properties": {}},
                        },
                    },
                ]

        registry = ToolRegistry()
        registry.clear()

        registry.register(MockToolA())
        registry.register(MockToolB())

        all_definitions = registry.get_all_tool_definitions()

        assert isinstance(all_definitions, list)
        assert len(all_definitions) == 3  # A: 1개, B: 2개

        function_names = [d["function"]["name"] for d in all_definitions]
        assert "def_tool_a" in function_names
        assert "def_tool_b_func1" in function_names
        assert "def_tool_b_func2" in function_names

    def test_registry_clear(self):
        """모든 도구를 초기화할 수 있음"""
        from src.core.tools.base import BaseTool
        from src.core.tools.registry import ToolRegistry

        class MockTool(BaseTool):
            @property
            def name(self) -> str:
                return "tool_to_clear"

            @property
            def description(self) -> str:
                return "초기화 테스트용 도구"

            async def execute(self, function_name: str, **kwargs: Any) -> Any:
                return {}

            def get_tool_definitions(self) -> list[dict[str, Any]]:
                return []

        registry = ToolRegistry()
        registry.register(MockTool())
        assert len(registry.list_tools()) > 0

        registry.clear()
        assert len(registry.list_tools()) == 0
