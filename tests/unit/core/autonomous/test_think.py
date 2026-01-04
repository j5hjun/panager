"""
Think 노드 테스트
"""

import json
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from src.core.autonomous.nodes.think import (
    _apply_business_rules,
    _build_prompt,
    _parse_llm_response,
    think_node,
    think_node_async,
)
from src.core.autonomous.state import AgentState, create_initial_state


class TestBusinessRules:
    """비즈니스 규칙 테스트"""

    def test_quiet_hours_blocks(self):
        """방해 금지 시간에는 wait 반환"""
        state: AgentState = {
            "is_quiet_hours": True,
            "today_notification_count": 0,
        }
        result = _apply_business_rules(state)

        assert result["decision"] == "wait"
        assert "방해 금지" in result["reasoning"]

    def test_notification_limit_blocks(self):
        """알림 7회 초과 시 wait 반환"""
        state: AgentState = {
            "is_quiet_hours": False,
            "today_notification_count": 7,
        }
        result = _apply_business_rules(state)

        assert result["decision"] == "wait"
        assert "한도 초과" in result["reasoning"]

    def test_rules_pass(self):
        """규칙 통과 시 pending 반환"""
        state: AgentState = {
            "is_quiet_hours": False,
            "today_notification_count": 3,
        }
        result = _apply_business_rules(state)

        assert result["decision"] == "pending"


class TestBuildPrompt:
    """프롬프트 빌드 테스트"""

    def test_build_prompt_with_data(self):
        """데이터가 있을 때 프롬프트 생성"""
        state: AgentState = {
            "current_time": datetime(2026, 1, 4, 10, 0, 0),
            "time_period": "morning",
            "is_quiet_hours": False,
            "weather": {"description": "맑음"},
            "needs_umbrella": False,
            "today_schedules": [{"start_time": "2026-01-04T14:00:00", "title": "미팅"}],
            "upcoming_schedule": {"title": "미팅"},
            "minutes_to_next": 240,
            "today_notification_count": 2,
            "relevant_lessons": [],
        }
        prompt = _build_prompt(state)

        assert "morning" in prompt
        assert "맑음" in prompt
        assert "미팅" in prompt
        assert "2/7" in prompt

    def test_build_prompt_empty_data(self):
        """데이터가 없을 때도 프롬프트 생성"""
        state: AgentState = create_initial_state()
        prompt = _build_prompt(state)

        assert prompt is not None
        assert len(prompt) > 0


class TestParseLLMResponse:
    """LLM 응답 파싱 테스트"""

    def test_parse_valid_json(self):
        """정상 JSON 파싱"""
        response = json.dumps(
            {
                "reasoning": "비가 예보됨",
                "decision": "act",
                "confidence": 0.85,
                "action": {"type": "notify", "message": "우산 챙기세요!"},
            }
        )
        result = _parse_llm_response(response)

        assert result["decision"] == "act"
        assert result["confidence"] == 0.85
        assert result["action"]["type"] == "notify"

    def test_parse_json_block(self):
        """```json 블록 파싱"""
        response = """```json
{
    "reasoning": "테스트",
    "decision": "wait",
    "confidence": 0.5
}
```"""
        result = _parse_llm_response(response)

        assert result["decision"] == "wait"

    def test_parse_invalid_json(self):
        """잘못된 JSON은 wait 반환"""
        response = "이건 JSON이 아닙니다"
        result = _parse_llm_response(response)

        assert result["decision"] == "wait"
        assert result["confidence"] == 0.0


class TestThinkNode:
    """Think 노드 통합 테스트"""

    def test_sync_node_returns_wait(self):
        """동기 노드는 wait 반환"""
        state = create_initial_state()
        result = think_node(state)

        assert result["decision"] == "wait"

    @pytest.mark.asyncio
    async def test_async_node_without_llm(self):
        """LLM 없으면 wait 반환"""
        state = create_initial_state()
        state["is_quiet_hours"] = False
        state["today_notification_count"] = 0

        result = await think_node_async(state, llm_client=None)

        assert result["decision"] == "wait"
        assert "클라이언트" in result["reasoning"]

    @pytest.mark.asyncio
    async def test_async_node_quiet_hours(self):
        """방해 금지 시간에는 LLM 호출 없이 wait"""
        state = create_initial_state()
        state["is_quiet_hours"] = True

        mock_llm = AsyncMock()

        result = await think_node_async(state, llm_client=mock_llm)

        assert result["decision"] == "wait"
        assert "방해 금지" in result["reasoning"]
        mock_llm.chat.assert_not_called()

    @pytest.mark.asyncio
    async def test_async_node_with_llm_act(self):
        """LLM이 act 결정 시"""
        state = create_initial_state()
        state["is_quiet_hours"] = False
        state["today_notification_count"] = 0

        mock_llm = AsyncMock()
        mock_llm.chat.return_value = json.dumps(
            {
                "reasoning": "비 예보가 있고 외출 일정이 있음",
                "decision": "act",
                "confidence": 0.9,
                "action": {"type": "notify", "message": "우산 챙기세요!"},
            }
        )

        result = await think_node_async(state, llm_client=mock_llm)

        assert result["decision"] == "act"
        assert result["confidence"] == 0.9
        assert result["action"]["type"] == "notify"

    @pytest.mark.asyncio
    async def test_async_node_low_confidence(self):
        """신뢰도 낮으면 wait으로 변경"""
        state = create_initial_state()
        state["is_quiet_hours"] = False
        state["today_notification_count"] = 0

        mock_llm = AsyncMock()
        mock_llm.chat.return_value = json.dumps(
            {
                "reasoning": "잘 모르겠음",
                "decision": "act",
                "confidence": 0.5,  # 0.7 미만
                "action": {"type": "notify", "message": "테스트"},
            }
        )

        result = await think_node_async(state, llm_client=mock_llm)

        assert result["decision"] == "wait"
        assert "신뢰도 부족" in result["reasoning"]

    @pytest.mark.asyncio
    async def test_async_node_llm_error(self):
        """LLM 에러 시 wait 반환"""
        state = create_initial_state()
        state["is_quiet_hours"] = False
        state["today_notification_count"] = 0

        mock_llm = AsyncMock()
        mock_llm.chat.side_effect = Exception("API Error")

        result = await think_node_async(state, llm_client=mock_llm)

        assert result["decision"] == "wait"
        assert "실패" in result["reasoning"]
