"""
OAuthService 테스트

TDD RED Phase: OAuth 서비스 테스트
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta


class TestOAuthService:
    """OAuthService 테스트"""

    @pytest.fixture
    def token_repository(self):
        """Mock TokenRepository"""
        from src.core.auth.token_repository import TokenRepository

        repo = TokenRepository(db_path=":memory:", encryption_key="test-key-32-bytes!")
        yield repo
        repo.close()

    @pytest.fixture
    def oauth_service(self, token_repository):
        """OAuthService 인스턴스"""
        from src.core.auth.oauth_service import OAuthService

        return OAuthService(
            token_repository=token_repository,
            google_client_id="test-client-id",
            google_client_secret="test-client-secret",
            redirect_uri="http://localhost:8080/oauth/callback",
        )

    def test_generate_auth_url_google(self, oauth_service):
        """Google 인증 URL 생성 (state 파라미터 포함)"""
        user_id = "U123"
        url, state = oauth_service.generate_auth_url("google", user_id)

        assert "accounts.google.com" in url
        assert "client_id=test-client-id" in url
        assert "redirect_uri=" in url
        assert "state=" in url
        assert state is not None
        # state에서 user_id 복원 가능해야 함
        decoded_user_id = oauth_service.decode_state(state)
        assert decoded_user_id == user_id

    def test_generate_auth_url_with_scopes(self, oauth_service):
        """스코프가 포함된 인증 URL"""
        url, state = oauth_service.generate_auth_url(
            "google",
            "U123",
            scopes=["https://www.googleapis.com/auth/calendar.readonly"]
        )

        assert "scope=" in url
        assert "calendar" in url

    @patch("src.core.auth.oauth_service.requests.post")
    def test_exchange_code(self, mock_post, oauth_service, token_repository):
        """인증 코드를 토큰으로 교환"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600,
            "token_type": "Bearer",
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # state 생성
        _, state = oauth_service.generate_auth_url("google", "U123")

        # 코드 교환
        result = oauth_service.exchange_code("google", "auth_code_123", state)

        assert result["access_token"] == "new_access_token"
        assert result["refresh_token"] == "new_refresh_token"

        # 토큰이 저장되었는지 확인
        token = token_repository.get_token("U123", "google")
        assert token is not None
        assert token["access_token"] == "new_access_token"

    @patch("src.core.auth.oauth_service.requests.post")
    def test_refresh_token(self, mock_post, oauth_service, token_repository):
        """토큰 갱신"""
        # 기존 토큰 저장
        token_repository.save_token(
            user_id="U123",
            provider="google",
            access_token="old_access",
            refresh_token="old_refresh",
            expires_at=datetime.now() + timedelta(hours=1),
        )

        # Mock 응답 설정
        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "refreshed_access_token",
            "expires_in": 3600,
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # 토큰 갱신
        result = oauth_service.refresh_token("U123", "google")

        assert result["access_token"] == "refreshed_access_token"

        # DB에도 업데이트되었는지 확인
        token = token_repository.get_token("U123", "google")
        assert token["access_token"] == "refreshed_access_token"

    @patch("src.core.auth.oauth_service.requests.post")
    def test_revoke_token(self, mock_post, oauth_service, token_repository):
        """토큰 해지"""
        # 기존 토큰 저장
        token_repository.save_token(
            user_id="U123",
            provider="google",
            access_token="access_to_revoke",
            refresh_token="refresh_to_revoke",
            expires_at=datetime.now() + timedelta(hours=1),
        )

        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # 토큰 해지
        result = oauth_service.revoke_token("U123", "google")

        assert result is True

        # DB에서 삭제되었는지 확인
        token = token_repository.get_token("U123", "google")
        assert token is None

    def test_decode_state_invalid(self, oauth_service):
        """잘못된 state 디코딩"""
        result = oauth_service.decode_state("invalid_state")
        assert result is None


class TestOAuthCallback:
    """OAuth 콜백 엔드포인트 테스트"""

    @pytest.fixture
    def test_client(self):
        """FastAPI 테스트 클라이언트"""
        from fastapi.testclient import TestClient
        from src.adapters.oauth.server import create_oauth_app
        from src.core.auth.token_repository import TokenRepository
        from src.core.auth.oauth_service import OAuthService

        # 테스트용 설정
        token_repo = TokenRepository(db_path=":memory:", encryption_key="test-key!")
        oauth_service = OAuthService(
            token_repository=token_repo,
            google_client_id="test-client-id",
            google_client_secret="test-client-secret",
            redirect_uri="http://localhost:8080/oauth/callback",
        )

        app = create_oauth_app(oauth_service)
        client = TestClient(app)
        yield client, oauth_service, token_repo
        token_repo.close()

    @patch("src.core.auth.oauth_service.requests.post")
    def test_callback_success(self, mock_post, test_client):
        """정상적인 OAuth 콜백"""
        client, oauth_service, _ = test_client

        # Mock 응답
        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "new_access",
            "refresh_token": "new_refresh",
            "expires_in": 3600,
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # state 생성
        _, state = oauth_service.generate_auth_url("google", "U123")

        # 콜백 요청
        response = client.get(f"/oauth/callback?code=auth_code&state={state}")

        assert response.status_code == 200
        assert "연결 완료" in response.text or "success" in response.text.lower()

    def test_callback_invalid_state(self, test_client):
        """잘못된 state로 콜백"""
        client, _, _ = test_client

        response = client.get("/oauth/callback?code=auth_code&state=invalid_state")

        assert response.status_code == 400

    def test_callback_error(self, test_client):
        """OAuth 에러 응답"""
        client, _, _ = test_client

        response = client.get("/oauth/callback?error=access_denied&error_description=User%20denied")

        assert response.status_code == 400
        assert "denied" in response.text.lower() or "error" in response.text.lower()

    def test_health_check(self, test_client):
        """헬스체크 엔드포인트"""
        client, _, _ = test_client

        response = client.get("/health")

        assert response.status_code == 200
