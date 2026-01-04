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

    async def handle_connect(self, ack: Any, command: dict, respond: Any) -> None:
        """
        /connect 명령어 처리

        사용법: /connect google
        """
        await ack()

        user_id = command["user_id"]
        provider = command.get("text", "").strip().lower()

        # 제공자 미입력
        if not provider:
            await respond(
                text="📎 사용법: `/connect [google|icloud]`\n\n"
                "예시:\n"
                "• `/connect google` - Google 계정 연결\n"
                "• `/connect icloud` - iCloud 계정 연결"
            )
            return

        # 지원하지 않는 제공자
        if provider not in SUPPORTED_PROVIDERS:
            await respond(
                text=f"❌ 지원하지 않는 서비스입니다: `{provider}`\n\n"
                f"지원 서비스: {', '.join(SUPPORTED_PROVIDERS)}"
            )
            return

        try:
            # OAuth URL 생성
            auth_url, state = self.oauth_service.generate_auth_url(provider, user_id, None)

            # 사용자에게 URL 전송
            await respond(
                text=f"🔗 *{provider.title()} 계정 연결*\n\n"
                f"아래 링크를 클릭하여 인증을 완료하세요:\n"
                f"<{auth_url}|{provider.title()} 연결하기>\n\n"
                f"_인증 완료 후 자동으로 연결됩니다._"
            )

            logger.info(f"OAuth URL 생성: {user_id}/{provider}")

        except Exception as e:
            logger.error(f"OAuth URL 생성 실패: {e}")
            await respond(text=f"❌ 연결 URL 생성 실패: {str(e)}")

    async def handle_disconnect(self, ack: Any, command: dict, respond: Any) -> None:
        """
        /disconnect 명령어 처리

        사용법: /disconnect google
        """
        await ack()

        user_id = command["user_id"]
        provider = command.get("text", "").strip().lower()

        # 제공자 미입력
        if not provider:
            await respond(
                text="📎 사용법: `/disconnect [google|icloud]`\n\n" "예시: `/disconnect google`"
            )
            return

        try:
            # 토큰 해지 및 삭제
            result = self.oauth_service.revoke_token(user_id, provider)

            if result:
                await respond(
                    text=f"✅ *{provider.title()} 계정 연결 해제 완료*\n\n"
                    f"다시 연결하려면 `/connect {provider}`를 사용하세요."
                )
            else:
                await respond(text=f"❌ 연결된 {provider.title()} 계정이 없습니다.")

        except Exception as e:
            logger.error(f"연결 해제 실패: {e}")
            await respond(text=f"❌ 연결 해제 실패: {str(e)}")

    async def handle_accounts(self, ack: Any, command: dict, respond: Any) -> None:
        """
        /accounts 명령어 처리

        연결된 계정 목록을 표시합니다.
        """
        await ack()

        user_id = command["user_id"]

        try:
            # 사용자 토큰 목록 조회
            tokens = self.token_repository.list_user_tokens(user_id)

            if not tokens:
                await respond(
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

            await respond(text="\n".join(lines))

        except Exception as e:
            logger.error(f"계정 목록 조회 실패: {e}")
            await respond(text=f"❌ 계정 목록 조회 실패: {str(e)}")

    def register_commands(self, app: Any) -> None:
        """
        Slack 앱에 명령어 핸들러 등록

        Args:
            app: Slack Bolt App 인스턴스
        """
        app.command("/connect")(self.handle_connect)
        app.command("/disconnect")(self.handle_disconnect)
        app.command("/accounts")(self.handle_accounts)

        logger.info("OAuth 명령어 등록 완료")
