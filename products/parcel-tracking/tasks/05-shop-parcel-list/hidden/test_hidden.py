from datetime import datetime
import pytest
from app.tracking import ParcelTracker


@pytest.fixture
def setup():
    t = ParcelTracker()
    a1 = t.register_parcel("Shop A", "Alice")
    b1 = t.register_parcel("Shop B", "Bob")
    a2 = t.register_parcel("Shop A", "Carol")
    return t, a1, b1, a2


def test_lists_only_own_parcels_sorted(setup):
    """A shop must see only its own parcels, sorted by tracking number."""
    t, a1, b1, a2 = setup
    result = t.list_parcels("Shop A")
    assert [p["tracking_number"] for p in result] == [a1, a2]
    assert result[0] == t.get_parcel(a1)


def test_unknown_shop_returns_empty(setup):
    """A shop without parcels must get an empty list."""
    t, *_ = setup
    assert t.list_parcels("Shop Z") == []


def test_shop_match_strips_but_is_case_sensitive(setup):
    """The shop name must match after trimming spaces, but upper and lower case must count."""
    t, a1, b1, a2 = setup
    assert len(t.list_parcels("  Shop A ")) == 2
    assert t.list_parcels("shop a") == []


def test_filter_by_status(setup):
    """The status filter must return only parcels with that current status."""
    t, a1, b1, a2 = setup
    t.add_status(a2, "picked_up", "Berlin", datetime(2026, 1, 1))
    assert [p["tracking_number"] for p in t.list_parcels("Shop A", "picked_up")] == [a2]
    assert [p["tracking_number"] for p in t.list_parcels("Shop A", "registered")] == [a1]
    assert t.list_parcels("Shop A", "delivered") == []


def test_filter_uses_current_status(setup):
    """The filter must use the newest status, not an older one."""
    t, a1, b1, a2 = setup
    t.add_status(a1, "picked_up", "Berlin", datetime(2026, 1, 1))
    t.add_status(a1, "delivered", "Munich", datetime(2026, 1, 2))
    assert t.list_parcels("Shop A", "picked_up") == []
    assert [p["tracking_number"] for p in t.list_parcels("Shop A", "delivered")] == [a1]


def test_invalid_status_raises_valueerror(setup):
    """An unknown status filter must raise ValueError."""
    t, *_ = setup
    with pytest.raises(ValueError):
        t.list_parcels("Shop A", "lost")


def test_returned_dicts_are_copies(setup):
    """Changing a listed dict must not change the stored parcel."""
    t, a1, b1, a2 = setup
    t.list_parcels("Shop A")[0]["status"] = "delivered"
    assert t.get_parcel(a1)["status"] == "registered"


def test_earlier_features_still_work(setup):
    """Registering and delivery locking must still work after adding the list."""
    t, a1, b1, a2 = setup
    assert t.register_parcel("Shop C", "Dan") == "PT00000004"
    t.add_status(b1, "delivered", "Munich", datetime(2026, 1, 1))
    with pytest.raises(ValueError):
        t.add_status(b1, "in_transit", "Munich", datetime(2026, 1, 2))
