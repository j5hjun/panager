"""
Kakao Maps 길찾기 서비스

Kakao Maps API를 통해 대중교통 경로를 검색합니다.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

import httpx

from src.core.entities.directions import DirectionsData

logger = logging.getLogger(__name__)

# Kakao Maps API 엔드포인트
KAKAO_LOCAL_SEARCH_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"
KAKAO_DIRECTIONS_URL = "https://apis-navi.kakaomobility.com/v1/directions"


class DirectionsService:
    """
    길찾기 서비스

    Kakao Maps API를 사용하여 대중교통 경로를 검색합니다.
    """

    def __init__(self, api_key: str):
        """
        DirectionsService 초기화

        Args:
            api_key: Kakao REST API 키
        """
        self.api_key = api_key
        self._headers = {"Authorization": f"KakaoAK {api_key}"}

        logger.info("DirectionsService 초기화 완료")

    async def _search_location(self, query: str) -> dict[str, Any] | None:
        """
        장소 검색으로 좌표 얻기

        Args:
            query: 검색어 (예: "창동역", "강남역")

        Returns:
            {"x": 경도, "y": 위도, "name": 장소명} 또는 None
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                KAKAO_LOCAL_SEARCH_URL,
                headers=self._headers,
                params={"query": query, "size": 1},
            )
            response.raise_for_status()
            data = response.json()

            if data.get("documents"):
                doc = data["documents"][0]
                return {"x": float(doc["x"]), "y": float(doc["y"]), "name": doc["place_name"]}
            return None

    async def _fetch_directions(
        self, origin: dict[str, float], destination: dict[str, float]
    ) -> dict[str, Any]:
        """
        Kakao Mobility API에서 경로 검색

        Args:
            origin: 출발지 좌표 {"x": 경도, "y": 위도}
            destination: 도착지 좌표 {"x": 경도, "y": 위도}

        Returns:
            API 응답 JSON
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                KAKAO_DIRECTIONS_URL,
                headers=self._headers,
                params={
                    "origin": f"{origin['x']},{origin['y']}",
                    "destination": f"{destination['x']},{destination['y']}",
                    "priority": "RECOMMEND",
                },
            )
            response.raise_for_status()
            return response.json()

    async def get_directions(self, origin: str, destination: str) -> DirectionsData:
        """
        대중교통 경로 검색

        Args:
            origin: 출발지 (예: "창동역")
            destination: 도착지 (예: "강남역")

        Returns:
            DirectionsData 엔티티

        Raises:
            ValueError: 경로를 찾을 수 없는 경우
        """
        try:
            # 출발지/도착지 좌표 검색
            origin_loc = await self._search_location(origin)
            dest_loc = await self._search_location(destination)

            if not origin_loc:
                raise ValueError(f"출발지를 찾을 수 없습니다: {origin}")
            if not dest_loc:
                raise ValueError(f"도착지를 찾을 수 없습니다: {destination}")

            # 경로 검색
            response = await self._fetch_directions(origin_loc, dest_loc)

            routes = response.get("routes", [])
            if not routes:
                raise ValueError(f"경로를 찾을 수 없습니다: {origin} → {destination}")

            route = routes[0]

            # 결과 코드 확인
            if route.get("result_code", 0) != 0:
                raise ValueError(f"경로를 찾을 수 없습니다: {origin} → {destination}")

            summary = route.get("summary", {})
            sections = route.get("sections", [])

            # 소요시간 (초 → 분)
            duration_seconds = summary.get("duration", 0)
            duration_minutes = duration_seconds // 60

            # 거리 (미터)
            distance_meters = summary.get("distance", 0)

            # 요금
            fare_info = summary.get("fare", {})
            regular_fare = fare_info.get("regular", {})
            fare = regular_fare.get("totalFare", 0)

            # 경로 단계 구성
            steps = []
            for section in sections:
                section_type = section.get("type", "")
                lane_info = section.get("lane", [{}])
                line_name = lane_info[0].get("name", "") if lane_info else ""

                steps.append(
                    {
                        "mode": section_type,
                        "line": line_name,
                        "from": section.get("from", {}).get("name", ""),
                        "to": section.get("to", {}).get("name", ""),
                    }
                )

            # 환승 횟수 계산 (SUBWAY/BUS 구간 수 - 1, 최소 0)
            transit_sections = [s for s in sections if s.get("type") in ("SUBWAY", "BUS")]
            transfer_count = max(0, len(transit_sections) - 1)

            logger.info(f"경로 검색 성공: {origin} → {destination} ({duration_minutes}분)")

            return DirectionsData(
                origin=origin_loc.get("name", origin),
                destination=dest_loc.get("name", destination),
                duration_minutes=duration_minutes,
                distance_meters=distance_meters,
                fare=fare,
                transfer_count=transfer_count,
                departure_time=None,
                arrival_time=None,
                steps=steps,
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"Kakao API 오류: {e}")
            if e.response.status_code == 401:
                raise ValueError("Kakao API 키가 유효하지 않습니다.") from e
            raise ValueError(f"길찾기 API 오류: {e.response.status_code}") from e
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"길찾기 실패: {e}")
            raise ValueError(f"길찾기 중 오류가 발생했습니다: {str(e)}") from e

    async def get_directions_formatted(self, origin: str, destination: str) -> str:
        """
        포맷된 경로 안내 반환

        Args:
            origin: 출발지
            destination: 도착지

        Returns:
            사람이 읽기 좋은 경로 안내 메시지
        """
        data = await self.get_directions(origin, destination)
        return data.to_message()

    def calculate_departure_time(self, arrival_time: datetime, duration_minutes: int) -> datetime:
        """
        도착 시간 기반 출발 시간 계산

        Args:
            arrival_time: 도착해야 하는 시간
            duration_minutes: 소요 시간 (분)

        Returns:
            출발해야 하는 시간
        """
        return arrival_time - timedelta(minutes=duration_minutes)
