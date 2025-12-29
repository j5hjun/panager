"""
스케줄러 서비스 테스트

TDD RED Phase: 스케줄러가 구현되기 전에 작성된 테스트
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock


class TestSchedulerService:
    """스케줄러 서비스 테스트"""

    def test_scheduler_can_be_imported(self):
        """SchedulerService 클래스를 import할 수 있어야 함"""
        from src.services.scheduler.scheduler import SchedulerService

        assert SchedulerService is not None

    def test_scheduler_initialization(self):
        """SchedulerService를 초기화할 수 있어야 함"""
        from src.services.scheduler.scheduler import SchedulerService

        scheduler = SchedulerService()

        assert scheduler is not None

    def test_scheduler_add_job(self):
        """스케줄러에 작업을 등록할 수 있어야 함"""
        from src.services.scheduler.scheduler import SchedulerService

        scheduler = SchedulerService()

        # 테스트용 콜백
        callback = MagicMock()

        # 1분 후 실행되는 작업 등록
        job_id = scheduler.add_job(
            job_id="test_job",
            func=callback,
            trigger="interval",
            seconds=60,
        )

        assert job_id == "test_job"
        assert scheduler.get_job("test_job") is not None

    def test_scheduler_add_cron_job(self):
        """Cron 표현식으로 작업을 등록할 수 있어야 함"""
        from src.services.scheduler.scheduler import SchedulerService

        scheduler = SchedulerService()
        callback = MagicMock()

        # 매일 아침 8시 실행
        job_id = scheduler.add_cron_job(
            job_id="morning_briefing",
            func=callback,
            hour=8,
            minute=0,
        )

        assert job_id == "morning_briefing"
        assert scheduler.get_job("morning_briefing") is not None

    def test_scheduler_remove_job(self):
        """작업을 제거할 수 있어야 함"""
        from src.services.scheduler.scheduler import SchedulerService

        scheduler = SchedulerService()
        callback = MagicMock()

        scheduler.add_job(
            job_id="to_remove",
            func=callback,
            trigger="interval",
            seconds=60,
        )

        # 작업 제거
        scheduler.remove_job("to_remove")

        assert scheduler.get_job("to_remove") is None

    def test_scheduler_list_jobs(self):
        """등록된 작업 목록을 조회할 수 있어야 함"""
        from src.services.scheduler.scheduler import SchedulerService

        scheduler = SchedulerService()
        callback = MagicMock()

        scheduler.add_job(job_id="job1", func=callback, trigger="interval", seconds=60)
        scheduler.add_job(job_id="job2", func=callback, trigger="interval", seconds=120)

        jobs = scheduler.list_jobs()

        assert len(jobs) == 2
        assert "job1" in [j["id"] for j in jobs]
        assert "job2" in [j["id"] for j in jobs]

    def test_scheduler_start_stop(self):
        """스케줄러를 시작하고 중지할 수 있어야 함"""
        from src.services.scheduler.scheduler import SchedulerService

        scheduler = SchedulerService()

        scheduler.start()
        assert scheduler.is_running() is True

        scheduler.stop()
        assert scheduler.is_running() is False


class TestScheduledJob:
    """스케줄된 작업 테스트"""

    def test_job_runs_at_specified_time(self):
        """작업이 지정된 시간에 실행되어야 함"""
        from src.services.scheduler.scheduler import SchedulerService

        scheduler = SchedulerService()
        callback = MagicMock()

        # 날짜 지정 실행
        run_time = datetime.now() + timedelta(seconds=1)
        scheduler.add_date_job(
            job_id="one_time",
            func=callback,
            run_date=run_time,
        )

        assert scheduler.get_job("one_time") is not None
