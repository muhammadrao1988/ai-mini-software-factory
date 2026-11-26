from datetime import datetime
import pytest
from app.tracking import ParcelTracker
from app.lookup import track


@pytest.fixture
def setup():
    t = ParcelTracker()
    n = t.register_parcel("Shop", "Alice")
    return t, n


def test_track_without_updates(setup):
    """A parcel without updates must show status registered and None for place and time."""
    t, n = setup
    assert track(t, n) == {
        "tracking_number": n,
        "current_status": "registered",
        "current_place": None,
        "last_update": None,
        "history": [],
    }


def test_track_with_updates(setup):
    """The result must show the newest status, place and time plus the full history."""
    t, n = setup
    t.add_status(n, "picked_up", "Berlin", datetime(2026, 1, 1, 9))
    t.add_status(n, "in_transit", "Hamburg", datetime(2026, 1, 2, 9))
    r = track(t, n)
    assert r["current_status"] == "in_transit"
    assert r["current_place"] == "Hamburg"
    assert r["last_update"] == datetime(2026, 1, 2, 9)
    assert [h["place"] for h in r["history"]] == ["Berlin", "Hamburg"]


def test_current_comes_from_newest_time(setup):
    """An update added late with an older time must not become the current place."""
    t, n = setup
    t.add_status(n, "in_transit", "Hamburg", datetime(2026, 1, 2, 9))
    t.add_status(n, "picked_up", "Berlin", datetime(2026, 1, 1, 9))
    r = track(t, n)
    assert r["current_place"] == "Hamburg"
    assert r["current_status"] == "in_transit"


def test_number_is_cleaned(setup):
    """A lower case number with spaces around it must find the parcel."""
    t, n = setup
    r = track(t, "  " + n.lower() + " ")
    assert r["tracking_number"] == n


def test_unknown_number_raises_keyerror(setup):
    """An unknown tracking number must raise KeyError."""
    t, _ = setup
    with pytest.raises(KeyError):
        track(t, "PT12345678")


def test_no_private_data(setup):
    """The customer view must contain exactly the five agreed keys."""
    t, n = setup
    r = track(t, n)
    assert set(r.keys()) == {"tracking_number", "current_status", "current_place", "last_update", "history"}
    assert "Alice" not in str(r)


def test_tracker_still_works(setup):
    """The tracker methods must keep working the same after track is used."""
    t, n = setup
    track(t, n)
    assert t.get_parcel(n)["status"] == "registered"
    with pytest.raises(KeyError):
        t.get_parcel(n.lower())
