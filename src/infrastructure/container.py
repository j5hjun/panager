"""의존성 주입(DI) 컨테이너"""
from typing import Optional
from functools import lru_cache

from src.config.settings import Settings
from src.infrastructure.db import get_db

# Repositories
from src.infrastructure.persistence.user_repo import SqlAlchemyUserRepository
from src.infrastructure.persistence.token_repo import SqlAlchemyTokenRepository
from src.infrastructure.persistence.event_repo import SqlAlchemyEventRepository

# Adapters
from src.infrastructure.google.calendar_adapter import GoogleCalendarAdapter
from src.infrastructure.google.auth import GoogleAuthManager
from src.infrastructure.slack.slack_adapter import SlackAdapter


@lru_cache()
def get_settings() -> Settings:
    """Settings 싱글톤"""
    return Settings()


class Container:
    """
    의존성 주입 컨테이너
    
    FastAPI의 Depends와 함께 사용하거나, 
    수동으로 인스턴스를 가져올 때 사용합니다.
    """
    
    _instance: Optional['Container'] = None
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self._slack_adapter: Optional[SlackAdapter] = None
        self._google_calendar_adapter: Optional[GoogleCalendarAdapter] = None
    
    @classmethod
    def get_instance(cls) -> 'Container':
        """Container 싱글톤 인스턴스"""
        if cls._instance is None:
            cls._instance = Container()
        return cls._instance
    
    # === Adapters ===
    
    @property
    def slack_adapter(self) -> SlackAdapter:
        """SlackAdapter 인스턴스"""
        if self._slack_adapter is None:
            if not self.settings.slack_bot_token:
                raise ValueError("SLACK_BOT_TOKEN is not configured")
            self._slack_adapter = SlackAdapter(
                bot_token=self.settings.slack_bot_token
            )
        return self._slack_adapter
    
    @property
    def google_calendar_adapter(self) -> GoogleCalendarAdapter:
        """GoogleCalendarAdapter 인스턴스"""
        if self._google_calendar_adapter is None:
            self._google_calendar_adapter = GoogleCalendarAdapter(
                settings=self.settings
            )
        return self._google_calendar_adapter
    
    # === Factory Methods (Session 필요) ===
    
    def get_user_repository(self, session):
        """UserRepository 인스턴스 생성"""
        return SqlAlchemyUserRepository(session)
    
    def get_token_repository(self, session):
        """TokenRepository 인스턴스 생성"""
        return SqlAlchemyTokenRepository(session)
    
    def get_event_repository(self, session):
        """EventRepository 인스턴스 생성"""
        return SqlAlchemyEventRepository(session)
    
    def get_google_auth_manager(self, session) -> GoogleAuthManager:
        """GoogleAuthManager 인스턴스 생성"""
        token_repo = self.get_token_repository(session)
        return GoogleAuthManager(
            token_repo=token_repo,
            settings=self.settings
        )


# === FastAPI Depends 헬퍼 ===

async def get_container() -> Container:
    """FastAPI Depends용 Container"""
    return Container.get_instance()


async def get_user_repo():
    """FastAPI Depends용 UserRepository"""
    container = Container.get_instance()
    async for session in get_db():
        yield container.get_user_repository(session)


async def get_token_repo():
    """FastAPI Depends용 TokenRepository"""
    container = Container.get_instance()
    async for session in get_db():
        yield container.get_token_repository(session)


async def get_event_repo():
    """FastAPI Depends용 EventRepository"""
    container = Container.get_instance()
    async for session in get_db():
        yield container.get_event_repository(session)


async def get_slack_adapter() -> SlackAdapter:
    """FastAPI Depends용 SlackAdapter"""
    return Container.get_instance().slack_adapter


async def get_calendar_adapter() -> GoogleCalendarAdapter:
    """FastAPI Depends용 GoogleCalendarAdapter"""
    return Container.get_instance().google_calendar_adapter
