"""
프롬프트 모듈

자율 판단 시스템에서 사용하는 프롬프트 템플릿을 정의합니다.
"""

from src.core.autonomous.prompts.reflect import REFLECT_PROMPT
from src.core.autonomous.prompts.think import THINK_PROMPT

__all__ = ["THINK_PROMPT", "REFLECT_PROMPT"]
