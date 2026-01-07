"""Phase 1 RED: Port 인터페이스 존재 여부 테스트"""


def test_calendar_port_exists():
    """CalendarPort 인터페이스가 존재하는지 확인"""
    from src.domain.ports.calendar_port import CalendarPort
    
    assert CalendarPort is not None
    # 필수 메서드 확인
    assert hasattr(CalendarPort, 'get_events')
    assert hasattr(CalendarPort, 'create_event')


def test_messenger_port_exists():
    """MessengerPort 인터페이스가 존재하는지 확인"""
    from src.domain.ports.messenger_port import MessengerPort
    
    assert MessengerPort is not None
    # 필수 메서드 확인
    assert hasattr(MessengerPort, 'send_message')
