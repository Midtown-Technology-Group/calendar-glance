from __future__ import annotations

import typer
from mtg_microsoft_auth import GraphAuthSession, GraphClient

from calendar_glance_cli.config import REQUIRED_SCOPE, has_required_scope, load_auth_config
from calendar_glance_cli.output import OutputRenderer
from calendar_glance_cli.repository import CalendarRepository
from calendar_glance_cli.service import CalendarGlanceService

app = typer.Typer(help="Read-only Microsoft 365 calendar glance.")


def build_service() -> CalendarGlanceService:
    session = GraphAuthSession(load_auth_config())
    client = GraphClient(session)
    repo = CalendarRepository(client)
    return CalendarGlanceService(repo)


def _renderer(output: str) -> OutputRenderer:
    return OutputRenderer(mode=output)


def _require_scope() -> None:
    if has_required_scope():
        return
    typer.echo(
        f"This command needs {REQUIRED_SCOPE}. Set CALENDAR_GLANCE_SCOPES={REQUIRED_SCOPE} "
        "before running the calendar glance toy."
    )
    raise typer.Exit(code=2)


@app.callback()
def root(
    ctx: typer.Context,
    output: str = typer.Option("interactive", "--output", "-o"),
) -> None:
    ctx.obj = {"output": output}


@app.command("agenda")
def agenda(
    ctx: typer.Context,
    days: int = typer.Option(1, "--days", min=1, max=30),
    limit: int = typer.Option(20, "--limit", "-n", min=1, max=100),
    calendar_name: str | None = typer.Option(None, "--calendar"),
) -> None:
    _require_scope()
    rows = build_service().agenda(days=days, limit=limit, calendar_name=calendar_name)
    _renderer(ctx.obj["output"]).render_events(rows)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
