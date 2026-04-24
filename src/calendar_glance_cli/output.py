from __future__ import annotations

import json

from rich.console import Console
from rich.table import Table


class OutputRenderer:
    def __init__(self, mode: str = "interactive") -> None:
        self.mode = mode
        self.console = Console(width=200)

    def render_events(self, rows) -> None:
        if self.mode == "json":
            print(json.dumps([row.model_dump() for row in rows], separators=(",", ":")))
            return
        table = Table(title="Agenda")
        table.add_column("Start")
        table.add_column("End")
        table.add_column("Subject")
        table.add_column("Location")
        for row in rows:
            table.add_row(row.start_at, row.end_at, row.subject, row.location or "")
        self.console.print(table)
