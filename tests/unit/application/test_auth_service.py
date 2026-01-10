"""Phase 1 RED: UserAuthService 테스트"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from src.domain.models.token import Token

@pytest.mark.asyncio
async def test_auth_service_generate_url():
    """인증 URL 생성 테스트"""
    from src.application.services.auth_service import UserAuthService
    
    # Mock
    mock_auth_manager = MagicMock()
    mock_auth_manager.get_authorization_url.return_value = "https://accounts.google.com/o/oauth2/auth?client_id=..."
    mock_user_repo = AsyncMock()
    
    service = UserAuthService(mock_user_repo, mock_auth_manager)
    
    url = service.generate_auth_url(slack_id="U12345")
    
    assert "https://accounts.google.com" in url
    mock_auth_manager.get_authorization_url.assert_called_once()

@pytest.mark.asyncio
async def test_auth_service_callback_success():
    """인증 콜백 처리 테스트 - 성공 케이스"""
    from src.application.services.auth_service import UserAuthService
    
    # Mock
    mock_user_repo = AsyncMock()
    mock_user_repo.get_by_slack_id.return_value = None  # 신규 유저
    
    mock_auth_manager = AsyncMock()
    mock_auth_manager.save_token_from_auth_response = AsyncMock()
    
    # aiogoogle client mock
    mock_aiogoogle = AsyncMock()
    mock_aiogoogle.__aenter__.return_value = mock_aiogoogle
    mock_aiogoogle.__aexit__.return_value = None
    mock_aiogoogle.oauth2.build_user_creds.return_value = {
        'access_token': 'access_123',
        'refresh_token': 'refresh_123',
        'expires_in': 3600
    }
    
    service = UserAuthService(mock_user_repo, mock_auth_manager)
    # 실제 aiogoogle 호출 부분은 Mocking이 까다로우므로 service 내부 메서드를 일부 Mocking하거나
    # Service 구현 시 aiogoogle 의존성을 어떻게 처리할지 고민 필요.
    # 여기서는 service.exchange_code_for_token 메서드를 Mocking한다고 가정하거나,
    # AuthManager에 exchange 로직을 위임하는 것이 나아보임. -> AuthManager 확장 필요
    
    # 전략 변경: AuthManager가 code exchange도 담당하도록 하면 Service가 더 깔끔해짐.
    # AuthManager 메서드 추가: exchange_code(code) -> token_dict
    
    mock_auth_manager.exchange_code.return_value = {
        'access_token': 'access_123',
        'refresh_token': 'refresh_123'
    }
    mock_auth_manager.save_token_from_auth_response.return_value = Token(
        user_slack_id="U12345", access_token="acc", refresh_token="ref", expires_at=datetime.now(timezone.utc)
    )
    
    success = await service.handle_google_callback(
        code="auth_code_123", 
        slack_id="U12345"
    )
    
    assert success is True
    # 유저 생성 또는 업데이트 확인
    mock_user_repo.save.assert_called_once()
    saved_user = mock_user_repo.save.call_args[0][0]
    assert saved_user.slack_id == "U12345"
    assert saved_user.is_active is True
