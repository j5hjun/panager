from abc import ABC, abstractmethod
from typing import Optional
from src.domain.models.user import User

class UserRepository(ABC):
    @abstractmethod
    async def get_by_slack_id(self, slack_id: str) -> Optional[User]:
        pass

    @abstractmethod
    async def save(self, user: User) -> User:
        pass
