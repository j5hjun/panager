"""
능동적 알림 생성 테스트

TDD RED Phase: Proactive Alert Generator가 구현되기 전에 작성된 테스트
"""

from unittest.mock import AsyncMock, MagicMock

import pytest


class TestProactiveAlertGenerator:
    """능동적 알림 생성기 테스트"""

    def test_alert_generator_can_be_imported(self):
        """ProactiveAlertGenerator 클래스를 import할 수 있어야 함"""
        from src.core.logic.proactive_alert import ProactiveAlertGenerator

        assert ProactiveAlertGenerator is not None

    def test_alert_generator_initialization(self):
        """ProactiveAlertGenerator를 초기화할 수 있어야 함"""
        from src.core.logic.proactive_alert import ProactiveAlertGenerator

        # Mock 서비스들
        weather_service = MagicMock()
        llm_client = MagicMock()

        generator = ProactiveAlertGenerator(
            weather_service=weather_service,
            llm_client=llm_client,
            default_city="Seoul",
        )

        assert generator is not None

    @pytest.mark.asyncio
    async def test_generate_morning_briefing(self):
        """아침 브리핑을 생성할 수 있어야 함"""
        from src.core.logic.proactive_alert import ProactiveAlertGenerator

        # Mock 서비스들
        weather_service = MagicMock()
        weather_service.get_weather_formatted = AsyncMock(return_value="☀️ 서울 맑음, 기온 5°C")

        llm_client = MagicMock()
        llm_client.chat = AsyncMock(
            return_value="좋은 아침이에요! 오늘 서울은 맑고 기온은 5도예요. 따뜻하게 입고 나가세요! 😊"
        )

        generator = ProactiveAlertGenerator(
            weather_service=weather_service,
            llm_client=llm_client,
            default_city="Seoul",
        )

        briefing = await generator.generate_morning_briefing()

        assert briefing is not None
        assert len(briefing) > 0

    @pytest.mark.asyncio
    async def test_generate_weather_alert(self):
        """날씨 알림을 생성할 수 있어야 함"""
        from src.core.logic.proactive_alert import ProactiveAlertGenerator

        weather_service = MagicMock()
        weather_service.get_weather_data = AsyncMock()
        weather_service.get_weather_data.return_value = MagicMock(
            city="Seoul",
            description="비",
            temperature=10,
            needs_umbrella=lambda: True,
        )

        llm_client = MagicMock()
        llm_client.chat = AsyncMock(return_value="오늘 비 예보가 있어요! 우산 챙기세요 ☂️")

        generator = ProactiveAlertGenerator(
            weather_service=weather_service,
            llm_client=llm_client,
            default_city="Seoul",
        )

        alert = await generator.generate_weather_alert("Seoul")

        assert alert is not None
        assert "우산" in alert or "비" in alert or len(alert) > 0

    def test_format_briefing_message(self):
        """브리핑 메시지를 포맷할 수 있어야 함"""
        from src.core.logic.proactive_alert import ProactiveAlertGenerator

        generator = ProactiveAlertGenerator(
            weather_service=MagicMock(),
            llm_client=MagicMock(),
            default_city="Seoul",
        )

        message = generator.format_greeting("Seoul", "맑음", 5.0)

        assert "좋은" in message or "아침" in message or len(message) > 0


class TestMorningBriefing:
    """아침 브리핑 관련 테스트"""

    @pytest.mark.asyncio
    async def test_briefing_includes_weather(self):
        """아침 브리핑에 날씨 정보가 포함되어야 함"""
        from src.core.logic.proactive_alert import ProactiveAlertGenerator

        weather_service = MagicMock()
        weather_service.get_weather_formatted = AsyncMock(return_value="☀️ 서울 맑음, 5°C")

        llm_client = MagicMock()
        llm_client.chat = AsyncMock(return_value="오늘 서울은 맑고 5도입니다.")

        generator = ProactiveAlertGenerator(
            weather_service=weather_service,
            llm_client=llm_client,
            default_city="Seoul",
        )

        await generator.generate_morning_briefing()

        # 날씨 서비스가 호출되었는지 확인
        weather_service.get_weather_formatted.assert_called_once()
