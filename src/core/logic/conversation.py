"""
대화 관리자

사용자별 대화 기록을 관리합니다.
"""

import logging
from collections import defaultdict
from typing import Literal

logger = logging.getLogger(__name__)

MessageRole = Literal["user", "assistant", "system"]


class ConversationManager:
    """
    대화 기록 관리자

    사용자별로 대화 기록을 저장하고 관리합니다.
    """

    def __init__(self, max_history: int = 20):
        """
        ConversationManager 초기화

        Args:
            max_history: 사용자당 최대 대화 기록 수
        """
        self.max_history = max_history
        self._histories: dict[str, list[dict[str, str]]] = defaultdict(list)

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
        self._histories[user_id].append({"role": role, "content": content})

        # 최대 길이 초과 시 오래된 메시지 삭제
        if len(self._histories[user_id]) > self.max_history:
            self._histories[user_id] = self._histories[user_id][-self.max_history :]

        logger.debug(f"메시지 추가: {user_id} ({role}): {content[:50]}...")

    def get_history(self, user_id: str) -> list[dict[str, str]]:
        """
        사용자의 대화 기록 조회

        Args:
            user_id: 사용자 ID

        Returns:
            대화 기록 리스트
        """
        return self._histories[user_id].copy()

    def clear_history(self, user_id: str) -> None:
        """
        사용자의 대화 기록 초기화

        Args:
            user_id: 사용자 ID
        """
        self._histories[user_id] = []
        logger.info(f"대화 기록 초기화: {user_id}")

    def get_all_users(self) -> list[str]:
        """모든 사용자 ID 반환"""
        return list(self._histories.keys())
