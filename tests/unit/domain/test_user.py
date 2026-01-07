import pytest
from pydantic import ValidationError
from src.domain.models.user import User

def test_user_creation():
    user = User(slack_id="U123456", name="Tester")
    assert user.slack_id == "U123456"
    assert user.is_active is True
    assert user.preferences == {}

def test_user_creation_validation_error():
    # slack_id는 필수
    with pytest.raises(ValidationError):
        User(name="Tester")

def test_user_update_preferences():
    user = User(slack_id="U1", name="Tester")
    user.preferences["alert_time"] = "09:00"
    assert user.preferences["alert_time"] == "09:00"
