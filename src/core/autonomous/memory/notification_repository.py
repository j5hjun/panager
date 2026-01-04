"""
NotificationRepository - 알림 이력 저장소

자율 판단 시스템에서 보낸 알림 이력을 SQLite에 저장합니다.
"""

import logging
import sqlite3
import uuid
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class NotificationRepository:
    """
    알림 이력 저장소

    Act 노드에서 전송한 알림을 기록하고 조회합니다.
    최대 100개의 알림 이력을 유지합니다.
    """

    MAX_NOTIFICATIONS = 100

    def __init__(self, db_path: str = "data/memory.db"):
        """
        NotificationRepository 초기화

        Args:
            db_path: SQLite DB 경로 (":memory:"면 인메모리 DB)
        """
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_table()

        logger.info(f"NotificationRepository 초기화 완료 (db={db_path})")

    def _create_table(self) -> None:
        """테이블 생성"""
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notification_history (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                message TEXT NOT NULL,
                notification_type TEXT,
                sent_at TEXT NOT NULL,
                user_reaction TEXT,
                reaction_at TEXT
            )
            """
        )
        self._conn.commit()

    def save(
        self,
        user_id: str,
        message: str,
        notification_type: str = "general",
    ) -> str:
        """
        알림 저장

        Args:
            user_id: 사용자 ID
            message: 알림 메시지
            notification_type: 알림 유형

        Returns:
            생성된 알림 ID
        """
        notification_id = str(uuid.uuid4())[:8]
        sent_at = datetime.now().isoformat()

        self._conn.execute(
            """
            INSERT INTO notification_history (id, user_id, message, notification_type, sent_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (notification_id, user_id, message, notification_type, sent_at),
        )
        self._conn.commit()

        # 최대 개수 초과 시 오래된 것 삭제
        self._enforce_limit(user_id)

        logger.debug(f"알림 저장: {notification_id}")
        return notification_id

    def get(self, notification_id: str) -> dict[str, Any] | None:
        """
        단일 알림 조회

        Args:
            notification_id: 알림 ID

        Returns:
            알림 dict 또는 None
        """
        cursor = self._conn.execute(
            "SELECT * FROM notification_history WHERE id = ?", (notification_id,)
        )
        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_dict(row)

    def get_by_user(self, user_id: str) -> list[dict[str, Any]]:
        """
        사용자별 알림 조회

        Args:
            user_id: 사용자 ID

        Returns:
            알림 목록
        """
        cursor = self._conn.execute(
            "SELECT * FROM notification_history WHERE user_id = ? ORDER BY sent_at DESC",
            (user_id,),
        )
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def update_reaction(self, notification_id: str, reaction: str) -> bool:
        """
        사용자 반응 업데이트

        Args:
            notification_id: 알림 ID
            reaction: 반응 (positive/negative/neutral)

        Returns:
            업데이트 성공 여부
        """
        reaction_at = datetime.now().isoformat()

        cursor = self._conn.execute(
            """
            UPDATE notification_history
            SET user_reaction = ?, reaction_at = ?
            WHERE id = ?
            """,
            (reaction, reaction_at, notification_id),
        )
        self._conn.commit()

        return cursor.rowcount > 0

    def get_today_count(self, user_id: str) -> int:
        """
        오늘 알림 개수 조회

        Args:
            user_id: 사용자 ID

        Returns:
            오늘 보낸 알림 개수
        """
        today = datetime.now().strftime("%Y-%m-%d")

        cursor = self._conn.execute(
            """
            SELECT COUNT(*) FROM notification_history
            WHERE user_id = ? AND sent_at LIKE ?
            """,
            (user_id, f"{today}%"),
        )

        return cursor.fetchone()[0]

    def get_recent(self, user_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        최근 알림 조회

        Args:
            user_id: 사용자 ID
            limit: 조회할 개수

        Returns:
            최신순 알림 목록
        """
        cursor = self._conn.execute(
            """
            SELECT * FROM notification_history
            WHERE user_id = ?
            ORDER BY sent_at DESC LIMIT ?
            """,
            (user_id, limit),
        )
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def _enforce_limit(self, user_id: str) -> None:
        """최대 알림 개수 유지 (사용자별)"""
        self._conn.execute(
            """
            DELETE FROM notification_history WHERE id IN (
                SELECT id FROM notification_history
                WHERE user_id = ?
                ORDER BY sent_at DESC LIMIT -1 OFFSET ?
            )
            """,
            (user_id, self.MAX_NOTIFICATIONS),
        )
        self._conn.commit()

    def _row_to_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        """Row를 dict로 변환"""
        return {
            "id": row["id"],
            "user_id": row["user_id"],
            "message": row["message"],
            "notification_type": row["notification_type"],
            "sent_at": row["sent_at"],
            "user_reaction": row["user_reaction"],
            "reaction_at": row["reaction_at"],
        }

    def close(self) -> None:
        """DB 연결 종료"""
        self._conn.close()
