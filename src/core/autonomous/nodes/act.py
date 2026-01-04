"""
Act 노드

판단 결과에 따라 행동을 실행합니다.
- 알림 전송 (Slack)
- 알림 이력 기록 (P-011: SQLite DB)
"""

import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any

from src.core.autonomous.memory.notification_repository import NotificationRepository
from src.core.autonomous.state import AgentState

logger = logging.getLogger(__name__)

# 알림 이력 저장소 (싱글톤)
_notification_repository: NotificationRepository | None = None


def _get_notification_repository() -> NotificationRepository:
    """알림 이력 저장소 싱글톤 반환"""
    global _notification_repository
    if _notification_repository is None:
        _notification_repository = NotificationRepository(db_path=":memory:")
    return _notification_repository


def set_notification_repository(repository: NotificationRepository) -> None:
    """알림 이력 저장소 설정 (DI용)"""
    global _notification_repository
    _notification_repository = repository


def act_node(state: AgentState) -> AgentState:
    """
    동기 행동 실행 노드

    decision이 "act"인 경우에만 호출됩니다.

    Args:
        state: 현재 에이전트 상태

    Returns:
        행동 결과가 포함된 상태
    """
    decision = state.get("decision")

    if decision != "act":
        logger.info(f"[Act] decision={decision}, 행동 스킵")
        return {
            **state,
            "action_result": None,
        }

    action = state.get("action")
    if not action:
        logger.warning("[Act] action이 None, 행동 스킵")
        return {
            **state,
            "action_result": {"success": False, "error": "No action specified"},
        }

    logger.info(f"[Act] 행동 실행: {action.get('type', 'unknown')}")

    # 행동 결과 (실제 전송은 async 버전에서)
    result = {
        "success": True,
        "action_type": action.get("type", "unknown"),
        "message": action.get("message", ""),
        "timestamp": datetime.now().isoformat(),
    }

    # 알림 이력 기록
    _record_notification(action, result, user_id="sync_user")

    return {
        **state,
        "action_result": result,
    }


async def act_node_async(
    state: AgentState,
    send_message: Callable[[str, str], Any] | None = None,
    user_id: str = "",
) -> AgentState:
    """
    비동기 행동 실행 노드

    실제 Slack 알림을 전송합니다.

    Args:
        state: 현재 에이전트 상태
        send_message: 메시지 전송 함수 (user_id, message) -> None
        user_id: 알림 받을 사용자 ID

    Returns:
        행동 결과가 포함된 상태
    """
    decision = state.get("decision")

    if decision != "act":
        logger.info(f"[Act] decision={decision}, 행동 스킵")
        return {
            **state,
            "action_result": None,
        }

    action = state.get("action")
    if not action:
        logger.warning("[Act] action이 None, 행동 스킵")
        return {
            **state,
            "action_result": {"success": False, "error": "No action specified"},
        }

    action_type = action.get("type", "unknown")
    message = action.get("message", "")

    logger.info(f"[Act] 행동 실행: {action_type}")

    result: dict[str, Any] = {
        "success": False,
        "action_type": action_type,
        "message": message,
        "timestamp": datetime.now().isoformat(),
    }

    try:
        if action_type == "notify":
            if send_message and user_id:
                # 실제 알림 전송
                await _send_notification(send_message, user_id, message)
                result["success"] = True
                logger.info(f"[Act] 알림 전송 성공: {message[:50]}...")
            else:
                logger.warning("[Act] send_message 또는 user_id 없음")
                result["error"] = "send_message or user_id not provided"

        elif action_type == "schedule":
            # TODO: 예약 알림
            logger.info("[Act] 예약 알림 (미구현)")
            result["error"] = "schedule action not implemented"

        else:
            logger.warning(f"[Act] 알 수 없는 action_type: {action_type}")
            result["error"] = f"Unknown action type: {action_type}"

    except Exception as e:
        logger.error(f"[Act] 행동 실행 실패: {e}")
        result["error"] = str(e)

    # 알림 이력 기록
    _record_notification(action, result, user_id=user_id or "unknown")

    # 알림 카운트 증가
    notification_count = state.get("today_notification_count", 0)
    if result["success"]:
        notification_count += 1

    return {
        **state,
        "action_result": result,
        "today_notification_count": notification_count,
    }


async def _send_notification(
    send_message: Callable[[str, str], Any],
    user_id: str,
    message: str,
) -> None:
    """알림 전송"""
    # 메시지에 이모지 추가
    formatted_message = f"🤖 *패니저 알림*\n\n{message}"

    # 동기/비동기 함수 모두 지원
    result = send_message(user_id, formatted_message)
    if hasattr(result, "__await__"):
        await result


def _record_notification(action: dict, result: dict, user_id: str = "unknown") -> None:
    """알림 이력 기록 (Repository 사용)"""
    repo = _get_notification_repository()

    notification_type = action.get("type", "unknown")
    message = action.get("message", "")

    repo.save(
        user_id=user_id,
        message=message,
        notification_type=notification_type,
    )

    logger.debug(f"[Act] 알림 기록 (DB): {notification_type}")


def get_notification_history() -> list[dict]:
    """알림 이력 조회"""
    repo = _get_notification_repository()
    # 모든 알림 조회 (user_id별로 조회하기 어려우므로 직접 DB 쿼리)
    cursor = repo._conn.execute("SELECT * FROM notification_history ORDER BY sent_at DESC")
    return [repo._row_to_dict(row) for row in cursor.fetchall()]


def get_today_notification_count() -> int:
    """오늘 알림 횟수 조회"""
    repo = _get_notification_repository()
    from datetime import datetime

    today = datetime.now().strftime("%Y-%m-%d")
    cursor = repo._conn.execute(
        "SELECT COUNT(*) FROM notification_history WHERE sent_at LIKE ?",
        (f"{today}%",),
    )
    return cursor.fetchone()[0]


def clear_notification_history() -> None:
    """알림 이력 초기화 (테스트용)"""
    global _notification_repository
    if _notification_repository:
        _notification_repository.close()
    _notification_repository = NotificationRepository(db_path=":memory:")
