"""
애플리케이션 설정 관리

pydantic-settings를 활용하여 환경 변수에서 설정을 로드합니다.
"""

from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    애플리케이션 전역 설정

    환경 변수 또는 .env 파일에서 설정을 로드합니다.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # 알 수 없는 환경 변수 무시
    )

    # ==================== Slack 설정 (필수) ====================
    slack_bot_token: str = Field(description="Slack Bot User OAuth Token (xoxb-...)")
    slack_app_token: str = Field(description="Slack App-Level Token (xapp-...)")
    slack_channel_id: str = Field(default="", description="알림을 보낼 기본 채널 ID (C... 형태)")

    # ==================== LLM 설정 ====================
    openai_api_key: str = Field(description="OpenAI 또는 Groq API Key")
    llm_provider: Literal["groq", "openai"] = Field(
        default="groq", description="LLM 제공자 (groq 또는 openai)"
    )
    llm_model: str = Field(default="llama-3.3-70b-versatile", description="사용할 LLM 모델명")

    # ==================== 날씨 API 설정 ====================
    kma_api_key: str = Field(default="", description="기상청 공공데이터포털 API Key")
    default_city: str = Field(default="Seoul", description="기본 도시명")

    # ==================== Kakao Maps API 설정 ====================
    kakao_rest_api_key: str = Field(default="", description="Kakao REST API Key (길찾기용)")

    # ==================== AI 비서 설정 ====================
    assistant_name: str = Field(default="패니저", description="AI 비서 이름")

    # ==================== 앱 설정 ====================
    log_level: str = Field(default="INFO", description="로깅 레벨 (DEBUG, INFO, WARNING, ERROR)")
    timezone: str = Field(default="Asia/Seoul", description="기본 타임존")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def llm_base_url(self) -> str:
        """LLM 제공자에 따른 API Base URL 반환"""
        if self.llm_provider == "groq":
            return "https://api.groq.com/openai/v1"
        elif self.llm_provider == "openai":
            return "https://api.openai.com/v1"
        else:
            raise ValueError(f"Unknown LLM provider: {self.llm_provider}")


# 싱글톤 인스턴스 (lazy loading)
_settings: Settings | None = None


def get_settings() -> Settings:
    """Settings 싱글톤 인스턴스 반환"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
