"""
캐시 서비스 테스트

SQLite 기반 CacheService를 검증합니다.
"""


class TestCacheService:
    """CacheService 테스트"""

    def test_cache_service_can_be_imported(self):
        """CacheService를 import할 수 있는지 확인"""
        from src.services.cache.sqlite_cache import CacheService

        assert CacheService is not None

    def test_cache_service_initialization(self):
        """CacheService 초기화 테스트"""
        from src.services.cache.sqlite_cache import CacheService

        service = CacheService(db_path=":memory:")
        assert service is not None

    def test_cache_service_set_and_get(self):
        """캐시 저장 및 조회"""
        from src.services.cache.sqlite_cache import CacheService

        service = CacheService(db_path=":memory:")

        # 저장
        service.set("test:key", {"value": 123}, ttl_seconds=3600)

        # 조회
        result = service.get("test:key")
        assert result is not None
        assert result["value"] == 123

    def test_cache_service_get_not_found(self):
        """존재하지 않는 키 조회 시 None 반환"""
        from src.services.cache.sqlite_cache import CacheService

        service = CacheService(db_path=":memory:")

        result = service.get("nonexistent:key")
        assert result is None

    def test_cache_service_get_expired(self):
        """만료된 캐시 조회 시 None 반환"""
        from src.services.cache.sqlite_cache import CacheService

        service = CacheService(db_path=":memory:")

        # TTL 0초로 저장 (즉시 만료)
        service.set("test:key", {"value": 123}, ttl_seconds=0)

        # 조회 시 만료되어 None
        result = service.get("test:key")
        assert result is None

    def test_cache_service_delete(self):
        """캐시 삭제"""
        from src.services.cache.sqlite_cache import CacheService

        service = CacheService(db_path=":memory:")

        service.set("test:key", {"value": 123}, ttl_seconds=3600)
        service.delete("test:key")

        result = service.get("test:key")
        assert result is None

    def test_cache_service_clear_expired(self):
        """만료된 캐시 일괄 삭제"""
        from src.services.cache.sqlite_cache import CacheService

        service = CacheService(db_path=":memory:")

        # 만료된 캐시와 유효한 캐시 저장
        service.set("expired:key", {"value": 1}, ttl_seconds=0)
        service.set("valid:key", {"value": 2}, ttl_seconds=3600)

        # 만료된 것 정리
        service.clear_expired()

        assert service.get("expired:key") is None
        assert service.get("valid:key") is not None

    def test_cache_service_update_existing(self):
        """기존 캐시 업데이트"""
        from src.services.cache.sqlite_cache import CacheService

        service = CacheService(db_path=":memory:")

        service.set("test:key", {"value": 1}, ttl_seconds=3600)
        service.set("test:key", {"value": 2}, ttl_seconds=3600)  # 업데이트

        result = service.get("test:key")
        assert result["value"] == 2


class TestCacheServiceStats:
    """캐시 통계 테스트"""

    def test_cache_hit_count(self):
        """캐시 히트 카운트"""
        from src.services.cache.sqlite_cache import CacheService

        service = CacheService(db_path=":memory:")

        service.set("test:key", {"value": 1}, ttl_seconds=3600)
        service.get("test:key")  # 히트
        service.get("test:key")  # 히트

        stats = service.get_stats()
        assert stats["hits"] == 2

    def test_cache_miss_count(self):
        """캐시 미스 카운트"""
        from src.services.cache.sqlite_cache import CacheService

        service = CacheService(db_path=":memory:")

        service.get("nonexistent:key")  # 미스
        service.get("another:key")  # 미스

        stats = service.get_stats()
        assert stats["misses"] == 2

    def test_cache_hit_rate(self):
        """캐시 히트율 계산"""
        from src.services.cache.sqlite_cache import CacheService

        service = CacheService(db_path=":memory:")

        service.set("test:key", {"value": 1}, ttl_seconds=3600)
        service.get("test:key")  # 히트
        service.get("test:key")  # 히트
        service.get("nonexistent:key")  # 미스

        stats = service.get_stats()
        # 2 hits / 3 total = 66.67%
        assert 0.66 <= stats["hit_rate"] <= 0.67
