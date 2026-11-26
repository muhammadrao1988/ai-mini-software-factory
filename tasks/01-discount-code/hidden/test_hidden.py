"""Hidden checks for task 01. The agent never sees this file. Each docstring is the short note the agent gets on a fail."""
import pytest

from shop.cart import Cart


def cart_of(amount: float) -> Cart:
    cart = Cart()
    cart.add_item("thing", amount)
    return cart


def test_ten_percent():
    """SAVE10 must take 10% off the total."""
    cart = cart_of(200.00)
    cart.apply_discount("SAVE10")
    assert cart.total() == 180.00


def test_twenty_five_percent_and_half():
    """SAVE25 must take 25% off and HALF must take 50% off."""
    cart = cart_of(80.00)
    cart.apply_discount("SAVE25")
    assert cart.total() == 60.00
    cart = cart_of(80.00)
    cart.apply_discount("HALF")
    assert cart.total() == 40.00


def test_code_in_small_letters():
    """Codes must work in any letter case, for example 'save10'."""
    cart = cart_of(100.00)
    cart.apply_discount("save10")
    assert cart.total() == 90.00


def test_unknown_code():
    """An unknown code must raise ValueError."""
    with pytest.raises(ValueError):
        cart_of(100.00).apply_discount("FREE")


def test_unknown_code_keeps_the_old_one():
    """A failed code must not remove a discount that was already active."""
    cart = cart_of(100.00)
    cart.apply_discount("SAVE10")
    with pytest.raises(ValueError):
        cart.apply_discount("NOPE")
    assert cart.total() == 90.00


def test_second_code_replaces_first():
    """A second code must replace the first one, not add to it."""
    cart = cart_of(100.00)
    cart.apply_discount("SAVE10")
    cart.apply_discount("HALF")
    assert cart.total() == 50.00


def test_rounding():
    """The total must be rounded to 2 decimal places."""
    cart = cart_of(19.99)
    cart.apply_discount("SAVE25")
    assert cart.total() == 14.99


def test_subtotal_unchanged():
    """subtotal() must stay the price before the discount."""
    cart = cart_of(100.00)
    cart.apply_discount("HALF")
    assert cart.subtotal() == 100.00


def test_item_added_after_the_code():
    """The discount must also apply to items added after the code."""
    cart = cart_of(100.00)
    cart.apply_discount("SAVE10")
    cart.add_item("more", 100.00)
    assert cart.total() == 180.00
