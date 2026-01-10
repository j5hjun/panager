from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import SyncState, User, GoogleCredentials
from app.core.config import settings
from app.core.security import decrypt_token
import logging
import uuid
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

class CalendarService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def process_webhook(self, channel_id: str, resource_state: str):
        """
        Process Google Calendar Webhook.
        1. Validate channel_id (resource_id in DB).
        2. If valid, trigger sync.
        """
        stmt = select(SyncState).where(SyncState.resource_id == channel_id)
        result = await self.session.execute(stmt)
        sync_state = result.scalar_one_or_none()

        if not sync_state:
            logger.warning(f"Received webhook for unknown channel: {channel_id}")
            # We return True even if not found to tell Google to stop? 
            # Or False/Error? Google retries on 500. 
            # If we return 200, Google thinks it's delivered.
            # If it's unknown, maybe we should return 404? 
            # But that might cause retries. 200 is safer to stop spam.
            return False

        logger.info(f"Processing webhook for user {sync_state.user_id}, state: {resource_state}")
        
        if resource_state == 'sync':
            # Initial sync or renewal
            pass
        elif resource_state == 'exists':
            # Something changed
            await self.sync_events(sync_state.user_id)
            
        return True

    async def _get_service(self, slack_id: str):
        stmt = select(GoogleCredentials).where(GoogleCredentials.user_id == slack_id)
        result = await self.session.execute(stmt)
        creds_db = result.scalars().first()
        
        if not creds_db:
             return None

        refresh_token = decrypt_token(creds_db.refresh_token) if creds_db.refresh_token else None
        
        creds = Credentials(
            token=creds_db.access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=["https://www.googleapis.com/auth/calendar.events"] 
        )
        return build('calendar', 'v3', credentials=creds)

    async def sync_events(self, user_id: str):
        """
        Sync events for user and send notification to Slack.
        """
        logger.info(f"Syncing events for user {user_id}")
        
        service = await self._get_service(user_id)
        if not service:
            logger.error(f"Cannot sync, no credentials for {user_id}")
            return

        # Get Sync Token from DB
        stmt = select(SyncState).where(SyncState.user_id == user_id)
        result = await self.session.execute(stmt)
        sync_state = result.scalars().first()
        sync_token = sync_state.sync_token if sync_state and sync_state.sync_token else None
        
        try:
            # List events (incremental sync)
            list_args = {'calendarId': 'primary', 'singleEvents': True}
            is_initial_sync = False

            if sync_token:
                list_args['syncToken'] = sync_token
            else:
                # Initial sync: Just get the token, don't notify
                is_initial_sync = True
                import datetime
                now = datetime.datetime.utcnow().isoformat() + 'Z'
                list_args['timeMin'] = now
                # Limit results on initial sync to avoid fetching too much data
                # We just need the nextSyncToken
                # But Google API requires iterating pages to get syncToken usually.
                # However, if we just want to suppress notification, we can fetch but skip loop.

            events_result = service.events().list(**list_args).execute()
            
            items = events_result.get('items', [])
            next_sync_token = events_result.get('nextSyncToken')
            
            # Update sync token
            if sync_state:
                sync_state.sync_token = next_sync_token
                await self.session.commit()
            
            if not items:
                logger.info("No new events found.")
                return
            
            # Skip notifications for initial sync (prevent spam)
            if is_initial_sync:
                logger.info(f"Initial sync complete. Found {len(items)} events (notifications skipped).")
                return

            # Notify Slack
            from app.core.slack import slack_app
            from app.services.slack_service import SlackService
            slack = SlackService(slack_app)
            
            for event in items:
                # "cancelled" status means deleted
                status = event.get('status')
                summary = event.get('summary', '(No Title)')
                start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date'))
                html_link = event.get('htmlLink', '#')
                
                msg = ""
                if status == 'cancelled':
                    msg = f"🗑️ 일정이 삭제되었습니다: *{summary}*"
                else:
                    msg = f"📅 일정이 변경/생성되었습니다: *<{html_link}|{summary}>*\n⏰ 시작: {start}"
                
                await slack.send_dm(user_id, msg)
                
        except Exception as e:
            if "Sync token is no longer valid" in str(e):
                 # Full sync required (delete sync token and retry)
                 logger.warning("Sync token invalid, clearing...")
                 if sync_state:
                     sync_state.sync_token = None
                     await self.session.commit()
                 # Retry logic needed? For now just fail and wait for next webhook
            logger.error(f"Error syncing events: {e}")

    async def watch_events(self, slack_id: str) -> bool:
        """
        Register a watch (webhook) for the user's primary calendar.
        """
        # 1. Get User Credentials
        stmt = select(GoogleCredentials).where(GoogleCredentials.user_id == slack_id)
        result = await self.session.execute(stmt)
        creds_db = result.scalars().first()
        
        if not creds_db:
            logger.error(f"No credentials found for user {slack_id}")
            return False

        # 2. Build Google Credentials Object
        # Need to decrypt refresh token if encrypted
        refresh_token = decrypt_token(creds_db.refresh_token) if creds_db.refresh_token else None
        
        creds = Credentials(
            token=creds_db.access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=["https://www.googleapis.com/auth/calendar.events"] 
        )
        
        # 3. Call Google API
        service = build('calendar', 'v3', credentials=creds)
        
        channel_id = str(uuid.uuid4())
        # Ideally, we need a public HTTPS URL. 
        # For local dev, we use ngrok URL from settings.
        # If not set, it will fail or we mock it.
        webhook_url = f"{settings.PUBLIC_URL}/api/v1/webhook/google/calendar" if hasattr(settings, 'PUBLIC_URL') else "https://example.com/webhook"
        
        try:
            body = {
                "id": channel_id,
                "type": "web_hook",
                "address": webhook_url
            }
            logger.info(f"Registering watch for {slack_id} with URL {webhook_url}")
            
            response = service.events().watch(calendarId='primary', body=body).execute()
            logger.info(f"Watch response: {response}")
            
            # 4. Save SyncState to DB
            # We need to save channel_id (id) and resourceId (from response) to validaate webhooks
            resource_id = response.get("resourceId")
            
            # Check if exists
            stmt = select(SyncState).where(SyncState.user_id == slack_id)
            result = await self.session.execute(stmt)
            sync_state = result.scalars().first()
            
            if not sync_state:
                sync_state = SyncState(user_id=slack_id)
                self.session.add(sync_state)
            
            sync_state.resource_id = channel_id # We used this as channel ID
            sync_state.sync_token = "" # Initial sync
            # We might want to save actual Google Resource ID too if needed for stopping channel
            
            await self.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to watch events: {e}")
            return False
