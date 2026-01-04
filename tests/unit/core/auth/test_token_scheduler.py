"""
TokenRefreshScheduler 테스트

TDD RED Phase: 토큰 갱신 스케줄러 테스트
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta


class TestTokenRefreshScheduler:
    """TokenRefreshScheduler 테스트"""

    @pytest.fixture
    def mock_token_repository(self):
        """Mock TokenRepository"""
        repo = Mock()
        repo.get_expiring_tokens.return_value = [
            {
                "user_id": "U123",
                "provider": "google",
                "access_token": "old_token",
                "refresh_token": "refresh_123",
                "expires_at": datetime.now() + timedelta(minutes=5),
            }
        ]
        return repo

    @pytest.fixture
    def mock_oauth_service(self):
        """Mock OAuthService"""
        service = Mock()
        service.refresh_token.return_value = {
            "access_token": "new_token",
            "expires_in": 3600,
        }
        return service

    @pytest.fixture
    def scheduler(self, mock_token_repository, mock_oauth_service):
        """TokenRefreshScheduler 인스턴스"""
        from src.core.auth.token_scheduler import TokenRefreshScheduler

        return TokenRefreshScheduler(
            token_repository=mock_token_repository,
            oauth_service=mock_oauth_service,
            check_interval_minutes=1,
        )

    def test_init(self, scheduler):
        """스케줄러 초기화"""
        assert scheduler is not None
        assert scheduler.check_interval_minutes == 1

    def test_check_and_refresh_tokens(self, scheduler, mock_token_repository, mock_oauth_service):
        """만료 임박 토큰 갱신"""
        # 갱신 실행
        scheduler.check_and_refresh_tokens()

        # 만료 임박 토큰 조회 확인
        mock_token_repository.get_expiring_tokens.assert_called_once()

        # 토큰 갱신 확인
        mock_oauth_service.refresh_token.assert_called_once_with("U123", "google")

    def test_check_and_refresh_no_expiring_tokens(self, scheduler, mock_token_repository, mock_oauth_service):
        """만료 임박 토큰 없음"""
        mock_token_repository.get_expiring_tokens.return_value = []

        scheduler.check_and_refresh_tokens()

        # 갱신 호출 안 됨
        mock_oauth_service.refresh_token.assert_not_called()

    def test_refresh_failure_handling(self, scheduler, mock_token_repository, mock_oauth_service):
        """갱신 실패 처리"""
        mock_oauth_service.refresh_token.side_effect = RuntimeError("API error")

        # 예외가 발생해도 크래시 안 됨
        scheduler.check_and_refresh_tokens()

        # 호출은 시도됨
        mock_oauth_service.refresh_token.assert_called_once()

    def test_start_scheduler(self, scheduler):
        """스케줄러 시작"""
        with patch.object(scheduler, "_scheduler") as mock_scheduler:
            mock_scheduler.running = False
            scheduler.start()
            mock_scheduler.start.assert_called_once()

    def test_stop_scheduler(self, scheduler):
        """스케줄러 중지"""
        with patch.object(scheduler, "_scheduler") as mock_scheduler:
            mock_scheduler.running = True
            scheduler.stop()
            mock_scheduler.shutdown.assert_called_once()

    def test_refresh_specific_token(self, scheduler, mock_oauth_service):
        """특정 토큰 갱신"""
        result = scheduler.refresh_specific_token("U123", "google")

        mock_oauth_service.refresh_token.assert_called_once_with("U123", "google")
        assert result is True

    def test_refresh_specific_token_failure(self, scheduler, mock_oauth_service):
        """특정 토큰 갱신 실패"""
        mock_oauth_service.refresh_token.side_effect = RuntimeError("Failed")

        result = scheduler.refresh_specific_token("U123", "google")

        assert result is False
