"""Notification Service Application Service Logic"""

from src.domain.ports.messenger_port import MessengerPort
from src.domain.models.event import CalendarEvent
from src.infrastructure.slack.blocks import EventMessageTemplates


class NotificationService:
    """사용자 알림 관리 서비스"""
    
    def __init__(self, messenger: MessengerPort):
        self.messenger = messenger
    
    async def send_welcome_message(self, slack_id: str, name: str) -> bool:
        """
        사용자에게 환영 메시지를 전송합니다.
        
        Args:
            slack_id: Slack 사용자 ID
            name: 사용자 이름
            
        Returns:
            전송 성공 여부
        """
        message = f"안녕하세요, {name}님! 👋\nPanager가 성공적으로 연결되었습니다. 이제 일정을 모니터링하고 미리 알려드릴게요."
        return await self.messenger.send_message(user_id=slack_id, text=message)
    
    async def send_event_reminder(self, slack_id: str, event: CalendarEvent) -> bool:
        """
        일정 리마인더를 전송합니다.
        
        Args:
            slack_id: Slack 사용자 ID
            event: 캘린더 이벤트 정보
            
        Returns:
            전송 성공 여부
        """
        blocks = EventMessageTemplates.event_reminder(
            event_title=event.summary,
            start_time=event.start_time,
            location=event.location,
            description=event.description
        )
        
        fallback_text = f"📅 일정 알림: {event.summary}"
        
        return await self.messenger.send_block_message(
            user_id=slack_id,
            blocks=blocks,
            text=fallback_text
        )
