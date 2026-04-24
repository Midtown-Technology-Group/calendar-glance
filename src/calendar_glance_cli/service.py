from __future__ import annotations


class CalendarGlanceService:
    def __init__(self, repo) -> None:
        self.repo = repo

    def agenda(self, days: int, limit: int, calendar_name: str | None = None):
        return self.repo.agenda(days=days, limit=limit, calendar_name=calendar_name)
