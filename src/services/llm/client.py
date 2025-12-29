"""
LLM 클라이언트

OpenAI SDK를 사용하여 Groq/OpenAI API와 통신합니다.
Tool Calling을 지원합니다.
"""

import logging
from typing import Any

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class LLMClient:
    """
    LLM API 클라이언트

    OpenAI SDK를 사용하여 Groq 또는 OpenAI와 통신합니다.
    Tool Calling을 지원합니다.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
    ):
        """
        LLMClient 초기화

        Args:
            api_key: API 키
            base_url: API 베이스 URL
            model: 사용할 모델명
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

        # OpenAI 클라이언트 초기화 (Groq도 동일한 API 사용)
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        logger.info(f"LLMClient 초기화 완료: {model} @ {base_url}")

    async def chat(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """
        LLM과 대화

        Args:
            messages: 대화 메시지 목록 [{"role": "user", "content": "..."}]
            system_prompt: 시스템 프롬프트 (선택)
            temperature: 응답 다양성 (0.0 ~ 1.0)
            max_tokens: 최대 토큰 수

        Returns:
            LLM 응답 텍스트
        """
        # 메시지 준비
        chat_messages: list[dict[str, Any]] = []

        # 시스템 프롬프트 추가
        if system_prompt:
            chat_messages.append({"role": "system", "content": system_prompt})

        # 사용자 메시지 추가
        chat_messages.extend(messages)

        logger.debug(f"LLM 요청: {len(chat_messages)} 메시지, model={self.model}")

        try:
            response = await self._client.chat.completions.create(
                model=self.model,
                messages=chat_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            content = response.choices[0].message.content or ""
            logger.debug(f"LLM 응답: {content[:100]}...")

            return content

        except Exception as e:
            logger.error(f"LLM API 오류: {e}")
            raise

    async def chat_with_tools(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> dict[str, Any]:
        """
        Tool Calling을 지원하는 LLM 대화

        Args:
            messages: 대화 메시지 목록
            system_prompt: 시스템 프롬프트
            tools: 사용 가능한 도구 정의 목록
            temperature: 응답 다양성
            max_tokens: 최대 토큰 수

        Returns:
            {"content": str, "tool_calls": list | None}
        """
        # 메시지 준비
        chat_messages: list[dict[str, Any]] = []

        if system_prompt:
            chat_messages.append({"role": "system", "content": system_prompt})

        chat_messages.extend(messages)

        logger.debug(f"LLM 요청 (with tools): {len(chat_messages)} 메시지")

        try:
            # Tool Calling 요청
            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": chat_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = await self._client.chat.completions.create(**kwargs)

            message = response.choices[0].message

            result: dict[str, Any] = {
                "content": message.content or "",
                "tool_calls": None,
            }

            # Tool Calls가 있으면 포함
            if message.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ]
                logger.info(
                    f"Tool calls: {[tc['function']['name'] for tc in result['tool_calls']]}"
                )

            return result

        except Exception as e:
            logger.error(f"LLM API 오류 (with tools): {e}")
            raise

    async def chat_with_tool_results(
        self,
        messages: list[dict[str, str]],
        assistant_message: dict[str, Any],
        tool_results: list[dict[str, Any]],
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """
        도구 실행 결과를 포함하여 최종 응답 생성

        Args:
            messages: 원래 대화 메시지
            assistant_message: 도구 호출이 포함된 assistant 메시지
            tool_results: 도구 실행 결과 목록
            system_prompt: 시스템 프롬프트

        Returns:
            최종 LLM 응답 텍스트
        """
        # 메시지 준비
        chat_messages: list[dict[str, Any]] = []

        if system_prompt:
            chat_messages.append({"role": "system", "content": system_prompt})

        chat_messages.extend(messages)

        # Assistant의 tool_calls 메시지 추가
        assistant_msg: dict[str, Any] = {
            "role": "assistant",
            "content": assistant_message.get("content") or "",
        }
        if assistant_message.get("tool_calls"):
            assistant_msg["tool_calls"] = assistant_message["tool_calls"]
        chat_messages.append(assistant_msg)

        # 도구 결과 메시지 추가
        for result in tool_results:
            chat_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": result["tool_call_id"],
                    "content": result["content"],
                }
            )

        logger.debug(f"LLM 요청 (with tool results): {len(chat_messages)} 메시지")

        try:
            response = await self._client.chat.completions.create(
                model=self.model,
                messages=chat_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            content = response.choices[0].message.content or ""
            logger.debug(f"LLM 최종 응답: {content[:100]}...")

            return content

        except Exception as e:
            logger.error(f"LLM API 오류 (with tool results): {e}")
            raise

    async def chat_with_history(
        self,
        user_message: str,
        history: list[dict[str, str]],
        system_prompt: str | None = None,
    ) -> str:
        """
        대화 기록을 포함하여 LLM과 대화

        Args:
            user_message: 사용자 메시지
            history: 이전 대화 기록
            system_prompt: 시스템 프롬프트

        Returns:
            LLM 응답 텍스트
        """
        messages = history + [{"role": "user", "content": user_message}]
        return await self.chat(messages, system_prompt)
