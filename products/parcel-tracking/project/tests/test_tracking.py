import pytest

from app.tracking import ParcelTracker


def test_numbers_are_sequential_and_padded():
    t = ParcelTracker()
    assert t.register_parcel("Shop", "Ann") == "PT00000001"
    assert t.register_parcel("Shop", "Bob") == "PT00000002"


def test_trackers_have_separate_counters_and_data():
    a, b = ParcelTracker(), ParcelTracker()
    assert a.register_parcel("S", "R") == "PT00000001"
    assert b.register_parcel("S", "R") == "PT00000001"
    a.register_parcel("S", "R")
    with pytest.raises(KeyError):
        b.get_parcel("PT00000002")


def test_get_parcel_returns_stripped_fields_and_status():
    t = ParcelTracker()
    n = t.register_parcel("  My Shop ", "\tAnn Lee\n")
    assert t.get_parcel(n) == {
        "tracking_number": n,
        "shop": "My Shop",
        "recipient": "Ann Lee",
        "status": "registered",
    }


@pytest.mark.parametrize("shop,recipient", [("", "R"), ("S", ""), ("   ", "R"), ("S", " \t ")])
def test_empty_input_raises_and_uses_no_number(shop, recipient):
    t = ParcelTracker()
    with pytest.raises(ValueError):
        t.register_parcel(shop, recipient)
    with pytest.raises(KeyError):
        t.get_parcel("PT00000001")
    assert t.register_parcel("S", "R") == "PT00000001"


def test_unknown_tracking_number_raises_keyerror():
    with pytest.raises(KeyError):
        ParcelTracker().get_parcel("PT99999999")


def test_returned_dict_is_a_copy():
    t = ParcelTracker()
    n = t.register_parcel("S", "R")
    d = t.get_parcel(n)
    d["status"] = "delivered"
    d["shop"] = "X"
    assert t.get_parcel(n)["status"] == "registered"
    assert t.get_parcel(n)["shop"] == "S"
    assert t.get_parcel(n) is not t.get_parcel(n)
