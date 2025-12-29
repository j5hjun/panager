"""
Settings 설정 클래스 테스트

TDD RED Phase: 이 테스트들은 Settings 클래스가 구현되기 전에 작성되었으며,
처음에는 모두 실패해야 합니다.
"""

import os
from unittest.mock import patch

import pytest


class TestSettings:
    """Settings 클래스 테스트"""

    def test_settings_loads_from_environment_variables(self):
        """환경 변수에서 설정을 로드할 수 있어야 함"""
        # Given: 환경 변수가 설정됨
        env_vars = {
            "SLACK_BOT_TOKEN": "xoxb-test-token",
            "SLACK_APP_TOKEN": "xapp-test-token",
            "OPENAI_API_KEY": "sk-test-key",
            "OPENWEATHERMAP_API_KEY": "test-weather-key",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # When: Settings를 생성
            from src.config.settings import Settings

            settings = Settings()

            # Then: 환경 변수 값이 로드됨
            assert settings.slack_bot_token == "xoxb-test-token"
            assert settings.slack_app_token == "xapp-test-token"
            assert settings.openai_api_key == "sk-test-key"
            assert settings.openweathermap_api_key == "test-weather-key"

    def test_settings_raises_error_when_required_fields_missing(self):
        """필수 설정이 누락되면 에러가 발생해야 함"""
        from pydantic import ValidationError
        from src.config.settings import Settings

        # Given: 필수 환경 변수가 없음 (clear=True로 모든 환경변수 제거)
        with patch.dict(os.environ, {}, clear=True):
            # When/Then: Settings 생성 시 ValidationError 발생
            # _env_file=None으로 .env 파일 로드도 차단
            with pytest.raises(ValidationError):
                Settings(_env_file=None)

    def test_settings_has_default_values(self):
        """기본값이 있는 설정은 환경 변수 없이도 기본값 사용"""
        # Given: 필수 설정만 있고 선택적 설정은 없음
        env_vars = {
            "SLACK_BOT_TOKEN": "xoxb-test-token",
            "SLACK_APP_TOKEN": "xapp-test-token",
            "OPENAI_API_KEY": "sk-test-key",
            "OPENWEATHERMAP_API_KEY": "test-weather-key",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # When: Settings 생성
            from src.config.settings import Settings

            settings = Settings()

            # Then: 기본값이 적용됨
            assert settings.llm_model == "llama-3.3-70b-versatile"  # Groq 기본 모델
            assert settings.llm_provider == "groq"
            assert settings.default_city == "Seoul"
            assert settings.log_level == "INFO"

    def test_settings_can_override_defaults(self):
        """기본값을 환경 변수로 오버라이드할 수 있어야 함"""
        # Given: 기본값을 오버라이드하는 환경 변수
        env_vars = {
            "SLACK_BOT_TOKEN": "xoxb-test-token",
            "SLACK_APP_TOKEN": "xapp-test-token",
            "OPENAI_API_KEY": "sk-test-key",
            "OPENWEATHERMAP_API_KEY": "test-weather-key",
            "LLM_MODEL": "gpt-4",
            "LLM_PROVIDER": "openai",
            "DEFAULT_CITY": "Busan",
            "LOG_LEVEL": "DEBUG",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # When: Settings 생성
            from src.config.settings import Settings

            settings = Settings()

            # Then: 오버라이드된 값 사용
            assert settings.llm_model == "gpt-4"
            assert settings.llm_provider == "openai"
            assert settings.default_city == "Busan"
            assert settings.log_level == "DEBUG"

    def test_settings_assistant_name_default(self):
        """AI 비서 이름 기본값은 '패니저'"""
        env_vars = {
            "SLACK_BOT_TOKEN": "xoxb-test-token",
            "SLACK_APP_TOKEN": "xapp-test-token",
            "OPENAI_API_KEY": "sk-test-key",
            "OPENWEATHERMAP_API_KEY": "test-weather-key",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            from src.config.settings import Settings

            settings = Settings()

            assert settings.assistant_name == "패니저"

    def test_settings_groq_base_url(self):
        """Groq 사용 시 올바른 base_url 반환"""
        env_vars = {
            "SLACK_BOT_TOKEN": "xoxb-test-token",
            "SLACK_APP_TOKEN": "xapp-test-token",
            "OPENAI_API_KEY": "sk-test-key",
            "OPENWEATHERMAP_API_KEY": "test-weather-key",
            "LLM_PROVIDER": "groq",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            from src.config.settings import Settings

            settings = Settings()

            assert settings.llm_base_url == "https://api.groq.com/openai/v1"

    def test_settings_openai_base_url(self):
        """OpenAI 사용 시 올바른 base_url 반환"""
        env_vars = {
            "SLACK_BOT_TOKEN": "xoxb-test-token",
            "SLACK_APP_TOKEN": "xapp-test-token",
            "OPENAI_API_KEY": "sk-test-key",
            "OPENWEATHERMAP_API_KEY": "test-weather-key",
            "LLM_PROVIDER": "openai",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            from src.config.settings import Settings

            settings = Settings()

            assert settings.llm_base_url == "https://api.openai.com/v1"
