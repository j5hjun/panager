"""
일정 관리 도구 플러그인

일정 조회 및 추가 기능을 제공합니다.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from src.core.tools.base import BaseTool
from src.services.calendar.sqlite_calendar import CalendarService

logger = logging.getLogger(__name__)


class CalendarTool(BaseTool):
    """
    일정 관리 도구

    일정 조회, 추가, 삭제 기능을 제공합니다.
    """

    def __init__(self, calendar_service: CalendarService):
        """
        CalendarTool 초기화

        Args:
            calendar_service: CalendarService 인스턴스
        """
        self._service = calendar_service
        logger.info("CalendarTool 초기화 완료")

    @property
    def name(self) -> str:
        return "calendar"

    @property
    def description(self) -> str:
        return "일정 관리 도구 (조회, 추가, 삭제)"

    async def execute(self, function_name: str, **kwargs: Any) -> Any:
        """
        일정 도구 실행

        Args:
            function_name: 실행할 함수 이름 ('get_schedule' 또는 'add_schedule')
            **kwargs: 함수 파라미터

        Returns:
            함수 실행 결과
        """
        if function_name == "get_schedule":
            return self._get_schedule(**kwargs)
        elif function_name == "add_schedule":
            return self._add_schedule(**kwargs)
        else:
            raise ValueError(f"알 수 없는 함수: {function_name}")

    def _get_schedule(self, date: str) -> dict[str, Any]:
        """특정 날짜의 일정 조회"""
        try:
            # 날짜 파싱
            if date.lower() == "today":
                target_date = datetime.now()
            elif date.lower() == "tomorrow":
                target_date = datetime.now() + timedelta(days=1)
            else:
                target_date = datetime.fromisoformat(date)

            schedules = self._service.get_schedules_by_date(target_date)
            formatted = self._service.format_schedule_list(schedules)

            return {
                "success": True,
                "date": target_date.strftime("%Y-%m-%d"),
                "count": len(schedules),
                "message": formatted,
                "schedules": [
                    {
                        "id": s.id,
                        "title": s.title,
                        "time": s.start_time.strftime("%H:%M"),
                        "location": s.location,
                    }
                    for s in schedules
                ],
            }
        except ValueError as e:
            return {"success": False, "error": f"날짜 형식 오류: {str(e)}"}

    def _add_schedule(
        self,
        title: str,
        date: str,
        time: str,
        location: str = "",
    ) -> dict[str, Any]:
        """일정 추가"""
        try:
            # 날짜 파싱
            if date.lower() == "today":
                target_date = datetime.now().date()
            elif date.lower() == "tomorrow":
                target_date = (datetime.now() + timedelta(days=1)).date()
            else:
                target_date = datetime.fromisoformat(date).date()

            # 시간 파싱 (HH:MM 또는 "오후 2시" 형태)
            if ":" in time:
                time_obj = datetime.strptime(time, "%H:%M").time()
            else:
                # 간단한 한국어 시간 파싱
                time = time.replace("오전 ", "").replace("오후 ", "")
                hour = int(time.replace("시", "").strip())
                if "오후" in time and hour < 12:
                    hour += 12
                time_obj = datetime.strptime(f"{hour:02d}:00", "%H:%M").time()

            start_time = datetime.combine(target_date, time_obj)

            schedule_id = self._service.add_schedule(
                title=title,
                start_time=start_time,
                location=location,
            )

            return {
                "success": True,
                "schedule_id": schedule_id,
                "message": f"일정이 추가되었어요! 📅\n• 제목: {title}\n• 날짜: {target_date}\n• 시간: {time_obj.strftime('%H:%M')}\n• 장소: {location or '(없음)'}",
            }
        except ValueError as e:
            return {"success": False, "error": f"일정 추가 실패: {str(e)}"}

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """LLM Tool Calling용 도구 정의"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_schedule",
                    "description": "특정 날짜의 일정을 조회합니다. 오늘, 내일, 특정 날짜의 일정을 확인할 때 사용합니다.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "조회할 날짜 (예: 'today', 'tomorrow', '2025-01-15'). today는 오늘, tomorrow는 내일을 의미합니다.",
                            }
                        },
                        "required": ["date"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "add_schedule",
                    "description": "새로운 일정을 추가합니다. 제목, 시간, 장소 등을 포함할 수 있습니다.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "일정 제목 (예: '팀 미팅', '점심 약속')",
                            },
                            "date": {
                                "type": "string",
                                "description": "날짜 (예: 'today', 'tomorrow', '2025-01-15')",
                            },
                            "time": {
                                "type": "string",
                                "description": "시간 (예: '14:00', '오후 2시')",
                            },
                            "location": {
                                "type": "string",
                                "description": "장소 (선택, 예: '강남역', '회의실 A')",
                            },
                        },
                        "required": ["title", "date", "time"],
                    },
                },
            },
        ]
