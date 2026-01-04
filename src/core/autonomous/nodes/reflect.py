"""
Reflect 노드

행동 결과를 분석하고 교훈을 추출합니다.
- 사용자 반응 분석
- LLM을 통한 교훈 추출
- 교훈 저장 (P-011: SQLite DB)
"""

import json
import logging
from datetime import datetime

from src.core.autonomous.memory.lesson_repository import LessonRepository
from src.core.autonomous.prompts.reflect import REFLECT_PROMPT
from src.core.autonomous.state import AgentState

logger = logging.getLogger(__name__)

# 교훈 저장소 (싱글톤)
_lesson_repository: LessonRepository | None = None


def _get_lesson_repository() -> LessonRepository:
    """교훈 저장소 싱글톤 반환"""
    global _lesson_repository
    if _lesson_repository is None:
        _lesson_repository = LessonRepository(db_path=":memory:")
    return _lesson_repository


def set_lesson_repository(repository: LessonRepository) -> None:
    """교훈 저장소 설정 (DI용)"""
    global _lesson_repository
    _lesson_repository = repository


def reflect_node(state: AgentState) -> AgentState:
    """
    동기 반성 노드

    행동 결과를 분석합니다. LLM 호출이 필요하므로, 비동기 버전을 권장합니다.

    Args:
        state: 현재 에이전트 상태

    Returns:
        교훈이 포함된 상태
    """
    action_result = state.get("action_result")

    if action_result is None:
        logger.info("[Reflect] 행동 없음, 반성 스킵")
        return {**state, "lesson": None}

    if not action_result.get("success"):
        logger.info("[Reflect] 행동 실패, 반성 스킵")
        return {**state, "lesson": None}

    logger.info("[Reflect] 동기 노드 - 기본 반성 수행")

    # 기본 반성: 성공적으로 전송됨
    lesson = None

    return {**state, "lesson": lesson}


async def reflect_node_async(
    state: AgentState,
    llm_client=None,
    user_reaction: str | None = None,
) -> AgentState:
    """
    비동기 반성 노드

    행동 결과와 사용자 반응을 분석하여 교훈을 추출합니다.

    Args:
        state: 현재 에이전트 상태
        llm_client: LLM 클라이언트
        user_reaction: 사용자 반응 (수동 입력 또는 자동 감지)

    Returns:
        교훈이 포함된 상태
    """
    action_result = state.get("action_result")

    if action_result is None:
        logger.info("[Reflect] 행동 없음, 반성 스킵")
        return {**state, "lesson": None, "user_reaction": None}

    if not action_result.get("success"):
        logger.info("[Reflect] 행동 실패, 반성 스킵")
        return {**state, "lesson": None, "user_reaction": None}

    # 사용자 반응 분석
    reaction_type = _analyze_user_reaction(user_reaction)
    logger.info(f"[Reflect] 사용자 반응: {reaction_type}")

    lesson = None

    # 부정적 반응인 경우 LLM으로 교훈 추출
    if reaction_type == "negative":
        if llm_client:
            try:
                lesson = await _extract_lesson(state, user_reaction, llm_client)
                if lesson:
                    _save_lesson(lesson)
                    logger.info(f"[Reflect] 교훈 저장: {lesson.get('lesson', '')[:50]}...")
            except Exception as e:
                logger.error(f"[Reflect] 교훈 추출 실패: {e}")
        else:
            logger.warning("[Reflect] LLM 클라이언트 없음, 교훈 추출 생략")

    return {
        **state,
        "lesson": lesson,
        "user_reaction": reaction_type,
    }


def _analyze_user_reaction(reaction: str | None) -> str:
    """
    사용자 반응 분석

    Returns:
        "positive", "negative", "neutral" 중 하나
    """
    if not reaction:
        return "neutral"

    reaction_lower = reaction.lower()

    # 긍정적 키워드 (먼저 체크 - "도움이 됐어" 같은 표현을 위해)
    positive_keywords = [
        "고마워",
        "감사",
        "좋아",
        "도움",
        "잘",
        "완벽",
        "thanks",
        "thank you",
        "great",
        "helpful",
    ]

    # 부정적 키워드
    negative_keywords = [
        "그만",
        "됐어",
        "필요없",
        "귀찮",
        "시끄러",
        "알았어",
        "네네",
        "stop",
        "quiet",
        "enough",
    ]

    # 긍정 먼저 체크
    for keyword in positive_keywords:
        if keyword in reaction_lower:
            return "positive"

    for keyword in negative_keywords:
        if keyword in reaction_lower:
            return "negative"

    return "neutral"


async def _extract_lesson(
    state: AgentState,
    user_reaction: str | None,
    llm_client,
) -> dict | None:
    """LLM을 사용하여 교훈 추출"""
    action_result = state.get("action_result", {})
    action = state.get("action", {})

    # 프롬프트 구성
    prompt = REFLECT_PROMPT.format(
        action_type=action.get("type", "unknown"),
        message=action.get("message", ""),
        sent_at=action_result.get("timestamp", "unknown"),
        time_period=state.get("time_period", "unknown"),
        weather=state.get("weather_context", {}).get("description", "unknown"),
        schedule=str(state.get("schedule_context", [])),
        user_reaction=user_reaction or "응답 없음",
    )

    # LLM 호출
    response = await llm_client.chat_async(prompt)

    # 응답 파싱
    return _parse_lesson_response(response)


def _parse_lesson_response(response: str) -> dict | None:
    """LLM 응답에서 교훈 추출"""
    try:
        # JSON 부분 추출
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            json_str = response[start:end].strip()
        elif "{" in response:
            start = response.find("{")
            end = response.rfind("}") + 1
            json_str = response[start:end].strip()
        else:
            json_str = response.strip()

        result = json.loads(json_str)

        # 교훈 저장 여부 확인
        if not result.get("should_save_lesson", False):
            return None

        lesson = result.get("lesson", {})
        if not lesson:
            return None

        return {
            "id": f"lesson_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "context": lesson.get("context", ""),
            "should_not": lesson.get("should_not", ""),
            "should_instead": lesson.get("should_instead", ""),
            "importance": lesson.get("importance", "medium"),
            "reaction_type": result.get("reaction_type", "negative"),
            "analysis": result.get("analysis", ""),
        }

    except (json.JSONDecodeError, ValueError, KeyError) as e:
        logger.warning(f"[Reflect] 교훈 파싱 실패: {e}")
        return None


def _save_lesson(lesson: dict) -> None:
    """교훈 저장 (Repository 사용)"""
    repo = _get_lesson_repository()

    # 교훈 내용 구성
    content = f"{lesson.get('should_not', '')} -> {lesson.get('should_instead', '')}"
    context = {
        "context": lesson.get("context", ""),
        "importance": lesson.get("importance", "medium"),
        "analysis": lesson.get("analysis", ""),
    }
    user_reaction = lesson.get("reaction_type", "negative")

    repo.save(content=content, context=context, user_reaction=user_reaction)
    logger.info("[Reflect] 교훈 저장 완료 (DB)")


def get_lessons() -> list[dict]:
    """저장된 교훈 조회"""
    repo = _get_lesson_repository()
    return repo.get_all()


def get_relevant_lessons(context: str | None = None) -> list[dict]:
    """관련 교훈 조회 (TODO: 의미 기반 검색)"""
    repo = _get_lesson_repository()

    if not context:
        return repo.get_recent(limit=5)

    # 현재는 최근 5개 반환 (향후 벡터 검색 구현)
    return repo.get_recent(limit=5)


def clear_lessons() -> None:
    """교훈 초기화 (테스트용)"""
    global _lesson_repository
    if _lesson_repository:
        _lesson_repository.close()
    _lesson_repository = LessonRepository(db_path=":memory:")
