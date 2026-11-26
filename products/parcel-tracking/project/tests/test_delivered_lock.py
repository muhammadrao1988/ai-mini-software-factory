import datetime as dt

import pytest

from app.tracking import ALLOWED_STATUSES, ParcelTracker

T0 = dt.datetime(2026, 1, 1, 8, 0)


@pytest.fixture
def delivered():
    t = ParcelTracker()
    n = t.register_parcel("Shop", "Ann")
    t.add_status(n, "picked_up", "Shop", T0)
    t.add_status(n, "delivered", "Home", T0 + dt.timedelta(hours=2))
    return t, n


@pytest.mark.parametrize("status", sorted(ALLOWED_STATUSES))
@pytest.mark.parametrize("hours", [-5, 1, 2, 10])
def test_any_add_after_delivery_raises_and_stores_nothing(delivered, status, hours):
    t, n = delivered
    before = t.get_history(n)
    with pytest.raises(ValueError):
        t.add_status(n, status, "Anywhere", T0 + dt.timedelta(hours=hours))
    assert t.get_history(n) == before
    assert t.get_parcel(n)["status"] == "delivered"


def test_earlier_checks_run_first(delivered):
    t, n = delivered
    with pytest.raises(KeyError):
        t.add_status("PT99999999", "in_transit", "Hub", T0)
    with pytest.raises(TypeError):
        t.add_status(n, "in_transit", "Hub", "not a time")
    with pytest.raises(ValueError, match="invalid status"):
        t.add_status(n, "lost", "Hub", T0)
    with pytest.raises(ValueError, match="place"):
        t.add_status(n, "in_transit", "  ", T0)


def test_is_delivered():
    t = ParcelTracker()
    n = t.register_parcel("Shop", "Ann")
    other = t.register_parcel("Shop", "Bob")
    assert t.is_delivered(n) is False
    t.add_status(n, "out_for_delivery", "Van", T0)
    assert t.is_delivered(n) is False
    t.add_status(n, "delivered", "Home", T0 + dt.timedelta(hours=1))
    assert t.is_delivered(n) is True
    assert t.is_delivered(other) is False
    t.add_status(other, "in_transit", "Hub", T0)
    assert len(t.get_history(other)) == 1


@pytest.mark.parametrize("number", ["PT99999999", "", None, 1])
def test_is_delivered_unknown_raises_key_error(number):
    with pytest.raises(KeyError):
        ParcelTracker().is_delivered(number)
