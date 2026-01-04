"""
AgentState

자율 판단 시스템의 상태를 정의합니다.
LangGraph의 StateGraph에서 사용됩니다.
"""

from datetime import datetime

from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    """
    자율 판단 에이전트의 상태

    Observe → Think → Act → Reflect 루프에서 공유되는 상태입니다.
    """

    # ==================== 시간 정보 ====================
    current_time: datetime
    time_period: str  # morning, afternoon, evening, night
    is_quiet_hours: bool  # 방해 금지 시간 (23:00 ~ 07:00)

    # ==================== 날씨 정보 ====================
    weather: dict | None
    needs_umbrella: bool

    # ==================== 일정 정보 ====================
    today_schedules: list[dict]
    upcoming_schedule: dict | None
    minutes_to_next: int | None

    # ==================== 알림 이력 ====================
    last_notification_time: datetime | None
    today_notification_count: int
    recent_notifications: list[dict]

    # ==================== 학습 정보 ====================
    relevant_lessons: list[dict]

    # ==================== 판단 결과 (Think) ====================
    decision: str | None  # "act" or "wait"
    reasoning: str | None
    confidence: float | None
    action: dict | None

    # ==================== 행동 결과 (Act) ====================
    action_result: dict | None

    # ==================== 반성 결과 (Reflect) ====================
    user_reaction: str | None
    lesson: dict | None


def get_time_period(dt: datetime) -> str:
    """시간대 문자열 반환"""
    hour = dt.hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"


def is_quiet_hours(dt: datetime) -> bool:
    """방해 금지 시간 여부 (23:00 ~ 07:00)"""
    hour = dt.hour
    return hour >= 23 or hour < 7


def create_initial_state() -> AgentState:
    """초기 상태 생성"""
    now = datetime.now()
    return AgentState(
        current_time=now,
        time_period=get_time_period(now),
        is_quiet_hours=is_quiet_hours(now),
        weather=None,
        needs_umbrella=False,
        today_schedules=[],
        upcoming_schedule=None,
        minutes_to_next=None,
        last_notification_time=None,
        today_notification_count=0,
        recent_notifications=[],
        relevant_lessons=[],
        decision=None,
        reasoning=None,
        confidence=None,
        action=None,
        action_result=None,
        user_reaction=None,
        lesson=None,
    )
