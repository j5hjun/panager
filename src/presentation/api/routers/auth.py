"""Auth API Router"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse

from src.application.services.auth_service import UserAuthService
from src.infrastructure.container import get_auth_service
from src.config.settings import Settings

router = APIRouter(prefix="/auth", tags=["Auth"])
settings = Settings()

@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    auth_service: UserAuthService = Depends(get_auth_service)
):
    """
    Google OAuth Callback 처리
    state 파라미터에는 slack_user_id가 담겨있음.
    """
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state")
        
    success = await auth_service.handle_google_callback(code, state)
    
    if not success:
        return {"status": "error", "message": "Authentication failed"}
    
    # 인증 성공 시 Slack 앱으로 리다이렉트
    # slack_app_id 등을 알면 더 정확한 링크 가능: slack://app?team={team_id}&id={app_id}
    # 일단 범용 링크 사용
    slack_deep_link = "slack://open"
    
    return RedirectResponse(url=slack_deep_link)
