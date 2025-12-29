"""
일정 엔티티

일정 데이터를 표현하는 도메인 모델
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Schedule:
    """
    일정 데이터

    사용자의 일정 정보를 표현하는 도메인 모델
    """

    id: str
    title: str
    start_time: datetime
    end_time: datetime | None = None
    location: str = ""
    description: str = ""

    def to_message(self) -> str:
        """
        사람이 읽기 좋은 형태의 메시지로 변환

        Returns:
            포맷된 일정 메시지
        """
        time_str = self.start_time.strftime("%Y년 %m월 %d일 %H:%M")

        parts = [f"📅 **{self.title}**", f"🕐 {time_str}"]

        if self.location:
            parts.append(f"📍 {self.location}")

        if self.description:
            parts.append(f"📝 {self.description}")

        return "\n".join(parts)

    def to_brief(self) -> str:
        """간략한 일정 정보"""
        time_str = self.start_time.strftime("%H:%M")
        if self.location:
            return f"{time_str} {self.title} @ {self.location}"
        return f"{time_str} {self.title}"
