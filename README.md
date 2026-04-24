# Calendar Glance CLI

Read-only Microsoft 365 calendar glance for the Midtown toy chest.

Project site: <https://midtown-technology-group.github.io/calendar-glance/>

## Required Scope

- `Calendars.Read`

This toy uses the shared `MTG Shared Microsoft Auth` app registration unchanged.

## Environment

```powershell
$env:CALENDAR_GLANCE_CLIENT_ID='e02be6f7-063a-46a6-b2cc-109d5f51055c'
$env:CALENDAR_GLANCE_TENANT_ID='a3599b15-c39c-4b41-a219-7e24dd5b5190'
$env:CALENDAR_GLANCE_SCOPES='Calendars.Read'
$env:CALENDAR_GLANCE_AUTH_MODE='wam'
$env:CALENDAR_GLANCE_ALLOW_BROKER='true'
```

## Usage

```powershell
.\invoke.ps1 agenda --days 1
.\invoke.ps1 agenda --calendar "Calendar" --days 7
.\invoke.ps1 --output json agenda --days 3
```

## Commands

- `agenda`: Show upcoming events from the signed-in user's calendar.

## Project Site

This repo includes a lightweight GitHub Pages site in `docs/`.

## License

GPL-3.0-or-later.
