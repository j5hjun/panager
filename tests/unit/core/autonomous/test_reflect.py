"""
Reflect 노드 테스트
"""

import json
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from src.core.autonomous.nodes.reflect import (
    _analyze_user_reaction,
    _parse_lesson_response,
    _save_lesson,
    clear_lessons,
    get_lessons,
    get_relevant_lessons,
    reflect_node,
    reflect_node_async,
)
from src.core.autonomous.state import create_initial_state


class TestAnalyzeUserReaction:
    """사용자 반응 분석 테스트"""

    def test_negative_keywords(self):
        """부정적 키워드 감지"""
        assert _analyze_user_reaction("그만해") == "negative"
        assert _analyze_user_reaction("됐어") == "negative"
        assert _analyze_user_reaction("필요없어") == "negative"
        assert _analyze_user_reaction("귀찮아") == "negative"

    def test_positive_keywords(self):
        """긍정적 키워드 감지"""
        assert _analyze_user_reaction("고마워!") == "positive"
        assert _analyze_user_reaction("도움이 됐어") == "positive"
        assert _analyze_user_reaction("감사합니다") == "positive"
        assert _analyze_user_reaction("완벽해") == "positive"

    def test_neutral(self):
        """중립 반응"""
        assert _analyze_user_reaction("알겠어") == "neutral"
        assert _analyze_user_reaction("") == "neutral"
        assert _analyze_user_reaction(None) == "neutral"


class TestParseLessonResponse:
    """교훈 파싱 테스트"""

    def test_parse_valid_lesson(self):
        """정상 교훈 파싱"""
        response = json.dumps(
            {
                "reaction_type": "negative",
                "analysis": "사용자가 불편해함",
                "should_save_lesson": True,
                "lesson": {
                    "context": "아침 7시에 알림",
                    "should_not": "너무 이른 시간에 알림하면 안됨",
                    "should_instead": "8시 이후에 알림",
                    "importance": "high",
                },
            }
        )

        result = _parse_lesson_response(response)

        assert result is not None
        assert result["context"] == "아침 7시에 알림"
        assert result["importance"] == "high"

    def test_parse_no_save_needed(self):
        """저장 불필요 시 None 반환"""
        response = json.dumps(
            {
                "reaction_type": "positive",
                "analysis": "사용자가 만족함",
                "should_save_lesson": False,
                "lesson": None,
            }
        )

        result = _parse_lesson_response(response)

        assert result is None

    def test_parse_json_block(self):
        """JSON 블록 형식 파싱"""
        response = """```json
{
    "reaction_type": "negative",
    "should_save_lesson": true,
    "lesson": {
        "context": "테스트",
        "should_not": "하지마",
        "should_instead": "이렇게 해",
        "importance": "low"
    }
}
```"""

        result = _parse_lesson_response(response)

        assert result is not None
        assert result["context"] == "테스트"

    def test_parse_invalid_json(self):
        """잘못된 JSON"""
        result = _parse_lesson_response("이건 JSON이 아니야")

        assert result is None


class TestLessonStorage:
    """교훈 저장소 테스트"""

    def setup_method(self):
        """테스트 전 교훈 초기화"""
        clear_lessons()

    def test_save_and_get_lesson(self):
        """교훈 저장 및 조회"""
        lesson = {
            "id": "test-001",
            "context": "테스트 상황",
            "should_not": "하지마",
            "should_instead": "이렇게 해",
        }

        _save_lesson(lesson)

        lessons = get_lessons()
        assert len(lessons) == 1
        # Repository 사용 시 ID는 자동 생성됨
        assert "id" in lessons[0]
        assert "하지마" in lessons[0]["content"]

    def test_lesson_limit(self):
        """최대 50개 유지"""
        for i in range(55):
            _save_lesson({"id": f"lesson-{i}", "should_not": f"msg-{i}", "should_instead": ""})

        lessons = get_lessons()
        assert len(lessons) == 50

    def test_get_relevant_lessons(self):
        """관련 교훈 조회"""
        for i in range(10):
            _save_lesson({"id": f"lesson-{i}", "should_not": f"msg-{i}", "should_instead": ""})

        relevant = get_relevant_lessons()
        assert len(relevant) == 5
        # 최신 5개 반환 (최신순)
        assert "msg-9" in relevant[0]["content"]

    def test_clear_lessons(self):
        """교훈 초기화"""
        _save_lesson({"id": "test", "should_not": "test", "should_instead": ""})
        clear_lessons()

        assert len(get_lessons()) == 0


class TestReflectNode:
    """Reflect 노드 테스트"""

    def setup_method(self):
        """테스트 전 교훈 초기화"""
        clear_lessons()

    def test_sync_node_no_action_result(self):
        """action_result 없으면 스킵"""
        state = create_initial_state()
        state["action_result"] = None

        result = reflect_node(state)

        assert result["lesson"] is None

    def test_sync_node_failed_action(self):
        """실패한 행동은 스킵"""
        state = create_initial_state()
        state["action_result"] = {"success": False}

        result = reflect_node(state)

        assert result["lesson"] is None

    def test_sync_node_success_action(self):
        """성공한 행동 반성"""
        state = create_initial_state()
        state["action_result"] = {"success": True}

        result = reflect_node(state)

        # 동기 노드는 기본 반성만 수행
        assert result["lesson"] is None


class TestReflectNodeAsync:
    """Reflect 노드 비동기 테스트"""

    def setup_method(self):
        """테스트 전 교훈 초기화"""
        clear_lessons()

    @pytest.mark.asyncio
    async def test_async_no_action_result(self):
        """action_result 없으면 스킵"""
        state = create_initial_state()
        state["action_result"] = None

        result = await reflect_node_async(state)

        assert result["lesson"] is None
        assert result["user_reaction"] is None

    @pytest.mark.asyncio
    async def test_async_neutral_reaction(self):
        """중립 반응은 교훈 추출 안 함"""
        state = create_initial_state()
        state["action_result"] = {"success": True}

        result = await reflect_node_async(state, user_reaction="알겠어")

        assert result["lesson"] is None
        assert result["user_reaction"] == "neutral"

    @pytest.mark.asyncio
    async def test_async_positive_reaction(self):
        """긍정 반응은 교훈 추출 안 함"""
        state = create_initial_state()
        state["action_result"] = {"success": True}

        result = await reflect_node_async(state, user_reaction="고마워!")

        assert result["lesson"] is None
        assert result["user_reaction"] == "positive"

    @pytest.mark.asyncio
    async def test_async_negative_with_llm(self):
        """부정 반응 + LLM으로 교훈 추출"""
        state = create_initial_state()
        state["action_result"] = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
        }
        state["action"] = {"type": "notify", "message": "우산 챙기세요!"}
        state["time_period"] = "morning"

        mock_llm = AsyncMock()
        mock_llm.chat_async.return_value = json.dumps(
            {
                "reaction_type": "negative",
                "analysis": "너무 이른 알림",
                "should_save_lesson": True,
                "lesson": {
                    "context": "아침 일찍 알림",
                    "should_not": "7시 전에 알림",
                    "should_instead": "8시 이후 알림",
                    "importance": "high",
                },
            }
        )

        result = await reflect_node_async(
            state,
            llm_client=mock_llm,
            user_reaction="그만해",
        )

        assert result["user_reaction"] == "negative"
        assert result["lesson"] is not None
        assert result["lesson"]["context"] == "아침 일찍 알림"

        # 저장 확인
        lessons = get_lessons()
        assert len(lessons) == 1

    @pytest.mark.asyncio
    async def test_async_negative_without_llm(self):
        """부정 반응이지만 LLM 없음"""
        state = create_initial_state()
        state["action_result"] = {"success": True}

        result = await reflect_node_async(
            state,
            llm_client=None,
            user_reaction="그만해",
        )

        assert result["user_reaction"] == "negative"
        assert result["lesson"] is None

    @pytest.mark.asyncio
    async def test_async_llm_error(self):
        """LLM 에러 핸들링"""
        state = create_initial_state()
        state["action_result"] = {"success": True}
        state["action"] = {"type": "notify", "message": "테스트"}

        mock_llm = AsyncMock()
        mock_llm.chat_async.side_effect = Exception("LLM Error")

        result = await reflect_node_async(
            state,
            llm_client=mock_llm,
            user_reaction="그만해",
        )

        assert result["user_reaction"] == "negative"
        assert result["lesson"] is None
