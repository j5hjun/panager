"""
Tool Registry

도구 플러그인을 동적으로 등록하고 관리하는 레지스트리입니다.
"""

import logging
from typing import Any

from src.core.tools.base import BaseTool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    도구 레지스트리 (싱글톤)

    Tool Plugin들을 등록하고 관리합니다.
    - register: 도구 등록
    - unregister: 도구 해제
    - get: 이름으로 도구 조회
    - list_tools: 등록된 도구 이름 목록
    - get_all_tool_definitions: 모든 도구의 LLM 스키마 반환
    """

    _instance: "ToolRegistry | None" = None
    _tools: dict[str, BaseTool]

    def __new__(cls) -> "ToolRegistry":
        """싱글톤 패턴 구현"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools = {}
            logger.info("ToolRegistry 인스턴스 생성")
        return cls._instance

    def register(self, tool: BaseTool) -> None:
        """
        도구 등록

        Args:
            tool: 등록할 도구 인스턴스

        Raises:
            ValueError: 동일한 이름의 도구가 이미 등록된 경우
        """
        if tool.name in self._tools:
            raise ValueError(
                f"이미 등록된 도구입니다: '{tool.name}'. " f"중복 등록은 허용되지 않습니다."
            )

        self._tools[tool.name] = tool
        logger.info(f"도구 등록 완료: {tool.name} - {tool.description}")

    def unregister(self, name: str) -> bool:
        """
        도구 해제

        Args:
            name: 해제할 도구 이름

        Returns:
            True if 성공적으로 해제됨, False if 도구가 존재하지 않음
        """
        if name in self._tools:
            del self._tools[name]
            logger.info(f"도구 해제 완료: {name}")
            return True
        else:
            logger.warning(f"해제 실패: 등록되지 않은 도구 '{name}'")
            return False

    def get(self, name: str) -> BaseTool | None:
        """
        이름으로 도구 조회

        Args:
            name: 조회할 도구 이름

        Returns:
            도구 인스턴스 또는 None (존재하지 않을 경우)
        """
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        """
        등록된 모든 도구 이름 반환

        Returns:
            도구 이름 리스트
        """
        return list(self._tools.keys())

    def get_all_tools(self) -> list[BaseTool]:
        """
        등록된 모든 도구 인스턴스 반환

        Returns:
            도구 인스턴스 리스트
        """
        return list(self._tools.values())

    def get_all_tool_definitions(self) -> list[dict[str, Any]]:
        """
        모든 도구의 LLM Tool 정의 반환

        각 도구의 get_tool_definitions() 결과를 합쳐서 반환합니다.

        Returns:
            LLM Tool Calling용 도구 정의 리스트
        """
        all_definitions: list[dict[str, Any]] = []

        for tool in self._tools.values():
            definitions = tool.get_tool_definitions()
            all_definitions.extend(definitions)

        logger.debug(f"총 {len(all_definitions)}개의 도구 정의 로드")
        return all_definitions

    def clear(self) -> None:
        """
        모든 도구 등록 해제 (테스트용)
        """
        self._tools.clear()
        logger.info("모든 도구 등록 해제됨")

    def __len__(self) -> int:
        return len(self._tools)

    def __repr__(self) -> str:
        return f"<ToolRegistry(tools={list(self._tools.keys())})>"
