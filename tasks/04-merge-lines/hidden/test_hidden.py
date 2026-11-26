"""Hidden checks for task 04. The agent never sees this file. Each docstring is the short note the agent gets on a fail."""
import pytest

from shop.cart import Cart


def test_same_item_twice_is_one_line():
    """Adding the same item twice must give one line, not two."""
    cart = Cart()
    cart.add_item("pen", 1.50, 2)
    cart.add_item("pen", 1.50, 3)
    assert cart.line_count() == 1
    assert cart.quantity_of("pen") == 5


def test_total_after_merge():
    """The total must be right after lines are merged."""
    cart = Cart()
    cart.add_item("pen", 1.50, 2)
    cart.add_item("book", 10.00)
    cart.add_item("pen", 1.50)
    assert cart.total() == 14.50


def test_different_price_is_refused():
    """The same name at a different price must raise ValueError."""
    cart = Cart()
    cart.add_item("pen", 1.50)
    with pytest.raises(ValueError):
        cart.add_item("pen", 2.00)


def test_cart_unchanged_after_refusal():
    """After a refused item, quantity and total must be as before."""
    cart = Cart()
    cart.add_item("pen", 1.50, 2)
    with pytest.raises(ValueError):
        cart.add_item("pen", 9.99, 4)
    assert cart.quantity_of("pen") == 2
    assert cart.total() == 3.00


def test_quantity_of_missing_item():
    """quantity_of must return 0 for an item that is not in the cart."""
    assert Cart().quantity_of("pen") == 0


def test_line_count():
    """line_count must count different items, not units."""
    cart = Cart()
    assert cart.line_count() == 0
    cart.add_item("pen", 1.50, 10)
    cart.add_item("book", 10.00)
    assert cart.line_count() == 2
