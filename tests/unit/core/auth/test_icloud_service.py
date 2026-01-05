"""
iCloudService 테스트

TDD RED Phase: iCloud CalDAV 연동 테스트
"""

from unittest.mock import Mock, patch

import pytest


class TestICloudService:
    """iCloudService 테스트"""

    @pytest.fixture
    def mock_token_repository(self):
        """Mock TokenRepository"""
        repo = Mock()
        repo.save_token.return_value = None
        # username|password 형식으로 저장됨
        repo.get_token.return_value = {
            "provider": "icloud",
            "access_token": "test@icloud.com|encrypted_password",
        }
        return repo

    @pytest.fixture
    def icloud_service(self, mock_token_repository):
        """iCloudService 인스턴스"""
        from src.core.auth.icloud_service import ICloudService

        return ICloudService(token_repository=mock_token_repository)

    def test_init(self, icloud_service):
        """서비스 초기화"""
        assert icloud_service is not None

    @patch("src.core.auth.icloud_service.caldav.DAVClient")
    def test_validate_credentials_success(self, mock_client, icloud_service):
        """자격증명 검증 성공"""
        # Mock 설정
        mock_principal = Mock()
        mock_principal.calendars.return_value = [Mock()]
        mock_client.return_value.principal.return_value = mock_principal

        result = icloud_service.validate_credentials(
            username="test@icloud.com",
            app_password="xxxx-xxxx-xxxx-xxxx",
        )

        assert result is True

    @patch("src.core.auth.icloud_service.caldav.DAVClient")
    def test_validate_credentials_failure(self, mock_client, icloud_service):
        """자격증명 검증 실패"""
        mock_client.return_value.principal.side_effect = Exception("Auth failed")

        result = icloud_service.validate_credentials(
            username="test@icloud.com",
            app_password="wrong-password",
        )

        assert result is False

    def test_save_credentials(self, icloud_service, mock_token_repository):
        """자격증명 저장"""
        icloud_service.save_credentials(
            user_id="U123",
            username="test@icloud.com",
            app_password="xxxx-xxxx-xxxx-xxxx",
        )

        mock_token_repository.save_token.assert_called_once()
        call_args = mock_token_repository.save_token.call_args
        assert call_args[1]["user_id"] == "U123"
        assert call_args[1]["provider"] == "icloud"

    @patch("src.core.auth.icloud_service.caldav.DAVClient")
    def test_list_calendars(self, mock_client, icloud_service, mock_token_repository):
        """캘린더 목록 조회"""
        # Mock 설정
        mock_cal1 = Mock()
        mock_cal1.name = "Work"
        mock_cal2 = Mock()
        mock_cal2.name = "Personal"
        mock_principal = Mock()
        mock_principal.calendars.return_value = [mock_cal1, mock_cal2]
        mock_client.return_value.principal.return_value = mock_principal

        calendars = icloud_service.list_calendars("U123")

        assert len(calendars) == 2
        assert "Work" in calendars
        assert "Personal" in calendars


class TestSlackICloudModal:
    """Slack iCloud 모달 테스트"""

    @pytest.fixture
    def mock_oauth_service(self):
        """Mock OAuthService"""
        return Mock()

    @pytest.fixture
    def mock_token_repository(self):
        """Mock TokenRepository"""
        return Mock()

    @pytest.fixture
    def mock_icloud_service(self):
        """Mock ICloudService"""
        service = Mock()
        service.validate_credentials.return_value = True
        service.save_credentials.return_value = None
        return service

    @pytest.fixture
    def commands(self, mock_oauth_service, mock_token_repository, mock_icloud_service):
        """SlackOAuthCommands 인스턴스"""
        from src.adapters.slack.oauth_commands import SlackOAuthCommands

        cmd = SlackOAuthCommands(
            oauth_service=mock_oauth_service,
            token_repository=mock_token_repository,
        )
        cmd.icloud_service = mock_icloud_service
        return cmd

    def test_connect_icloud_opens_modal(self, commands):
        """'/connect icloud' → 모달 열기"""
        ack = Mock()
        respond = Mock()
        client = Mock()
        command = {
            "user_id": "U123",
            "text": "icloud",
            "trigger_id": "trigger_123",
        }

        commands.handle_connect(ack, command, respond, client=client)

        ack.assert_called_once()
        # iCloud일 때 모달을 열어야 함
        client.views_open.assert_called_once()
