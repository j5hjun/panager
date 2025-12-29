"""
LLM Tool Definitions

LLM Tool Calling에서 사용할 도구 정의
"""

from typing import Any

# OpenAI/Groq Tool Calling 형식의 도구 정의
WEATHER_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "지정된 도시의 현재 날씨를 조회합니다. 기온, 습도, 날씨 상태, 우산 필요 여부 등을 알려줍니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "날씨를 조회할 도시명 (예: Seoul, Busan, Tokyo). 영문으로 입력해야 합니다.",
                    }
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_umbrella",
            "description": "지정된 도시에 우산이 필요한지 확인합니다. 비나 눈 예보가 있을 때 우산을 챙기라고 알려줍니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "확인할 도시명 (예: Seoul, Busan). 영문으로 입력해야 합니다.",
                    }
                },
                "required": ["city"],
            },
        },
    },
]

REMINDER_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "set_reminder",
            "description": "지정된 시간 후에 알림을 설정합니다. 사용자가 '5분 후 알림', '1시간 후 알려줘' 등을 요청할 때 사용합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "minutes": {
                        "type": "string",
                        "description": "몇 분 후에 알림을 보낼지 (예: '5', '30', '60')",
                    },
                    "message": {
                        "type": "string",
                        "description": "알림에 포함할 메시지 내용",
                    },
                },
                "required": ["minutes", "message"],
            },
        },
    },
]

CALENDAR_TOOLS: list[dict[str, Any]] = [
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


def get_all_tools() -> list[dict[str, Any]]:
    """모든 도구 정의 반환"""
    return WEATHER_TOOLS + REMINDER_TOOLS + CALENDAR_TOOLS


def get_tool_names() -> list[str]:
    """도구 이름 목록 반환"""
    all_tools = get_all_tools()
    return [tool["function"]["name"] for tool in all_tools]
