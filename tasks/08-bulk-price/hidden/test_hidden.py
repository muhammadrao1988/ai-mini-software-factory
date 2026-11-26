"""Hidden checks for task 08. The agent never sees this file. Each docstring is the short note the agent gets on a fail."""
import pytest

from shop.cart import Cart


def test_three_units_get_ten_percent_off():
    """A line with 3 units must get 10% off: 3 x 10.00 is 27.00."""
    cart = Cart()
    cart.add_item("book", 10.00, 3)
    assert cart.line_total("book") == 27.00
    assert cart.total() == 27.00


def test_two_units_pay_full_price():
    """A line with 2 units must pay the full price."""
    cart = Cart()
    cart.add_item("book", 10.00, 2)
    assert cart.line_total("book") == 20.00
    assert cart.total() == 20.00


def test_only_the_big_line_is_cheaper():
    """Only the line with 3 or more units gets the lower price, not the whole cart."""
    cart = Cart()
    cart.add_item("book", 10.00, 3)
    cart.add_item("pen", 2.00, 1)
    assert cart.total() == 29.00


def test_two_small_lines_get_nothing():
    """Two different items with 2 units each must get no bulk price."""
    cart = Cart()
    cart.add_item("book", 10.00, 2)
    cart.add_item("pen", 2.00, 2)
    assert cart.total() == 24.00


def test_subtotal_unchanged():
    """subtotal() must stay the amount before the bulk price."""
    cart = Cart()
    cart.add_item("book", 10.00, 3)
    assert cart.subtotal() == 30.00


def test_rounding():
    """A line total must be rounded to 2 decimal places: 3 x 1.99 with 10% off is 5.37."""
    cart = Cart()
    cart.add_item("sweet", 1.99, 3)
    assert cart.line_total("sweet") == 5.37


def test_unknown_item():
    """line_total for an item that is not in the cart must raise KeyError."""
    with pytest.raises(KeyError):
        Cart().line_total("book")


def test_many_units():
    """Ten units must also get 10% off: 10 x 4.00 is 36.00."""
    cart = Cart()
    cart.add_item("mug", 4.00, 10)
    assert cart.total() == 36.00
