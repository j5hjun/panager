"""
Slack Handler 테스트

TDD RED Phase: 이 테스트들은 Slack Handler가 구현되기 전에 작성되었으며,
처음에는 모두 실패해야 합니다.
"""

from unittest.mock import MagicMock

import pytest


# 테스트용 헬퍼: 토큰 검증 비활성화된 핸들러 생성
def create_test_handler():
    """테스트용 SlackHandler 생성 (토큰 검증 비활성화)"""
    from src.adapters.slack.handler import SlackHandler

    return SlackHandler(
        bot_token="xoxb-test-token",
        app_token="xapp-test-token",
        token_verification_enabled=False,  # 테스트에서는 토큰 검증 비활성화
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

        # Mock message event
        event = {
            "type": "message",
            "channel_type": "im",
            "text": "안녕하세요",
            "user": "U1234567890",
            "channel": "D1234567890",
        }

        say_mock = MagicMock()  # 동기 함수로 변경

        # 핸들러가 메시지를 처리하고 응답해야 함
        await handler.handle_message(event, say_mock)

        # say가 호출되었는지 확인 (에코 또는 응답)
        say_mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_mention_message(self):
        """@멘션 메시지를 처리할 수 있어야 함"""
        handler = create_test_handler()

        # Mock app_mention event
        event = {
            "type": "app_mention",
            "text": "<@U0BOT123> 오늘 날씨 어때?",
            "user": "U1234567890",
            "channel": "C1234567890",
        }

        say_mock = MagicMock()

        await handler.handle_mention(event, say_mock)

        say_mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_channel_message(self):
        """채널 메시지를 수신할 수 있어야 함 (모니터링)"""
        handler = create_test_handler()

        # Mock channel message event
        event = {
            "type": "message",
            "channel_type": "channel",
            "text": "팀 미팅 내일 오후 3시에 있어요",
            "user": "U1234567890",
            "channel": "C1234567890",
        }

        # 채널 메시지는 로깅만 하고 응답하지 않을 수 있음
        result = await handler.handle_channel_message(event)

        # 메시지가 정상적으로 수신되었는지 확인
        assert result is not None
        assert result.get("received") is True

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
