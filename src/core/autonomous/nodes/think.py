"""
Think 노드

LLM을 사용하여 행동 여부를 판단합니다.
"""

import json
import logging
from typing import Any

from src.core.autonomous.prompts.think import THINK_PROMPT
from src.core.autonomous.state import AgentState

logger = logging.getLogger(__name__)


def think_node(state: AgentState) -> AgentState:
    """
    동기 판단 노드 (스켈레톤)

    실제 LLM 호출이 필요하므로 비동기 버전(think_node_async)을 사용하세요.
    이 함수는 기본값을 반환합니다.
    """
    logger.info("[Think] 동기 노드 - 기본값 반환 (wait)")

    return {
        **state,
        "decision": "wait",
        "reasoning": "동기 노드는 LLM 호출 불가",
        "confidence": 0.0,
        "action": None,
    }


async def think_node_async(
    state: AgentState,
    llm_client=None,
) -> AgentState:
    """
    비동기 판단 노드

    현재 상태를 분석하여 행동(act) 또는 대기(wait)를 결정합니다.

    Args:
        state: 현재 에이전트 상태
        llm_client: LLM 클라이언트 (LLMClient)

    Returns:
        판단 결과가 포함된 상태
    """
    # 비즈니스 규칙 우선 적용
    pre_check = _apply_business_rules(state)
    if pre_check["decision"] == "wait":
        logger.info(f"[Think] 비즈니스 규칙 적용: {pre_check['reasoning']}")
        return {**state, **pre_check}

    # LLM 호출
    if llm_client is None:
        logger.warning("[Think] LLM 클라이언트 없음 - wait 반환")
        return {
            **state,
            "decision": "wait",
            "reasoning": "LLM 클라이언트가 설정되지 않음",
            "confidence": 0.0,
            "action": None,
        }

    try:
        # 프롬프트 구성
        prompt = _build_prompt(state)

        # LLM 호출
        messages = [{"role": "user", "content": prompt}]
        response = await llm_client.chat(messages, temperature=0.3, max_tokens=512)

        # JSON 파싱
        result = _parse_llm_response(response)

        # 신뢰도 검증
        if result["confidence"] < 0.7:
            logger.info(f"[Think] 신뢰도 부족: {result['confidence']:.2f} < 0.7")
            result["decision"] = "wait"
            result["reasoning"] += " (신뢰도 부족으로 wait 결정)"

        logger.info(f"[Think] 판단 결과: {result['decision']} (신뢰도: {result['confidence']:.2f})")

        return {
            **state,
            "decision": result["decision"],
            "reasoning": result["reasoning"],
            "confidence": result["confidence"],
            "action": result.get("action"),
        }

    except Exception as e:
        logger.error(f"[Think] LLM 호출 실패: {e}")
        return {
            **state,
            "decision": "wait",
            "reasoning": f"LLM 호출 실패: {e}",
            "confidence": 0.0,
            "action": None,
        }


def _apply_business_rules(state: AgentState) -> dict[str, Any]:
    """
    비즈니스 규칙 적용

    LLM 호출 전에 규칙 기반으로 먼저 필터링합니다.

    Returns:
        {"decision": "act"|"wait", "reasoning": str, "confidence": float}
    """
    # 규칙 1: 방해 금지 시간 (23:00 ~ 07:00)
    if state.get("is_quiet_hours", False):
        # TODO: 긴급 상황 예외 처리
        return {
            "decision": "wait",
            "reasoning": "방해 금지 시간 (23:00~07:00)",
            "confidence": 1.0,
            "action": None,
        }

    # 규칙 2: 일일 알림 7회 초과
    notification_count = state.get("today_notification_count", 0)
    if notification_count >= 7:
        return {
            "decision": "wait",
            "reasoning": f"일일 알림 한도 초과 ({notification_count}/7)",
            "confidence": 1.0,
            "action": None,
        }

    # 규칙 통과 - LLM 판단 필요
    return {
        "decision": "pending",  # LLM 판단 필요
        "reasoning": "비즈니스 규칙 통과, LLM 판단 필요",
        "confidence": 0.0,
        "action": None,
    }


def _build_prompt(state: AgentState) -> str:
    """상태 정보로 프롬프트 구성"""
    # 날씨 정보
    weather = state.get("weather", {})
    weather_desc = weather.get("description", "정보 없음") if weather else "정보 없음"

    # 일정 정보
    schedules = state.get("today_schedules", [])
    schedule_text = "없음"
    if schedules:
        schedule_items = []
        for s in schedules:
            time_str = s.get("start_time", "")[:16] if s.get("start_time") else ""
            schedule_items.append(f"- {time_str}: {s.get('title', '')}")
        schedule_text = "\n".join(schedule_items)

    # 다가오는 일정
    upcoming = state.get("upcoming_schedule")
    upcoming_text = "없음"
    if upcoming:
        minutes = state.get("minutes_to_next", 0)
        upcoming_text = f"{upcoming.get('title', '')} ({minutes}분 후)"

    # 교훈 (TODO: P-011에서 구현)
    lessons = state.get("relevant_lessons", [])
    lessons_text = "없음"
    if lessons:
        lessons_text = "\n".join([f"- {lesson.get('lesson', '')}" for lesson in lessons])

    # 알림 횟수
    notification_count = state.get("today_notification_count", 0)

    return THINK_PROMPT.format(
        current_time=(
            state.get("current_time", "").isoformat()[:16] if state.get("current_time") else ""
        ),
        time_period=state.get("time_period", ""),
        is_quiet_hours=state.get("is_quiet_hours", False),
        weather_description=weather_desc,
        needs_umbrella=state.get("needs_umbrella", False),
        schedules=schedule_text,
        upcoming=upcoming_text,
        notification_count=notification_count,
        lessons=lessons_text,
    )


def _parse_llm_response(response: str) -> dict[str, Any]:
    """LLM 응답을 JSON으로 파싱"""
    try:
        # JSON 블록 추출 (```json ... ``` 형식 처리)
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            json_str = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            json_str = response[start:end].strip()
        else:
            # 전체를 JSON으로 파싱 시도
            json_str = response.strip()

        result = json.loads(json_str)

        # 필수 필드 검증
        return {
            "reasoning": result.get("reasoning", ""),
            "decision": result.get("decision", "wait"),
            "confidence": float(result.get("confidence", 0.0)),
            "action": result.get("action"),
        }

    except (json.JSONDecodeError, ValueError, KeyError) as e:
        logger.warning(f"[Think] JSON 파싱 실패: {e}, 응답: {response[:200]}")
        return {
            "reasoning": f"JSON 파싱 실패: {response[:100]}...",
            "decision": "wait",
            "confidence": 0.0,
            "action": None,
        }
