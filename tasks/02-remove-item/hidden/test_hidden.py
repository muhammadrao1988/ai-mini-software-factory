"""Hidden checks for task 02. The agent never sees this file. Each docstring is the short note the agent gets on a fail."""
import pytest

from shop.cart import Cart


def test_removed_item_is_not_counted():
    """After remove_item, the total must not count that item."""
    cart = Cart()
    cart.add_item("pen", 1.50, 2)
    cart.add_item("book", 10.00)
    cart.remove_item("pen")
    assert cart.total() == 10.00


def test_unknown_name():
    """Removing a name that is not in the cart must raise KeyError."""
    cart = Cart()
    cart.add_item("pen", 1.50)
    with pytest.raises(KeyError):
        cart.remove_item("book")


def test_empty_cart():
    """Removing from an empty cart must raise KeyError."""
    with pytest.raises(KeyError):
        Cart().remove_item("pen")


def test_every_line_with_the_name_goes():
    """If the same name was added twice, both lines must be removed."""
    cart = Cart()
    cart.add_item("pen", 1.50)
    cart.add_item("book", 10.00)
    cart.add_item("pen", 2.00)
    cart.remove_item("pen")
    assert cart.total() == 10.00


def test_removing_twice():
    """Removing the same name a second time must raise KeyError."""
    cart = Cart()
    cart.add_item("pen", 1.50)
    cart.remove_item("pen")
    with pytest.raises(KeyError):
        cart.remove_item("pen")


def test_names_are_exact():
    """Names must match exactly: 'Pen' is not 'pen'."""
    cart = Cart()
    cart.add_item("pen", 1.50)
    with pytest.raises(KeyError):
        cart.remove_item("Pen")
    assert cart.total() == 1.50
