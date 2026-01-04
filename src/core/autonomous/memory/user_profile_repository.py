"""
UserProfileRepository - 사용자 프로필 저장소

사용자 프로필 및 학습된 패턴을 SQLite에 저장합니다.
"""

import json
import logging
import sqlite3
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class UserProfileRepository:
    """
    사용자 프로필 저장소

    사용자의 선호도, 패턴 등을 저장하고 조회합니다.
    """

    def __init__(self, db_path: str = "data/memory.db"):
        """
        UserProfileRepository 초기화

        Args:
            db_path: SQLite DB 경로 (":memory:"면 인메모리 DB)
        """
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_table()

        logger.info(f"UserProfileRepository 초기화 완료 (db={db_path})")

    def _create_table(self) -> None:
        """테이블 생성"""
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                first_seen_at TEXT NOT NULL,
                last_active_at TEXT NOT NULL,
                preferences TEXT,
                patterns TEXT
            )
            """
        )
        self._conn.commit()

    def create(self, user_id: str) -> bool:
        """
        프로필 생성

        Args:
            user_id: 사용자 ID

        Returns:
            생성 성공 여부
        """
        now = datetime.now().isoformat()

        try:
            self._conn.execute(
                """
                INSERT INTO user_profiles (user_id, first_seen_at, last_active_at, preferences, patterns)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, now, now, "{}", "{}"),
            )
            self._conn.commit()
            logger.info(f"사용자 프로필 생성: {user_id}")
            return True
        except sqlite3.IntegrityError:
            # 이미 존재
            return False

    def get(self, user_id: str) -> dict[str, Any] | None:
        """
        프로필 조회

        Args:
            user_id: 사용자 ID

        Returns:
            프로필 dict 또는 None
        """
        cursor = self._conn.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_dict(row)

    def get_or_create(self, user_id: str) -> dict[str, Any]:
        """
        프로필 조회 (없으면 생성)

        Args:
            user_id: 사용자 ID

        Returns:
            프로필 dict
        """
        profile = self.get(user_id)
        if profile is None:
            self.create(user_id)
            profile = self.get(user_id)

        return profile  # type: ignore

    def get_all(self) -> list[dict[str, Any]]:
        """모든 프로필 조회"""
        cursor = self._conn.execute("SELECT * FROM user_profiles")
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def update_last_active(self, user_id: str) -> bool:
        """
        마지막 활동 시간 업데이트

        Args:
            user_id: 사용자 ID

        Returns:
            업데이트 성공 여부
        """
        now = datetime.now().isoformat()

        cursor = self._conn.execute(
            "UPDATE user_profiles SET last_active_at = ? WHERE user_id = ?",
            (now, user_id),
        )
        self._conn.commit()

        return cursor.rowcount > 0

    def update_preferences(self, user_id: str, preferences: dict[str, Any]) -> bool:
        """
        선호도 업데이트

        Args:
            user_id: 사용자 ID
            preferences: 선호도 dict

        Returns:
            업데이트 성공 여부
        """
        preferences_json = json.dumps(preferences, ensure_ascii=False)

        cursor = self._conn.execute(
            "UPDATE user_profiles SET preferences = ? WHERE user_id = ?",
            (preferences_json, user_id),
        )
        self._conn.commit()

        return cursor.rowcount > 0

    def update_patterns(self, user_id: str, patterns: dict[str, Any]) -> bool:
        """
        패턴 업데이트

        Args:
            user_id: 사용자 ID
            patterns: 학습된 패턴 dict

        Returns:
            업데이트 성공 여부
        """
        patterns_json = json.dumps(patterns, ensure_ascii=False)

        cursor = self._conn.execute(
            "UPDATE user_profiles SET patterns = ? WHERE user_id = ?",
            (patterns_json, user_id),
        )
        self._conn.commit()

        return cursor.rowcount > 0

    def delete(self, user_id: str) -> bool:
        """
        프로필 삭제

        Args:
            user_id: 사용자 ID

        Returns:
            삭제 성공 여부
        """
        cursor = self._conn.execute("DELETE FROM user_profiles WHERE user_id = ?", (user_id,))
        self._conn.commit()

        return cursor.rowcount > 0

    def _row_to_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        """Row를 dict로 변환"""
        return {
            "user_id": row["user_id"],
            "first_seen_at": row["first_seen_at"],
            "last_active_at": row["last_active_at"],
            "preferences": json.loads(row["preferences"]) if row["preferences"] else {},
            "patterns": json.loads(row["patterns"]) if row["patterns"] else {},
        }

    def close(self) -> None:
        """DB 연결 종료"""
        self._conn.close()
