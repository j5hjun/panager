"""
ConversationRepository - 대화 기록 저장소

사용자별 대화 기록을 SQLite에 저장합니다.
"""

import logging
import sqlite3
from datetime import datetime
from typing import Literal

logger = logging.getLogger(__name__)

MessageRole = Literal["user", "assistant", "system"]


class ConversationRepository:
    """
    대화 기록 저장소

    사용자별 대화 기록을 SQLite에 저장합니다.
    """

    def __init__(self, db_path: str = "data/memory.db", max_history: int = 20):
        """
        ConversationRepository 초기화

        Args:
            db_path: SQLite DB 경로 (":memory:"면 인메모리 DB)
            max_history: 사용자당 최대 대화 기록 수
        """
        self.db_path = db_path
        self.max_history = max_history
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_table()

        logger.info(f"ConversationRepository 초기화 완료 (db={db_path})")

    def _create_table(self) -> None:
        """테이블 생성"""
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id)"
        )
        self._conn.commit()

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
        created_at = datetime.now().isoformat()

        self._conn.execute(
            """
            INSERT INTO conversations (user_id, role, content, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, role, content, created_at),
        )
        self._conn.commit()

        # 최대 개수 초과 시 오래된 메시지 삭제
        self._enforce_limit(user_id)

        logger.debug(f"메시지 추가: {user_id} ({role}): {content[:50]}...")

    def get_history(self, user_id: str, limit: int | None = None) -> list[dict[str, str]]:
        """
        사용자의 대화 기록 조회

        Args:
            user_id: 사용자 ID
            limit: 조회할 최대 개수 (기본값: max_history)

        Returns:
            대화 기록 리스트
        """
        limit = limit or self.max_history

        cursor = self._conn.execute(
            """
            SELECT role, content FROM conversations
            WHERE user_id = ?
            ORDER BY id DESC LIMIT ?
            """,
            (user_id, limit),
        )

        # 역순으로 가져왔으므로 다시 역순 (오래된 것이 먼저)
        rows = cursor.fetchall()
        return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]

    def clear_history(self, user_id: str) -> None:
        """
        사용자의 대화 기록 초기화

        Args:
            user_id: 사용자 ID
        """
        self._conn.execute("DELETE FROM conversations WHERE user_id = ?", (user_id,))
        self._conn.commit()
        logger.info(f"대화 기록 초기화: {user_id}")

    def get_all_users(self) -> list[str]:
        """모든 사용자 ID 반환"""
        cursor = self._conn.execute("SELECT DISTINCT user_id FROM conversations")
        return [row[0] for row in cursor.fetchall()]

    def _enforce_limit(self, user_id: str) -> None:
        """사용자별 최대 대화 기록 유지"""
        self._conn.execute(
            """
            DELETE FROM conversations WHERE id IN (
                SELECT id FROM conversations
                WHERE user_id = ?
                ORDER BY id DESC LIMIT -1 OFFSET ?
            )
            """,
            (user_id, self.max_history),
        )
        self._conn.commit()

    def close(self) -> None:
        """DB 연결 종료"""
        self._conn.close()
