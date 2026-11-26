from datetime import datetime
import pytest
from app.tracking import ParcelTracker, ALLOWED_STATUSES


@pytest.fixture
def setup():
    t = ParcelTracker()
    n = t.register_parcel("Shop", "Alice")
    return t, n


def test_allowed_statuses_content():
    """ALLOWED_STATUSES must contain exactly the five courier statuses."""
    assert set(ALLOWED_STATUSES) == {"picked_up", "in_transit", "out_for_delivery", "failed_attempt", "delivered"}


def test_add_status_changes_current_status(setup):
    """After an update the parcel status must be the new status."""
    t, n = setup
    t.add_status(n, "picked_up", "Berlin", datetime(2026, 1, 1, 9, 0))
    assert t.get_parcel(n)["status"] == "picked_up"
    assert t.get_history(n) == [{"status": "picked_up", "place": "Berlin", "time": datetime(2026, 1, 1, 9, 0)}]


def test_history_sorted_by_time(setup):
    """History must be sorted oldest first and the current status must come from the newest time."""
    t, n = setup
    t.add_status(n, "in_transit", "Hamburg", datetime(2026, 1, 2, 10, 0))
    t.add_status(n, "picked_up", "Berlin", datetime(2026, 1, 1, 9, 0))
    hist = t.get_history(n)
    assert [h["status"] for h in hist] == ["picked_up", "in_transit"]
    assert t.get_parcel(n)["status"] == "in_transit"


def test_same_time_keeps_added_order(setup):
    """Updates with the same time must stay in the order they were added."""
    t, n = setup
    when = datetime(2026, 1, 1, 12, 0)
    t.add_status(n, "out_for_delivery", "Munich", when)
    t.add_status(n, "failed_attempt", "Munich", when)
    assert [h["status"] for h in t.get_history(n)] == ["out_for_delivery", "failed_attempt"]
    assert t.get_parcel(n)["status"] == "failed_attempt"


def test_no_updates_gives_empty_history(setup):
    """A parcel without updates must have an empty history and status registered."""
    t, n = setup
    assert t.get_history(n) == []
    assert t.get_parcel(n)["status"] == "registered"


def test_unknown_number_raises_keyerror(setup):
    """Adding to or reading history of an unknown tracking number must raise KeyError."""
    t, _ = setup
    with pytest.raises(KeyError):
        t.add_status("PT99999999", "picked_up", "Berlin", datetime(2026, 1, 1))
    with pytest.raises(KeyError):
        t.get_history("PT99999999")


def test_invalid_input_raises_and_stores_nothing(setup):
    """A bad status or empty place must raise ValueError, a non-datetime time must raise TypeError, and nothing must be stored."""
    t, n = setup
    with pytest.raises(ValueError):
        t.add_status(n, "registered", "Berlin", datetime(2026, 1, 1))
    with pytest.raises(ValueError):
        t.add_status(n, "lost", "Berlin", datetime(2026, 1, 1))
    with pytest.raises(ValueError):
        t.add_status(n, "picked_up", "   ", datetime(2026, 1, 1))
    with pytest.raises(TypeError):
        t.add_status(n, "picked_up", "Berlin", "2026-01-01")
    assert t.get_history(n) == []


def test_place_is_stripped(setup):
    """The place must be stored without surrounding whitespace."""
    t, n = setup
    t.add_status(n, "picked_up", "  Berlin  ", datetime(2026, 1, 1))
    assert t.get_history(n)[0]["place"] == "Berlin"
