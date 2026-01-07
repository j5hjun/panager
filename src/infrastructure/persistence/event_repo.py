from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domain.models.event import CalendarEvent
from src.domain.ports.event_repo import EventRepository
from src.infrastructure.schema import EventORM, UserORM

class SqlAlchemyEventRepository(EventRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, event_id: str) -> Optional[CalendarEvent]:
        stmt = select(EventORM).where(EventORM.id == event_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_upcoming_events(self, slack_id: str, limit: int = 5) -> List[CalendarEvent]:
        stmt = (
            select(EventORM)
            .join(UserORM)
            .where(UserORM.slack_id == slack_id)
            .where(EventORM.start_time >= datetime.now().astimezone()) # Timezone aware comparison
            .order_by(EventORM.start_time.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(o) for o in orms]
        
    async def get_by_range(self, slack_id: str, start: datetime, end: datetime) -> List[CalendarEvent]:
        stmt = (
            select(EventORM)
            .join(UserORM)
            .where(UserORM.slack_id == slack_id)
            .where(EventORM.start_time >= start)
            .where(EventORM.end_time <= end)
            .order_by(EventORM.start_time.asc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(o) for o in orms]

    async def save(self, event: CalendarEvent, user_id: int) -> CalendarEvent:
        # Check existing
        stmt = select(EventORM).where(EventORM.id == event.id)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.summary = event.summary
            existing.description = event.description
            existing.location = event.location
            existing.start_time = event.start_time
            existing.end_time = event.end_time
            existing.status = event.status
            # user_id change? usually not allowed or handled here.
            await self.session.commit()
            await self.session.refresh(existing)
            return self._to_domain(existing)
        else:
            new_orm = EventORM(
                id=event.id,
                user_id=user_id,
                summary=event.summary,
                description=event.description,
                location=event.location,
                start_time=event.start_time,
                end_time=event.end_time,
                status=event.status
            )
            self.session.add(new_orm)
            await self.session.commit()
            await self.session.refresh(new_orm)
            return self._to_domain(new_orm)

    def _to_domain(self, orm: EventORM) -> CalendarEvent:
        return CalendarEvent(
            id=orm.id,
            summary=orm.summary,
            description=orm.description,
            location=orm.location,
            start_time=orm.start_time,
            end_time=orm.end_time,
            status=orm.status
        )
