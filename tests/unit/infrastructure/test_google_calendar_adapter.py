"""Phase 2 RED: Google Calendar Adapter 테스트"""
import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_google_calendar_adapter_implements_port():
    """GoogleCalendarAdapter가 CalendarPort를 구현하는지 확인"""
    from src.infrastructure.google.calendar_adapter import GoogleCalendarAdapter
    from src.domain.ports.calendar_port import CalendarPort
    
    assert issubclass(GoogleCalendarAdapter, CalendarPort)


@pytest.mark.asyncio
async def test_get_events_returns_list():
    """get_events가 이벤트 리스트를 반환하는지 확인"""
    from src.infrastructure.google.calendar_adapter import GoogleCalendarAdapter
    
    # Mock aiogoogle
    with patch('src.infrastructure.google.calendar_adapter.Aiogoogle') as mock_aiogoogle:
        # Mock 설정
        mock_calendar = AsyncMock()
        mock_calendar.events.list.return_value = {
            'items': [
                {
                    'id': 'event_1',
                    'summary': 'Test Meeting',
                    'start': {'dateTime': '2026-01-08T10:00:00+09:00'},
                    'end': {'dateTime': '2026-01-08T11:00:00+09:00'},
                    'status': 'confirmed'
                }
            ]
        }
        
        mock_instance = AsyncMock()
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None
        mock_instance.discover = AsyncMock(return_value=mock_calendar)
        mock_instance.as_user = AsyncMock(return_value={'items': [
            {
                'id': 'event_1',
                'summary': 'Test Meeting',
                'start': {'dateTime': '2026-01-08T10:00:00+09:00'},
                'end': {'dateTime': '2026-01-08T11:00:00+09:00'},
                'status': 'confirmed'
            }
        ]})
        
        mock_aiogoogle.return_value = mock_instance
        
        adapter = GoogleCalendarAdapter()
        events = await adapter.get_events(user_id="U12345")
        
        assert isinstance(events, list)
        assert len(events) >= 0  # 빈 리스트도 허용
