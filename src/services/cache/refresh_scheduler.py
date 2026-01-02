"""
캐시 갱신 스케줄러

백그라운드에서 주기적으로 캐시를 갱신합니다.
"""

import logging
from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler

from src.services.cache.sqlite_cache import CacheService

logger = logging.getLogger(__name__)


class CacheRefreshScheduler:
    """
    캐시 갱신 스케줄러

    - 만료된 캐시 정리
    - 자주 사용하는 데이터 미리 갱신
    """

    def __init__(self, cache_service: CacheService):
        """
        CacheRefreshScheduler 초기화

        Args:
            cache_service: 캐시 서비스
        """
        self._cache = cache_service
        self._scheduler = BackgroundScheduler()
        self._refresh_callbacks: list[tuple[str, Any]] = []

        logger.info("CacheRefreshScheduler 초기화 완료")

    def add_refresh_job(
        self,
        job_id: str,
        callback: Any,
        interval_minutes: int,
    ) -> None:
        """
        캐시 갱신 작업 추가

        Args:
            job_id: 작업 ID
            callback: 갱신 콜백 함수 (async 함수)
            interval_minutes: 갱신 주기 (분)
        """
        self._refresh_callbacks.append((job_id, callback))

        # APScheduler는 동기 함수만 지원하므로 래퍼 사용
        def sync_wrapper():
            import asyncio

            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            try:
                loop.run_until_complete(callback())
                logger.info(f"캐시 갱신 완료: {job_id}")
            except Exception as e:
                logger.error(f"캐시 갱신 실패: {job_id} - {e}")

        self._scheduler.add_job(
            sync_wrapper,
            "interval",
            minutes=interval_minutes,
            id=job_id,
        )
        logger.info(f"캐시 갱신 작업 등록: {job_id} (주기={interval_minutes}분)")

    def add_cleanup_job(self, interval_minutes: int = 30) -> None:
        """
        만료된 캐시 정리 작업 추가

        Args:
            interval_minutes: 정리 주기 (분)
        """

        def cleanup():
            deleted = self._cache.clear_expired()
            if deleted > 0:
                logger.info(f"만료된 캐시 {deleted}개 정리됨")

        self._scheduler.add_job(
            cleanup,
            "interval",
            minutes=interval_minutes,
            id="cache_cleanup",
        )
        logger.info(f"캐시 정리 작업 등록 (주기={interval_minutes}분)")

    def start(self) -> None:
        """스케줄러 시작"""
        if not self._scheduler.running:
            self._scheduler.start()
            logger.info("캐시 갱신 스케줄러 시작됨")

    def stop(self) -> None:
        """스케줄러 중지"""
        if self._scheduler.running:
            self._scheduler.shutdown()
            logger.info("캐시 갱신 스케줄러 중지됨")

    def get_stats(self) -> dict[str, Any]:
        """스케줄러 통계"""
        jobs = self._scheduler.get_jobs()
        return {
            "running": self._scheduler.running,
            "job_count": len(jobs),
            "jobs": [
                {"id": job.id, "next_run": str(getattr(job, "next_fire_time", None))}
                for job in jobs
            ],
            "cache_stats": self._cache.get_stats(),
        }
