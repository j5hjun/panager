"""
날씨 서비스 테스트

기상청 단기예보 API를 사용하는 날씨 서비스 테스트
"""

from unittest.mock import AsyncMock, patch

import pytest


class TestWeatherService:
    """날씨 서비스 테스트"""

    def test_weather_service_can_be_imported(self):
        """WeatherService 클래스를 import할 수 있어야 함"""
        from src.services.weather.kma_weather import WeatherService

        assert WeatherService is not None

    def test_weather_service_initialization(self):
        """WeatherService를 초기화할 수 있어야 함"""
        from src.services.weather.kma_weather import WeatherService

        service = WeatherService(api_key="test-api-key")

        assert service is not None
        assert service.api_key == "test-api-key"

    @pytest.mark.asyncio
    async def test_get_current_weather(self):
        """현재 날씨를 조회할 수 있어야 함"""
        from src.services.weather.kma_weather import WeatherService

        service = WeatherService(api_key="test-api-key")

        # Mock 기상청 API 응답
        mock_response = {
            "response": {
                "header": {"resultCode": "00", "resultMsg": "NORMAL_SERVICE"},
                "body": {
                    "items": {
                        "item": [
                            {"category": "T1H", "fcstValue": "5"},
                            {"category": "REH", "fcstValue": "60"},
                            {"category": "SKY", "fcstValue": "1"},
                            {"category": "PTY", "fcstValue": "0"},
                            {"category": "WSD", "fcstValue": "2.5"},
                        ]
                    }
                },
            }
        }

        with patch.object(service, "_fetch_weather", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_response

            weather = await service.get_current_weather("Seoul")

            assert weather is not None
            assert weather["city"] == "Seoul"
            assert weather["temperature"] == 5.0
            assert weather["description"] == "맑음"

    @pytest.mark.asyncio
    async def test_get_weather_formatted(self):
        """포맷된 날씨 정보를 반환할 수 있어야 함"""
        from src.services.weather.kma_weather import WeatherService

        service = WeatherService(api_key="test-api-key")

        mock_response = {
            "response": {
                "header": {"resultCode": "00", "resultMsg": "NORMAL_SERVICE"},
                "body": {
                    "items": {
                        "item": [
                            {"category": "T1H", "fcstValue": "5"},
                            {"category": "REH", "fcstValue": "60"},
                            {"category": "SKY", "fcstValue": "1"},
                            {"category": "PTY", "fcstValue": "0"},
                            {"category": "WSD", "fcstValue": "2.5"},
                        ]
                    }
                },
            }
        }

        with patch.object(service, "_fetch_weather", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_response

            formatted = await service.get_weather_formatted("Seoul")

            assert "Seoul" in formatted or "서울" in formatted
            assert "5" in formatted


class TestWeatherEntity:
    """날씨 엔티티 테스트"""

    def test_weather_data_can_be_imported(self):
        """WeatherData 클래스를 import할 수 있어야 함"""
        from src.core.entities.weather import WeatherData

        assert WeatherData is not None

    def test_weather_data_creation(self):
        """WeatherData를 생성할 수 있어야 함"""
        from src.core.entities.weather import WeatherData

        weather = WeatherData(
            city="Seoul",
            temperature=5.5,
            feels_like=3.2,
            humidity=60,
            description="맑음",
            wind_speed=2.5,
        )

        assert weather.city == "Seoul"
        assert weather.temperature == 5.5

    def test_needs_umbrella(self):
        """우산 필요 여부를 판단할 수 있어야 함"""
        from src.core.entities.weather import WeatherData

        # 비 오는 날
        rainy = WeatherData(
            city="Seoul",
            temperature=10,
            feels_like=8,
            humidity=80,
            description="비",
            wind_speed=3,
            icon="10d",
        )
        assert rainy.needs_umbrella() is True

        # 맑은 날
        sunny = WeatherData(
            city="Seoul",
            temperature=20,
            feels_like=18,
            humidity=40,
            description="맑음",
            wind_speed=2,
            icon="01d",
        )
        assert sunny.needs_umbrella() is False

    def test_to_message(self):
        """사람이 읽기 좋은 메시지로 변환할 수 있어야 함"""
        from src.core.entities.weather import WeatherData

        weather = WeatherData(
            city="Seoul",
            temperature=5.5,
            feels_like=3.2,
            humidity=60,
            description="맑음",
            wind_speed=2.5,
        )

        message = weather.to_message()
        assert "Seoul" in message or "서울" in message
        assert "5" in message
        assert "맑음" in message
