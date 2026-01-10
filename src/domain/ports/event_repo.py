from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from src.domain.models.event import CalendarEvent

class EventRepository(ABC):
    @abstractmethod
    async def get_by_id(self, event_id: str) -> Optional[CalendarEvent]:
        pass

    @abstractmethod
    async def get_upcoming_events(self, slack_id: str, limit: int = 5) -> List[CalendarEvent]:
        pass
        
    @abstractmethod
    async def get_by_range(self, slack_id: str, start: datetime, end: datetime) -> List[CalendarEvent]:
        pass

    @abstractmethod
    async def save(self, event: CalendarEvent, user_id: int) -> CalendarEvent:
        pass
