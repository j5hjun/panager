from datetime import datetime, timedelta, timezone
from src.domain.models.token import Token

def test_token_is_expired():
    # 과거 시간 설정
    past = datetime.now(timezone.utc) - timedelta(hours=1)
    token = Token(
        access_token="acc",
        refresh_token="ref",
        expires_at=past,
        user_slack_id="U1"
    )
    assert token.is_expired() is True

def test_token_is_not_expired():
    # 미래 시간 설정
    future = datetime.now(timezone.utc) + timedelta(hours=1)
    token = Token(
        access_token="acc",
        refresh_token="ref",
        expires_at=future,
        user_slack_id="U1"
    )
    assert token.is_expired() is False
