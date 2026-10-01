# Calendar Glance guidance

Calendar Glance is a read-only Microsoft 365 agenda CLI. Read [README](README.md), `pyproject.toml` and the affected implementation under `src/calendar_glance_cli/`. Keep CLI formatting, service logic, repository access, models and auth configuration in their existing modules.

Preserve the `Calendars.Read` boundary. Do not add calendar writes or change the shared MTG Microsoft Auth application as an incidental fix. Shared token-cache behavior belongs to `mtg-microsoft-auth`; use `MTG_AUTH_CACHE_NAMESPACE` for deliberately isolated tests and preserve account-hint behavior. Never log tokens, cached credentials or real calendar subjects in fixtures.

Python >=3.10 and the development dependencies are declared in `pyproject.toml`. The pytest configuration discovers `tests/`; `tests/test_cli.py` uses fake services for JSON, timezone and scope behavior. Verify those contracts with pytest in an isolated development environment, and add focused coverage for changed behavior. Preserve local-time defaults and explicit IANA timezone overrides.

The documented live command is `.\invoke.ps1 agenda --days 1`; it accesses the signed-in user's calendar and is not an offline test. Use authorized account scope and redact personal information in evidence.

Release packaging is in `packaging/windows/` and `.github/workflows/release-msi.yml`. MSI installation is per-machine and needs elevation; release tags use `vX.Y.Z`. Preserve installer checksum/ProductCode and downstream mtg-winget dispatch semantics. The Sonar job can skip without a token and is not a test suite. Report unit tests, live agenda validation and MSI/release evidence separately; updating source does not authorize publishing or installing it.
