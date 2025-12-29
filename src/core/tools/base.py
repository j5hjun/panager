"""
Tool Base Class

모든 Tool Plugin이 상속해야 하는 기본 추상 클래스입니다.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """
    도구 플러그인 기본 클래스

    모든 도구는 이 클래스를 상속하고 필수 메서드를 구현해야 합니다.
    - name: 도구의 고유 식별자
    - description: 도구 설명
    - execute: 도구 실행 로직
    - get_tool_definitions: LLM Tool Calling 스키마 정의
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        도구의 고유 이름

        Returns:
            도구 이름 (예: 'weather', 'calendar')
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        도구 설명

        Returns:
            도구가 수행하는 작업에 대한 설명
        """
        pass

    @abstractmethod
    async def execute(self, function_name: str, **kwargs: Any) -> Any:
        """
        도구 실행

        Args:
            function_name: LLM이 호출한 함수 이름 (예: 'get_current_weather')
            **kwargs: 도구 실행에 필요한 파라미터

        Returns:
            도구 실행 결과
        """
        pass

    @abstractmethod
    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """
        LLM Tool Calling용 도구 정의 반환

        OpenAI/Groq 형식의 Tool Calling 스키마를 반환합니다.

        Returns:
            Tool 정의 리스트 (각 도구가 여러 함수를 제공할 수 있음)

        Example:
            [
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "description": "날씨 조회",
                        "parameters": {
                            "type": "object",
                            "properties": {...},
                            "required": [...]
                        }
                    }
                }
            ]
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name!r})>"
