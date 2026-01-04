"""
LessonRepository - 교훈 저장소

자율 판단 시스템에서 학습한 교훈을 SQLite에 저장합니다.
"""

import json
import logging
import sqlite3
import uuid
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class LessonRepository:
    """
    교훈 저장소

    Reflect 노드에서 추출한 교훈을 저장하고 조회합니다.
    최대 50개의 교훈을 유지합니다.
    """

    MAX_LESSONS = 50

    def __init__(self, db_path: str = "data/memory.db"):
        """
        LessonRepository 초기화

        Args:
            db_path: SQLite DB 경로 (":memory:"면 인메모리 DB)
        """
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_table()

        logger.info(f"LessonRepository 초기화 완료 (db={db_path})")

    def _create_table(self) -> None:
        """테이블 생성"""
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS lessons (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                context TEXT,
                user_reaction TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    def save(
        self,
        content: str,
        context: dict[str, Any] | None = None,
        user_reaction: str = "neutral",
    ) -> str:
        """
        교훈 저장

        Args:
            content: 교훈 내용
            context: 발생 맥락 (JSON 직렬화)
            user_reaction: 사용자 반응 (positive/negative/neutral)

        Returns:
            생성된 교훈 ID
        """
        lesson_id = str(uuid.uuid4())[:8]
        created_at = datetime.now().isoformat()
        context_json = json.dumps(context or {}, ensure_ascii=False)

        self._conn.execute(
            """
            INSERT INTO lessons (id, content, context, user_reaction, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (lesson_id, content, context_json, user_reaction, created_at),
        )
        self._conn.commit()

        # 최대 개수 초과 시 오래된 것 삭제
        self._enforce_limit()

        logger.debug(f"교훈 저장: {lesson_id}")
        return lesson_id

    def get(self, lesson_id: str) -> dict[str, Any] | None:
        """
        단일 교훈 조회

        Args:
            lesson_id: 교훈 ID

        Returns:
            교훈 dict 또는 None
        """
        cursor = self._conn.execute("SELECT * FROM lessons WHERE id = ?", (lesson_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_dict(row)

    def get_all(self) -> list[dict[str, Any]]:
        """모든 교훈 조회"""
        cursor = self._conn.execute("SELECT * FROM lessons ORDER BY created_at DESC")
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def get_recent(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        최근 교훈 조회

        Args:
            limit: 조회할 개수

        Returns:
            최신순 교훈 목록
        """
        cursor = self._conn.execute(
            "SELECT * FROM lessons ORDER BY created_at DESC LIMIT ?", (limit,)
        )
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def get_by_reaction(self, reaction: str) -> list[dict[str, Any]]:
        """
        반응 유형별 교훈 조회

        Args:
            reaction: 반응 유형 (positive/negative/neutral)

        Returns:
            해당 반응의 교훈 목록
        """
        cursor = self._conn.execute(
            "SELECT * FROM lessons WHERE user_reaction = ? ORDER BY created_at DESC",
            (reaction,),
        )
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def delete(self, lesson_id: str) -> bool:
        """
        교훈 삭제

        Args:
            lesson_id: 삭제할 교훈 ID

        Returns:
            삭제 성공 여부
        """
        cursor = self._conn.execute("DELETE FROM lessons WHERE id = ?", (lesson_id,))
        self._conn.commit()
        return cursor.rowcount > 0

    def _enforce_limit(self) -> None:
        """최대 교훈 개수 유지"""
        self._conn.execute(
            """
            DELETE FROM lessons WHERE id IN (
                SELECT id FROM lessons ORDER BY created_at DESC LIMIT -1 OFFSET ?
            )
            """,
            (self.MAX_LESSONS,),
        )
        self._conn.commit()

    def _row_to_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        """Row를 dict로 변환"""
        return {
            "id": row["id"],
            "content": row["content"],
            "context": json.loads(row["context"]) if row["context"] else {},
            "user_reaction": row["user_reaction"],
            "created_at": row["created_at"],
        }

    def close(self) -> None:
        """DB 연결 종료"""
        self._conn.close()
