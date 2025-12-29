"""
길찾기 도구 플러그인

Kakao Maps API를 사용하여 대중교통 경로를 제공합니다.
"""

import logging
from datetime import datetime
from typing import Any

from src.core.tools.base import BaseTool
from src.services.directions.kakao_maps import DirectionsService

logger = logging.getLogger(__name__)


class DirectionsTool(BaseTool):
    """
    길찾기 도구

    대중교통 경로 검색, 소요시간 확인, 출발시간 계산 기능을 제공합니다.
    """

    def __init__(self, directions_service: DirectionsService):
        """
        DirectionsTool 초기화

        Args:
            directions_service: DirectionsService 인스턴스
        """
        self._service = directions_service
        logger.info("DirectionsTool 초기화 완료")

    @property
    def name(self) -> str:
        return "directions"

    @property
    def description(self) -> str:
        return "길찾기 도구 (대중교통 경로, 소요시간, 출발시간 계산)"

    async def execute(self, function_name: str, **kwargs: Any) -> Any:
        """
        길찾기 도구 실행

        Args:
            function_name: 실행할 함수 이름 ('get_directions' 또는 'calculate_departure')
            **kwargs: 함수 파라미터

        Returns:
            함수 실행 결과
        """
        if function_name == "get_directions":
            return await self._get_directions(**kwargs)
        elif function_name == "calculate_departure":
            return self._calculate_departure(**kwargs)
        else:
            raise ValueError(f"알 수 없는 함수: {function_name}")

    async def _get_directions(self, origin: str, destination: str) -> dict[str, Any]:
        """대중교통 경로 검색"""
        try:
            data = await self._service.get_directions(origin, destination)
            return {
                "success": True,
                "message": data.to_message(),
                "data": {
                    "origin": data.origin,
                    "destination": data.destination,
                    "duration_minutes": data.duration_minutes,
                    "distance_km": data.distance_meters / 1000,
                    "fare": data.fare,
                    "transfer_count": data.transfer_count,
                    "steps": data.steps,
                },
            }
        except ValueError as e:
            return {"success": False, "error": str(e)}

    def _calculate_departure(self, arrival_time: str, duration_minutes: int) -> dict[str, Any]:
        """출발 시간 계산"""
        try:
            # 시간 파싱 (HH:MM 형식)
            if ":" in arrival_time:
                time_parts = arrival_time.split(":")
                hour = int(time_parts[0])
                minute = int(time_parts[1]) if len(time_parts) > 1 else 0
            else:
                # "1시", "13시" 형식
                hour = int(arrival_time.replace("시", "").strip())
                minute = 0

            # 오늘 날짜로 datetime 생성
            now = datetime.now()
            arrival_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # 출발 시간 계산
            departure_dt = self._service.calculate_departure_time(arrival_dt, duration_minutes)

            return {
                "success": True,
                "message": f"⏰ **{arrival_time}**까지 도착하려면\n🚀 **{departure_dt.strftime('%H:%M')}**에 출발하세요! ({duration_minutes}분 소요)",
                "departure_time": departure_dt.strftime("%H:%M"),
                "arrival_time": arrival_time,
                "duration_minutes": duration_minutes,
            }
        except ValueError as e:
            return {"success": False, "error": f"시간 형식 오류: {str(e)}"}

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """LLM Tool Calling용 도구 정의"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_directions",
                    "description": "출발지에서 도착지까지 대중교통 경로를 검색합니다. 소요시간, 환승 정보, 요금을 알려줍니다.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "origin": {
                                "type": "string",
                                "description": "출발지 (예: '창동역', '서울역', '강남역')",
                            },
                            "destination": {
                                "type": "string",
                                "description": "도착지 (예: '강남역', '홍대입구역', '판교역')",
                            },
                        },
                        "required": ["origin", "destination"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_departure",
                    "description": "특정 시간까지 도착하려면 몇 시에 출발해야 하는지 계산합니다. 소요시간을 알고 있어야 합니다.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "arrival_time": {
                                "type": "string",
                                "description": "도착해야 하는 시간 (예: '13:00', '14:30', '9시')",
                            },
                            "duration_minutes": {
                                "type": "integer",
                                "description": "예상 소요시간 (분 단위, 예: 45)",
                            },
                        },
                        "required": ["arrival_time", "duration_minutes"],
                    },
                },
            },
        ]
