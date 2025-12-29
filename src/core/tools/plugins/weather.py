"""
날씨 도구 플러그인

OpenWeatherMap API를 사용하여 날씨 정보를 제공합니다.
"""

import logging
from typing import Any

from src.core.tools.base import BaseTool
from src.services.weather.openweathermap import WeatherService

logger = logging.getLogger(__name__)


class WeatherTool(BaseTool):
    """
    날씨 도구

    현재 날씨 조회, 우산 필요 여부 확인 기능을 제공합니다.
    """

    def __init__(self, weather_service: WeatherService):
        """
        WeatherTool 초기화

        Args:
            weather_service: WeatherService 인스턴스
        """
        self._service = weather_service
        logger.info("WeatherTool 초기화 완료")

    @property
    def name(self) -> str:
        return "weather"

    @property
    def description(self) -> str:
        return "날씨 정보 조회 도구 (현재 날씨, 우산 필요 여부)"

    async def execute(self, function_name: str, **kwargs: Any) -> Any:
        """
        날씨 도구 실행

        Args:
            function_name: 실행할 함수 이름 ('get_current_weather' 또는 'check_umbrella')
            **kwargs: 함수 파라미터

        Returns:
            함수 실행 결과
        """
        if function_name == "get_current_weather":
            return await self._get_current_weather(**kwargs)
        elif function_name == "check_umbrella":
            return await self._check_umbrella(**kwargs)
        else:
            raise ValueError(f"알 수 없는 함수: {function_name}")

    async def _get_current_weather(self, city: str | None = None) -> dict[str, Any]:
        """현재 날씨 조회"""
        try:
            weather_data = await self._service.get_weather_data(city)
            return {
                "success": True,
                "message": weather_data.to_message(),
                "data": {
                    "city": weather_data.city,
                    "temperature": weather_data.temperature,
                    "feels_like": weather_data.feels_like,
                    "humidity": weather_data.humidity,
                    "description": weather_data.description,
                    "wind_speed": weather_data.wind_speed,
                    "needs_umbrella": weather_data.needs_umbrella(),
                },
            }
        except ValueError as e:
            return {"success": False, "error": str(e)}

    async def _check_umbrella(self, city: str | None = None) -> dict[str, Any]:
        """우산 필요 여부 확인"""
        try:
            needs_umbrella, message = await self._service.needs_umbrella(city)
            return {
                "success": True,
                "needs_umbrella": needs_umbrella,
                "message": message,
            }
        except ValueError as e:
            return {"success": False, "error": str(e)}

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """LLM Tool Calling용 도구 정의"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "지정된 도시의 현재 날씨를 조회합니다. 기온, 습도, 날씨 상태, 우산 필요 여부 등을 알려줍니다.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "날씨를 조회할 도시명 (예: Seoul, Busan, Tokyo). 영문으로 입력해야 합니다.",
                            }
                        },
                        "required": ["city"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "check_umbrella",
                    "description": "지정된 도시에 우산이 필요한지 확인합니다. 비나 눈 예보가 있을 때 우산을 챙기라고 알려줍니다.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "확인할 도시명 (예: Seoul, Busan). 영문으로 입력해야 합니다.",
                            }
                        },
                        "required": ["city"],
                    },
                },
            },
        ]
