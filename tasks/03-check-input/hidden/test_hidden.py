"""Hidden checks for task 03. The agent never sees this file. Each docstring is the short note the agent gets on a fail."""
import pytest

from shop.cart import Cart


@pytest.mark.parametrize("quantity", [0, -1, -10])
def test_quantity_below_one(quantity):
    """A quantity of zero or less must raise ValueError."""
    with pytest.raises(ValueError):
        Cart().add_item("pen", 1.50, quantity)


def test_quantity_not_whole():
    """A quantity that is not a whole number, like 1.5, must raise ValueError."""
    with pytest.raises(ValueError):
        Cart().add_item("pen", 1.50, 1.5)


def test_negative_price():
    """A negative price must raise ValueError."""
    with pytest.raises(ValueError):
        Cart().add_item("pen", -0.01)


def test_free_item_is_allowed():
    """A price of zero must be allowed."""
    cart = Cart()
    cart.add_item("gift", 0, 1)
    cart.add_item("pen", 1.50)
    assert cart.total() == 1.50


@pytest.mark.parametrize("name", ["", "   "])
def test_empty_name(name):
    """An empty name, or a name of only spaces, must raise ValueError."""
    with pytest.raises(ValueError):
        Cart().add_item(name, 1.00)


def test_cart_unchanged_after_refusal():
    """After refused input, the cart must be exactly as before."""
    cart = Cart()
    cart.add_item("pen", 1.50, 2)
    for bad in (("book", -5.00, 1), ("book", 5.00, 0), ("", 5.00, 1)):
        with pytest.raises(ValueError):
            cart.add_item(*bad)
    assert cart.total() == 3.00
    assert len(cart.items) == 1


def test_good_input_still_works():
    """Normal input must still work as before."""
    cart = Cart()
    cart.add_item("pen", 1.50, 2)
    cart.add_item("book", 10.00)
    assert cart.total() == 13.00
