"""
Act 노드 테스트
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from src.core.autonomous.nodes.act import (
    _record_notification,
    act_node,
    act_node_async,
    clear_notification_history,
    get_notification_history,
    get_today_notification_count,
)
from src.core.autonomous.state import create_initial_state


class TestActNode:
    """Act 노드 기본 테스트"""

    def setup_method(self):
        """테스트 전 알림 이력 초기화"""
        clear_notification_history()

    def test_act_node_skips_when_wait(self):
        """decision이 wait이면 스킵"""
        state = create_initial_state()
        state["decision"] = "wait"

        result = act_node(state)

        assert result["action_result"] is None

    def test_act_node_skips_when_no_action(self):
        """action이 없으면 에러 반환"""
        state = create_initial_state()
        state["decision"] = "act"
        state["action"] = None

        result = act_node(state)

        assert result["action_result"]["success"] is False
        assert "No action" in result["action_result"]["error"]

    def test_act_node_executes_action(self):
        """action이 있으면 실행"""
        state = create_initial_state()
        state["decision"] = "act"
        state["action"] = {"type": "notify", "message": "테스트 알림"}

        result = act_node(state)

        assert result["action_result"]["success"] is True
        assert result["action_result"]["action_type"] == "notify"
        assert result["action_result"]["message"] == "테스트 알림"

    def test_act_node_records_notification(self):
        """알림이 기록되어야 함"""
        state = create_initial_state()
        state["decision"] = "act"
        state["action"] = {"type": "notify", "message": "기록 테스트"}

        act_node(state)

        history = get_notification_history()
        assert len(history) == 1
        assert history[0]["message"] == "기록 테스트"


class TestActNodeAsync:
    """Act 노드 비동기 테스트"""

    def setup_method(self):
        """테스트 전 알림 이력 초기화"""
        clear_notification_history()

    @pytest.mark.asyncio
    async def test_async_skips_when_wait(self):
        """decision이 wait이면 스킵"""
        state = create_initial_state()
        state["decision"] = "wait"

        result = await act_node_async(state)

        assert result["action_result"] is None

    @pytest.mark.asyncio
    async def test_async_sends_notification(self):
        """알림 전송 테스트"""
        state = create_initial_state()
        state["decision"] = "act"
        state["action"] = {"type": "notify", "message": "비동기 알림"}
        state["today_notification_count"] = 0

        mock_send = AsyncMock()

        result = await act_node_async(
            state,
            send_message=mock_send,
            user_id="U123",
        )

        assert result["action_result"]["success"] is True
        mock_send.assert_called_once()
        assert result["today_notification_count"] == 1

    @pytest.mark.asyncio
    async def test_async_without_send_message(self):
        """send_message 없으면 에러"""
        state = create_initial_state()
        state["decision"] = "act"
        state["action"] = {"type": "notify", "message": "알림"}

        result = await act_node_async(state, send_message=None, user_id="U123")

        assert result["action_result"]["success"] is False
        assert "not provided" in result["action_result"]["error"]

    @pytest.mark.asyncio
    async def test_async_handles_send_error(self):
        """전송 에러 핸들링"""
        state = create_initial_state()
        state["decision"] = "act"
        state["action"] = {"type": "notify", "message": "에러 테스트"}

        mock_send = AsyncMock(side_effect=Exception("Slack Error"))

        result = await act_node_async(
            state,
            send_message=mock_send,
            user_id="U123",
        )

        assert result["action_result"]["success"] is False
        assert "Slack Error" in result["action_result"]["error"]

    @pytest.mark.asyncio
    async def test_async_supports_sync_send_message(self):
        """동기 send_message도 지원"""
        state = create_initial_state()
        state["decision"] = "act"
        state["action"] = {"type": "notify", "message": "동기 테스트"}
        state["today_notification_count"] = 0

        mock_send = MagicMock()

        result = await act_node_async(
            state,
            send_message=mock_send,
            user_id="U123",
        )

        assert result["action_result"]["success"] is True
        mock_send.assert_called_once()


class TestNotificationHistory:
    """알림 이력 테스트"""

    def setup_method(self):
        """테스트 전 알림 이력 초기화"""
        clear_notification_history()

    def test_record_notification(self):
        """알림 기록 테스트"""
        action = {"type": "notify", "message": "테스트"}
        result = {"success": True, "timestamp": datetime.now().isoformat()}

        _record_notification(action, result)

        history = get_notification_history()
        assert len(history) == 1
        assert history[0]["success"] is True

    def test_history_limit(self):
        """이력 최대 100개 유지"""
        for i in range(105):
            _record_notification(
                {"type": "notify", "message": f"msg{i}"},
                {"success": True, "timestamp": datetime.now().isoformat()},
            )

        history = get_notification_history()
        assert len(history) == 100
        assert history[0]["message"] == "msg5"  # 처음 5개 삭제됨

    def test_today_notification_count(self):
        """오늘 알림 횟수 계산"""
        today = datetime.now().isoformat()

        _record_notification(
            {"type": "notify", "message": "오늘1"},
            {"success": True, "timestamp": today},
        )
        _record_notification(
            {"type": "notify", "message": "오늘2"},
            {"success": True, "timestamp": today},
        )
        _record_notification(
            {"type": "notify", "message": "실패"},
            {"success": False, "timestamp": today},
        )

        count = get_today_notification_count()
        assert count == 2

    def test_clear_history(self):
        """이력 초기화"""
        _record_notification(
            {"type": "notify", "message": "테스트"},
            {"success": True, "timestamp": datetime.now().isoformat()},
        )

        clear_notification_history()

        history = get_notification_history()
        assert len(history) == 0
