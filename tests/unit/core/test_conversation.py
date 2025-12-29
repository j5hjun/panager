"""
대화 로직 테스트
"""


class TestConversationLogic:
    """대화 로직 통합 테스트"""

    def test_conversation_module_exists(self):
        """대화 모듈이 존재해야 함"""
        from src.core.logic import conversation

        assert conversation is not None
