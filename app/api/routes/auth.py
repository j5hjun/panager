from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.db.session import get_db
from app.services.user_service import AuthService, UserService
from app.services.slack_service import SlackService
from app.services.calendar_service import CalendarService
from app.core.slack import slack_app
from app.core.exceptions import AuthError
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/google/login")
async def login(slack_user_id: str = Query(..., alias="slack_user_id")):
    """
    Redirects user to Google OAuth consent screen.
    Uses slack_user_id as state.
    """
    if not slack_user_id:
         raise HTTPException(status_code=400, detail="slack_user_id is required")
         
    auth_service = AuthService()
    url, state = auth_service.get_authorization_url(slack_user_id)
    return RedirectResponse(url)

@router.get("/google/callback")
async def callback(
    code: str, 
    state: str, 
    db: AsyncSession = Depends(get_db)
):
    """
    Callback from Google. Exchange code for tokens and save to DB.
    state parameter contains slack_user_id.
    """
    if not code or not state:
        raise HTTPException(status_code=400, detail="Invalid request parameters")
        
    slack_user_id = state
    auth_service = AuthService()
    user_service = UserService(db)
    
    try:
        # 1. Exchange code for tokens
        token_data = auth_service.exchange_code(code)
        
        # 2. Save to DB
        await user_service.save_credentials(slack_user_id, token_data)
        
        # 3. Commit
        await db.commit()

        # 4. Send Slack DM (Success Notification)
        try:
            slack_service = SlackService(slack_app)
            await slack_service.send_dm(
                user_id=slack_user_id,
                text="✅ *구글 캘린더 연동 성공!*\n이제 캘린더 일정이 변경되면 알림을 보내드립니다."
            )
        except Exception as e:
            logger.error(f"Failed to send Slack DM: {e}")
            # Don't fail the whole request just because slack msg failed for some reason
        
        # 5. Trigger Calendar Watch
        try:
            calendar_service = CalendarService(db)
            watch_result = await calendar_service.watch_events(slack_user_id)
            if watch_result:
                logger.info(f"Successfully registered watch for user {slack_user_id}")
            else:
                logger.warning(f"Failed to register watch for user {slack_user_id}")
        except Exception as e:
            logger.error(f"Error registering watch: {e}")

        # 6. Return HTML Success Page
        # Dynamically read the template to avoid complex template engine for now
        template_path = Path("app/templates/success.html")
        if template_path.exists():
            return HTMLResponse(content=template_path.read_text(), status_code=200)
        
        return HTMLResponse(content="<h1>Authentication Successful</h1><p>You can close this window.</p>", status_code=200)
        
    except Exception as e:
        logger.error(f"Auth failed: {e}")
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")
