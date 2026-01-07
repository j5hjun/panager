"""Slack API Router"""
import logging
from fastapi import APIRouter, Request, HTTPException, Depends
from slack_sdk.signature import SignatureVerifier

from src.config.settings import Settings

router = APIRouter(prefix="/slack", tags=["Slack"])
settings = Settings()

# Signature Verifier
verifier = SignatureVerifier(settings.slack_signing_secret)


async def verify_signature(request: Request):
    """Slack Request Signature 검증"""
    body = await request.body()
    decoded_body = body.decode("utf-8")
    
    # 헤더 가져오기
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    signature = request.headers.get("X-Slack-Signature")
    
    if not timestamp or not signature:
        # 테스트 환경 등에서 bypass 옵션이 필요할 수 있음
        if settings.env == "development":
            return
        raise HTTPException(status_code=400, detail="Missing Slack headers")
    
    if not verifier.is_valid(decoded_body, timestamp, signature):
        if settings.env == "development":
           return
        raise HTTPException(status_code=401, detail="Invalid signature")


@router.post("/events")
async def slack_events(
    request: Request,
    verification: None = Depends(verify_signature)
):
    """
    Slack Events API 엔드포인트
    1. URL Verification 처리
    2. Event Callback 처리 (Enqueue)
    """
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # 1. URL Verification
    if data.get("type") == "url_verification":
        return {"challenge": data.get("challenge")}
    
    # 2. Event Callback
    if data.get("type") == "event_callback":
        # Retry 처리 (X-Slack-Retry-Num 헤더 확인 가능)
        retry_num = request.headers.get("X-Slack-Retry-Num")
        if retry_num:
            logging.info(f"Retry request: {retry_num}")
            # 간단히 200 OK로 응답하여 재시도 중단시키거나, 
            # 멱등성 처리가 되어 있다면 그냥 진행.
        
        # Enqueue Job
        if hasattr(request.app.state, 'arq_pool'):
            await request.app.state.arq_pool.enqueue_job(
                'handle_slack_event',
                data['event']
            )
        else:
            logging.error("ARQ pool not found in app state")
        
        return {"status": "ok"}
    
    return {"status": "ignored"}
