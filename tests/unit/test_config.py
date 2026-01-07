import os
from src.config.settings import Settings

def test_settings_load_from_env():
    # Arrange: 환경변수 설정 (테스트용)
    os.environ["SLACK_BOT_TOKEN"] = "xoxb-test-token"
    os.environ["SLACK_APP_TOKEN"] = "xapp-test-token"
    os.environ["OPENAI_API_KEY"] = "sk-test-key"
    
    # Act
    settings = Settings()
    
    # Assert
    assert settings.slack_bot_token == "xoxb-test-token"
    assert settings.slack_app_token == "xapp-test-token"
    assert settings.openai_api_key == "sk-test-key"
    assert settings.env == "development"  # 기본값 확인

def test_settings_validation():
    # 필수값이 없을 때 에러 발생하는지 등 (여기서는 생략하고 기본 로딩만 확인)
    pass
