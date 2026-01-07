from datetime import datetime
from typing import Optional
from pydantic import BaseModel, model_validator

class CalendarEvent(BaseModel):
    id: str  # Google Calendar Event ID
    summary: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: datetime
    end_time: datetime
    status: str = "confirmed"  # confirmed, tentative, cancelled

    @model_validator(mode='after')
    def check_dates(self):
        if self.end_time < self.start_time:
            raise ValueError('end_time must be after start_time')
        return self
