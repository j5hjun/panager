from slack_bolt.async_app import AsyncApp
from app.core.config import settings

slack_app = AsyncApp(
    token=settings.SLACK_BOT_TOKEN,
    signing_secret=settings.SLACK_SIGNING_SECRET
)

@slack_app.message("로그인")
async def handle_login_message(message, say):
    """
    Handle '로그인' message.
    Send the Google OAuth login link.
    """
    user_id = message["user"]
    # We use our API endpoint /api/v1/auth/google/login?slack_user_id=...
    # to let the browser handle the redirect.
    # Construct the full URL. 
    # For local, it's http://localhost:8000...
    # For prod, it should be the domain.
    # For now, let's assume we send the direct Google URL or our wrapper.
    # Using wrapper is better to track state.
    
    # We need to constructing the URL to our own backend.
    # But settings might not have PUBLIC_URL.
    # Let's use `AuthService` directly here to get the Google URL directly?
    # NO, the requirement (FR-Auth-01) says "link".
    # If we use our backend redirect, we need the backend URL.
    # Let's assume http://localhost:8000 for MVP or add PUBLIC_URL to settings.
    # Or just use the Google URL directly?
    # If we use Google URL directly, we can pass state=slack_user_id.
    
    from app.services.user_service import AuthService
    auth_service = AuthService()
    url, _ = auth_service.get_authorization_url(slack_user_id=user_id)
    
    await say(
        text=f"구글 캘린더를 연결하시겠습니까? 👉 <{url}|로그인하기>",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"👋 안녕하세요! Proactive Manager입니다.\n구글 캘린더 연동을 위해 아래 버튼을 클릭해주세요."
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Google 계정 연결",
                            "emoji": True
                        },
                        "url": url,
                        "action_id": "google_login"
                    }
                ]
            }
        ]
    )

@slack_app.action("google_login")
async def handle_google_login_action(ack, body, logger):
    """
    Handle the button click. 
    Even though the button has a URL, Slack sends an event that needs acknowledgement.
    """
    await ack()
    logger.info(f"User clicked login button: {body['user']['id']}")
