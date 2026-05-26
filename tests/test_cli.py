from typer.testing import CliRunner

from calendar_glance_cli.cli import app
from calendar_glance_cli.config import DEFAULT_CLIENT_ID, load_auth_config
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
    monkeypatch.setattr("calendar_glance_cli.cli.get_localzone_name", lambda: "America/Indianapolis")
    monkeypatch.delenv("CALENDAR_GLANCE_TIMEZONE", raising=False)
    runner = CliRunner()

    result = runner.invoke(app, ["--output", "json", "agenda", "--days", "3"])

    assert result.exit_code == 0
    assert '"subject":"Weekly Review"' in result.stdout
    assert '"location":"Teams"' in result.stdout
    assert '"start_at":"2026-04-24T09:00:00-04:00"' in result.stdout
    assert '"timezone":"America/Indianapolis"' in result.stdout


def test_agenda_command_allows_timezone_override(monkeypatch):
    monkeypatch.setattr("calendar_glance_cli.cli.build_service", lambda: FakeService())
    monkeypatch.setattr("calendar_glance_cli.cli.get_localzone_name", lambda: "America/Indianapolis")
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["--output", "json", "agenda", "--timezone", "America/Los_Angeles"],
    )

    assert result.exit_code == 0
    assert '"start_at":"2026-04-24T06:00:00-07:00"' in result.stdout
    assert '"timezone":"America/Los_Angeles"' in result.stdout


def test_agenda_command_allows_timezone_env_override(monkeypatch):
    monkeypatch.setattr("calendar_glance_cli.cli.build_service", lambda: FakeService())
    monkeypatch.setattr("calendar_glance_cli.cli.get_localzone_name", lambda: "America/Indianapolis")
    monkeypatch.setenv("CALENDAR_GLANCE_TIMEZONE", "America/New_York")
    runner = CliRunner()

    result = runner.invoke(app, ["--output", "json", "agenda"])

    assert result.exit_code == 0
    assert '"start_at":"2026-04-24T09:00:00-04:00"' in result.stdout
    assert '"timezone":"America/New_York"' in result.stdout


def test_missing_scope_explains_required_calendar_permission(monkeypatch):
    monkeypatch.setattr("calendar_glance_cli.cli.has_required_scope", lambda: False)
    runner = CliRunner()

    result = runner.invoke(app, ["agenda"])

    assert result.exit_code != 0
    assert "Calendars.Read" in result.stdout


def test_load_auth_config_defaults_to_shared_client_id(monkeypatch):
    monkeypatch.delenv("CALENDAR_GLANCE_CLIENT_ID", raising=False)
    monkeypatch.setenv("CALENDAR_GLANCE_AUTH_MODE", "wam")

    config = load_auth_config()

    assert config.client_id == DEFAULT_CLIENT_ID


def test_load_auth_config_allows_client_id_override(monkeypatch):
    monkeypatch.setenv("CALENDAR_GLANCE_CLIENT_ID", "11111111-1111-1111-1111-111111111112")
    monkeypatch.setenv("CALENDAR_GLANCE_AUTH_MODE", "wam")

    config = load_auth_config()

    assert config.client_id == "11111111-1111-1111-1111-111111111112"
