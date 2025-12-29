"""
AI 서비스

LLM 클라이언트, 대화 관리자, 도구를 통합하여 완전한 AI 서비스를 제공합니다.
"""

import json
import logging
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from src.core.logic.conversation import ConversationManager
from src.core.prompts.panager_persona import get_system_prompt
from src.core.tools.plugins import CalendarTool, WeatherTool
from src.core.tools.registry import ToolRegistry
from src.services.calendar.sqlite_calendar import CalendarService
from src.services.llm.client import LLMClient
from src.services.weather.openweathermap import WeatherService

logger = logging.getLogger(__name__)

# 도구 이름 → 플러그인 이름 매핑 (LLM이 호출하는 함수명 → 플러그인)
TOOL_FUNCTION_TO_PLUGIN: dict[str, str] = {
    "get_current_weather": "weather",
    "check_umbrella": "weather",
    "get_schedule": "calendar",
    "add_schedule": "calendar",
}


class AIService:
    """
    통합 AI 서비스

    LLM 클라이언트와 대화 관리자, 도구를 조합하여
    사용자와 자연스러운 대화를 제공합니다.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        assistant_name: str = "패니저",
        max_history: int = 20,
        weather_api_key: str | None = None,
        default_city: str = "Seoul",
        calendar_db_path: str = "data/calendar.db",
    ):
        """
        AIService 초기화

        Args:
            api_key: LLM API 키
            base_url: LLM API 베이스 URL
            model: 사용할 모델명
            assistant_name: AI 비서 이름
            max_history: 사용자당 최대 대화 기록 수
            weather_api_key: OpenWeatherMap API 키
            default_city: 기본 도시명
            calendar_db_path: 일정 DB 경로
        """
        self.assistant_name = assistant_name
        self.default_city = default_city

        # LLM 클라이언트 초기화
        self.llm = LLMClient(
            api_key=api_key,
            base_url=base_url,
            model=model,
        )

        # 대화 관리자 초기화
        self.conversation = ConversationManager(max_history=max_history)

        # Tool Registry 초기화
        self.registry = ToolRegistry()
        self.registry.clear()  # 기존 등록 도구 초기화

        # 날씨 서비스 및 도구 초기화 (옵션)
        self.weather: WeatherService | None = None
        if weather_api_key:
            self.weather = WeatherService(
                api_key=weather_api_key,
                default_city=default_city,
            )
            # WeatherTool 등록
            weather_tool = WeatherTool(weather_service=self.weather)
            self.registry.register(weather_tool)
            logger.info("날씨 도구 등록됨")

        # 일정 서비스 및 도구 초기화
        self.calendar = CalendarService(db_path=calendar_db_path)
        calendar_tool = CalendarTool(calendar_service=self.calendar)
        self.registry.register(calendar_tool)
        logger.info("일정 도구 등록됨")

        # 시스템 프롬프트
        self.system_prompt = get_system_prompt(assistant_name)

        # 도구 정의 (Registry에서 가져옴)
        self.tools = self.registry.get_all_tool_definitions()

        # 스케줄러와 메시지 발송 콜백 (외부에서 주입)
        self._scheduler: Any = None
        self._send_message: Callable[[str, str], None] | None = None
        self._reminder_count = 0

        logger.info(
            f"AIService 초기화 완료: {assistant_name} "
            f"(tools={len(self.tools)}, plugins={self.registry.list_tools()})"
        )

    def set_scheduler(self, scheduler: Any, send_message: Callable[[str, str], None]):
        """
        스케줄러와 메시지 발송 콜백 설정

        Args:
            scheduler: SchedulerService 인스턴스
            send_message: 메시지 발송 함수 (channel_id, message) -> None
        """
        self._scheduler = scheduler
        self._send_message = send_message
        logger.info("스케줄러 연동 완료")

    async def _execute_tool(
        self, tool_name: str, arguments: dict[str, Any], user_id: str = ""
    ) -> str:
        """
        도구 실행 (Registry를 통해 플러그인 실행)

        Args:
            tool_name: LLM이 호출한 함수 이름 (예: 'get_current_weather')
            arguments: 함수 인자
            user_id: 사용자 ID (리마인더용)

        Returns:
            도구 실행 결과 문자열
        """
        logger.info(f"도구 실행: {tool_name}({arguments})")

        try:
            # 리마인더는 별도 처리 (플러그인이 아님)
            if tool_name == "set_reminder":
                minutes_raw = arguments.get("minutes", "1")
                try:
                    minutes_int = int(minutes_raw)
                    if minutes_int <= 0 or minutes_int > 1440:
                        return "⚠️ 알림 시간은 1분에서 24시간 사이로 설정해주세요."
                except (ValueError, TypeError):
                    minutes_int = 1
                return self._set_reminder(
                    user_id=user_id,
                    minutes=minutes_int,
                    message=arguments.get("message", "알림"),
                )

            # Registry를 통해 플러그인 찾기
            plugin_name = TOOL_FUNCTION_TO_PLUGIN.get(tool_name)
            if not plugin_name:
                return f"알 수 없는 도구: {tool_name}"

            plugin = self.registry.get(plugin_name)
            if not plugin:
                return f"{plugin_name} 서비스가 설정되지 않았습니다."

            # 플러그인 execute 호출
            result = await plugin.execute(function_name=tool_name, **arguments)

            # 결과 포맷팅
            if isinstance(result, dict):
                if result.get("success"):
                    return result.get("message", str(result))
                else:
                    return f"😅 {result.get('error', '알 수 없는 오류')}"
            return str(result)

        except Exception as e:
            logger.error(f"도구 실행 오류: {e}", exc_info=True)
            return "😅 죄송해요, 요청을 처리하는 중 문제가 발생했어요. 다시 시도해주세요."

    def _set_reminder(self, user_id: str, minutes: int, message: str) -> str:
        """
        리마인더 설정

        Args:
            user_id: 사용자 ID
            minutes: 몇 분 후에 알림
            message: 알림 메시지

        Returns:
            설정 결과 메시지
        """
        if not self._scheduler or not self._send_message:
            return "알림 기능이 설정되지 않았습니다."

        # 실행 시간 계산
        run_time = datetime.now() + timedelta(minutes=minutes)
        self._reminder_count += 1
        job_id = f"reminder_{user_id}_{self._reminder_count}"

        # 알림 발송 함수 생성
        def send_reminder():
            logger.info(f"📢 리마인더 발송: {user_id} - {message}")
            reminder_text = f"⏰ 리마인더: {message}"
            if self._send_message:
                self._send_message(user_id, reminder_text)

        # 스케줄러에 작업 등록
        self._scheduler.add_date_job(
            job_id=job_id,
            func=send_reminder,
            run_date=run_time,
        )

        logger.info(f"리마인더 설정: {job_id} → {run_time}")
        return (
            f"알림이 설정되었습니다. {minutes}분 후({run_time.strftime('%H:%M')})에 알려드릴게요!"
        )

    def _get_schedule(self, date_str: str) -> str:
        """
        일정 조회

        Args:
            date_str: 날짜 문자열 ("today", "tomorrow", "2025-01-15")

        Returns:
            일정 목록 문자열
        """
        try:
            # 날짜 파싱
            if date_str.lower() == "today":
                schedules = self.calendar.get_today_schedules()
                date_label = "오늘"
            elif date_str.lower() == "tomorrow":
                schedules = self.calendar.get_tomorrow_schedules()
                date_label = "내일"
            else:
                # YYYY-MM-DD 형식
                target_date = datetime.strptime(date_str, "%Y-%m-%d")
                schedules = self.calendar.get_schedules_by_date(target_date)
                date_label = target_date.strftime("%m월 %d일")

            if not schedules:
                return f"{date_label} 일정이 없습니다."

            formatted = self.calendar.format_schedule_list(schedules)
            return f"📅 {date_label} 일정:\n{formatted}"

        except Exception as e:
            logger.error(f"일정 조회 실패: {e}")
            return "일정을 조회하는 중 오류가 발생했습니다."

    def _add_schedule(self, title: str, date_str: str, time_str: str, location: str = "") -> str:
        """
        일정 추가

        Args:
            title: 일정 제목
            date_str: 날짜 문자열 ("today", "tomorrow", "2025-01-15")
            time_str: 시간 문자열 ("14:00", "오후 2시")
            location: 장소 (선택)

        Returns:
            결과 메시지
        """
        try:
            # 날짜 파싱
            if date_str.lower() == "today":
                target_date = datetime.now()
            elif date_str.lower() == "tomorrow":
                target_date = datetime.now() + timedelta(days=1)
            else:
                target_date = datetime.strptime(date_str, "%Y-%m-%d")

            # 시간 파싱 (간단한 버전)
            time_str_clean = time_str.replace("오후", "PM").replace("오전", "AM")
            time_str_clean = time_str_clean.replace("시", ":").replace(" ", "")

            # HH:MM 형식으로 변환
            hour_int: int
            minute_int: int
            if ":" in time_str_clean:
                hour_str, minute_str = time_str_clean.split(":")[:2]
                if "PM" in time_str_clean and int(hour_str) < 12:
                    hour_int = int(hour_str) + 12
                else:
                    hour_int = int(hour_str)
                minute_int = int(minute_str) if minute_str else 0
            else:
                # 숫자만 있는 경우
                hour_int = int(time_str_clean.replace("PM", "").replace("AM", ""))
                if "PM" in time_str_clean and hour_int < 12:
                    hour_int += 12
                minute_int = 0

            # 시작 시간 생성
            start_time = target_date.replace(
                hour=hour_int, minute=minute_int, second=0, microsecond=0
            )

            # 일정 추가
            self.calendar.add_schedule(
                title=title,
                start_time=start_time,
                location=location,
            )

            logger.info(f"일정 추가 완료: {title} @ {start_time}")
            return f"✅ 일정이 추가되었습니다: {title} ({start_time.strftime('%m월 %d일 %H:%M')})"

        except Exception as e:
            logger.error(f"일정 추가 실패: {e}")
            return f"일정을 추가하는 중 오류가 발생했습니다: {e}"

    async def chat(self, user_id: str, message: str) -> str:
        """
        사용자와 대화 (Tool Calling 지원)

        Args:
            user_id: 사용자 ID
            message: 사용자 메시지

        Returns:
            AI 응답
        """
        # 사용자 메시지를 히스토리에 추가
        self.conversation.add_message(user_id, "user", message)

        # 대화 기록 가져오기
        history = self.conversation.get_history(user_id)

        try:
            # LLM에게 요청 (Tool Calling 포함)
            response = await self.llm.chat_with_tools(
                messages=history,
                system_prompt=self.system_prompt,
                tools=self.tools if self.tools else None,
            )

            # Tool Call이 있는 경우 처리
            if response.get("tool_calls"):
                tool_results = []

                for tool_call in response["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    arguments = json.loads(tool_call["function"]["arguments"])

                    # 도구 실행 (user_id 전달)
                    result = await self._execute_tool(tool_name, arguments, user_id)
                    tool_results.append(
                        {
                            "tool_call_id": tool_call["id"],
                            "role": "tool",
                            "content": result,
                        }
                    )

                # 도구 결과를 포함하여 다시 LLM 호출
                final_response = await self.llm.chat_with_tool_results(
                    messages=history,
                    assistant_message=response,
                    tool_results=tool_results,
                    system_prompt=self.system_prompt,
                )
                content = final_response

            else:
                # 일반 응답
                content = response.get("content", "")

            # AI 응답을 히스토리에 추가
            self.conversation.add_message(user_id, "assistant", content)

            logger.info(f"AI 응답 생성 완료: {user_id}")
            return content

        except Exception as e:
            logger.error(f"AI 응답 생성 실패: {e}")
            # 오류 시 히스토리에서 마지막 메시지 제거
            history = self.conversation.get_history(user_id)
            if history:
                self.conversation._histories[user_id] = history[:-1]
            return "죄송해요, 일시적인 오류가 발생했어요. 😅 잠시 후 다시 시도해주세요."

    def clear_history(self, user_id: str) -> None:
        """사용자 대화 기록 초기화"""
        self.conversation.clear_history(user_id)
        logger.info(f"대화 기록 초기화: {user_id}")
