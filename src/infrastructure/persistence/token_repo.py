from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload
from src.domain.models.token import Token
from src.domain.ports.token_repo import TokenRepository
from src.infrastructure.schema import TokenORM, UserORM

class SqlAlchemyTokenRepository(TokenRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_user_id(self, slack_id: str) -> Optional[Token]:
        stmt = (
            select(TokenORM)
            .join(UserORM)
            .where(UserORM.slack_id == slack_id)
        )
        result = await self.session.execute(stmt)
        token_orm = result.scalar_one_or_none()
        
        if not token_orm:
            return None
        
        # token_orm.user에 접근하려면 joinedload 필요하거나 explicit join.
        # 하지만 user_slack_id만 필요하므로, 여기서 다시 select user 필요없음. 
        # TokenORM에 user relationship이 있음.
        # But wait, we need slack_id to construct domain Token.
        # So we should eagerly load user.
        
        # Re-query with eager load if user is not loaded
        if 'user' not in token_orm.__dict__:
             # Lazy loading in async is tricky. Better to use joinedload in the first query.
             # 다시 작성
             stmt = (
                select(TokenORM)
                .join(UserORM)
                .options(joinedload(TokenORM.user))
                .where(UserORM.slack_id == slack_id)
            )
             result = await self.session.execute(stmt)
             token_orm = result.scalar_one_or_none()
             if not token_orm:
                 return None

        return self._to_domain(token_orm)

    async def save(self, token: Token) -> Token:
        # Find user internal ID first
        user_stmt = select(UserORM).where(UserORM.slack_id == token.user_slack_id)
        user_result = await self.session.execute(user_stmt)
        user_orm = user_result.scalar_one_or_none()
        
        if not user_orm:
            raise ValueError(f"User with slack_id {token.user_slack_id} not found")
        
        # Check existing token
        stmt = select(TokenORM).where(TokenORM.user_id == user_orm.id)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.access_token = token.access_token
            existing.refresh_token = token.refresh_token
            existing.expires_at = token.expires_at
            
            await self.session.commit()
            await self.session.refresh(existing)
            # Need to re-fetch user for domain conversion? We know the slack_id already.
            # But let's construct domain manually to save query.
            return token # Return the input object as it's updated basically.
        else:
            new_orm = TokenORM(
                user_id=user_orm.id,
                access_token=token.access_token,
                refresh_token=token.refresh_token,
                expires_at=token.expires_at
            )
            self.session.add(new_orm)
            await self.session.commit()
            await self.session.refresh(new_orm)
            return token

    async def delete(self, slack_id: str) -> None:
        # User ID lookup needed? or Delete via Join?
        # Delete with Join is supported in newer SA or PG.
        # But simpler: subquery.
        
        subq = select(UserORM.id).where(UserORM.slack_id == slack_id).scalar_subquery()
        stmt = delete(TokenORM).where(TokenORM.user_id == subq)
        await self.session.execute(stmt)
        await self.session.commit()

    def _to_domain(self, orm: TokenORM) -> Token:
        return Token(
            user_slack_id=orm.user.slack_id,
            access_token=orm.access_token,
            refresh_token=orm.refresh_token,
            expires_at=orm.expires_at
        )
