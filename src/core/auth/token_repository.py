"""
토큰 저장소

OAuth 토큰을 SQLite에 암호화하여 저장합니다.
"""

import base64
import hashlib
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Any

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class TokenRepository:
    """
    OAuth 토큰 저장소

    사용자별 OAuth 토큰을 암호화하여 SQLite에 저장합니다.
    """

    def __init__(self, db_path: str = "data/auth.db", encryption_key: str | None = None):
        """
        TokenRepository 초기화

        Args:
            db_path: SQLite DB 경로 (":memory:"면 인메모리)
            encryption_key: 암호화 키 (32바이트 이상 권장)
        """
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None

        # Fernet 키 생성 (32바이트 base64 인코딩)
        if encryption_key:
            # 키를 32바이트로 패딩하고 base64 인코딩
            key_bytes = hashlib.sha256(encryption_key.encode()).digest()
            self._fernet_key = base64.urlsafe_b64encode(key_bytes)
        else:
            # 키가 없으면 새로 생성 (프로덕션에서는 환경변수 사용)
            self._fernet_key = Fernet.generate_key()

        self._fernet = Fernet(self._fernet_key)
        self._init_db()

        logger.info(f"TokenRepository 초기화 (db={db_path})")

    def _init_db(self) -> None:
        """데이터베이스 초기화"""
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row

        cursor = self._conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS oauth_tokens (
                user_id TEXT NOT NULL,
                provider TEXT NOT NULL,
                access_token TEXT NOT NULL,
                refresh_token TEXT,
                expires_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (user_id, provider)
            )
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_expires ON oauth_tokens(expires_at)")
        self._conn.commit()

    def _encrypt(self, plaintext: str) -> str:
        """문자열 암호화"""
        return self._fernet.encrypt(plaintext.encode()).decode()

    def _decrypt(self, ciphertext: str) -> str:
        """문자열 복호화"""
        return self._fernet.decrypt(ciphertext.encode()).decode()

    def save_token(
        self,
        user_id: str,
        provider: str,
        access_token: str,
        refresh_token: str | None = None,
        expires_at: datetime | None = None,
    ) -> None:
        """
        OAuth 토큰 저장 (암호화)

        Args:
            user_id: 사용자 ID (Slack user ID)
            provider: 제공자 (google, icloud)
            access_token: 액세스 토큰
            refresh_token: 리프레시 토큰
            expires_at: 만료 시간
        """
        if not self._conn:
            raise RuntimeError("Database connection not initialized")

        encrypted_access = self._encrypt(access_token)
        encrypted_refresh = self._encrypt(refresh_token) if refresh_token else None
        now = datetime.now().isoformat()

        cursor = self._conn.cursor()
        cursor.execute(
            """
            INSERT INTO oauth_tokens
                (user_id, provider, access_token, refresh_token, expires_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, provider) DO UPDATE SET
                access_token = excluded.access_token,
                refresh_token = excluded.refresh_token,
                expires_at = excluded.expires_at,
                updated_at = excluded.updated_at
            """,
            (
                user_id,
                provider,
                encrypted_access,
                encrypted_refresh,
                expires_at.isoformat() if expires_at else None,
                now,
                now,
            ),
        )
        self._conn.commit()
        logger.info(f"토큰 저장: {user_id}/{provider}")

    def get_token(self, user_id: str, provider: str) -> dict[str, Any] | None:
        """
        OAuth 토큰 조회

        Args:
            user_id: 사용자 ID
            provider: 제공자

        Returns:
            토큰 정보 딕셔너리 또는 None
        """
        if not self._conn:
            raise RuntimeError("Database connection not initialized")

        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM oauth_tokens WHERE user_id = ? AND provider = ?",
            (user_id, provider),
        )
        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "user_id": row["user_id"],
            "provider": row["provider"],
            "access_token": self._decrypt(row["access_token"]),
            "refresh_token": (
                self._decrypt(row["refresh_token"]) if row["refresh_token"] else None
            ),
            "expires_at": (
                datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None
            ),
            "created_at": datetime.fromisoformat(row["created_at"]),
            "updated_at": datetime.fromisoformat(row["updated_at"]),
        }

    def delete_token(self, user_id: str, provider: str) -> bool:
        """
        OAuth 토큰 삭제

        Args:
            user_id: 사용자 ID
            provider: 제공자

        Returns:
            삭제 성공 여부
        """
        if not self._conn:
            raise RuntimeError("Database connection not initialized")

        cursor = self._conn.cursor()
        cursor.execute(
            "DELETE FROM oauth_tokens WHERE user_id = ? AND provider = ?",
            (user_id, provider),
        )
        self._conn.commit()

        deleted = cursor.rowcount > 0
        if deleted:
            logger.info(f"토큰 삭제: {user_id}/{provider}")
        return deleted

    def list_user_tokens(self, user_id: str) -> list[dict[str, Any]]:
        """
        사용자의 모든 토큰 조회

        Args:
            user_id: 사용자 ID

        Returns:
            토큰 정보 리스트
        """
        if not self._conn:
            raise RuntimeError("Database connection not initialized")

        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM oauth_tokens WHERE user_id = ?",
            (user_id,),
        )

        tokens = []
        for row in cursor.fetchall():
            tokens.append(
                {
                    "user_id": row["user_id"],
                    "provider": row["provider"],
                    "access_token": self._decrypt(row["access_token"]),
                    "refresh_token": (
                        self._decrypt(row["refresh_token"]) if row["refresh_token"] else None
                    ),
                    "expires_at": (
                        datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None
                    ),
                    "created_at": datetime.fromisoformat(row["created_at"]),
                    "updated_at": datetime.fromisoformat(row["updated_at"]),
                }
            )

        return tokens

    def get_expiring_tokens(self, minutes: int = 10) -> list[dict[str, Any]]:
        """
        만료 임박 토큰 조회

        Args:
            minutes: 이 시간 내 만료되는 토큰

        Returns:
            만료 임박 토큰 리스트
        """
        if not self._conn:
            raise RuntimeError("Database connection not initialized")

        threshold = (datetime.now() + timedelta(minutes=minutes)).isoformat()

        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT * FROM oauth_tokens
            WHERE expires_at IS NOT NULL AND expires_at <= ?
            ORDER BY expires_at
            """,
            (threshold,),
        )

        tokens = []
        for row in cursor.fetchall():
            tokens.append(
                {
                    "user_id": row["user_id"],
                    "provider": row["provider"],
                    "access_token": self._decrypt(row["access_token"]),
                    "refresh_token": (
                        self._decrypt(row["refresh_token"]) if row["refresh_token"] else None
                    ),
                    "expires_at": (
                        datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None
                    ),
                }
            )

        return tokens

    def close(self) -> None:
        """리소스 정리"""
        if self._conn:
            self._conn.close()
            self._conn = None
