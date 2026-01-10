from pydantic import BaseModel, Field
from typing import Dict, Any

class User(BaseModel):
    id: int | None = None  # DB PK (Optional)
    slack_id: str
    name: str = "Unknown"
    is_active: bool = True
    preferences: Dict[str, Any] = Field(default_factory=dict)
