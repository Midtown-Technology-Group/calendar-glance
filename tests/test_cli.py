from typer.testing import CliRunner

from calendar_glance_cli.cli import app
from calendar_glance_cli.models import CalendarEvent


class FakeService:
    def agenda(self, days: int, limit: int, calendar_name: str | None = None):
        return [
            CalendarEvent(
                id="1",
                subject="Weekly Review",
                start_at="2026-04-24T13:00:00Z",
                end_at="2026-04-24T13:30:00Z",
                location="Teams",
            )
        ]


def test_agenda_command_supports_json_output(monkeypatch):
    monkeypatch.setattr("calendar_glance_cli.cli.build_service", lambda: FakeService())
    runner = CliRunner()

    result = runner.invoke(app, ["--output", "json", "agenda", "--days", "3"])

    assert result.exit_code == 0
    assert '"subject":"Weekly Review"' in result.stdout
    assert '"location":"Teams"' in result.stdout


def test_missing_scope_explains_required_calendar_permission(monkeypatch):
    monkeypatch.setattr("calendar_glance_cli.cli.has_required_scope", lambda: False)
    runner = CliRunner()

    result = runner.invoke(app, ["agenda"])

    assert result.exit_code != 0
    assert "Calendars.Read" in result.stdout
