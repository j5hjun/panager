"""
캐시 갱신 스케줄러 테스트
"""

from unittest.mock import MagicMock


class TestCacheRefreshScheduler:
    """CacheRefreshScheduler 테스트"""

    def test_can_be_imported(self):
        """import 확인"""
        from src.services.cache.refresh_scheduler import CacheRefreshScheduler

        assert CacheRefreshScheduler is not None

    def test_initialization(self):
        """초기화 테스트"""
        from src.services.cache.refresh_scheduler import CacheRefreshScheduler

        mock_cache = MagicMock()
        scheduler = CacheRefreshScheduler(cache_service=mock_cache)

        assert scheduler is not None

    def test_add_cleanup_job(self):
        """정리 작업 등록 테스트"""
        from src.services.cache.refresh_scheduler import CacheRefreshScheduler

        mock_cache = MagicMock()
        scheduler = CacheRefreshScheduler(cache_service=mock_cache)

        scheduler.add_cleanup_job(interval_minutes=30)

        stats = scheduler.get_stats()
        assert stats["job_count"] == 1

    def test_get_stats(self):
        """통계 조회 테스트"""
        from src.services.cache.refresh_scheduler import CacheRefreshScheduler

        mock_cache = MagicMock()
        mock_cache.get_stats.return_value = {"hits": 10, "misses": 5}

        scheduler = CacheRefreshScheduler(cache_service=mock_cache)
        stats = scheduler.get_stats()

        assert "running" in stats
        assert "job_count" in stats
        assert "cache_stats" in stats

    def test_start_and_stop(self):
        """시작/중지 테스트"""
        from src.services.cache.refresh_scheduler import CacheRefreshScheduler

        mock_cache = MagicMock()
        scheduler = CacheRefreshScheduler(cache_service=mock_cache)

        scheduler.start()
        assert scheduler._scheduler.running is True

        scheduler.stop()
        assert scheduler._scheduler.running is False
