"""
캐시 연동 길찾기 서비스

DirectionsService를 캐시로 감싸서 API 호출을 최소화합니다.
"""

import logging
from datetime import datetime

from src.core.entities.cache import generate_cache_key
from src.core.entities.directions import DirectionsData
from src.services.cache.sqlite_cache import CacheService
from src.services.directions.kakao_maps import DirectionsService

logger = logging.getLogger(__name__)

# 캐시 TTL (초)
DIRECTIONS_CACHE_TTL = 900  # 15분 (교통 상황 변동 고려)


class CachedDirectionsService:
    """
    캐시 연동 길찾기 서비스

    경로 데이터를 15분 동안 캐시하여 API 호출을 최소화합니다.
    """

    def __init__(
        self,
        directions_service: DirectionsService,
        cache_service: CacheService,
        cache_ttl: int = DIRECTIONS_CACHE_TTL,
    ):
        """
        CachedDirectionsService 초기화

        Args:
            directions_service: 실제 길찾기 서비스
            cache_service: 캐시 서비스
            cache_ttl: 캐시 TTL (초)
        """
        self._directions = directions_service
        self._cache = cache_service
        self._ttl = cache_ttl

        logger.info(f"CachedDirectionsService 초기화 완료 (TTL={cache_ttl}s)")

    async def get_directions(self, origin: str, destination: str) -> DirectionsData:
        """
        경로 검색 (캐시 우선)

        Args:
            origin: 출발지
            destination: 도착지

        Returns:
            DirectionsData 엔티티
        """
        cache_key = generate_cache_key(
            "directions", origin=origin.strip(), destination=destination.strip()
        )

        # 캐시 확인
        cached = self._cache.get(cache_key)
        if cached:
            logger.info(f"경로 캐시 히트: {origin} → {destination}")
            return DirectionsData(**cached)

        # API 호출
        logger.info(f"경로 API 호출: {origin} → {destination}")
        directions = await self._directions.get_directions(origin, destination)

        # 캐시 저장 (DirectionsData를 dict로 변환)
        cache_data = {
            "origin": directions.origin,
            "destination": directions.destination,
            "duration_minutes": directions.duration_minutes,
            "distance_meters": directions.distance_meters,
            "fare": directions.fare,
            "transfer_count": directions.transfer_count,
            "departure_time": (
                directions.departure_time.isoformat() if directions.departure_time else None
            ),
            "arrival_time": (
                directions.arrival_time.isoformat() if directions.arrival_time else None
            ),
            "steps": directions.steps,
        }
        self._cache.set(cache_key, cache_data, self._ttl)

        return directions

    async def get_directions_formatted(self, origin: str, destination: str) -> str:
        """포맷된 경로 안내 반환"""
        data = await self.get_directions(origin, destination)
        return data.to_message()

    def calculate_departure_time(self, arrival_time: datetime, duration_minutes: int) -> datetime:
        """도착 시간 기반 출발 시간 계산 (캐시 불필요)"""
        return self._directions.calculate_departure_time(arrival_time, duration_minutes)
