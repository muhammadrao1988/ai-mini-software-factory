import re
import pytest
from app.tracking import ParcelTracker


def test_first_number_format():
    """The first registered parcel must get the tracking number PT00000001."""
    t = ParcelTracker()
    number = t.register_parcel("Shop A", "Alice")
    assert number == "PT00000001"
    assert re.fullmatch(r"PT\d{8}", number)


def test_numbers_are_sequential_and_unique():
    """Tracking numbers must count up by one for each new parcel."""
    t = ParcelTracker()
    numbers = [t.register_parcel("Shop", f"R{i}") for i in range(3)]
    assert numbers == ["PT00000001", "PT00000002", "PT00000003"]


def test_get_parcel_returns_fields():
    """get_parcel must return the shop, recipient and the status registered."""
    t = ParcelTracker()
    n = t.register_parcel("Shop A", "Alice")
    assert t.get_parcel(n) == {
        "tracking_number": n,
        "shop": "Shop A",
        "recipient": "Alice",
        "status": "registered",
    }


def test_unknown_number_raises_keyerror():
    """An unknown tracking number must raise KeyError."""
    t = ParcelTracker()
    with pytest.raises(KeyError):
        t.get_parcel("PT99999999")


def test_empty_inputs_raise_valueerror():
    """An empty or whitespace-only shop or recipient must raise ValueError."""
    t = ParcelTracker()
    with pytest.raises(ValueError):
        t.register_parcel("", "Alice")
    with pytest.raises(ValueError):
        t.register_parcel("Shop", "   ")


def test_failed_register_uses_no_number():
    """A failed registration must not use up a tracking number."""
    t = ParcelTracker()
    with pytest.raises(ValueError):
        t.register_parcel(" ", "Alice")
    assert t.register_parcel("Shop", "Alice") == "PT00000001"


def test_whitespace_is_stripped_and_trackers_are_separate():
    """Names must be stored without surrounding whitespace and each tracker must count on its own."""
    t1 = ParcelTracker()
    t2 = ParcelTracker()
    n1 = t1.register_parcel("  Shop A ", " Alice  ")
    n2 = t2.register_parcel("Shop B", "Bob")
    assert n1 == n2 == "PT00000001"
    p = t1.get_parcel(n1)
    assert p["shop"] == "Shop A"
    assert p["recipient"] == "Alice"


def test_returned_dict_is_a_copy():
    """Changing the dict from get_parcel must not change the stored parcel."""
    t = ParcelTracker()
    n = t.register_parcel("Shop", "Alice")
    p = t.get_parcel(n)
    p["status"] = "delivered"
    p["shop"] = "Other"
    assert t.get_parcel(n)["status"] == "registered"
    assert t.get_parcel(n)["shop"] == "Shop"
