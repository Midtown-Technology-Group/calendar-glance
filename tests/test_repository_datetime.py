import pytest

from calendar_glance_cli.repository import CalendarRepository


class FakeGraph:
    def __init__(self, row):
        self.row = row

    def get_all(self, path, params=None, max_items=None):
        assert path == "/me/calendarView"
        return {"value": [self.row]}


@pytest.mark.parametrize(
    "digits", ["", "1", "12", "123", "1234", "12345", "123456", "1234567"]
)
@pytest.mark.parametrize("suffix", ["", "Z", "+09:00", "-05:00"])
def test_graph_fraction_precision_on_supported_python(digits, suffix):
    fraction = f".{digits}" if digits else ""
    timestamp = f"2026-11-01T05:30:00{fraction}{suffix}"
    value = {"dateTime": timestamp, "timeZone": "Asia/Tokyo"}
    repo = CalendarRepository(
        FakeGraph({"id": "fraction", "start": value, "end": value})
    )
    result = repo.agenda(days=1, limit=20)[0]
    offset = "+00:00" if suffix == "Z" else suffix or "+09:00"
    expected_fraction = f".{digits[:6].ljust(6, '0')}" if digits else ""
    expected = f"2026-11-01T05:30:00{expected_fraction}{offset}"
    assert result.start_at == expected
    assert result.end_at == expected


@pytest.mark.parametrize("value", [None, {}, {"dateTime": ""}, {"dateTime": None}])
def test_missing_graph_datetime_stays_empty(value):
    assert CalendarRepository._event_datetime(value) == ""
