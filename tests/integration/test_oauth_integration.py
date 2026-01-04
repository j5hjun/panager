"""
OAuth 시스템 통합 테스트

전체 OAuth 흐름을 테스트합니다.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta


class TestOAuthIntegration:
    """OAuth 시스템 통합 테스트"""

    @pytest.fixture
    def token_repository(self):
        """인메모리 TokenRepository"""
        from src.core.auth.token_repository import TokenRepository

        repo = TokenRepository(db_path=":memory:", encryption_key="test-key-32!")
        yield repo
        repo.close()

    @pytest.fixture
    def oauth_service(self, token_repository):
        """OAuthService"""
        from src.core.auth.oauth_service import OAuthService

        return OAuthService(
            token_repository=token_repository,
            google_client_id="test-client-id",
            google_client_secret="test-client-secret",
            redirect_uri="http://localhost:8080/oauth/callback",
        )

    @pytest.fixture
    def token_scheduler(self, token_repository, oauth_service):
        """TokenRefreshScheduler"""
        from src.core.auth.token_scheduler import TokenRefreshScheduler

        return TokenRefreshScheduler(
            token_repository=token_repository,
            oauth_service=oauth_service,
            check_interval_minutes=1,
        )

    @pytest.fixture
    def slack_commands(self, oauth_service, token_repository):
        """SlackOAuthCommands"""
        from src.adapters.slack.oauth_commands import SlackOAuthCommands

        return SlackOAuthCommands(
            oauth_service=oauth_service,
            token_repository=token_repository,
        )

    def test_full_oauth_flow(self, token_repository, oauth_service):
        """전체 OAuth 흐름: URL 생성 → 토큰 교환 → 저장 → 조회"""
        user_id = "U_INTEGRATION_TEST"

        # 1. 인증 URL 생성
        auth_url, state = oauth_service.generate_auth_url("google", user_id)
        assert "accounts.google.com" in auth_url
        assert state is not None

        # 2. state 검증
        decoded_user = oauth_service.decode_state(state)
        assert decoded_user == user_id

        # 3. 토큰 교환 (mock)
        with patch("src.core.auth.oauth_service.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "access_token": "integration_access_token",
                "refresh_token": "integration_refresh_token",
                "expires_in": 3600,
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            result = oauth_service.exchange_code("google", "test_code", state)
            assert result["access_token"] == "integration_access_token"

        # 4. 저장된 토큰 조회
        token = token_repository.get_token(user_id, "google")
        assert token is not None
        assert token["access_token"] == "integration_access_token"
        assert token["refresh_token"] == "integration_refresh_token"

    def test_token_refresh_flow(self, token_repository, oauth_service, token_scheduler):
        """토큰 갱신 흐름: 저장 → 만료 임박 → 갱신"""
        user_id = "U_REFRESH_TEST"

        # 1. 만료 임박 토큰 저장
        expires_soon = datetime.now() + timedelta(minutes=5)
        token_repository.save_token(
            user_id=user_id,
            provider="google",
            access_token="old_access",
            refresh_token="test_refresh",
            expires_at=expires_soon,
        )

        # 2. 갱신 (mock)
        with patch("src.core.auth.oauth_service.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "access_token": "refreshed_access",
                "expires_in": 3600,
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            token_scheduler.check_and_refresh_tokens()

        # 3. 갱신된 토큰 확인
        token = token_repository.get_token(user_id, "google")
        assert token["access_token"] == "refreshed_access"

    @pytest.mark.asyncio
    async def test_slack_connect_flow(self, slack_commands, oauth_service):
        """Slack 명령어 흐름: /connect → URL 응답"""
        ack = AsyncMock()
        respond = AsyncMock()
        command = {"user_id": "U_SLACK_TEST", "text": "google"}

        await slack_commands.handle_connect(ack, command, respond)

        # ack 호출
        ack.assert_called_once()

        # 응답에 URL 포함
        respond.assert_called_once()
        response_text = str(respond.call_args)
        assert "accounts.google.com" in response_text or "연결" in response_text

    @pytest.mark.asyncio
    async def test_slack_disconnect_flow(self, slack_commands, token_repository, oauth_service):
        """Slack 명령어 흐름: 연결 → /disconnect → 삭제"""
        user_id = "U_DISCONNECT_TEST"

        # 1. 토큰 저장
        token_repository.save_token(
            user_id=user_id,
            provider="google",
            access_token="to_delete",
            refresh_token="to_delete_refresh",
            expires_at=datetime.now() + timedelta(hours=1),
        )

        # 2. disconnect 실행
        with patch("src.core.auth.oauth_service.requests.post"):  # revoke mock
            ack = AsyncMock()
            respond = AsyncMock()
            command = {"user_id": user_id, "text": "google"}

            await slack_commands.handle_disconnect(ack, command, respond)

        # 3. 토큰 삭제 확인
        token = token_repository.get_token(user_id, "google")
        assert token is None

    @pytest.mark.asyncio
    async def test_slack_accounts_flow(self, slack_commands, token_repository):
        """Slack 명령어 흐름: /accounts → 목록 표시"""
        user_id = "U_ACCOUNTS_TEST"

        # 1. 토큰 저장
        token_repository.save_token(
            user_id=user_id,
            provider="google",
            access_token="test",
            refresh_token="test_refresh",
            expires_at=datetime.now() + timedelta(hours=1),
        )

        # 2. accounts 실행
        ack = AsyncMock()
        respond = AsyncMock()
        command = {"user_id": user_id, "text": ""}

        await slack_commands.handle_accounts(ack, command, respond)

        # 3. 응답 확인
        respond.assert_called_once()
        response_text = str(respond.call_args)
        assert "google" in response_text.lower() or "연결" in response_text
