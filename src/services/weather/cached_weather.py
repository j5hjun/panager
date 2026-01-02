"""
캐시 연동 날씨 서비스

WeatherService를 캐시로 감싸서 API 호출을 최소화합니다.
"""

import logging
from typing import Any

from src.core.entities.cache import generate_cache_key
from src.core.entities.weather import WeatherData
from src.services.cache.sqlite_cache import CacheService
from src.services.weather.openweathermap import WeatherService

logger = logging.getLogger(__name__)

# 캐시 TTL (초)
WEATHER_CACHE_TTL = 3600  # 1시간


class CachedWeatherService:
    """
    캐시 연동 날씨 서비스

    날씨 데이터를 1시간 동안 캐시하여 API 호출을 최소화합니다.
    """

    def __init__(
        self,
        weather_service: WeatherService,
        cache_service: CacheService,
        cache_ttl: int = WEATHER_CACHE_TTL,
    ):
        """
        CachedWeatherService 초기화

        Args:
            weather_service: 실제 날씨 서비스
            cache_service: 캐시 서비스
            cache_ttl: 캐시 TTL (초)
        """
        self._weather = weather_service
        self._cache = cache_service
        self._ttl = cache_ttl

        logger.info(f"CachedWeatherService 초기화 완료 (TTL={cache_ttl}s)")

    async def get_current_weather(self, city: str | None = None) -> dict[str, Any]:
        """
        현재 날씨 조회 (캐시 우선)

        Args:
            city: 도시명 (None이면 기본 도시)

        Returns:
            날씨 데이터 딕셔너리
        """
        city = city or self._weather.default_city
        cache_key = generate_cache_key("weather", city=city.lower())

        # 캐시 확인
        cached = self._cache.get(cache_key)
        if cached:
            logger.info(f"날씨 캐시 히트: {city}")
            return cached

        # API 호출
        logger.info(f"날씨 API 호출: {city}")
        weather_info = await self._weather.get_current_weather(city)

        # 캐시 저장
        self._cache.set(cache_key, weather_info, self._ttl)

        return weather_info

    async def get_weather_data(self, city: str | None = None) -> WeatherData:
        """WeatherData 엔티티로 날씨 조회"""
        weather_info = await self.get_current_weather(city)
        return WeatherData(**weather_info)

    async def get_weather_formatted(self, city: str | None = None) -> str:
        """포맷된 날씨 정보 조회"""
        weather = await self.get_weather_data(city)
        return weather.to_message()

    async def needs_umbrella(self, city: str | None = None) -> tuple[bool, str]:
        """우산 필요 여부 확인"""
        weather = await self.get_weather_data(city)

        if weather.needs_umbrella():
            return (
                True,
                f"{weather.city}에 {weather.description} 예보가 있어요. 우산을 챙기세요! ☂️",
            )
        else:
            return (
                False,
                f"{weather.city}는 {weather.description}이에요. 우산은 필요 없을 것 같아요! 😊",
            )

    @property
    def default_city(self) -> str:
        """기본 도시명"""
        return self._weather.default_city
