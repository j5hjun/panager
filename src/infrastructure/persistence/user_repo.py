from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domain.models.user import User
from src.domain.ports.user_repo import UserRepository
from src.infrastructure.schema import UserORM

class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_slack_id(self, slack_id: str) -> Optional[User]:
        stmt = select(UserORM).where(UserORM.slack_id == slack_id)
        result = await self.session.execute(stmt)
        user_orm = result.scalar_one_or_none()
        
        if not user_orm:
            return None
            
        return self._to_domain(user_orm)

    async def save(self, user: User) -> User:
        stmt = select(UserORM).where(UserORM.slack_id == user.slack_id)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.name = user.name
            existing.is_active = user.is_active
            existing.preferences = user.preferences
            await self.session.flush() # Commit is mostly done by service layer, but here we do simple save
            # But wait, repo usually doesn't commit transaction if UnitOfWork is used.
            # For simplicity in this project (as Plan didn't specify UoW), we commit here.
            await self.session.commit()
            await self.session.refresh(existing)
            return self._to_domain(existing)
        else:
            new_orm = UserORM(
                slack_id=user.slack_id,
                name=user.name,
                is_active=user.is_active,
                preferences=user.preferences
            )
            self.session.add(new_orm)
            await self.session.commit()
            await self.session.refresh(new_orm)
            return self._to_domain(new_orm)

    def _to_domain(self, orm: UserORM) -> User:
        return User(
            id=orm.id,
            slack_id=orm.slack_id,
            name=orm.name,
            is_active=orm.is_active,
            preferences=orm.preferences
        )
