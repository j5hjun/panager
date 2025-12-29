"""
알림 템플릿

다양한 알림 유형에 대한 템플릿을 정의합니다.
"""


class AlertTemplates:
    """알림 템플릿 모음"""

    MORNING_BRIEFING = """다음 날씨 정보를 바탕으로 아침 브리핑을 작성해주세요.
친근하고 따뜻한 인사와 함께 오늘 하루를 시작하는 데 도움이 되는 조언을 해주세요.
간결하게 2-3문장으로 작성해주세요.

날씨 정보:
{weather_info}

현재 시간: {current_time}
"""

    WEATHER_ALERT = """다음 날씨 정보를 바탕으로 우산 알림을 작성해주세요.
친근하게 우산을 챙기라고 알려주세요. 1-2문장으로 작성해주세요.

도시: {city}
날씨: {description}
기온: {temperature}°C
"""

    REMINDER = """다음 리마인더를 친근하게 전달해주세요.
1-2문장으로 작성해주세요.

리마인더 내용: {message}
설정 시간: {set_time}
"""

    SCHEDULE_ALERT = """다음 일정에 대한 알림을 친근하게 전달해주세요.
1-2문장으로 작성해주세요.

일정: {schedule_title}
시간: {schedule_time}
장소: {location}
"""

    @classmethod
    def get_morning_briefing(cls, weather_info: str, current_time: str) -> str:
        """아침 브리핑 템플릿 반환"""
        return cls.MORNING_BRIEFING.format(
            weather_info=weather_info,
            current_time=current_time,
        )

    @classmethod
    def get_weather_alert(cls, city: str, description: str, temperature: float) -> str:
        """날씨 알림 템플릿 반환"""
        return cls.WEATHER_ALERT.format(
            city=city,
            description=description,
            temperature=temperature,
        )

    @classmethod
    def get_reminder(cls, message: str, set_time: str) -> str:
        """리마인더 템플릿 반환"""
        return cls.REMINDER.format(
            message=message,
            set_time=set_time,
        )

    @classmethod
    def get_schedule_alert(cls, schedule_title: str, schedule_time: str, location: str = "") -> str:
        """일정 알림 템플릿 반환"""
        return cls.SCHEDULE_ALERT.format(
            schedule_title=schedule_title,
            schedule_time=schedule_time,
            location=location or "미정",
        )
