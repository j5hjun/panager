"""
스케줄러 서비스

APScheduler를 활용한 작업 스케줄링 서비스
"""

import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class SchedulerService:
    """
    스케줄러 서비스

    APScheduler를 래핑하여 작업 스케줄링을 제공합니다.
    """

    def __init__(self):
        """SchedulerService 초기화"""
        self._scheduler = BackgroundScheduler()
        self._started = False

        logger.info("SchedulerService 초기화 완료")

    def add_job(
        self,
        job_id: str,
        func: Callable,
        trigger: str = "interval",
        **trigger_args: Any,
    ) -> str:
        """
        작업 등록

        Args:
            job_id: 작업 ID
            func: 실행할 함수
            trigger: 트리거 유형 (interval, cron, date)
            **trigger_args: 트리거 인자

        Returns:
            등록된 작업 ID
        """
        if trigger == "interval":
            trigger_obj = IntervalTrigger(**trigger_args)
        elif trigger == "cron":
            trigger_obj = CronTrigger(**trigger_args)
        elif trigger == "date":
            trigger_obj = DateTrigger(**trigger_args)
        else:
            raise ValueError(f"지원하지 않는 트리거: {trigger}")

        self._scheduler.add_job(
            func,
            trigger=trigger_obj,
            id=job_id,
            replace_existing=True,
        )

        logger.info(f"작업 등록: {job_id} ({trigger})")
        return job_id

    def add_cron_job(
        self,
        job_id: str,
        func: Callable,
        hour: int,
        minute: int = 0,
        day_of_week: str = "*",
    ) -> str:
        """
        Cron 표현식으로 작업 등록

        Args:
            job_id: 작업 ID
            func: 실행할 함수
            hour: 실행 시간 (0-23)
            minute: 실행 분 (0-59)
            day_of_week: 요일 ("*" = 매일)

        Returns:
            등록된 작업 ID
        """
        return self.add_job(
            job_id=job_id,
            func=func,
            trigger="cron",
            hour=hour,
            minute=minute,
            day_of_week=day_of_week,
        )

    def add_date_job(
        self,
        job_id: str,
        func: Callable,
        run_date: datetime,
    ) -> str:
        """
        특정 날짜/시간에 한 번 실행되는 작업 등록

        Args:
            job_id: 작업 ID
            func: 실행할 함수
            run_date: 실행 날짜/시간

        Returns:
            등록된 작업 ID
        """
        return self.add_job(
            job_id=job_id,
            func=func,
            trigger="date",
            run_date=run_date,
        )

    def remove_job(self, job_id: str) -> None:
        """
        작업 제거

        Args:
            job_id: 제거할 작업 ID
        """
        try:
            self._scheduler.remove_job(job_id)
            logger.info(f"작업 제거: {job_id}")
        except Exception as e:
            logger.warning(f"작업 제거 실패: {job_id} - {e}")

    def get_job(self, job_id: str) -> Any | None:
        """
        작업 조회

        Args:
            job_id: 조회할 작업 ID

        Returns:
            작업 객체 또는 None
        """
        return self._scheduler.get_job(job_id)

    def list_jobs(self) -> list[dict[str, Any]]:
        """
        등록된 모든 작업 목록 조회

        Returns:
            작업 정보 리스트
        """
        jobs = []
        for job in self._scheduler.get_jobs():
            # APScheduler 버전에 따라 next_run_time이 다르게 접근됨
            next_run = getattr(job, "next_run_time", None)
            jobs.append(
                {
                    "id": job.id,
                    "name": getattr(job, "name", job.id),
                    "next_run_time": str(next_run) if next_run else None,
                    "trigger": str(job.trigger),
                }
            )
        return jobs

    def start(self) -> None:
        """스케줄러 시작"""
        if not self._started:
            self._scheduler.start()
            self._started = True
            logger.info("스케줄러 시작됨")

    def stop(self) -> None:
        """스케줄러 중지"""
        if self._started:
            self._scheduler.shutdown(wait=False)
            self._started = False
            logger.info("스케줄러 중지됨")

    def is_running(self) -> bool:
        """스케줄러 실행 중 여부"""
        return self._started
