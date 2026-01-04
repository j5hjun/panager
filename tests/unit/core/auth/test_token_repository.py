"""
TokenRepository 테스트

TDD RED Phase: 토큰 저장소가 구현되기 전에 작성된 테스트
"""

import pytest
from datetime import datetime, timedelta


class TestTokenRepository:
    """TokenRepository 테스트"""

    @pytest.fixture
    def repository(self):
        """테스트용 인메모리 TokenRepository"""
        from src.core.auth.token_repository import TokenRepository

        repo = TokenRepository(db_path=":memory:", encryption_key="test-key-32-bytes-long-padding!")
        yield repo
        repo.close()

    def test_save_token(self, repository):
        """토큰을 저장할 수 있어야 함"""
        expires_at = datetime.now() + timedelta(hours=1)

        repository.save_token(
            user_id="U123",
            provider="google",
            access_token="access_token_123",
            refresh_token="refresh_token_123",
            expires_at=expires_at,
        )

        token = repository.get_token("U123", "google")
        assert token is not None
        assert token["access_token"] == "access_token_123"
        assert token["refresh_token"] == "refresh_token_123"

    def test_get_token(self, repository):
        """저장된 토큰을 조회할 수 있어야 함"""
        expires_at = datetime.now() + timedelta(hours=1)

        repository.save_token(
            user_id="U123",
            provider="google",
            access_token="access_123",
            refresh_token="refresh_123",
            expires_at=expires_at,
        )

        token = repository.get_token("U123", "google")
        assert token is not None
        assert token["user_id"] == "U123"
        assert token["provider"] == "google"

    def test_get_token_not_found(self, repository):
        """존재하지 않는 토큰은 None 반환"""
        token = repository.get_token("U999", "google")
        assert token is None

    def test_delete_token(self, repository):
        """토큰을 삭제할 수 있어야 함"""
        expires_at = datetime.now() + timedelta(hours=1)

        repository.save_token(
            user_id="U123",
            provider="google",
            access_token="access_123",
            refresh_token="refresh_123",
            expires_at=expires_at,
        )

        result = repository.delete_token("U123", "google")
        assert result is True

        token = repository.get_token("U123", "google")
        assert token is None

    def test_token_encryption(self, repository):
        """토큰은 암호화되어 저장되어야 함"""
        expires_at = datetime.now() + timedelta(hours=1)

        repository.save_token(
            user_id="U123",
            provider="google",
            access_token="plain_access_token",
            refresh_token="plain_refresh_token",
            expires_at=expires_at,
        )

        # DB에서 직접 조회하여 암호화 확인
        cursor = repository._conn.cursor()
        cursor.execute(
            "SELECT access_token, refresh_token FROM oauth_tokens WHERE user_id = ?",
            ("U123",),
        )
        row = cursor.fetchone()

        # 평문이 아닌 암호화된 값이 저장되어야 함
        assert row[0] != "plain_access_token"
        assert row[1] != "plain_refresh_token"

    def test_list_user_tokens(self, repository):
        """사용자의 모든 토큰 목록 조회"""
        expires_at = datetime.now() + timedelta(hours=1)

        repository.save_token("U123", "google", "access1", "refresh1", expires_at)
        repository.save_token("U123", "icloud", "access2", "refresh2", expires_at)
        repository.save_token("U456", "google", "access3", "refresh3", expires_at)

        tokens = repository.list_user_tokens("U123")
        assert len(tokens) == 2

        providers = [t["provider"] for t in tokens]
        assert "google" in providers
        assert "icloud" in providers

    def test_update_token(self, repository):
        """기존 토큰 업데이트"""
        expires_at = datetime.now() + timedelta(hours=1)

        repository.save_token("U123", "google", "old_access", "old_refresh", expires_at)
        repository.save_token("U123", "google", "new_access", "new_refresh", expires_at)

        token = repository.get_token("U123", "google")
        assert token["access_token"] == "new_access"
        assert token["refresh_token"] == "new_refresh"

    def test_get_expiring_tokens(self, repository):
        """만료 임박 토큰 조회"""
        soon = datetime.now() + timedelta(minutes=5)
        later = datetime.now() + timedelta(hours=2)

        repository.save_token("U123", "google", "access1", "refresh1", soon)
        repository.save_token("U456", "google", "access2", "refresh2", later)

        # 10분 내 만료되는 토큰
        expiring = repository.get_expiring_tokens(minutes=10)
        assert len(expiring) == 1
        assert expiring[0]["user_id"] == "U123"
