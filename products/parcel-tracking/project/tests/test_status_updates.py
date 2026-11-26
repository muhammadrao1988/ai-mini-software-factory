import datetime as dt

import pytest

from app.tracking import ALLOWED_STATUSES, ParcelTracker

T0 = dt.datetime(2026, 1, 1, 8, 0)


def at(minutes):
    return T0 + dt.timedelta(minutes=minutes)


@pytest.fixture
def setup():
    t = ParcelTracker()
    return t, t.register_parcel("Shop", "Ann")


def test_allowed_statuses():
    assert set(ALLOWED_STATUSES) == {
        "picked_up", "in_transit", "out_for_delivery", "failed_attempt", "delivered"
    }


def test_empty_history_and_registered_status(setup):
    t, n = setup
    assert t.get_history(n) == []
    assert t.get_parcel(n)["status"] == "registered"


def test_history_sorted_stable_and_status_follows_latest(setup):
    t, n = setup
    t.add_status(n, "in_transit", "  Hub  ", at(10))
    t.add_status(n, "picked_up", "Shop", at(0))
    t.add_status(n, "out_for_delivery", "Van", at(20))
    t.add_status(n, "failed_attempt", "Door", at(20))
    assert t.get_history(n) == [
        {"status": "picked_up", "place": "Shop", "time": at(0)},
        {"status": "in_transit", "place": "Hub", "time": at(10)},
        {"status": "out_for_delivery", "place": "Van", "time": at(20)},
        {"status": "failed_attempt", "place": "Door", "time": at(20)},
    ]
    assert t.get_parcel(n)["status"] == "failed_attempt"
    t.add_status(n, "delivered", "Door", at(5))  # older update: status unchanged
    assert t.get_parcel(n)["status"] == "failed_attempt"


def test_history_is_a_new_list(setup):
    t, n = setup
    t.add_status(n, "picked_up", "Shop", at(0))
    hist = t.get_history(n)
    hist.append("x")
    hist[0]["status"] = "delivered"
    assert t.get_history(n) == [{"status": "picked_up", "place": "Shop", "time": at(0)}]


def test_unknown_number_raises_keyerror_first():
    t = ParcelTracker()
    with pytest.raises(KeyError):
        t.add_status("PT00000001", "bad", "", "not a time")
    with pytest.raises(KeyError):
        t.get_history("PT00000001")


@pytest.mark.parametrize(
    "status,place,time,exc",
    [
        ("registered", "Hub", T0, ValueError),
        ("lost", "", "x", ValueError),
        ("in_transit", "   ", "x", ValueError),
        ("in_transit", "", T0, ValueError),
        ("in_transit", "Hub", "2026-01-01", TypeError),
        ("in_transit", "Hub", dt.date(2026, 1, 1), TypeError),
    ],
)
def test_validation_order_and_nothing_stored(setup, status, place, time, exc):
    t, n = setup
    with pytest.raises(exc):
        t.add_status(n, status, place, time)
    assert t.get_history(n) == []
    assert t.get_parcel(n)["status"] == "registered"
