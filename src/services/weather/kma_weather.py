"""
기상청 단기예보 서비스

기상청 단기예보 API를 통해 날씨 정보를 조회합니다.
공공데이터포털: https://www.data.go.kr/data/15084084/openapi.do
"""

import logging
from datetime import datetime, timedelta
from typing import Any

import httpx

from src.core.entities.weather import WeatherData

logger = logging.getLogger(__name__)

# 기상청 단기예보 API 엔드포인트
KMA_API_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"

# 도시별 격자 좌표 (nx, ny)
CITY_COORDINATES = {
    "seoul": (60, 127),
    "busan": (98, 76),
    "daegu": (89, 90),
    "incheon": (55, 124),
    "gwangju": (58, 74),
    "daejeon": (67, 100),
    "ulsan": (102, 84),
    "sejong": (66, 103),
    "suwon": (60, 121),
    "seongnam": (63, 124),
    "goyang": (57, 128),
    "yongin": (64, 119),
    "changwon": (90, 77),
    "cheongju": (69, 106),
    "jeonju": (63, 89),
    "cheonan": (63, 110),
    "pohang": (102, 94),
    "jeju": (52, 38),
    "gangnam": (61, 126),  # 강남역
}

# 하늘 상태 코드
SKY_CODES = {
    "1": "맑음",
    "3": "구름많음",
    "4": "흐림",
}

# 강수 형태 코드
PTY_CODES = {
    "0": "없음",
    "1": "비",
    "2": "비/눈",
    "3": "눈",
    "4": "소나기",
    "5": "빗방울",  # 초단기예보
    "6": "빗방울눈날림",  # 초단기예보
    "7": "눈날림",  # 초단기예보
}


class KMAWeatherService:
    """
    기상청 날씨 서비스

    기상청 단기예보 API를 사용하여 실시간 날씨 정보를 제공합니다.
    """

    def __init__(self, api_key: str, default_city: str = "Seoul"):
        """
        KMAWeatherService 초기화

        Args:
            api_key: 공공데이터포털 API 키 (Decoding)
            default_city: 기본 도시명
        """
        self.api_key = api_key
        self.default_city = default_city

        logger.info(f"KMAWeatherService 초기화 완료 (default_city={default_city})")

    def _get_base_datetime(self) -> tuple[str, str]:
        """
        기준 날짜 및 시간 계산

        초단기예보는 매시 30분에 발표되므로, 현재 시간 기준으로 가장 최근 발표 시간을 계산합니다.

        Returns:
            (base_date, base_time) 튜플
        """
        now = datetime.now()

        # 매시 30분에 발표, 45분 후부터 조회 가능
        if now.minute < 45:
            # 이전 시간의 발표 사용
            base = now - timedelta(hours=1)
        else:
            base = now

        base_date = base.strftime("%Y%m%d")
        base_time = base.strftime("%H30")

        return base_date, base_time

    def _get_coordinates(self, city: str) -> tuple[int, int]:
        """
        도시명을 격자 좌표로 변환

        Args:
            city: 도시명 (영문)

        Returns:
            (nx, ny) 좌표 튜플
        """
        city_lower = city.lower()

        if city_lower in CITY_COORDINATES:
            return CITY_COORDINATES[city_lower]

        # 기본값: 서울
        logger.warning(f"알 수 없는 도시: {city}, 서울 좌표 사용")
        return CITY_COORDINATES["seoul"]

    async def _fetch_weather(self, city: str) -> dict[str, Any]:
        """
        기상청 API에서 날씨 데이터 조회

        Args:
            city: 도시명 (영문)

        Returns:
            API 응답 JSON
        """
        base_date, base_time = self._get_base_datetime()
        nx, ny = self._get_coordinates(city)

        params = {
            "serviceKey": self.api_key,
            "numOfRows": "60",
            "pageNo": "1",
            "dataType": "JSON",
            "base_date": base_date,
            "base_time": base_time,
            "nx": str(nx),
            "ny": str(ny),
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(KMA_API_URL, params=params)
            response.raise_for_status()
            return response.json()

    def _parse_weather_data(self, data: dict, city: str) -> dict[str, Any]:
        """
        API 응답 데이터 파싱

        Args:
            data: API 응답 JSON
            city: 도시명

        Returns:
            정규화된 날씨 데이터
        """
        try:
            items = data["response"]["body"]["items"]["item"]
        except (KeyError, TypeError) as e:
            logger.error(f"날씨 데이터 파싱 실패: {data}")
            raise ValueError("날씨 데이터 형식이 올바르지 않습니다.") from e

        # 카테고리별 데이터 수집
        weather_values = {}
        for item in items:
            category = item.get("category")
            value = item.get("fcstValue")
            weather_values[category] = value

        # 기온 (T1H: 기온)
        temperature = float(weather_values.get("T1H", "0"))

        # 습도 (REH: 습도)
        humidity = int(weather_values.get("REH", "0"))

        # 하늘 상태 (SKY)
        sky_code = weather_values.get("SKY", "1")
        sky_desc = SKY_CODES.get(sky_code, "맑음")

        # 강수 형태 (PTY)
        pty_code = weather_values.get("PTY", "0")
        pty_desc = PTY_CODES.get(pty_code, "없음")

        # 풍속 (WSD: 풍속)
        wind_speed = float(weather_values.get("WSD", "0"))

        # 날씨 설명 생성
        if pty_code != "0":
            description = pty_desc
        else:
            description = sky_desc

        return {
            "city": city.title(),
            "temperature": temperature,
            "feels_like": temperature,  # 기상청 API는 체감온도 미제공
            "humidity": humidity,
            "description": description,
            "wind_speed": wind_speed,
            "icon": self._get_weather_icon(sky_code, pty_code),
        }

    def _get_weather_icon(self, sky_code: str, pty_code: str) -> str:
        """날씨 아이콘 반환"""
        if pty_code in ("1", "4", "5"):
            return "🌧️"
        elif pty_code in ("2", "6"):
            return "🌨️"
        elif pty_code in ("3", "7"):
            return "❄️"
        elif sky_code == "1":
            return "☀️"
        elif sky_code == "3":
            return "⛅"
        else:
            return "☁️"

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

            # 응답 검증
            result_code = data.get("response", {}).get("header", {}).get("resultCode")
            if result_code != "00":
                result_msg = data.get("response", {}).get("header", {}).get("resultMsg", "Unknown error")
                logger.error(f"기상청 API 오류: {result_code} - {result_msg}")
                raise ValueError(f"기상청 API 오류: {result_msg}")

            weather_info = self._parse_weather_data(data, city)

            logger.info(f"날씨 조회 성공: {city} - {weather_info['description']}")
            return weather_info

        except httpx.HTTPStatusError as e:
            logger.error(f"기상청 API HTTP 오류: {e}")
            raise ValueError(f"날씨 정보를 가져오는 중 오류가 발생했습니다: {e.response.status_code}") from e
        except httpx.TimeoutException as e:
            logger.error("기상청 API 타임아웃")
            raise ValueError("날씨 정보 조회 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.") from e
        except Exception as e:
            logger.error(f"날씨 조회 실패: {e}")
            raise ValueError(f"날씨 조회 중 예상치 못한 오류가 발생했습니다: {str(e)}") from e

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
            return True, f"{weather.city}에 {weather.description} 예보가 있어요. 우산을 챙기세요! ☔"
        else:
            return (
                False,
                f"{weather.city}는 {weather.description}이에요. 우산은 필요 없을 것 같아요! 😊",
            )


# 별칭 (기존 코드 호환성)
WeatherService = KMAWeatherService
