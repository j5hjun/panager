"""
LLM 서비스 테스트

TDD RED Phase: LLM 서비스가 구현되기 전에 작성된 테스트
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestLLMClient:
    """LLM 클라이언트 테스트"""

    def test_llm_client_can_be_imported(self):
        """LLMClient 클래스를 import할 수 있어야 함"""
        from src.services.llm.client import LLMClient

        assert LLMClient is not None

    def test_llm_client_initialization(self):
        """LLMClient를 초기화할 수 있어야 함"""
        from src.services.llm.client import LLMClient

        client = LLMClient(
            api_key="test-api-key",
            base_url="https://api.groq.com/openai/v1",
            model="llama-3.3-70b-versatile",
        )

        assert client is not None
        assert client.model == "llama-3.3-70b-versatile"

    @pytest.mark.asyncio
    async def test_llm_client_chat_completion(self):
        """LLM에게 메시지를 보내고 응답을 받을 수 있어야 함"""
        from src.services.llm.client import LLMClient

        client = LLMClient(
            api_key="test-api-key",
            base_url="https://api.groq.com/openai/v1",
            model="llama-3.3-70b-versatile",
        )

        # Mock the OpenAI client
        with patch.object(client, "_client") as mock_client:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "안녕하세요! 반갑습니다."
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            response = await client.chat(messages=[{"role": "user", "content": "안녕"}])

            assert response == "안녕하세요! 반갑습니다."

    @pytest.mark.asyncio
    async def test_llm_client_with_system_prompt(self):
        """시스템 프롬프트와 함께 대화할 수 있어야 함"""
        from src.services.llm.client import LLMClient

        client = LLMClient(
            api_key="test-api-key",
            base_url="https://api.groq.com/openai/v1",
            model="llama-3.3-70b-versatile",
        )

        with patch.object(client, "_client") as mock_client:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "저는 패니저입니다!"
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            response = await client.chat(
                messages=[{"role": "user", "content": "넌 누구야?"}],
                system_prompt="너는 패니저라는 AI 비서야.",
            )

            assert "패니저" in response


class TestConversationManager:
    """대화 관리자 테스트"""

    def test_conversation_manager_can_be_imported(self):
        """ConversationManager 클래스를 import할 수 있어야 함"""
        from src.core.logic.conversation import ConversationManager

        assert ConversationManager is not None

    def test_conversation_manager_add_message(self):
        """대화에 메시지를 추가할 수 있어야 함"""
        from src.core.logic.conversation import ConversationManager

        manager = ConversationManager()

        manager.add_message("user123", "user", "안녕하세요")
        manager.add_message("user123", "assistant", "안녕하세요! 반갑습니다.")

        history = manager.get_history("user123")
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "안녕하세요"

    def test_conversation_manager_separate_users(self):
        """사용자별로 대화가 분리되어야 함"""
        from src.core.logic.conversation import ConversationManager

        manager = ConversationManager()

        manager.add_message("user1", "user", "안녕")
        manager.add_message("user2", "user", "반가워")

        assert len(manager.get_history("user1")) == 1
        assert len(manager.get_history("user2")) == 1
        assert manager.get_history("user1")[0]["content"] == "안녕"
        assert manager.get_history("user2")[0]["content"] == "반가워"

    def test_conversation_manager_max_history(self):
        """대화 기록이 최대 길이를 초과하면 오래된 것부터 삭제"""
        from src.core.logic.conversation import ConversationManager

        manager = ConversationManager(max_history=4)

        for i in range(10):
            manager.add_message("user1", "user", f"메시지 {i}")

        history = manager.get_history("user1")
        assert len(history) == 4
        assert history[0]["content"] == "메시지 6"  # 가장 오래된 것은 삭제됨

    def test_conversation_manager_clear_history(self):
        """대화 기록을 초기화할 수 있어야 함"""
        from src.core.logic.conversation import ConversationManager

        manager = ConversationManager()

        manager.add_message("user1", "user", "안녕")
        manager.clear_history("user1")

        assert len(manager.get_history("user1")) == 0


class TestPanizerPersona:
    """패니저 페르소나 테스트"""

    def test_persona_prompt_can_be_imported(self):
        """패니저 시스템 프롬프트를 import할 수 있어야 함"""
        from src.core.prompts.panager_persona import get_system_prompt

        prompt = get_system_prompt()
        assert prompt is not None
        assert "패니저" in prompt

    def test_persona_prompt_includes_key_characteristics(self):
        """페르소나 프롬프트에 핵심 특성이 포함되어야 함"""
        from src.core.prompts.panager_persona import get_system_prompt

        prompt = get_system_prompt()

        # 핵심 특성 확인
        assert "패니저" in prompt
        assert len(prompt) > 50  # 기본적인 내용이 있어야 함
