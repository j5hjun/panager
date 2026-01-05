"""
Slack OAuth 명령어

OAuth 계정 연결/해제를 위한 슬래시 명령어 핸들러입니다.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# 지원하는 제공자 목록
SUPPORTED_PROVIDERS = ["google", "icloud"]


class SlackOAuthCommands:
    """
    Slack OAuth 명령어 핸들러

    /connect, /disconnect, /accounts 명령어를 처리합니다.
    """

    def __init__(self, oauth_service: Any, token_repository: Any):
        """
        SlackOAuthCommands 초기화

        Args:
            oauth_service: OAuthService 인스턴스
            token_repository: TokenRepository 인스턴스
        """
        self.oauth_service = oauth_service
        self.token_repository = token_repository
        self.icloud_service = None  # 나중에 설정

    def set_icloud_service(self, icloud_service: Any) -> None:
        """iCloudService 설정"""
        self.icloud_service = icloud_service

    def handle_connect(self, ack: Any, command: dict, respond: Any, client: Any = None) -> None:
        """
        /connect 명령어 처리

        사용법: /connect google
        """
        ack()

        user_id = command["user_id"]
        provider = command.get("text", "").strip().lower()

        # 제공자 미입력
        if not provider:
            respond(
                text="📎 사용법: `/connect [google|icloud]`\n\n"
                "예시:\n"
                "• `/connect google` - Google 계정 연결\n"
                "• `/connect icloud` - iCloud 계정 연결"
            )
            return

        # 지원하지 않는 제공자
        if provider not in SUPPORTED_PROVIDERS:
            respond(
                text=f"❌ 지원하지 않는 서비스입니다: `{provider}`\n\n"
                f"지원 서비스: {', '.join(SUPPORTED_PROVIDERS)}"
            )
            return

        # iCloud: 모달로 자격증명 입력
        if provider == "icloud":
            self._open_icloud_modal(command, respond, client)
            return

        # Google: OAuth URL 생성
        try:
            auth_url, state = self.oauth_service.generate_auth_url(provider, user_id, None)

            respond(
                text=f"🔗 *{provider.title()} 계정 연결*\n\n"
                f"아래 링크를 클릭하여 인증을 완료하세요:\n"
                f"<{auth_url}|{provider.title()} 연결하기>\n\n"
                f"_인증 완료 후 자동으로 연결됩니다._"
            )

            logger.info(f"OAuth URL 생성: {user_id}/{provider}")

        except Exception as e:
            logger.error(f"OAuth URL 생성 실패: {e}")
            respond(text=f"❌ 연결 URL 생성 실패: {str(e)}")

    def _open_icloud_modal(self, command: dict, respond: Any, client: Any) -> None:
        """iCloud 자격증명 입력 모달 열기"""
        if not client:
            respond(
                text="🍎 *iCloud 계정 연결*\n\n"
                "iCloud는 앱 암호가 필요합니다.\n"
                "1. https://appleid.apple.com 접속\n"
                "2. 보안 → 앱 암호 생성\n"
                "3. 생성된 암호를 DM으로 보내주세요:\n"
                "`icloud <Apple ID> <앱암호>`\n\n"
                "예: `icloud myemail@icloud.com xxxx-xxxx-xxxx-xxxx`"
            )
            return

        try:
            client.views_open(
                trigger_id=command["trigger_id"],
                view={
                    "type": "modal",
                    "callback_id": "icloud_credentials",
                    "title": {"type": "plain_text", "text": "iCloud 연결"},
                    "submit": {"type": "plain_text", "text": "연결"},
                    "close": {"type": "plain_text", "text": "취소"},
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "🍎 *iCloud 캘린더 연결*\n\n"
                                "앱 암호가 필요합니다:\n"
                                "1. https://appleid.apple.com 접속\n"
                                "2. 보안 → 앱 암호 생성",
                            },
                        },
                        {
                            "type": "input",
                            "block_id": "apple_id_block",
                            "element": {
                                "type": "plain_text_input",
                                "action_id": "apple_id",
                                "placeholder": {"type": "plain_text", "text": "example@icloud.com"},
                            },
                            "label": {"type": "plain_text", "text": "Apple ID"},
                        },
                        {
                            "type": "input",
                            "block_id": "app_password_block",
                            "element": {
                                "type": "plain_text_input",
                                "action_id": "app_password",
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "xxxx-xxxx-xxxx-xxxx",
                                },
                            },
                            "label": {"type": "plain_text", "text": "앱 암호"},
                        },
                    ],
                    "private_metadata": command["user_id"],
                },
            )
        except Exception as e:
            logger.error(f"모달 열기 실패: {e}")
            respond(text=f"❌ 모달 열기 실패: {str(e)}")

    def handle_disconnect(self, ack: Any, command: dict, respond: Any) -> None:
        """
        /disconnect 명령어 처리

        사용법: /disconnect google
        """
        ack()

        user_id = command["user_id"]
        provider = command.get("text", "").strip().lower()

        # 제공자 미입력
        if not provider:
            respond(
                text="📎 사용법: `/disconnect [google|icloud]`\n\n" "예시: `/disconnect google`"
            )
            return

        try:
            # 토큰 해지 및 삭제
            result = self.oauth_service.revoke_token(user_id, provider)

            if result:
                respond(
                    text=f"✅ *{provider.title()} 계정 연결 해제 완료*\n\n"
                    f"다시 연결하려면 `/connect {provider}`를 사용하세요."
                )
            else:
                respond(text=f"❌ 연결된 {provider.title()} 계정이 없습니다.")

        except Exception as e:
            logger.error(f"연결 해제 실패: {e}")
            respond(text=f"❌ 연결 해제 실패: {str(e)}")

    def handle_accounts(self, ack: Any, command: dict, respond: Any) -> None:
        """
        /accounts 명령어 처리

        연결된 계정 목록을 표시합니다.
        """
        ack()

        user_id = command["user_id"]

        try:
            # 사용자 토큰 목록 조회
            tokens = self.token_repository.list_user_tokens(user_id)

            if not tokens:
                respond(
                    text="📭 연결된 계정이 없습니다.\n\n"
                    "`/connect google` 또는 `/connect icloud`로 계정을 연결하세요."
                )
                return

            # 계정 목록 포맷
            lines = ["*📋 연결된 계정 목록*\n"]
            for token in tokens:
                provider = token["provider"]
                emoji = "🔵" if provider == "google" else "🍎"
                lines.append(f"{emoji} {provider.title()}")

            lines.append(f"\n_총 {len(tokens)}개 계정 연결됨_")
            lines.append("\n연결 해제: `/disconnect [provider]`")

            respond(text="\n".join(lines))

        except Exception as e:
            logger.error(f"계정 목록 조회 실패: {e}")
            respond(text=f"❌ 계정 목록 조회 실패: {str(e)}")

    def handle_icloud_modal_submit(self, ack: Any, body: dict, view: dict, client: Any) -> None:
        """
        iCloud 자격증명 모달 제출 처리
        """
        ack()

        user_id = view.get("private_metadata", "")
        values = view.get("state", {}).get("values", {})

        apple_id = values.get("apple_id_block", {}).get("apple_id", {}).get("value", "")
        app_password = values.get("app_password_block", {}).get("app_password", {}).get("value", "")

        if not apple_id or not app_password:
            logger.error("iCloud 자격증명 누락")
            return

        try:
            # 자격증명 검증
            if self.icloud_service and self.icloud_service.validate_credentials(
                apple_id, app_password
            ):
                # 저장
                self.icloud_service.save_credentials(user_id, apple_id, app_password)

                # 성공 메시지
                client.chat_postMessage(
                    channel=user_id,
                    text="✅ *iCloud 계정 연결 완료!*\n\n"
                    f"Apple ID: `{apple_id}`\n\n"
                    "이제 iCloud 캘린더를 사용할 수 있습니다.",
                )
                logger.info(f"iCloud 연결 성공: {user_id}")
            else:
                client.chat_postMessage(
                    channel=user_id,
                    text="❌ *iCloud 연결 실패*\n\n"
                    "Apple ID 또는 앱 암호가 올바르지 않습니다.\n"
                    "앱 암호를 다시 확인해주세요.",
                )

        except Exception as e:
            logger.error(f"iCloud 연결 처리 실패: {e}")
            client.chat_postMessage(
                channel=user_id,
                text=f"❌ iCloud 연결 중 오류 발생: {str(e)}",
            )

    def register_commands(self, app: Any) -> None:
        """
        Slack 앱에 명령어 핸들러 등록

        Args:
            app: Slack Bolt App 인스턴스
        """
        app.command("/connect")(self.handle_connect)
        app.command("/disconnect")(self.handle_disconnect)
        app.command("/accounts")(self.handle_accounts)

        # 모달 제출 핸들러
        app.view("icloud_credentials")(self.handle_icloud_modal_submit)

        logger.info("OAuth 명령어 등록 완료")
