"""
캐시 연동 서비스 테스트
"""

from unittest.mock import AsyncMock, MagicMock

import pytest


class TestCachedWeatherService:
    """CachedWeatherService 테스트"""

    def test_cached_weather_service_can_be_imported(self):
        """import 확인"""
        from src.services.weather.cached_weather import CachedWeatherService

        assert CachedWeatherService is not None

    @pytest.mark.asyncio
    async def test_cache_hit(self):
        """캐시 히트 시 API 미호출"""
        from src.services.weather.cached_weather import CachedWeatherService

        # Mock 설정
        mock_weather = MagicMock()
        mock_weather.default_city = "Seoul"
        mock_weather.get_current_weather = AsyncMock()

        mock_cache = MagicMock()
        mock_cache.get.return_value = {"temp": 15, "description": "맑음"}

        service = CachedWeatherService(mock_weather, mock_cache)
        result = await service.get_current_weather("Seoul")

        # 캐시에서 반환했으므로 API 미호출
        mock_weather.get_current_weather.assert_not_called()
        assert result["temp"] == 15

    @pytest.mark.asyncio
    async def test_cache_miss(self):
        """캐시 미스 시 API 호출 후 캐시 저장"""
        from src.services.weather.cached_weather import CachedWeatherService

        # Mock 설정
        mock_weather = MagicMock()
        mock_weather.default_city = "Seoul"
        mock_weather.get_current_weather = AsyncMock(
            return_value={"temp": 20, "description": "흐림"}
        )

        mock_cache = MagicMock()
        mock_cache.get.return_value = None  # 캐시 미스

        service = CachedWeatherService(mock_weather, mock_cache)
        result = await service.get_current_weather("Seoul")

        # API 호출됨
        mock_weather.get_current_weather.assert_called_once_with("Seoul")
        # 캐시에 저장됨
        mock_cache.set.assert_called_once()
        assert result["temp"] == 20


class TestCachedDirectionsService:
    """CachedDirectionsService 테스트"""

    def test_cached_directions_service_can_be_imported(self):
        """import 확인"""
        from src.services.directions.cached_directions import CachedDirectionsService

        assert CachedDirectionsService is not None

    @pytest.mark.asyncio
    async def test_cache_hit(self):
        """캐시 히트 시 API 미호출"""
        from src.services.directions.cached_directions import CachedDirectionsService

        # Mock 설정
        mock_directions = MagicMock()
        mock_directions.get_directions = AsyncMock()

        mock_cache = MagicMock()
        mock_cache.get.return_value = {
            "origin": "창동역",
            "destination": "강남역",
            "duration_minutes": 45,
            "distance_meters": 15000,
            "fare": 1500,
            "transfer_count": 1,
            "departure_time": None,
            "arrival_time": None,
            "steps": [],
        }

        service = CachedDirectionsService(mock_directions, mock_cache)
        result = await service.get_directions("창동역", "강남역")

        # 캐시에서 반환했으므로 API 미호출
        mock_directions.get_directions.assert_not_called()
        assert result.duration_minutes == 45

    @pytest.mark.asyncio
    async def test_cache_miss(self):
        """캐시 미스 시 API 호출 후 캐시 저장"""
        from src.core.entities.directions import DirectionsData
        from src.services.directions.cached_directions import CachedDirectionsService

        # Mock 설정
        mock_directions = MagicMock()
        mock_directions.get_directions = AsyncMock(
            return_value=DirectionsData(
                origin="창동역",
                destination="강남역",
                duration_minutes=50,
                distance_meters=16000,
                fare=1600,
                transfer_count=2,
                departure_time=None,
                arrival_time=None,
                steps=[],
            )
        )

        mock_cache = MagicMock()
        mock_cache.get.return_value = None  # 캐시 미스

        service = CachedDirectionsService(mock_directions, mock_cache)
        result = await service.get_directions("창동역", "강남역")

        # API 호출됨
        mock_directions.get_directions.assert_called_once()
        # 캐시에 저장됨
        mock_cache.set.assert_called_once()
        assert result.duration_minutes == 50
