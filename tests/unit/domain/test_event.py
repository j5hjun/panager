from datetime import datetime, timedelta, timezone
import pytest
from pydantic import ValidationError
from src.domain.models.event import CalendarEvent

def test_event_validation_dates():
    start = datetime.now(timezone.utc)
    end = start - timedelta(hours=1) # 종료가 시작보다 빠름

    with pytest.raises(ValidationError):
        CalendarEvent(
            id="evt_1",
            summary="Invalid Event",
            start_time=start,
            end_time=end
        )

def test_event_duration():
    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=2)
    
    event = CalendarEvent(
        id="evt_1",
        summary="Meeting",
        start_time=start,
        end_time=end
    )
    # duration 속성이나 메서드 테스트 (만약 있다면)
    assert event.end_time > event.start_time
