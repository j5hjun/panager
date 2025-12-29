"""
OpenWeatherMap 날씨 서비스

OpenWeatherMap API를 통해 날씨 정보를 조회합니다.
"""

import logging
from typing import Any

import httpx

from src.core.entities.weather import WeatherData

logger = logging.getLogger(__name__)

# OpenWeatherMap API 엔드포인트
OPENWEATHERMAP_API_URL = "https://api.openweathermap.org/data/2.5/weather"


class WeatherService:
    """
    날씨 서비스

    OpenWeatherMap API를 사용하여 실시간 날씨 정보를 제공합니다.
    """

    def __init__(self, api_key: str, default_city: str = "Seoul"):
        """
        WeatherService 초기화

        Args:
            api_key: OpenWeatherMap API 키
            default_city: 기본 도시명
        """
        self.api_key = api_key
        self.default_city = default_city

        logger.info(f"WeatherService 초기화 완료 (default_city={default_city})")

    async def _fetch_weather(self, city: str) -> dict[str, Any]:
        """
        OpenWeatherMap API에서 날씨 데이터 조회

        Args:
            city: 도시명 (영문)

        Returns:
            API 응답 JSON
        """
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",  # 섭씨
            "lang": "kr",  # 한국어 설명
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(OPENWEATHERMAP_API_URL, params=params)
            response.raise_for_status()
            return response.json()

    async def get_current_weather(self, city: str | None = None) -> dict[str, Any]:
        """
        현재 날씨 조회

        Args:
            city: 도시명 (None이면 기본 도시)

        Returns:
            정규화된 날씨 데이터 딕셔너리
        """
        city = city or self.default_city

        try:
            data = await self._fetch_weather(city)

            weather_info = {
                "city": data.get("name", city),
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "icon": data["weather"][0].get("icon", ""),
            }

            logger.info(f"날씨 조회 성공: {city} - {weather_info['description']}")
            return weather_info

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.error(f"도시를 찾을 수 없음: {city}")
                raise ValueError(f"'{city}' 도시를 찾을 수 없습니다. 영문 도시명을 확인해주세요.")
            elif e.response.status_code == 401:
                logger.error("날씨 API 키 인증 실패")
                raise ValueError("날씨 API 키가 유효하지 않습니다.")
            elif e.response.status_code == 429:
                logger.error("날씨 API 요청 제한 초과")
                raise ValueError("날씨 API 요청 횟수가 초과되었습니다. 잠시 후 다시 시도해주세요.")
            else:
                logger.error(f"날씨 API 오류: {e}")
                raise ValueError(
                    f"날씨 정보를 가져오는 중 오류가 발생했습니다: {e.response.status_code}"
                )
        except KeyError as e:
            logger.error(f"날씨 데이터 파싱 오류: {e}")
            raise ValueError("날씨 데이터 형식이 올바르지 않습니다.")
        except Exception as e:
            logger.error(f"날씨 조회 실패: {e}")
            raise ValueError(f"날씨 조회 중 예상치 못한 오류가 발생했습니다: {str(e)}")

    async def get_weather_data(self, city: str | None = None) -> WeatherData:
        """
        WeatherData 엔티티로 날씨 조회

        Args:
            city: 도시명

        Returns:
            WeatherData 엔티티
        """
        weather_info = await self.get_current_weather(city)
        return WeatherData(**weather_info)

    async def get_weather_formatted(self, city: str | None = None) -> str:
        """
        포맷된 날씨 정보 조회

        Args:
            city: 도시명

        Returns:
            사람이 읽기 좋은 날씨 메시지
        """
        weather = await self.get_weather_data(city)
        return weather.to_message()

    async def needs_umbrella(self, city: str | None = None) -> tuple[bool, str]:
        """
        우산 필요 여부 확인

        Args:
            city: 도시명

        Returns:
            (우산 필요 여부, 설명 메시지)
        """
        weather = await self.get_weather_data(city)

        if weather.needs_umbrella():
            return True, f"{weather.city}에 {weather.description} 예보가 있어요. 우산을 챙기세요! ☂️"
        else:
            return (
                False,
                f"{weather.city}는 {weather.description}이에요. 우산은 필요 없을 것 같아요! 😊",
            )
