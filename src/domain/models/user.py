from pydantic import BaseModel, Field
from typing import Dict, Any

class User(BaseModel):
    slack_id: str
    name: str = "Unknown"
    is_active: bool = True
    preferences: Dict[str, Any] = Field(default_factory=dict)
