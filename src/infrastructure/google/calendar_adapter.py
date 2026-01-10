"""Google Calendar Adapter - aiogoogle 기반 구현"""
from typing import List, Optional
from datetime import datetime, timezone
from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import UserCreds

from src.domain.ports.calendar_port import CalendarPort
from src.domain.models.event import CalendarEvent
from src.config.settings import Settings


class GoogleCalendarAdapter(CalendarPort):
    """Google Calendar API를 사용한 CalendarPort 구현체"""
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
    
    async def get_events(
        self, 
        user_id: str, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        max_results: int = 10
    ) -> List[CalendarEvent]:
        """사용자의 캘린더 이벤트 목록을 조회합니다."""
        
        # 기본값: 현재 시간부터
        if start_time is None:
            start_time = datetime.now(timezone.utc)
        
        # user_id로 저장된 토큰 조회 (TokenRepository 필요)
        # TODO: 실제 구현 시 TokenRepository에서 user_creds 가져오기
        user_creds = await self._get_user_credentials(user_id)
        
        if not user_creds:
            return []
        
        async with Aiogoogle(user_creds=user_creds) as aiogoogle:
            calendar_v3 = await aiogoogle.discover('calendar', 'v3')
            
            # API 호출 파라미터
            params = {
                'calendarId': 'primary',
                'timeMin': start_time.isoformat(),
                'maxResults': max_results,
                'singleEvents': True,
                'orderBy': 'startTime'
            }
            
            if end_time:
                params['timeMax'] = end_time.isoformat()
            
            response = await aiogoogle.as_user(
                calendar_v3.events.list(**params)
            )
            
            events = []
            for item in response.get('items', []):
                event = self._parse_event(item)
                if event:
                    events.append(event)
            
            return events

    async def create_event(
        self, 
        user_id: str, 
        event: CalendarEvent
    ) -> CalendarEvent:
        """새 캘린더 이벤트를 생성합니다."""
        
        user_creds = await self._get_user_credentials(user_id)
        
        if not user_creds:
            raise ValueError(f"User {user_id} credentials not found")
        
        async with Aiogoogle(user_creds=user_creds) as aiogoogle:
            calendar_v3 = await aiogoogle.discover('calendar', 'v3')
            
            event_body = {
                'summary': event.summary,
                'description': event.description,
                'location': event.location,
                'start': {'dateTime': event.start_time.isoformat()},
                'end': {'dateTime': event.end_time.isoformat()},
            }
            
            response = await aiogoogle.as_user(
                calendar_v3.events.insert(
                    calendarId='primary',
                    json=event_body
                )
            )
            
            return self._parse_event(response)

    async def delete_event(
        self, 
        user_id: str, 
        event_id: str
    ) -> bool:
        """캘린더 이벤트를 삭제합니다."""
        
        user_creds = await self._get_user_credentials(user_id)
        
        if not user_creds:
            return False
        
        try:
            async with Aiogoogle(user_creds=user_creds) as aiogoogle:
                calendar_v3 = await aiogoogle.discover('calendar', 'v3')
                
                await aiogoogle.as_user(
                    calendar_v3.events.delete(
                        calendarId='primary',
                        eventId=event_id
                    )
                )
                return True
        except Exception:
            return False

    async def _get_user_credentials(self, user_id: str) -> Optional[UserCreds]:
        """
        사용자의 OAuth 자격 증명을 조회합니다.
        TODO: TokenRepository와 연동하여 실제 토큰 로드
        """
        # 현재는 placeholder - 실제 구현 시 TokenRepository 연동
        # token = await token_repo.get_by_user_id(user_id)
        # if token:
        #     return UserCreds(
        #         access_token=token.access_token,
        #         refresh_token=token.refresh_token,
        #         expires_at=token.expires_at.isoformat()
        #     )
        return None

    def _parse_event(self, item: dict) -> Optional[CalendarEvent]:
        """Google Calendar API 응답을 CalendarEvent로 변환"""
        try:
            # start/end는 dateTime 또는 date 형식
            start = item.get('start', {})
            end = item.get('end', {})
            
            start_time = self._parse_datetime(start.get('dateTime') or start.get('date'))
            end_time = self._parse_datetime(end.get('dateTime') or end.get('date'))
            
            if not start_time or not end_time:
                return None
            
            return CalendarEvent(
                id=item.get('id'),
                summary=item.get('summary', 'Untitled'),
                description=item.get('description'),
                location=item.get('location'),
                start_time=start_time,
                end_time=end_time,
                status=item.get('status', 'confirmed')
            )
        except Exception:
            return None

    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """ISO 형식 문자열을 datetime으로 파싱"""
        if not dt_str:
            return None
        
        try:
            # ISO 형식 파싱 (Python 3.11+)
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except ValueError:
            return None
