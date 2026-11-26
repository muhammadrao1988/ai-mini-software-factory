import datetime as dt

import pytest

from app.lookup import track
from app.tracking import ParcelTracker

T0 = dt.datetime(2026, 1, 1, 8, 0)


@pytest.fixture
def setup():
    t = ParcelTracker()
    return t, t.register_parcel("Secret Shop", "Ann Lee")


def test_no_updates(setup):
    t, n = setup
    assert track(t, n) == {
        "tracking_number": n,
        "current_status": "registered",
        "current_place": None,
        "last_update": None,
        "history": [],
    }


def test_with_updates_uses_latest_by_time(setup):
    t, n = setup
    t.add_status(n, "in_transit", "Hub", T0 + dt.timedelta(hours=1))
    t.add_status(n, "picked_up", "Shop", T0)
    result = track(t, n)
    assert result["current_status"] == "in_transit" == t.get_parcel(n)["status"]
    assert result["current_place"] == "Hub"
    assert result["last_update"] == T0 + dt.timedelta(hours=1)
    assert result["history"] == t.get_history(n)
    assert [h["status"] for h in result["history"]] == ["picked_up", "in_transit"]


def test_number_is_cleaned(setup):
    t, n = setup
    result = track(t, " pt00000001 \n")
    assert result["tracking_number"] == n == "PT00000001"


def test_hides_shop_and_recipient(setup):
    t, n = setup
    t.add_status(n, "picked_up", "Depot", T0)
    result = track(t, n)
    assert set(result) == {
        "tracking_number", "current_status", "current_place", "last_update", "history"
    }
    assert "Secret Shop" not in repr(result)
    assert "Ann Lee" not in repr(result)


@pytest.mark.parametrize("number", ["PT00000002", "", "   ", None, 1])
def test_unknown_raises_key_error(setup, number):
    t, _ = setup
    with pytest.raises(KeyError):
        track(t, number)
