from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App
    env: str = "development"
    debug: bool = True
    
    # Slack
    slack_bot_token: str = ""
    slack_app_token: str = ""
    slack_signing_secret: str = ""
    
    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"
    
    # LLM
    openai_api_key: str = ""
    google_api_key: str = ""
    
    # Infrastructure
    redis_url: str = "redis://localhost:6379"

    # Database
    db_url: str = "postgresql+asyncpg://panager:password@localhost:5432/panager_dev"

    # Config
    model_config = SettingsConfigDict(
        env_file=(".env.local", ".env"),  # .env.local 우선
        env_file_encoding="utf-8",
        extra="ignore"  # 정의되지 않은 환경변수는 무시
    )
