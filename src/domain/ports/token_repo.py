from abc import ABC, abstractmethod
from typing import Optional
from src.domain.models.token import Token

class TokenRepository(ABC):
    @abstractmethod
    async def get_by_user_id(self, slack_id: str) -> Optional[Token]:
        pass

    @abstractmethod
    async def save(self, token: Token) -> Token:
        pass
    
    @abstractmethod
    async def delete(self, slack_id: str) -> None:
        pass
