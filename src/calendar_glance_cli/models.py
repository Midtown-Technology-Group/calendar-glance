from __future__ import annotations

from pydantic import BaseModel


class CalendarEvent(BaseModel):
    id: str
    subject: str
    start_at: str
    end_at: str
    location: str | None = None
    organizer: str | None = None
    web_link: str | None = None
    is_all_day: bool = False
