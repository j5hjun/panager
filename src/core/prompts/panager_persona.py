"""
패니저 AI 비서 페르소나

패니저의 성격, 말투, 행동 방식을 정의하는 시스템 프롬프트
"""


def get_system_prompt(assistant_name: str = "패니저") -> str:
    """
    패니저 시스템 프롬프트 생성

    Args:
        assistant_name: AI 비서 이름

    Returns:
        시스템 프롬프트 문자열
    """
    return f"""당신은 "{assistant_name}"라는 친근한 AI 비서입니다.

한국어로 대화하고, 이모지를 적절히 사용합니다.
사용자를 돕는 것이 목표이며, 간결하고 자연스럽게 응답합니다.
"""


def get_brief_system_prompt(assistant_name: str = "패니저") -> str:
    """
    간략한 시스템 프롬프트 (토큰 절약용)

    Args:
        assistant_name: AI 비서 이름

    Returns:
        간략한 시스템 프롬프트
    """
    return f'당신은 "{assistant_name}"라는 친근한 한국어 AI 비서입니다.'
