"""
ConversationRepository 테스트

대화 기록을 SQLite에 저장하는 기능을 테스트합니다.
"""

import pytest
from src.core.autonomous.memory.conversation_repository import ConversationRepository


class TestConversationRepository:
    """ConversationRepository 테스트"""

    @pytest.fixture
    def repository(self):
        """테스트용 인메모리 Repository"""
        repo = ConversationRepository(db_path=":memory:")
        yield repo
        repo.close()

    def test_save_message(self, repository):
        """메시지 저장 테스트"""
        repository.add_message(
            user_id="U12345",
            role="user",
            content="안녕하세요, 제 이름은 준호입니다.",
        )

        history = repository.get_history("U12345")
        assert len(history) == 1
        assert history[0]["role"] == "user"
        assert "준호" in history[0]["content"]

    def test_get_history(self, repository):
        """대화 기록 조회 테스트"""
        repository.add_message("U12345", "user", "안녕!")
        repository.add_message("U12345", "assistant", "안녕하세요!")
        repository.add_message("U12345", "user", "날씨 어때?")

        history = repository.get_history("U12345")

        assert len(history) == 3
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"
        assert history[2]["role"] == "user"

    def test_get_history_with_limit(self, repository):
        """대화 기록 조회 (제한) 테스트"""
        for i in range(30):
            repository.add_message("U12345", "user", f"메시지 {i}")

        # 기본 20개 제한
        history = repository.get_history("U12345", limit=20)

        assert len(history) == 20
        # 최신 20개 반환
        assert "메시지 10" in history[0]["content"]

    def test_clear_history(self, repository):
        """대화 기록 초기화 테스트"""
        repository.add_message("U12345", "user", "테스트")
        repository.add_message("U12345", "assistant", "응답")

        repository.clear_history("U12345")

        history = repository.get_history("U12345")
        assert len(history) == 0

    def test_separate_users(self, repository):
        """사용자별 분리 저장 테스트"""
        repository.add_message("U111", "user", "사용자 1 메시지")
        repository.add_message("U222", "user", "사용자 2 메시지")

        history1 = repository.get_history("U111")
        history2 = repository.get_history("U222")

        assert len(history1) == 1
        assert len(history2) == 1
        assert "사용자 1" in history1[0]["content"]
        assert "사용자 2" in history2[0]["content"]

    def test_get_all_users(self, repository):
        """모든 사용자 ID 조회 테스트"""
        repository.add_message("U111", "user", "1")
        repository.add_message("U222", "user", "2")
        repository.add_message("U333", "user", "3")

        users = repository.get_all_users()

        assert len(users) == 3
        assert "U111" in users
        assert "U222" in users
        assert "U333" in users
