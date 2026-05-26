from __future__ import annotations

import json
from datetime import datetime
from zoneinfo import ZoneInfo

from rich.console import Console
from rich.table import Table


class OutputRenderer:
    def __init__(self, mode: str = "interactive", timezone_name: str = "America/Indianapolis") -> None:
        self.mode = mode
        self.timezone_name = timezone_name
        self.timezone = ZoneInfo(timezone_name)
        self.console = Console(width=200)

    def render_events(self, rows) -> None:
        if self.mode == "json":
            print(
                json.dumps(
                    [self._localize_row(row.model_dump()) for row in rows],
                    separators=(",", ":"),
                )
            )
            return
        table = Table(title="Agenda")
        table.add_column("Start")
        table.add_column("End")
        table.add_column("Subject")
        table.add_column("Location")
        for row in rows:
            table.add_row(
                self._format_local(row.start_at),
                self._format_local(row.end_at),
                row.subject,
                row.location or "",
            )
        self.console.print(table)

    def _localize_row(self, row: dict) -> dict:
        row["start_at"] = self._format_local(row["start_at"])
        row["end_at"] = self._format_local(row["end_at"])
        row["timezone"] = self.timezone_name
        return row

    def _format_local(self, value: str) -> str:
        if not value:
            return ""
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=ZoneInfo("UTC"))
        return parsed.astimezone(self.timezone).isoformat()
