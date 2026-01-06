"""
Observe 노드

현재 상태 정보를 수집합니다:
- 시간 정보
- 날씨 정보
- 일정 정보
- 알림 이력
"""

import logging
from datetime import datetime

from src.core.autonomous.state import AgentState, get_time_period, is_quiet_hours

logger = logging.getLogger(__name__)


def observe_node(state: AgentState) -> AgentState:
    """
    상태 관찰 노드

    현재 시간, 날씨, 일정 등의 정보를 수집하여 상태를 업데이트합니다.

    Args:
        state: 현재 에이전트 상태

    Returns:
        업데이트된 에이전트 상태
    """
    now = datetime.now()
    time_period = get_time_period(now)
    quiet_hours = is_quiet_hours(now)

    logger.info(f"[Observe] 시간: {now.strftime('%H:%M')} ({time_period}), 방해금지: {quiet_hours}")

    # 기본 시간 정보 업데이트
    updated_state: AgentState = {
        **state,
        "current_time": now,
        "time_period": time_period,
        "is_quiet_hours": quiet_hours,
    }

    return updated_state


async def observe_node_async(
    state: AgentState,
    weather_service=None,
    calendar_service=None,
) -> AgentState:
    """
    비동기 상태 관찰 노드

    외부 서비스(날씨, 일정)를 호출하여 상태를 수집합니다.

    Args:
        state: 현재 에이전트 상태
        weather_service: 날씨 서비스 (WeatherService)
        calendar_service: 일정 서비스 (CalendarService)

    Returns:
        업데이트된 에이전트 상태
    """
    now = datetime.now()
    time_period = get_time_period(now)
    quiet_hours = is_quiet_hours(now)

    logger.info(f"[Observe] 시간: {now.strftime('%H:%M')} ({time_period})")

    # 날씨 정보 수집
    weather = None
    needs_umbrella = False

    if weather_service:
        try:
            weather_data = await weather_service.get_current_weather()
            weather = weather_data
            umbrella_result = await weather_service.needs_umbrella()
            needs_umbrella = umbrella_result[0]
            logger.info(
                f"[Observe] 날씨: {weather.get('description', 'N/A')}, 우산: {needs_umbrella}"
            )
        except Exception as e:
            logger.warning(f"[Observe] 날씨 정보 수집 실패: {e}")

    # 일정 정보 수집
    today_schedules: list[dict] = []
    upcoming_schedule: dict | None = None
    minutes_to_next: int | None = None

    if calendar_service:
        try:
            schedules = calendar_service.get_today_schedules()
            today_schedules = [_schedule_to_dict(s) for s in schedules]

            # 다가오는 일정 찾기
            for schedule in schedules:
                if schedule.start_time > now:
                    upcoming_schedule = _schedule_to_dict(schedule)
                    minutes_to_next = int((schedule.start_time - now).total_seconds() / 60)
                    break

            logger.info(
                f"[Observe] 오늘 일정: {len(today_schedules)}개, 다음 일정: {minutes_to_next}분 후"
            )
        except Exception as e:
            logger.warning(f"[Observe] 일정 정보 수집 실패: {e}")

    # 알림 이력 (TODO: 실제 저장소에서 조회)
    # 현재는 state에서 가져오거나 기본값 사용
    notification_count = state.get("today_notification_count", 0)
    recent_notifications = state.get("recent_notifications", [])

    updated_state: AgentState = {
        **state,
        "current_time": now,
        "time_period": time_period,
        "is_quiet_hours": quiet_hours,
        "weather": weather,
        "needs_umbrella": needs_umbrella,
        "today_schedules": today_schedules,
        "upcoming_schedule": upcoming_schedule,
        "minutes_to_next": minutes_to_next,
        "today_notification_count": notification_count,
        "recent_notifications": recent_notifications,
        "relevant_lessons": [],  # TODO: P-011에서 구현
    }

    return updated_state


def _schedule_to_dict(schedule) -> dict:
    """Schedule 객체를 dict로 변환"""
    return {
        "id": schedule.id,
        "title": schedule.title,
        "start_time": schedule.start_time.isoformat(),
        "end_time": schedule.end_time.isoformat() if schedule.end_time else None,
        "location": schedule.location,
        "description": schedule.description,
    }
