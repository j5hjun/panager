from datetime import datetime, timezone
from pydantic import BaseModel

class Token(BaseModel):
    user_slack_id: str
    access_token: str
    refresh_token: str
    expires_at: datetime
    token_type: str = "Bearer"
    scope: str = ""

    def is_expired(self) -> bool:
        """현재 시간 기준으로 토큰 만료 여부 반환 (UTC 기준)"""
        now = datetime.now(timezone.utc)
        # expires_at이 timezone 정보가 없다면 UTC로 가정
        if self.expires_at.tzinfo is None:
            return self.expires_at.replace(tzinfo=timezone.utc) < now
        return self.expires_at < now
