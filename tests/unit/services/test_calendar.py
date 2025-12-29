"""
일정 서비스 테스트 (Calendar Service)

TDD RED Phase - 일정 서비스 테스트
"""

from datetime import datetime, timedelta


class TestCalendarEntity:
    """일정 엔티티 테스트"""

    def test_schedule_data_can_be_imported(self):
        """Schedule 엔티티를 import 할 수 있어야 한다"""
        from src.core.entities.calendar import Schedule

        assert Schedule is not None

    def test_schedule_creation(self):
        """Schedule 객체를 생성할 수 있어야 한다"""
        from src.core.entities.calendar import Schedule

        schedule = Schedule(
            id="1",
            title="미팅",
            start_time=datetime(2025, 12, 30, 10, 0),
            end_time=datetime(2025, 12, 30, 11, 0),
            location="강남역",
            description="프로젝트 미팅",
        )

        assert schedule.title == "미팅"
        assert schedule.location == "강남역"
        assert schedule.start_time.hour == 10

    def test_schedule_to_message(self):
        """Schedule을 사용자 친화적 메시지로 변환할 수 있어야 한다"""
        from src.core.entities.calendar import Schedule

        schedule = Schedule(
            id="1",
            title="미팅",
            start_time=datetime(2025, 12, 30, 10, 0),
            location="강남역",
        )

        message = schedule.to_message()
        assert "미팅" in message
        assert "10:00" in message
        assert "강남역" in message


class TestCalendarService:
    """일정 서비스 테스트"""

    def test_calendar_service_can_be_imported(self):
        """CalendarService를 import 할 수 있어야 한다"""
        from src.services.calendar.sqlite_calendar import CalendarService

        assert CalendarService is not None

    def test_calendar_service_initialization(self):
        """CalendarService를 초기화할 수 있어야 한다"""
        from src.services.calendar.sqlite_calendar import CalendarService

        service = CalendarService(":memory:")  # 메모리 DB 사용
        assert service is not None

    def test_add_schedule(self):
        """일정을 추가할 수 있어야 한다"""
        from src.services.calendar.sqlite_calendar import CalendarService

        service = CalendarService(":memory:")

        schedule_id = service.add_schedule(
            title="미팅",
            start_time=datetime(2025, 12, 30, 10, 0),
            location="강남역",
        )

        assert schedule_id is not None

    def test_get_schedule(self):
        """일정을 조회할 수 있어야 한다"""
        from src.services.calendar.sqlite_calendar import CalendarService

        service = CalendarService(":memory:")

        schedule_id = service.add_schedule(
            title="미팅",
            start_time=datetime(2025, 12, 30, 10, 0),
            location="강남역",
        )

        schedule = service.get_schedule(schedule_id)
        assert schedule is not None
        assert schedule.title == "미팅"

    def test_get_schedules_by_date(self):
        """특정 날짜의 일정을 조회할 수 있어야 한다"""
        from src.services.calendar.sqlite_calendar import CalendarService

        service = CalendarService(":memory:")

        # 12월 30일 일정 추가
        service.add_schedule(
            title="오전 미팅",
            start_time=datetime(2025, 12, 30, 10, 0),
        )
        service.add_schedule(
            title="오후 미팅",
            start_time=datetime(2025, 12, 30, 14, 0),
        )
        # 12월 31일 일정 추가
        service.add_schedule(
            title="연말 모임",
            start_time=datetime(2025, 12, 31, 19, 0),
        )

        # 12월 30일 일정 조회
        schedules = service.get_schedules_by_date(datetime(2025, 12, 30))
        assert len(schedules) == 2
        assert any(s.title == "오전 미팅" for s in schedules)
        assert any(s.title == "오후 미팅" for s in schedules)

    def test_delete_schedule(self):
        """일정을 삭제할 수 있어야 한다"""
        from src.services.calendar.sqlite_calendar import CalendarService

        service = CalendarService(":memory:")

        schedule_id = service.add_schedule(
            title="삭제할 일정",
            start_time=datetime(2025, 12, 30, 10, 0),
        )

        result = service.delete_schedule(schedule_id)
        assert result is True

        schedule = service.get_schedule(schedule_id)
        assert schedule is None

    def test_get_today_schedules(self):
        """오늘의 일정을 조회할 수 있어야 한다"""
        from src.services.calendar.sqlite_calendar import CalendarService

        service = CalendarService(":memory:")

        today = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)

        service.add_schedule(
            title="오늘 일정",
            start_time=today,
        )

        schedules = service.get_today_schedules()
        assert len(schedules) >= 1

    def test_get_tomorrow_schedules(self):
        """내일의 일정을 조회할 수 있어야 한다"""
        from src.services.calendar.sqlite_calendar import CalendarService

        service = CalendarService(":memory:")

        tomorrow = (datetime.now() + timedelta(days=1)).replace(
            hour=10, minute=0, second=0, microsecond=0
        )

        service.add_schedule(
            title="내일 일정",
            start_time=tomorrow,
        )

        schedules = service.get_tomorrow_schedules()
        assert len(schedules) >= 1

    def test_format_schedule_list(self):
        """일정 목록을 포맷팅할 수 있어야 한다"""
        from src.services.calendar.sqlite_calendar import CalendarService

        service = CalendarService(":memory:")

        service.add_schedule(
            title="미팅",
            start_time=datetime(2025, 12, 30, 10, 0),
            location="강남역",
        )

        schedules = service.get_schedules_by_date(datetime(2025, 12, 30))
        formatted = service.format_schedule_list(schedules)

        assert "미팅" in formatted
        assert "10:00" in formatted
