"""Hidden checks for task 10. The agent never sees this file. Each docstring is the short note the agent gets on a fail."""
from shop.cart import Cart


def test_looks_at_the_line_not_the_unit_price():
    """most_expensive must compare price times quantity, not the unit price."""
    cart = Cart()
    cart.add_item("book", 10.00, 1)
    cart.add_item("pen", 1.50, 10)
    assert cart.most_expensive() == "pen"


def test_simple_case():
    """most_expensive must return the name of the line that costs the most."""
    cart = Cart()
    cart.add_item("pen", 1.50, 2)
    cart.add_item("book", 10.00)
    assert cart.most_expensive() == "book"


def test_tie_goes_to_the_first():
    """When two lines cost the same, the one added first must win."""
    cart = Cart()
    cart.add_item("mug", 5.00, 2)
    cart.add_item("book", 10.00, 1)
    assert cart.most_expensive() == "mug"


def test_empty_cart():
    """An empty cart must return None."""
    assert Cart().most_expensive() is None


def test_clear():
    """After clear(), the total must be 0 and most_expensive must return None."""
    cart = Cart()
    cart.add_item("book", 10.00)
    cart.clear()
    assert cart.total() == 0
    assert cart.most_expensive() is None


def test_cart_works_after_clear():
    """After clear(), new items must be accepted as usual."""
    cart = Cart()
    cart.add_item("book", 10.00)
    cart.clear()
    cart.add_item("pen", 1.50, 2)
    assert cart.total() == 3.00
    assert cart.most_expensive() == "pen"


def test_single_free_item():
    """A cart with one free item must return that item's name, not None."""
    cart = Cart()
    cart.add_item("gift", 0)
    assert cart.most_expensive() == "gift"
