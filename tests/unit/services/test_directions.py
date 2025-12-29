"""
길찾기 서비스 테스트

Kakao Maps API를 사용하는 DirectionsService를 검증합니다.
"""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest


class TestDirectionsService:
    """DirectionsService 테스트"""

    def test_directions_service_can_be_imported(self):
        """DirectionsService를 import 할 수 있음"""
        from src.services.directions.kakao_maps import DirectionsService

        assert DirectionsService is not None

    def test_directions_service_initialization(self):
        """DirectionsService 초기화"""
        from src.services.directions.kakao_maps import DirectionsService

        service = DirectionsService(api_key="test-api-key")

        assert service.api_key == "test-api-key"

    @pytest.mark.asyncio
    async def test_get_directions_success(self):
        """경로 검색 성공"""
        from src.services.directions.kakao_maps import DirectionsService

        service = DirectionsService(api_key="test-api-key")

        # Mock 장소 검색 결과
        mock_origin = {"x": 127.0, "y": 37.5, "name": "창동역"}
        mock_dest = {"x": 127.1, "y": 37.6, "name": "강남역"}

        # Mock API 응답
        mock_response = {
            "routes": [
                {
                    "result_code": 0,
                    "summary": {
                        "origin": {"name": "창동역"},
                        "destination": {"name": "강남역"},
                        "duration": 2700,  # 초
                        "distance": 15000,  # 미터
                        "fare": {"regular": {"totalFare": 1500}},
                    },
                    "sections": [
                        {
                            "type": "SUBWAY",
                            "lane": [{"name": "4호선"}],
                            "from": {"name": "창동역"},
                            "to": {"name": "동대문역사문화공원역"},
                            "duration": 1200,
                            "distance": 8000,
                        },
                        {
                            "type": "SUBWAY",
                            "lane": [{"name": "2호선"}],
                            "from": {"name": "동대문역사문화공원역"},
                            "to": {"name": "강남역"},
                            "duration": 1500,
                            "distance": 7000,
                        },
                    ],
                }
            ]
        }

        with patch.object(service, "_search_location", new_callable=AsyncMock) as mock_search:
            mock_search.side_effect = [mock_origin, mock_dest]

            with patch.object(service, "_fetch_directions", new_callable=AsyncMock) as mock_fetch:
                mock_fetch.return_value = mock_response

                result = await service.get_directions("창동역", "강남역")

                assert result.origin == "창동역"
                assert result.destination == "강남역"
                assert result.duration_minutes == 45
                assert result.transfer_count >= 1

    @pytest.mark.asyncio
    async def test_get_directions_not_found(self):
        """경로를 찾을 수 없는 경우"""
        from src.services.directions.kakao_maps import DirectionsService

        service = DirectionsService(api_key="test-api-key")

        mock_origin = {"x": 127.0, "y": 37.5, "name": "알수없는장소"}
        mock_dest = {"x": 127.1, "y": 37.6, "name": "없는곳"}

        with patch.object(service, "_search_location", new_callable=AsyncMock) as mock_search:
            mock_search.side_effect = [mock_origin, mock_dest]

            with patch.object(service, "_fetch_directions", new_callable=AsyncMock) as mock_fetch:
                mock_fetch.return_value = {"routes": []}

                with pytest.raises(ValueError, match="경로를 찾을 수 없습니다"):
                    await service.get_directions("알수없는장소", "없는곳")

    @pytest.mark.asyncio
    async def test_get_directions_api_error(self):
        """API 오류 처리"""
        from src.services.directions.kakao_maps import DirectionsService

        service = DirectionsService(api_key="test-api-key")

        mock_origin = {"x": 127.0, "y": 37.5, "name": "창동역"}
        mock_dest = {"x": 127.1, "y": 37.6, "name": "강남역"}

        with patch.object(service, "_search_location", new_callable=AsyncMock) as mock_search:
            mock_search.side_effect = [mock_origin, mock_dest]

            with patch.object(service, "_fetch_directions", new_callable=AsyncMock) as mock_fetch:
                mock_fetch.side_effect = Exception("API 오류")

                with pytest.raises(ValueError, match="길찾기"):
                    await service.get_directions("창동역", "강남역")

    @pytest.mark.asyncio
    async def test_get_directions_formatted(self):
        """포맷된 경로 안내 반환"""
        from src.core.entities.directions import DirectionsData
        from src.services.directions.kakao_maps import DirectionsService

        service = DirectionsService(api_key="test-api-key")

        mock_data = DirectionsData(
            origin="창동역",
            destination="강남역",
            duration_minutes=45,
            distance_meters=15000,
            fare=1500,
            transfer_count=1,
            departure_time=None,
            arrival_time=None,
            steps=[],
        )

        with patch.object(service, "get_directions", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_data

            result = await service.get_directions_formatted("창동역", "강남역")

            assert "창동역" in result
            assert "강남역" in result

    def test_calculate_departure_time(self):
        """도착 시간 기반 출발 시간 계산"""
        from src.services.directions.kakao_maps import DirectionsService

        service = DirectionsService(api_key="test-api-key")

        arrival_time = datetime(2025, 1, 15, 13, 0)  # 오후 1시
        duration_minutes = 45

        departure_time = service.calculate_departure_time(arrival_time, duration_minutes)

        assert departure_time == datetime(2025, 1, 15, 12, 15)  # 12시 15분
