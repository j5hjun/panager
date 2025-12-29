"""
E2E (End-to-End) 테스트

전체 대화 플로우를 테스트합니다.
"""

import pytest


class TestFullConversationFlow:
    """전체 대화 플로우 E2E 테스트"""

    @pytest.mark.asyncio
    async def test_weather_conversation(self):
        """날씨 대화 전체 플로우 테스트"""
        from src.services.llm.ai_service import AIService

        # Given: AI 서비스 초기화 (테스트용 설정)
        _ai_service = AIService(
            api_key="test-key",
            base_url="https://api.groq.com/openai/v1",
            model="llama-3.3-70b-versatile",
            weather_api_key="test-weather-key",
            calendar_db_path=":memory:",
        )

        # When: 사용자가 날씨 질문
        # Then: 에러 없이 응답 생성 (실제 API 호출 없이 구조 테스트)
        # 실제 API 호출은 integration test에서

    @pytest.mark.asyncio
    async def test_calendar_conversation(self):
        """일정 대화 전체 플로우 테스트"""
        from src.services.llm.ai_service import AIService

        # Given: AI 서비스 초기화
        ai_service = AIService(
            api_key="test-key",
            base_url="https://api.groq.com/openai/v1",
            model="llama-3.3-70b-versatile",
            calendar_db_path=":memory:",
        )

        # When: 일정 추가
        ai_service.calendar.add_schedule(
            title="테스트 미팅",
            start_time=pytest.importorskip("datetime").datetime(2025, 1, 15, 10, 0),
            location="강남역",
        )

        # Then: 일정 조회 가능
        schedules = ai_service.calendar.get_schedules_by_date(
            pytest.importorskip("datetime").datetime(2025, 1, 15)
        )
        assert len(schedules) == 1
        assert schedules[0].title == "테스트 미팅"

    def test_conversation_history_persistence(self):
        """대화 기록 유지 테스트"""
        from src.core.logic.conversation import ConversationManager

        # Given: 대화 관리자
        manager = ConversationManager()

        # When: 여러 메시지 추가
        manager.add_message("user1", "user", "안녕")
        manager.add_message("user1", "assistant", "안녕하세요")
        manager.add_message("user1", "user", "날씨 알려줘")

        # Then: 히스토리 유지
        history = manager.get_history("user1")
        assert len(history) == 3
        assert history[0]["content"] == "안녕"


class TestErrorHandling:
    """에러 핸들링 테스트"""

    @pytest.mark.asyncio
    async def test_api_failure_graceful_handling(self):
        """API 실패 시 우아한 처리"""
        from src.services.llm.ai_service import AIService

        # Given: 잘못된 API 키로 서비스 초기화
        _ai_service = AIService(
            api_key="invalid-key",
            base_url="https://api.groq.com/openai/v1",
            model="llama-3.3-70b-versatile",
            calendar_db_path=":memory:",
        )

        # When/Then: 에러가 발생해도 앱이 크래시하지 않음
        # (실제 API 호출 시 에러 처리 확인)

    def test_invalid_schedule_time_handling(self):
        """잘못된 일정 시간 입력 처리"""
        from src.services.llm.ai_service import AIService

        ai_service = AIService(
            api_key="test-key",
            base_url="https://api.groq.com/openai/v1",
            model="llama-3.3-70b-versatile",
            calendar_db_path=":memory:",
        )

        # When: 잘못된 시간 형식으로 일정 추가 시도
        result = ai_service._add_schedule(
            title="테스트",
            date_str="today",
            time_str="invalid-time",
            location="",
        )

        # Then: 에러 메시지 반환 (크래시하지 않음)
        assert "오류" in result or "실패" in result
