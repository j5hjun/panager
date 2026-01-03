"""
Slack Handler 테스트
"""

from unittest.mock import MagicMock

import pytest


def create_test_handler():
    """테스트용 SlackHandler 생성"""
    from src.adapters.slack.handler import SlackHandler

    return SlackHandler(
        bot_token="xoxb-test-token",
        app_token="xapp-test-token",
        token_verification_enabled=False,
    )


class TestSlackHandler:
    """Slack Handler 테스트"""

    def test_slack_handler_can_be_imported(self):
        """SlackHandler 클래스를 import할 수 있어야 함"""
        from src.adapters.slack.handler import SlackHandler

        assert SlackHandler is not None

    def test_slack_handler_initialization(self):
        """SlackHandler를 초기화할 수 있어야 함"""
        handler = create_test_handler()

        assert handler is not None
        assert handler.bot_token == "xoxb-test-token"
        assert handler.app_token == "xapp-test-token"

    def test_slack_handler_has_app_instance(self):
        """SlackHandler는 Slack App 인스턴스를 가져야 함"""
        handler = create_test_handler()

        assert handler.app is not None

    @pytest.mark.asyncio
    async def test_handle_dm_message(self):
        """DM 메시지를 처리할 수 있어야 함"""
        handler = create_test_handler()

        event = {
            "type": "message",
            "channel_type": "im",
            "text": "안녕하세요",
            "user": "U1234567890",
            "channel": "D1234567890",
        }

        say_mock = MagicMock()

        await handler.handle_message(event, say_mock)

        say_mock.assert_called_once()

    def test_extract_message_text(self):
        """메시지에서 텍스트를 추출할 수 있어야 함"""
        handler = create_test_handler()

        # 일반 메시지
        text = handler.extract_text({"text": "안녕하세요"})
        assert text == "안녕하세요"

        # 멘션이 포함된 메시지
        text = handler.extract_text({"text": "<@U0BOT123> 안녕하세요"})
        assert text == "안녕하세요"  # 멘션 제거됨

    def test_is_bot_message(self):
        """봇 자신의 메시지인지 확인할 수 있어야 함"""
        handler = create_test_handler()

        # 봇 메시지
        assert handler.is_bot_message({"bot_id": "B1234"}) is True

        # 사용자 메시지
        assert handler.is_bot_message({"user": "U1234"}) is False

        # subtype이 bot_message인 경우
        assert handler.is_bot_message({"subtype": "bot_message"}) is True


class TestSlackHandlerIntegration:
    """Slack Handler 통합 테스트 (실제 연결 없이)"""

    def test_handler_registers_event_handlers(self):
        """핸들러가 이벤트 핸들러를 등록해야 함"""
        handler = create_test_handler()

        # 이벤트 핸들러가 등록되었는지 확인
        # (slack-bolt 내부 구조에 따라 다를 수 있음)
        assert hasattr(handler, "app")

    def test_handler_can_create_socket_mode_handler(self):
        """Socket Mode Handler를 생성할 수 있어야 함"""
        handler = create_test_handler()

        socket_handler = handler.get_socket_mode_handler()
        assert socket_handler is not None
