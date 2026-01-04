"""
Slack OAuth 명령어 테스트

TDD RED Phase: Slack 슬래시 명령어 테스트
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch


class TestSlackOAuthCommands:
    """Slack OAuth 명령어 테스트"""

    @pytest.fixture
    def mock_oauth_service(self):
        """Mock OAuthService"""
        service = Mock()
        service.generate_auth_url.return_value = (
            "https://accounts.google.com/o/oauth2/auth?...",
            "test_state_123",
        )
        service.revoke_token.return_value = True
        service.get_token.return_value = {
            "provider": "google",
            "access_token": "test_token",
        }
        return service

    @pytest.fixture
    def mock_token_repository(self):
        """Mock TokenRepository"""
        repo = Mock()
        repo.list_user_tokens.return_value = [
            {"provider": "google", "access_token": "token1"},
            {"provider": "icloud", "access_token": "token2"},
        ]
        return repo

    @pytest.fixture
    def commands(self, mock_oauth_service, mock_token_repository):
        """SlackOAuthCommands 인스턴스"""
        from src.adapters.slack.oauth_commands import SlackOAuthCommands

        return SlackOAuthCommands(
            oauth_service=mock_oauth_service,
            token_repository=mock_token_repository,
        )

    @pytest.mark.asyncio
    async def test_connect_google_command(self, commands, mock_oauth_service):
        """'/connect google' 명령어 처리"""
        # Mock Slack context
        ack = AsyncMock()
        respond = AsyncMock()
        command = {
            "user_id": "U123",
            "text": "google",
        }

        await commands.handle_connect(ack, command, respond)

        # ack 호출 확인
        ack.assert_called_once()

        # OAuth URL 생성 확인
        mock_oauth_service.generate_auth_url.assert_called_once_with("google", "U123", None)

        # 응답에 URL 포함 확인
        respond.assert_called_once()
        response_text = respond.call_args[1].get("text", "") or respond.call_args[0][0]
        assert "https://accounts.google.com" in response_text or "연결" in response_text

    @pytest.mark.asyncio
    async def test_connect_invalid_provider(self, commands):
        """지원하지 않는 제공자"""
        ack = AsyncMock()
        respond = AsyncMock()
        command = {
            "user_id": "U123",
            "text": "invalid_provider",
        }

        await commands.handle_connect(ack, command, respond)

        ack.assert_called_once()
        respond.assert_called_once()
        response_text = str(respond.call_args)
        assert "지원" in response_text or "google" in response_text.lower()

    @pytest.mark.asyncio
    async def test_connect_no_provider(self, commands):
        """제공자 미입력"""
        ack = AsyncMock()
        respond = AsyncMock()
        command = {
            "user_id": "U123",
            "text": "",
        }

        await commands.handle_connect(ack, command, respond)

        ack.assert_called_once()
        respond.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_command(self, commands, mock_oauth_service):
        """'/disconnect google' 명령어 처리"""
        ack = AsyncMock()
        respond = AsyncMock()
        command = {
            "user_id": "U123",
            "text": "google",
        }

        await commands.handle_disconnect(ack, command, respond)

        ack.assert_called_once()
        mock_oauth_service.revoke_token.assert_called_once_with("U123", "google")
        respond.assert_called_once()

    @pytest.mark.asyncio
    async def test_accounts_command(self, commands, mock_token_repository):
        """'/accounts' 명령어 - 연결된 계정 목록"""
        ack = AsyncMock()
        respond = AsyncMock()
        command = {
            "user_id": "U123",
            "text": "",
        }

        await commands.handle_accounts(ack, command, respond)

        ack.assert_called_once()
        mock_token_repository.list_user_tokens.assert_called_once_with("U123")
        respond.assert_called_once()

        # 응답에 provider 정보 포함 확인
        response_text = str(respond.call_args)
        assert "google" in response_text.lower() or "연결" in response_text

    @pytest.mark.asyncio
    async def test_accounts_no_connections(self, commands, mock_token_repository):
        """연결된 계정 없음"""
        mock_token_repository.list_user_tokens.return_value = []

        ack = AsyncMock()
        respond = AsyncMock()
        command = {
            "user_id": "U123",
            "text": "",
        }

        await commands.handle_accounts(ack, command, respond)

        ack.assert_called_once()
        respond.assert_called_once()
        response_text = str(respond.call_args)
        assert "없" in response_text or "연결" in response_text
