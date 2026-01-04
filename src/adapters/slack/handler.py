"""
Slack Handler

Slack Bot의 메시지 처리를 담당하는 핸들러입니다.
"""

import logging
import re
from collections.abc import Callable
from typing import Any

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

logger = logging.getLogger(__name__)


class SlackHandler:
    """
    Slack 메시지 핸들러

    DM(Direct Message)을 통한 1:1 대화를 처리합니다.
    """

    def __init__(
        self,
        bot_token: str,
        app_token: str,
        message_callback: Callable[[dict], str] | None = None,
        token_verification_enabled: bool = True,
    ):
        """
        SlackHandler 초기화

        Args:
            bot_token: Slack Bot User OAuth Token (xoxb-...)
            app_token: Slack App-Level Token (xapp-...)
            message_callback: 메시지 처리 콜백 함수 (LLM 연동 시 사용)
            token_verification_enabled: 토큰 검증 활성화 여부 (테스트 시 False)
        """
        self.bot_token = bot_token
        self.app_token = app_token
        self.message_callback = message_callback

        # 최근 대화한 사용자 ID (자율 판단 알림용)
        self._active_user_id: str | None = None

        # Slack App 초기화
        self.app = App(
            token=bot_token,
            token_verification_enabled=token_verification_enabled,
        )

        # 이벤트 핸들러 등록
        self._register_handlers()

        logger.info("SlackHandler 초기화 완료")

    def _register_handlers(self) -> None:
        """Slack 이벤트 핸들러 등록"""

        @self.app.event("message")
        def handle_message_event(event: dict, say: Callable, logger: Any) -> None:
            """메시지 이벤트 처리"""
            if self.is_bot_message(event):
                return

            channel_type = event.get("channel_type", "")

            if channel_type == "im":
                logger.info(f"DM 메시지 수신: {event.get('text', '')[:50]}")
                self._handle_dm(event, say)

    def _handle_dm(self, event: dict, say: Callable) -> None:
        """DM 메시지 처리"""
        text = self.extract_text(event)
        user = event.get("user", "unknown")

        # 최근 대화한 사용자 ID 저장 (자율 판단 알림용)
        if user and user != "unknown":
            self._active_user_id = user
            logger.debug(f"활성 사용자 ID 업데이트: {user}")

        logger.info(f"DM from {user}: {text}")

        # 콜백이 있으면 사용, 없으면 에코
        if self.message_callback:
            response = self.message_callback({"type": "dm", "text": text, "user": user})
        else:
            response = f"💬 받은 메시지: {text}"

        say(response)

    # ==================== Public Methods (테스트용) ====================

    async def handle_message(self, event: dict, say: Callable) -> None:
        """DM 메시지 처리 (테스트용 public 메서드)"""
        self._handle_dm(event, say)

    # ==================== Utility Methods ====================

    def extract_text(self, event: dict) -> str:
        """
        메시지에서 텍스트 추출

        멘션 태그(<@U...>)를 제거하고 순수 텍스트만 반환
        """
        text = event.get("text", "")

        # <@U1234567890> 형태의 멘션 제거
        text = re.sub(r"<@U[A-Z0-9]+>", "", text)

        # 앞뒤 공백 제거
        text = text.strip()

        return text

    def is_bot_message(self, event: dict) -> bool:
        """봇 자신의 메시지인지 확인"""
        # bot_id가 있으면 봇 메시지
        if event.get("bot_id"):
            return True

        # subtype이 bot_message이면 봇 메시지
        if event.get("subtype") == "bot_message":
            return True

        return False

    def get_active_user_id(self) -> str | None:
        """최근 대화한 사용자 ID 반환 (자율 판단 알림용)"""
        return self._active_user_id

    def set_active_user_id(self, user_id: str) -> None:
        """활성 사용자 ID 수동 설정"""
        self._active_user_id = user_id
        logger.info(f"활성 사용자 ID 설정: {user_id}")

    def get_socket_mode_handler(self) -> SocketModeHandler:
        """Socket Mode Handler 반환"""
        return SocketModeHandler(self.app, self.app_token)

    def start(self) -> None:
        """봇 시작 (blocking)"""
        logger.info("Slack Bot 시작...")
        handler = self.get_socket_mode_handler()
        handler.start()

    async def start_async(self) -> None:
        """봇 비동기 시작"""
        logger.info("Slack Bot 비동기 시작...")
        handler = self.get_socket_mode_handler()
        await handler.start_async()

    def send_message(self, channel: str, text: str) -> None:
        """
        채널에 메시지 전송 (능동적 알림용)

        Args:
            channel: 채널 ID 또는 사용자 ID
            text: 전송할 메시지
        """
        try:
            self.app.client.chat_postMessage(channel=channel, text=text)
            logger.info(f"메시지 전송 완료: {channel}")
        except Exception as e:
            logger.error(f"메시지 전송 실패: {channel} - {e}")
