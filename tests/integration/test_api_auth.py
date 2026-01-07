"""Phase 4 RED: Auth API Integration Test"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_google_callback_success():
    """Google Callback 성공 및 리다이렉트 테스트"""
    from src.presentation.api.routers import auth
    from fastapi import FastAPI
    from src.infrastructure.container import Container
    
    app = FastAPI()
    app.include_router(auth.router)
    
    # Mock Container Dependency
    mock_container = MagicMock()
    mock_auth_service = AsyncMock()
    mock_auth_service.handle_google_callback.return_value = True
    
    mock_container.get_auth_service.return_value = mock_auth_service
    
    # Patch Container.get_instance
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(Container, "get_instance", lambda: mock_container)
        
        # FastAPI TestClient
        # Depends(get_auth_service) 가 실제로는 get_db()를 호출하므로 override 필요
        
        from src.infrastructure.container import get_auth_service
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
        
        client = TestClient(app)
        
        response = client.get(
            "/auth/google/callback",
            params={"code": "auth_code_123", "state": "U12345"},
            follow_redirects=False
        )
        
        assert response.status_code == 307
        assert "slack://" in response.headers["location"]
        mock_auth_service.handle_google_callback.assert_called_with("auth_code_123", "U12345")
