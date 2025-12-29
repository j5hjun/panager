"""
날씨 엔티티

날씨 데이터를 표현하는 도메인 모델
"""

from dataclasses import dataclass


@dataclass
class WeatherData:
    """
    날씨 데이터

    OpenWeatherMap API 응답을 정규화한 도메인 모델
    """

    city: str
    temperature: float  # 섭씨
    feels_like: float  # 체감 온도
    humidity: int  # 습도 (%)
    description: str  # 날씨 설명 (맑음, 흐림 등)
    wind_speed: float  # 풍속 (m/s)
    icon: str = ""  # 날씨 아이콘 코드

    def needs_umbrella(self) -> bool:
        """
        우산이 필요한지 판단

        Returns:
            True if 비/눈 예보가 있을 때
        """
        rain_keywords = ["비", "rain", "雨", "소나기", "shower", "drizzle", "눈", "snow"]
        rain_icons = ["09", "10", "11", "13"]  # 비, 폭풍우, 눈 아이콘

        # 설명에서 비/눈 키워드 확인
        description_lower = self.description.lower()
        for keyword in rain_keywords:
            if keyword in description_lower:
                return True

        # 아이콘 코드로 확인
        for icon_code in rain_icons:
            if icon_code in self.icon:
                return True

        return False

    def to_message(self) -> str:
        """
        사람이 읽기 좋은 형태의 메시지로 변환

        Returns:
            포맷된 날씨 메시지
        """
        # 온도에 따른 이모지
        if self.temperature >= 30:
            temp_emoji = "🔥"
        elif self.temperature >= 20:
            temp_emoji = "☀️"
        elif self.temperature >= 10:
            temp_emoji = "🌤️"
        elif self.temperature >= 0:
            temp_emoji = "❄️"
        else:
            temp_emoji = "🥶"

        # 날씨에 따른 이모지
        if self.needs_umbrella():
            weather_emoji = "🌧️"
            umbrella_msg = "우산을 챙기세요! ☂️"
        else:
            weather_emoji = "☀️"
            umbrella_msg = ""

        message = (
            f"{weather_emoji} **{self.city}** 현재 날씨\n"
            f"{temp_emoji} 기온: {self.temperature:.1f}°C (체감 {self.feels_like:.1f}°C)\n"
            f"💨 풍속: {self.wind_speed:.1f}m/s\n"
            f"💧 습도: {self.humidity}%\n"
            f"📝 상태: {self.description}"
        )

        if umbrella_msg:
            message += f"\n\n⚠️ {umbrella_msg}"

        return message

    def to_brief(self) -> str:
        """간략한 날씨 정보"""
        return f"{self.city}: {self.description}, {self.temperature:.1f}°C"
