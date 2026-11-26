from datetime import datetime
import pytest
from app.tracking import ParcelTracker
from app.lookup import track


@pytest.fixture
def setup():
    t = ParcelTracker()
    n = t.register_parcel("Shop", "Alice")
    return t, n


def test_is_delivered_false_at_start(setup):
    """A new parcel must not count as delivered."""
    t, n = setup
    assert t.is_delivered(n) is False


def test_is_delivered_true_after_delivery(setup):
    """A parcel with a delivered update must count as delivered."""
    t, n = setup
    t.add_status(n, "picked_up", "Berlin", datetime(2026, 1, 1))
    t.add_status(n, "delivered", "Munich", datetime(2026, 1, 3))
    assert t.is_delivered(n) is True
    assert t.get_parcel(n)["status"] == "delivered"


def test_update_after_delivery_raises(setup):
    """Any update after delivery must raise ValueError and store nothing."""
    t, n = setup
    t.add_status(n, "delivered", "Munich", datetime(2026, 1, 3))
    with pytest.raises(ValueError):
        t.add_status(n, "in_transit", "Munich", datetime(2026, 1, 4))
    with pytest.raises(ValueError):
        t.add_status(n, "delivered", "Munich", datetime(2026, 1, 5))
    assert len(t.get_history(n)) == 1


def test_earlier_time_after_delivery_raises(setup):
    """An update with a time before the delivery must also raise ValueError."""
    t, n = setup
    t.add_status(n, "delivered", "Munich", datetime(2026, 1, 3))
    with pytest.raises(ValueError):
        t.add_status(n, "picked_up", "Berlin", datetime(2026, 1, 1))
    assert track(t, n)["current_status"] == "delivered"


def test_unknown_number_raises_keyerror(setup):
    """is_delivered with an unknown tracking number must raise KeyError."""
    t, _ = setup
    with pytest.raises(KeyError):
        t.is_delivered("PT99999999")


def test_other_parcels_not_affected(setup):
    """Delivering one parcel must not block updates to another parcel."""
    t, n = setup
    m = t.register_parcel("Shop", "Bob")
    t.add_status(n, "delivered", "Munich", datetime(2026, 1, 3))
    t.add_status(m, "picked_up", "Berlin", datetime(2026, 1, 4))
    assert t.get_parcel(m)["status"] == "picked_up"
    assert t.is_delivered(m) is False


def test_failed_attempt_does_not_lock(setup):
    """A failed delivery attempt must still allow more updates."""
    t, n = setup
    t.add_status(n, "failed_attempt", "Munich", datetime(2026, 1, 2))
    t.add_status(n, "delivered", "Munich", datetime(2026, 1, 3))
    assert t.is_delivered(n) is True
