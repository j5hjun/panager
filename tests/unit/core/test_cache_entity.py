"""
캐시 엔티티 테스트

CachedData 모델을 검증합니다.
"""

from datetime import datetime, timedelta


class TestCachedData:
    """CachedData 테스트"""

    def test_cached_data_can_be_imported(self):
        """CachedData를 import할 수 있는지 확인"""
        from src.core.entities.cache import CachedData

        assert CachedData is not None

    def test_cached_data_creation(self):
        """CachedData 생성 테스트"""
        from src.core.entities.cache import CachedData

        now = datetime.now()
        cached = CachedData(
            key="weather:seoul",
            value={"temp": 15, "condition": "맑음"},
            created_at=now,
            expires_at=now + timedelta(hours=1),
        )

        assert cached.key == "weather:seoul"
        assert cached.value["temp"] == 15
        assert cached.created_at == now

    def test_cached_data_is_expired_false(self):
        """만료되지 않은 캐시 확인"""
        from src.core.entities.cache import CachedData

        now = datetime.now()
        cached = CachedData(
            key="weather:seoul",
            value={"temp": 15},
            created_at=now,
            expires_at=now + timedelta(hours=1),
        )

        assert cached.is_expired() is False

    def test_cached_data_is_expired_true(self):
        """만료된 캐시 확인"""
        from src.core.entities.cache import CachedData

        past = datetime.now() - timedelta(hours=2)
        cached = CachedData(
            key="weather:seoul",
            value={"temp": 15},
            created_at=past,
            expires_at=past + timedelta(hours=1),  # 1시간 전에 만료됨
        )

        assert cached.is_expired() is True

    def test_cached_data_ttl_seconds(self):
        """TTL(초) 계산 테스트"""
        from src.core.entities.cache import CachedData

        now = datetime.now()
        cached = CachedData(
            key="weather:seoul",
            value={"temp": 15},
            created_at=now,
            expires_at=now + timedelta(hours=1),
        )

        # TTL은 대략 3600초 (1시간)에 가까워야 함
        assert 3590 <= cached.ttl_seconds() <= 3600

    def test_cached_data_ttl_seconds_expired(self):
        """만료된 캐시의 TTL은 0"""
        from src.core.entities.cache import CachedData

        past = datetime.now() - timedelta(hours=2)
        cached = CachedData(
            key="weather:seoul",
            value={"temp": 15},
            created_at=past,
            expires_at=past + timedelta(hours=1),
        )

        assert cached.ttl_seconds() == 0


class TestCacheKey:
    """캐시 키 생성 테스트"""

    def test_generate_cache_key(self):
        """캐시 키 생성 함수 테스트"""
        from src.core.entities.cache import generate_cache_key

        key = generate_cache_key("weather", city="seoul")
        assert key == "weather:city=seoul"

    def test_generate_cache_key_multiple_params(self):
        """여러 파라미터로 캐시 키 생성"""
        from src.core.entities.cache import generate_cache_key

        key = generate_cache_key("directions", origin="창동역", destination="강남역")
        assert "directions:" in key
        assert "origin=창동역" in key
        assert "destination=강남역" in key

    def test_generate_cache_key_no_params(self):
        """파라미터 없이 캐시 키 생성"""
        from src.core.entities.cache import generate_cache_key

        key = generate_cache_key("news")
        assert key == "news"
