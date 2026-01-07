from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App
    env: str = "development"
    debug: bool = True
    
    # Slack
    slack_bot_token: str = ""
    slack_app_token: str = ""
    
    # LLM
    openai_api_key: str = ""
    google_api_key: str = ""

    # Config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # 정의되지 않은 환경변수는 무시
    )
