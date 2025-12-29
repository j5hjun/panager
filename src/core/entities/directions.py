"""
길찾기 엔티티

대중교통 경로 정보를 표현하는 도메인 모델
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RouteStep:
    """
    경로 단계 정보

    하나의 교통 수단 구간을 표현합니다.
    """

    mode: str  # SUBWAY, BUS, WALK 등
    line: str  # 노선명 (예: "4호선", "151번")
    start_name: str  # 출발 정류장/역
    end_name: str  # 도착 정류장/역
    duration_minutes: int  # 소요 시간 (분)
    distance_meters: int  # 거리 (미터)

    def __str__(self) -> str:
        mode_emoji = {
            "SUBWAY": "🚇",
            "BUS": "🚌",
            "WALK": "🚶",
        }.get(self.mode, "🚗")

        return f"{mode_emoji} {self.line}: {self.start_name} → {self.end_name} ({self.duration_minutes}분)"


@dataclass
class DirectionsData:
    """
    길찾기 결과 데이터

    출발지에서 도착지까지의 대중교통 경로 정보
    """

    origin: str  # 출발지
    destination: str  # 도착지
    duration_minutes: int  # 총 소요 시간 (분)
    distance_meters: int  # 총 거리 (미터)
    fare: int  # 요금 (원)
    transfer_count: int  # 환승 횟수
    departure_time: datetime | None  # 출발 시간
    arrival_time: datetime | None  # 도착 시간
    steps: list[dict] = field(default_factory=list)  # 경로 단계 (raw dict)

    def to_message(self) -> str:
        """
        사람이 읽기 좋은 형태의 메시지로 변환

        Returns:
            포맷된 경로 안내 메시지
        """
        lines = [
            f"🚇 **{self.origin} → {self.destination}**",
            f"⏱️ 소요시간: **{self.duration_minutes}분**",
            f"📏 거리: {self.distance_meters / 1000:.1f}km",
            f"💰 요금: {self.fare:,}원",
            f"🔄 환승: {self.transfer_count}회",
        ]

        if self.departure_time:
            lines.append(f"🕐 출발: {self.departure_time.strftime('%H:%M')}")
        if self.arrival_time:
            lines.append(f"🕐 도착: {self.arrival_time.strftime('%H:%M')}")

        if self.steps:
            lines.append("")
            lines.append("**경로 상세:**")
            for i, step in enumerate(self.steps, 1):
                mode = step.get("mode", "")
                line_name = step.get("line", "")
                from_name = step.get("from", "")
                to_name = step.get("to", "")

                mode_emoji = {"SUBWAY": "🚇", "BUS": "🚌", "WALK": "🚶"}.get(mode, "🚗")
                lines.append(f"{i}. {mode_emoji} {line_name}: {from_name} → {to_name}")

        return "\n".join(lines)

    def to_brief(self) -> str:
        """간략한 경로 정보"""
        return f"{self.origin} → {self.destination}: {self.duration_minutes}분, 환승 {self.transfer_count}회"
