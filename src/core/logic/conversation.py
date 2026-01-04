"""
대화 관리자

사용자별 대화 기록을 관리합니다.
P-011 Phase 6: SQLite 영속화
"""

import logging
from typing import Literal

from src.core.autonomous.memory.conversation_repository import ConversationRepository

logger = logging.getLogger(__name__)

MessageRole = Literal["user", "assistant", "system"]


class ConversationManager:
    """
    대화 기록 관리자

    사용자별로 대화 기록을 저장하고 관리합니다.
    P-011: SQLite 기반 영속화
    """

    def __init__(
        self,
        max_history: int = 20,
        repository: ConversationRepository | None = None,
        db_path: str = "data/memory.db",
    ):
        """
        ConversationManager 초기화

        Args:
            max_history: 사용자당 최대 대화 기록 수
            repository: ConversationRepository (DI용)
            db_path: DB 경로 (repository가 없을 때 사용)
        """
        self.max_history = max_history
        self._repository = repository or ConversationRepository(
            db_path=db_path, max_history=max_history
        )

        logger.info(f"ConversationManager 초기화 (max_history={max_history})")

    def add_message(
        self,
        user_id: str,
        role: MessageRole,
        content: str,
    ) -> None:
        """
        대화에 메시지 추가

        Args:
            user_id: 사용자 ID
            role: 메시지 역할 (user, assistant, system)
            content: 메시지 내용
        """
        self._repository.add_message(user_id, role, content)

    def get_history(self, user_id: str) -> list[dict[str, str]]:
        """
        사용자의 대화 기록 조회

        Args:
            user_id: 사용자 ID

        Returns:
            대화 기록 리스트
        """
        return self._repository.get_history(user_id, limit=self.max_history)

    def clear_history(self, user_id: str) -> None:
        """
        사용자의 대화 기록 초기화

        Args:
            user_id: 사용자 ID
        """
        self._repository.clear_history(user_id)

    def get_all_users(self) -> list[str]:
        """모든 사용자 ID 반환"""
        return self._repository.get_all_users()

    def close(self) -> None:
        """리소스 정리"""
        self._repository.close()
