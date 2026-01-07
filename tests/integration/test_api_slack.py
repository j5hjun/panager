"""Phase 2 RED: Slack API Integration Test"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

# src.main이 아직 없으므로 router만 따로 테스트하거나, main을 Phase 2에서 만들어야 함.
# Phase 2 task에 main.py 등록이 포함되어 있으므로, 여기서 main도 같이 꾸며야 함.
# 일단 Router만 떼어서 테스트하는 방식으로 접근.


@pytest.fixture
def client():
    from src.presentation.api.routers import slack
    from fastapi import FastAPI
    
    app = FastAPI()
    app.include_router(slack.router)
    
    # Mock Dependency if any
    return TestClient(app)


@pytest.mark.asyncio
async def test_slack_url_verification():
    """Slack URL Verification 요청 테스트"""
    # Slack SDK의 SignatureVerifier를 Mocking해야 함 (또는 미들웨어를 Mocking)
    # 여기서는 로직 자체를 검증하므로 Verifier Mocking이 중요
    
    from src.presentation.api.routers import slack
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(slack.router)
    client = TestClient(app)
    
    # Challenge Request
    response = client.post(
        "/slack/events",
        json={"type": "url_verification", "challenge": "challenge_token_123"}
    )
    
    # Verifier가 실패하면 400 or 401, 성공하면 200 반환해야 함.
    # 지금은 구현 전이라 404가 뜰 것임. 
    # 구현 후에는 Verifier Mocking 필요.
    
    # 일단 404를 기대하는 것이 아니라, 구현 후 200을 기대.
    assert response.status_code != 404


@pytest.mark.asyncio
async def test_slack_event_enqueue():
    """Slack Event 수신 및 Enqueue 테스트"""
    from src.presentation.api.routers.slack import router
    from fastapi import FastAPI
    
    app = FastAPI()
    app.include_router(router)
    
    # Mock ARQ Pool
    mock_pool = AsyncMock()
    app.state.arq_pool = mock_pool
    
    client = TestClient(app)
    
    # RequestVerifier Mocking (Dependency Override)
    # FastAPI Dependency Override는 app.dependency_overrides 사용
    # 하지만 RequestVerifier가 @router 단위에서 Depends로 쓰일지, Middleware로 쓰일지 결정 필요.
    # 보통 Slack은 Body를 읽어야 해서 Middleware보다 Depends가 나을 수 있음 (Starlette Request 객체 사용 시).
    
    # Phase 2에서는 Signature Verification을 pass 하는 식으로 가정하거나 Header 조작 필요.
    
    response = client.post(
        "/slack/events",
        json={"type": "event_callback", "event": {"type": "message", "text": "hello"}},
        headers={
            "X-Slack-Signature": "v0=stub",
            "X-Slack-Request-Timestamp": "1234567890"
        }
    )
    
    # 구현이 없으므로 404 예상되지만, 구현 후에는 200과 enqueue 확인 필요
    assert response.status_code == 200
    mock_pool.enqueue_job.assert_called_once()
