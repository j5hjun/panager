"""Calendar 서비스 추상 인터페이스 (Port)"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from src.domain.models.event import CalendarEvent


class CalendarPort(ABC):
    """캘린더 서비스와의 상호작용을 정의하는 Port"""
    
    @abstractmethod
    async def get_events(
        self, 
        user_id: str, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        max_results: int = 10
    ) -> List[CalendarEvent]:
        """
        사용자의 캘린더 이벤트 목록을 조회합니다.
        
        Args:
            user_id: 사용자 식별자 (slack_id)
            start_time: 조회 시작 시간 (기본값: 현재)
            end_time: 조회 종료 시간 (기본값: None - 무제한)
            max_results: 최대 조회 개수
            
        Returns:
            CalendarEvent 리스트
        """
        pass

    @abstractmethod
    async def create_event(
        self, 
        user_id: str, 
        event: CalendarEvent
    ) -> CalendarEvent:
        """
        새 캘린더 이벤트를 생성합니다.
        
        Args:
            user_id: 사용자 식별자
            event: 생성할 이벤트 정보
            
        Returns:
            생성된 CalendarEvent (ID 포함)
        """
        pass

    @abstractmethod
    async def delete_event(
        self, 
        user_id: str, 
        event_id: str
    ) -> bool:
        """
        캘린더 이벤트를 삭제합니다.
        
        Args:
            user_id: 사용자 식별자
            event_id: 삭제할 이벤트 ID
            
        Returns:
            삭제 성공 여부
        """
        pass
