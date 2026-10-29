from datetime import datetime, timezone

import pytest
from mtg_microsoft_auth import GraphClient

from calendar_glance_cli.output import OutputRenderer
from calendar_glance_cli.repository import CalendarRepository


def event(identifier="event-1", zone="UTC", start="2026-11-01T05:30:00.0000000"):
    return {
        "id": identifier,
        "start": {"dateTime": start, "timeZone": zone},
        "end": {"dateTime": "2026-11-01T07:30:00.0000000", "timeZone": "UTC"},
    }


class Response:
    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload


def graph(monkeypatch, pages):
    client = GraphClient(None)
    calls = []

    def request(method, url, params=None):
        assert method == "GET"
        calls.append((url, params))
        return Response(pages[url])

    monkeypatch.setattr(client, "_request_with_retry", request)
    return CalendarRepository(client), calls


@pytest.mark.parametrize(
    ("zone", "start", "expected"),
    [
        (
            "America/New_York",
            "2026-11-01T00:30:00.0000000",
            "2026-11-01T04:30:00+00:00",
        ),
        ("Asia/Tokyo", "2026-11-02T00:30:00", "2026-11-01T15:30:00+00:00"),
        (
            "Eastern Standard Time",
            "2026-03-08T03:30:00.0000000",
            "2026-03-08T07:30:00+00:00",
        ),
        (None, "2026-11-01T05:30:00", "2026-11-01T05:30:00+00:00"),
        ("UTC", "2026-11-01T05:30:00Z", "2026-11-01T05:30:00+00:00"),
        ("UTC", "2026-11-01T05:30:00.0000000", "2026-11-01T05:30:00+00:00"),
        ("America/New_York", "2026-11-01T01:30:00-05:00", "2026-11-01T06:30:00+00:00"),
    ],
)
def test_graph_event_timezone_preserves_instant(monkeypatch, zone, start, expected):
    repo, _ = graph(
        monkeypatch,
        {
            GraphClient.BASE_URL
            + "/me/calendarView": {"value": [event(zone=zone, start=start)]},
        },
    )
    row = repo.agenda(days=1, limit=20)[0]
    renderer = OutputRenderer(timezone_name="UTC")
    assert renderer._format_local(row.start_at) == expected
    assert renderer._format_local(row.end_at) == "2026-11-01T07:30:00+00:00"


def test_agenda_reads_pages_and_caps_total_without_reusing_params(monkeypatch):
    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 10, 31, 23, 30, tzinfo=timezone.utc)

    monkeypatch.setattr("calendar_glance_cli.repository.datetime", FixedDatetime)
    first = GraphClient.BASE_URL + "/me/calendarView"
    second = first + "?$skiptoken=opaque"
    third = first + "?$skiptoken=unused"
    repo, calls = graph(
        monkeypatch,
        {
            first: {"value": [event("one")], "@odata.nextLink": second},
            second: {"value": [event("two"), event("three")], "@odata.nextLink": third},
        },
    )
    rows = repo.agenda(days=3, limit=2)
    assert [row.id for row in rows] == ["one", "two"]
    assert [url for url, _ in calls] == [first, second]
    assert calls[1][1] is None
    params = calls[0][1]
    assert params["$top"] == 2
    start = datetime.fromisoformat(params["startDateTime"])
    end = datetime.fromisoformat(params["endDateTime"])
    assert start.tzinfo == timezone.utc
    assert start == datetime(2026, 10, 31, 23, 30, tzinfo=timezone.utc)
    assert end == datetime(2026, 11, 3, 23, 30, tzinfo=timezone.utc)
    assert (end - start).total_seconds() == 3 * 86400


def test_sparse_event_dates_and_non_utc_end(monkeypatch):
    row = event()
    row["start"] = None
    row["end"] = {
        "dateTime": "2026-11-02T00:30:00",
        "timeZone": "Tokyo Standard Time",
    }
    repo, _ = graph(
        monkeypatch,
        {GraphClient.BASE_URL + "/me/calendarView": {"value": [row]}},
    )
    result = repo.agenda(days=1, limit=20)[0]
    assert result.start_at == ""
    assert result.subject == "(no subject)"
    assert result.location is None
    assert result.organizer is None
    assert OutputRenderer(timezone_name="UTC")._format_local(result.end_at) == (
        "2026-11-01T15:30:00+00:00"
    )


def test_named_calendar_lookup_reads_later_pages(monkeypatch):
    first = GraphClient.BASE_URL + "/me/calendars"
    second = first + "?$skiptoken=opaque"
    agenda = GraphClient.BASE_URL + "/me/calendars/target/calendarView"
    repo, calls = graph(
        monkeypatch,
        {
            first: {
                "value": [{"id": "other", "name": "Other"}],
                "@odata.nextLink": second,
            },
            second: {"value": [{"id": "target", "name": "Chosen"}]},
            agenda: {"value": [event()]},
        },
    )
    assert len(repo.agenda(days=1, limit=20, calendar_name="chosen")) == 1
    assert [url for url, _ in calls] == [first, second, agenda]
    assert calls[1][1] is None
