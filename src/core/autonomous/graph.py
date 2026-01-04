"""
자율 판단 그래프 (Autonomous Agent Graph)

LangGraph 기반의 Observe-Think-Act-Reflect 루프를 정의합니다.
"""

import logging
from collections.abc import Callable
from typing import Any

from langgraph.graph import END, StateGraph

from src.core.autonomous.state import AgentState, create_initial_state

logger = logging.getLogger(__name__)


def create_autonomous_agent() -> StateGraph:
    """
    자율 판단 에이전트 그래프 생성 (동기)

    Returns:
        컴파일된 StateGraph

    흐름:
        observe → think → (act → reflect) or (wait) → END
    """
    from src.core.autonomous.nodes.act import act_node
    from src.core.autonomous.nodes.observe import observe_node
    from src.core.autonomous.nodes.reflect import reflect_node
    from src.core.autonomous.nodes.think import think_node

    # 그래프 생성
    graph = StateGraph(AgentState)

    # 노드 추가
    graph.add_node("observe", observe_node)
    graph.add_node("think", think_node)
    graph.add_node("act", act_node)
    graph.add_node("reflect", reflect_node)

    # 엣지 연결
    graph.add_edge("observe", "think")

    # 조건부 엣지: decision에 따라 분기
    graph.add_conditional_edges(
        "think",
        _route_decision,
        {"act": "act", "wait": END},
    )

    graph.add_edge("act", "reflect")
    graph.add_edge("reflect", END)

    # 시작점 설정
    graph.set_entry_point("observe")

    return graph.compile()


def _route_decision(state: AgentState) -> str:
    """decision에 따라 라우팅"""
    decision = state.get("decision", "wait")
    if decision == "act":
        return "act"
    return "wait"


class AutonomousRunner:
    """
    자율 판단 에이전트 러너

    비동기 노드들을 사용하여 자율 판단 루프를 실행합니다.
    """

    def __init__(
        self,
        llm_client=None,
        weather_service=None,
        calendar_service=None,
        send_message: Callable[[str, str], Any] | None = None,
        user_id: str = "",
    ):
        """
        Args:
            llm_client: LLM 클라이언트
            weather_service: 캐시된 날씨 서비스
            calendar_service: 일정 서비스
            send_message: 메시지 전송 함수
            user_id: 알림 받을 사용자 ID
        """
        self.llm_client = llm_client
        self.weather_service = weather_service
        self.calendar_service = calendar_service
        self.send_message = send_message
        self.user_id = user_id

        self._is_running = False
        logger.info("[AutonomousRunner] 초기화 완료")

    async def run_once(self) -> dict[str, Any]:
        """
        자율 판단 루프 1회 실행

        Returns:
            최종 상태
        """
        from src.core.autonomous.nodes.act import act_node_async
        from src.core.autonomous.nodes.observe import observe_node_async
        from src.core.autonomous.nodes.reflect import reflect_node_async
        from src.core.autonomous.nodes.think import think_node_async

        logger.info("[AutonomousRunner] 루프 시작")

        # 1. 초기 상태 생성
        state = create_initial_state()

        # 2. Observe: 상태 관찰
        state = await observe_node_async(
            state,
            weather_service=self.weather_service,
            calendar_service=self.calendar_service,
        )
        logger.info(f"[Observe] 완료 - 시간대: {state.get('time_period')}")

        # 3. Think: 판단
        state = await think_node_async(state, llm_client=self.llm_client)
        decision = state.get("decision", "wait")
        logger.info(f"[Think] 완료 - 결정: {decision}")

        # 4. Act: 행동 (decision이 "act"인 경우만)
        if decision == "act":
            state = await act_node_async(
                state,
                send_message=self.send_message,
                user_id=self.user_id,
            )
            logger.info(f"[Act] 완료 - 성공: {state.get('action_result', {}).get('success')}")

            # 5. Reflect: 반성 (행동 후)
            # TODO: 사용자 반응 대기 로직 (P-011에서 구현)
            state = await reflect_node_async(state, llm_client=self.llm_client)
            logger.info(f"[Reflect] 완료 - 교훈: {state.get('lesson') is not None}")
        else:
            logger.info("[AutonomousRunner] 행동 없음 (wait)")

        logger.info("[AutonomousRunner] 루프 종료")
        return dict(state)

    def start(self) -> None:
        """러너 시작 표시"""
        self._is_running = True
        logger.info("[AutonomousRunner] 시작됨")

    def stop(self) -> None:
        """러너 중지 표시"""
        self._is_running = False
        logger.info("[AutonomousRunner] 중지됨")

    @property
    def is_running(self) -> bool:
        """러너 실행 상태"""
        return self._is_running
