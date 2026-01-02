"""
SQLite 기반 캐시 서비스

디스크에 캐시를 저장하여 메모리 사용을 최소화합니다.
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


class CacheService:
    """
    SQLite 기반 캐시 서비스

    디스크에 데이터를 저장하여 메모리 사용을 최소화합니다.
    1GB 환경에서도 안정적으로 동작합니다.
    """

    def __init__(self, db_path: str = "data/cache.db"):
        """
        CacheService 초기화

        Args:
            db_path: SQLite DB 경로 (":memory:"는 인메모리 DB)
        """
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

        # 통계
        self._hits = 0
        self._misses = 0

        logger.info(f"CacheService 초기화 완료 (db={db_path})")

    def _create_table(self) -> None:
        """캐시 테이블 생성"""
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """
        캐시 저장

        Args:
            key: 캐시 키
            value: 저장할 값 (JSON 직렬화 가능)
            ttl_seconds: TTL (초)
        """
        now = datetime.now()
        expires_at = now + timedelta(seconds=ttl_seconds)

        value_json = json.dumps(value, ensure_ascii=False)

        self._conn.execute(
            """
            INSERT OR REPLACE INTO cache (key, value, created_at, expires_at)
            VALUES (?, ?, ?, ?)
            """,
            (key, value_json, now.isoformat(), expires_at.isoformat()),
        )
        self._conn.commit()

        logger.debug(f"캐시 저장: {key} (TTL={ttl_seconds}s)")

    def get(self, key: str) -> Any | None:
        """
        캐시 조회

        Args:
            key: 캐시 키

        Returns:
            캐시된 값 또는 None (없거나 만료됨)
        """
        cursor = self._conn.execute("SELECT value, expires_at FROM cache WHERE key = ?", (key,))
        row = cursor.fetchone()

        if row is None:
            self._misses += 1
            logger.debug(f"캐시 미스: {key}")
            return None

        value_json, expires_at_str = row
        expires_at = datetime.fromisoformat(expires_at_str)

        if datetime.now() >= expires_at:
            # 만료됨 - 삭제하고 None 반환
            self.delete(key)
            self._misses += 1
            logger.debug(f"캐시 만료: {key}")
            return None

        self._hits += 1
        logger.debug(f"캐시 히트: {key}")
        return json.loads(value_json)

    def delete(self, key: str) -> None:
        """
        캐시 삭제

        Args:
            key: 삭제할 캐시 키
        """
        self._conn.execute("DELETE FROM cache WHERE key = ?", (key,))
        self._conn.commit()

    def clear_expired(self) -> int:
        """
        만료된 캐시 일괄 삭제

        Returns:
            삭제된 캐시 수
        """
        now = datetime.now().isoformat()
        cursor = self._conn.execute("DELETE FROM cache WHERE expires_at < ?", (now,))
        self._conn.commit()

        deleted = cursor.rowcount
        if deleted > 0:
            logger.info(f"만료된 캐시 {deleted}개 삭제됨")

        return deleted

    def get_stats(self) -> dict[str, Any]:
        """
        캐시 통계 조회

        Returns:
            {hits, misses, hit_rate, total_entries}
        """
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0

        cursor = self._conn.execute("SELECT COUNT(*) FROM cache")
        total_entries = cursor.fetchone()[0]

        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "total_entries": total_entries,
        }

    def close(self) -> None:
        """DB 연결 종료"""
        self._conn.close()
