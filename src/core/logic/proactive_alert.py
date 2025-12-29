"""
능동적 알림 생성기

사용자 컨텍스트를 분석하여 능동적 알림을 생성합니다.
"""

import logging
from datetime import datetime
from typing import Any

from src.core.templates.alert_templates import AlertTemplates

logger = logging.getLogger(__name__)


class ProactiveAlertGenerator:
    """
    능동적 알림 생성기

    날씨, 일정 등 다양한 정보를 종합하여
    사용자에게 능동적으로 보낼 알림을 생성합니다.
    """

    def __init__(
        self,
        weather_service: Any,
        llm_client: Any,
        calendar_service: Any | None = None,
        default_city: str = "Seoul",
    ):
        """
        ProactiveAlertGenerator 초기화

        Args:
            weather_service: 날씨 서비스
            llm_client: LLM 클라이언트
            calendar_service: 일정 서비스 (선택)
            default_city: 기본 도시
        """
        self.weather_service = weather_service
        self.llm_client = llm_client
        self.calendar_service = calendar_service
        self.default_city = default_city

        logger.info(f"ProactiveAlertGenerator 초기화 완료 (city={default_city})")

    async def generate_morning_briefing(self, city: str | None = None) -> str:
        """
        아침 브리핑 생성

        오늘 하루를 시작하는 데 필요한 정보를 종합하여 알려줍니다.

        Args:
            city: 도시명 (None이면 기본 도시)

        Returns:
            아침 브리핑 메시지
        """
        city = city or self.default_city

        try:
            # 날씨 정보 조회
            weather_info = await self.weather_service.get_weather_formatted(city)

            # 일정 정보 조회
            schedule_info = ""
            if self.calendar_service:
                schedules = self.calendar_service.get_today_schedules()
                if schedules:
                    schedule_info = (
                        f"\n\n오늘의 일정:\n{self.calendar_service.format_schedule_list(schedules)}"
                    )
                else:
                    schedule_info = "\n\n오늘은 일정이 없습니다."

            # 템플릿으로 프롬프트 생성
            current_time = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")
            prompt = AlertTemplates.get_morning_briefing(weather_info + schedule_info, current_time)

            briefing = await self.llm_client.chat(
                messages=[{"role": "user", "content": prompt}],
            )

            logger.info(f"아침 브리핑 생성 완료: {city}")
            return briefing

        except Exception as e:
            logger.error(f"아침 브리핑 생성 실패: {e}")
            return self._fallback_morning_briefing(city)

    async def generate_weather_alert(self, city: str | None = None) -> str:
        """
        날씨 알림 생성

        우산이 필요하거나 특별한 날씨일 때 알림을 생성합니다.

        Args:
            city: 도시명

        Returns:
            날씨 알림 메시지
        """
        city = city or self.default_city

        try:
            weather_data = await self.weather_service.get_weather_data(city)

            if weather_data.needs_umbrella():
                # 템플릿으로 프롬프트 생성
                prompt = AlertTemplates.get_weather_alert(
                    city=weather_data.city,
                    description=weather_data.description,
                    temperature=weather_data.temperature,
                )
                alert = await self.llm_client.chat(
                    messages=[{"role": "user", "content": prompt}],
                )
            else:
                alert = f"☀️ {city}는 오늘 {weather_data.description}이에요! 좋은 하루 보내세요 😊"

            logger.info(f"날씨 알림 생성 완료: {city}")
            return alert

        except Exception as e:
            logger.error(f"날씨 알림 생성 실패: {e}")
            return "날씨 정보를 가져오는 중 오류가 발생했어요."

    def format_greeting(self, city: str, description: str, temperature: float) -> str:
        """
        인사말 포맷

        Args:
            city: 도시
            description: 날씨 설명
            temperature: 기온

        Returns:
            포맷된 인사말
        """
        hour = datetime.now().hour

        if 5 <= hour < 12:
            greeting = "좋은 아침이에요! ☀️"
        elif 12 <= hour < 18:
            greeting = "좋은 오후예요! 🌤️"
        else:
            greeting = "좋은 저녁이에요! 🌙"

        return f"{greeting}\n" f"오늘 {city}은 {description}이고, 기온은 {temperature:.1f}°C예요."

    def _fallback_morning_briefing(self, city: str) -> str:
        """LLM 실패 시 기본 브리핑"""
        hour = datetime.now().hour

        if 5 <= hour < 12:
            greeting = "좋은 아침이에요! ☀️"
        elif 12 <= hour < 18:
            greeting = "좋은 오후예요! 🌤️"
        else:
            greeting = "좋은 저녁이에요! 🌙"

        return f"{greeting} 오늘도 좋은 하루 되세요, {city}에서! 😊"
