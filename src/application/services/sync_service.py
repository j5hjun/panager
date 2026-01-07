"""Calendar Sync Service Application Service Logic"""
from datetime import datetime, timezone, timedelta

from src.domain.ports.calendar_port import CalendarPort
from src.domain.ports.event_repo import EventRepository
from src.domain.ports.user_repo import UserRepository


class CalendarSyncService:
    """사용자 캘린더 동기화 서비스"""
    
    def __init__(
        self,
        calendar_adapter: CalendarPort,
        event_repo: EventRepository,
        user_repo: UserRepository
    ):
        self.calendar_adapter = calendar_adapter
        self.event_repo = event_repo
        self.user_repo = user_repo

    async def sync_user_calendar(self, slack_id: str) -> int:
        """
        사용자의 Google Calendar 이벤트를 조회하여 DB에 동기화합니다.
        
        Args:
            slack_id: Slack 사용자 ID
            
        Returns:
            동기화된 이벤트 개수
        """
        # 1. 사용자 조회 (DB ID 필요)
        user = await self.user_repo.get_by_slack_id(slack_id)
        if not user or user.id is None:
            # 사용자가 없거나 DB ID가 없으면 동기화 불가
            return 0
            
        # 2. Google Calendar 이벤트 조회 (최근 1개월 ~ 미래 6개월 등, 일단 default)
        start_time = datetime.now(timezone.utc) - timedelta(days=7) # 최근 7일 포함
        end_time = datetime.now(timezone.utc) + timedelta(days=90)  # 미래 3달
        
        events = await self.calendar_adapter.get_events(
            user_id=slack_id,
            start_time=start_time,
            end_time=end_time
        )
        
        if not events:
            return 0
            
        # 3. DB에 저장 (Upsert 로직은 Repository 구현에 의존하거나 여기서 처리)
        # EventRepository.save 메서드는 ORM의 merge 등을 사용하여 Upsert를 처리한다고 가정
        # 혹은 JPA처럼 id가 있으면 update, 없으면 insert
        
        count = 0
        for event in events:
            # 이벤트를 DB 모델로 저장
            await self.event_repo.save(event, user.id)
            count += 1
            
        return count
