import datetime as dt

import pytest

from app.tracking import ALLOWED_STATUSES, ParcelTracker

T0 = dt.datetime(2026, 1, 1, 8, 0)


@pytest.fixture
def setup():
    t = ParcelTracker()
    a1 = t.register_parcel("Shop A", "Ann")
    b1 = t.register_parcel("Shop B", "Bob")
    a2 = t.register_parcel("  Shop A ", "Cid")
    t.register_parcel("shop a", "Dee")
    t.add_status(a2, "in_transit", "Hub", T0)
    return t, a1, a2, b1


def test_lists_shop_parcels_sorted_like_get_parcel(setup):
    t, a1, a2, _ = setup
    assert t.list_parcels("Shop A") == [t.get_parcel(a1), t.get_parcel(a2)]
    assert t.list_parcels("Shop A")[1]["status"] == "in_transit"


def test_shop_is_stripped_and_case_sensitive(setup):
    t, a1, a2, _ = setup
    assert [p["tracking_number"] for p in t.list_parcels("\tShop A  ")] == [a1, a2]
    assert len(t.list_parcels("shop a")) == 1
    assert t.list_parcels("SHOP A") == []


def test_unknown_shop_gives_empty_list(setup):
    t = setup[0]
    assert t.list_parcels("Nope") == []
    assert ParcelTracker().list_parcels("Shop A") == []


def test_status_filter(setup):
    t, a1, a2, _ = setup
    assert [p["tracking_number"] for p in t.list_parcels("Shop A", "registered")] == [a1]
    assert [p["tracking_number"] for p in t.list_parcels("Shop A", "in_transit")] == [a2]
    assert t.list_parcels("Shop A", "delivered") == []


def test_filter_uses_latest_status_by_time(setup):
    t, a1, _, _ = setup
    t.add_status(a1, "out_for_delivery", "Van", T0 + dt.timedelta(hours=2))
    t.add_status(a1, "picked_up", "Shop", T0)
    assert t.list_parcels("Shop A", "picked_up") == []
    assert [p["tracking_number"] for p in t.list_parcels("Shop A", "out_for_delivery")] == [a1]


@pytest.mark.parametrize("status", sorted(ALLOWED_STATUSES) + ["registered"])
def test_all_valid_statuses_accepted(setup, status):
    assert isinstance(setup[0].list_parcels("Shop A", status), list)


@pytest.mark.parametrize("status", ["", "Registered", "lost", " delivered", 1, ["x"]])
def test_invalid_status_raises(setup, status):
    with pytest.raises(ValueError):
        setup[0].list_parcels("Shop A", status)


def test_invalid_status_raises_even_for_unknown_shop():
    with pytest.raises(ValueError):
        ParcelTracker().list_parcels("Nope", "bad")


def test_results_are_copies(setup):
    t, a1, _, _ = setup
    first = t.list_parcels("Shop A")
    first[0]["status"] = "delivered"
    first[0]["shop"] = "X"
    first.clear()
    assert t.get_parcel(a1)["status"] == "registered"
    assert t.get_parcel(a1)["shop"] == "Shop A"
    assert len(t.list_parcels("Shop A")) == 2
    assert t.list_parcels("Shop A") is not t.list_parcels("Shop A")


def test_sorted_by_number_beyond_registration_order():
    t = ParcelTracker()
    nums = [t.register_parcel("S", f"R{i}") for i in range(12)]
    assert [p["tracking_number"] for p in t.list_parcels("S")] == nums
