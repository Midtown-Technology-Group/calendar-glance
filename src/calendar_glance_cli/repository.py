from __future__ import annotations

from datetime import datetime, timedelta, timezone

from calendar_glance_cli.models import CalendarEvent


class CalendarRepository:
    def __init__(self, client) -> None:
        self.client = client

    def agenda(self, days: int, limit: int, calendar_name: str | None = None) -> list[CalendarEvent]:
        calendar_id = self._resolve_calendar_id(calendar_name)
        start = datetime.now(timezone.utc)
        end = start + timedelta(days=days)
        params = {
            "startDateTime": start.isoformat(),
            "endDateTime": end.isoformat(),
            "$top": limit,
            "$orderby": "start/dateTime",
        }
        path = f"/me/calendars/{calendar_id}/calendarView" if calendar_id else "/me/calendarView"
        payload = self.client.get(path, params=params)
        return self._parse_events(payload.get("value", []))

    def _resolve_calendar_id(self, calendar_name: str | None) -> str | None:
        if not calendar_name:
            return None
        payload = self.client.get("/me/calendars", params={"$select": "id,name"})
        for row in payload.get("value", []):
            if (row.get("name") or "").lower() == calendar_name.lower():
                return row["id"]
        raise ValueError(f"Calendar '{calendar_name}' was not found.")

    def _parse_events(self, rows: list[dict]) -> list[CalendarEvent]:
        events = []
        for row in rows:
            location = (row.get("location") or {}).get("displayName")
            organizer = ((row.get("organizer") or {}).get("emailAddress") or {}).get("name")
            events.append(
                CalendarEvent(
                    id=row["id"],
                    subject=row.get("subject") or "(no subject)",
                    start_at=((row.get("start") or {}).get("dateTime")) or "",
                    end_at=((row.get("end") or {}).get("dateTime")) or "",
                    location=location,
                    organizer=organizer,
                    web_link=row.get("webLink"),
                    is_all_day=bool(row.get("isAllDay", False)),
                )
            )
        return events
