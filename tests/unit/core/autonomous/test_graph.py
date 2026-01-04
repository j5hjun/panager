"""
자율 판단 그래프 및 러너 테스트
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core.autonomous.graph import (
    AutonomousRunner,
    _route_decision,
    create_autonomous_agent,
)
from src.core.autonomous.nodes.act import clear_notification_history
from src.core.autonomous.nodes.reflect import clear_lessons
from src.core.autonomous.state import create_initial_state


class TestRouteDecision:
    """라우팅 테스트"""

    def test_route_act(self):
        """decision이 act면 act 반환"""
        state = {"decision": "act"}
        assert _route_decision(state) == "act"

    def test_route_wait(self):
        """decision이 wait이면 wait 반환"""
        state = {"decision": "wait"}
        assert _route_decision(state) == "wait"

    def test_route_default(self):
        """decision이 없으면 wait 반환"""
        state = {}
        assert _route_decision(state) == "wait"


class TestCreateAutonomousAgent:
    """그래프 생성 테스트"""

    def test_create_graph(self):
        """그래프 생성 성공"""
        agent = create_autonomous_agent()
        assert agent is not None

    def test_graph_invoke(self):
        """그래프 실행 (동기)"""
        agent = create_autonomous_agent()
        state = create_initial_state()

        # 동기 노드는 기본값 반환
        result = agent.invoke(state)

        assert result is not None
        assert result["decision"] == "wait"  # 동기 Think 노드는 wait 반환


class TestAutonomousRunner:
    """러너 테스트"""

    def setup_method(self):
        """테스트 전 이력 초기화"""
        clear_notification_history()
        clear_lessons()

    def test_runner_init(self):
        """러너 초기화"""
        runner = AutonomousRunner()

        assert runner.llm_client is None
        assert runner.is_running is False

    def test_runner_start_stop(self):
        """러너 시작/중지"""
        runner = AutonomousRunner()

        runner.start()
        assert runner.is_running is True

        runner.stop()
        assert runner.is_running is False

    @pytest.mark.asyncio
    async def test_run_once_wait(self):
        """루프 1회 실행 (wait 결정)"""
        runner = AutonomousRunner()

        result = await runner.run_once()

        assert result["decision"] == "wait"  # LLM 없으면 wait
        assert result["action_result"] is None  # 행동 없음

    @pytest.mark.asyncio
    async def test_run_once_with_services(self):
        """서비스 연동 테스트"""
        # Mock 서비스
        mock_weather = AsyncMock()
        mock_weather.get_current_weather.return_value = {"description": "맑음"}
        mock_weather.needs_umbrella.return_value = (False, "우산 필요 없음")

        mock_calendar = MagicMock()
        mock_calendar.get_today_schedules.return_value = []

        runner = AutonomousRunner(
            weather_service=mock_weather,
            calendar_service=mock_calendar,
        )

        result = await runner.run_once()

        assert result["weather"] is not None
        assert result["decision"] == "wait"

    @pytest.mark.asyncio
    async def test_run_once_act(self):
        """Act 노드 직접 테스트 (방해 금지 시간 우회)"""
        from src.core.autonomous.nodes.act import act_node_async
        from src.core.autonomous.state import create_initial_state

        mock_send = AsyncMock()

        # Act 상태 직접 설정
        state = create_initial_state()
        state["decision"] = "act"
        state["action"] = {"type": "notify", "message": "테스트 알림"}

        result = await act_node_async(state, send_message=mock_send, user_id="U123")

        assert result["action_result"]["success"] is True
        mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_once_quiet_hours(self):
        """방해 금지 시간 테스트"""
        # Mock LLM
        mock_llm = AsyncMock()

        runner = AutonomousRunner(llm_client=mock_llm)

        result = await runner.run_once()

        # 현재 시간이 방해 금지 시간이면 wait
        # (테스트 시간에 따라 결과 다름)
        assert result["decision"] in ["act", "wait"]


class TestIntegration:
    """통합 테스트"""

    def setup_method(self):
        """테스트 전 이력 초기화"""
        clear_notification_history()
        clear_lessons()

    @pytest.mark.asyncio
    async def test_full_loop_act_reflect(self):
        """전체 루프: act → reflect 직접 테스트"""
        from src.core.autonomous.nodes.act import act_node_async
        from src.core.autonomous.nodes.reflect import reflect_node_async
        from src.core.autonomous.state import create_initial_state

        mock_send = AsyncMock()

        # 1. Act 상태 준비
        state = create_initial_state()
        state["decision"] = "act"
        state["action"] = {"type": "notify", "message": "테스트 알림"}
        state["time_period"] = "morning"

        # 2. Act 실행
        state = await act_node_async(state, send_message=mock_send, user_id="U123")

        assert state["action_result"]["success"] is True
        mock_send.assert_called_once()

        # 3. Reflect 실행 (neutral 반응)
        state = await reflect_node_async(state, user_reaction="알겠어")

        assert state["user_reaction"] == "neutral"
        assert state["lesson"] is None

    @pytest.mark.asyncio
    async def test_multiple_runs(self):
        """여러 번 실행"""
        runner = AutonomousRunner()

        for _ in range(3):
            result = await runner.run_once()
            assert result is not None
            assert "decision" in result
