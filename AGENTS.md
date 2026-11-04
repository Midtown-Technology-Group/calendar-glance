# Calendar Glance guidance

Calendar Glance is a read-only Microsoft 365 agenda CLI. Read [README](README.md), `pyproject.toml` and the affected implementation under `src/calendar_glance_cli/`. Keep CLI formatting, service logic, repository access, models and auth configuration in their existing modules.

Preserve the `Calendars.Read` boundary. Do not add calendar writes or change the shared MTG Microsoft Auth application as an incidental fix. Shared token-cache behavior belongs to `mtg-microsoft-auth`; use `MTG_AUTH_CACHE_NAMESPACE` for deliberately isolated tests and preserve account-hint behavior. Never log tokens, cached credentials or real calendar subjects in fixtures.

Python >=3.10 and the development dependencies are declared in `pyproject.toml`. The pytest configuration discovers `tests/`; `tests/test_cli.py` uses fake services for JSON, timezone and scope behavior. Verify those contracts with pytest in an isolated development environment, and add focused coverage for changed behavior. Preserve local-time defaults and explicit IANA timezone overrides.

The documented live command is `.\invoke.ps1 agenda --days 1`; it accesses the signed-in user's calendar and is not an offline test. Use authorized account scope and redact personal information in evidence.

Release packaging is in `packaging/windows/` and `.github/workflows/release-msi.yml`. MSI installation is per-machine and needs elevation; release tags use `vX.Y.Z`. Preserve installer checksum/ProductCode and downstream mtg-winget dispatch semantics. The Sonar job can skip without a token and is not a test suite. Report unit tests, live agenda validation and MSI/release evidence separately; updating source does not authorize publishing or installing it.

## Secret gate before publication

Before publishing the current PR branch, commit the complete candidate and run
`python3 -I scripts/secret_gate.py --base refs/remotes/origin/main` (native Windows PowerShell: `& "$env:MTG_SECRET_GATE_PYTHON" -I`). Require exit 0;
missing tooling/authentication, scan errors and skipped scans block publication.
Then run the existing repository gates. Repeat after changing outgoing commits.
Push exactly the scanned HEAD. This PR scan covers the current branch against its
fetched intended base; other refs, multi-ref pushes and rewritten history require
`--pre-push` with Git's complete ref-update stream. Stop if any pushed ref is
uncovered. See [secret scanning](SECRET-SCANNING.md) for base selection, new branches,
pre-push input and prerequisites. Preserve GitGuardian App, CI and Gitleaks checks.

For a non-default PR target, fetch its destination and pass that exact ref to
`--base`; the remote default is not a substitute for a release/maintenance base.

The secret gate requires Python 3.11+ and approved ggshield >=1.56.1,<2.

Explicit bases require fully qualified refs such as `refs/remotes/origin/main`
or full commit SHAs; ambiguous short names block with exit 20.
