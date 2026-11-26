"""Hidden checks for task 07. The agent never sees this file. Each docstring is the short note the agent gets on a fail."""
from shop.cart import Cart


def test_two_items():
    """The receipt must list each item as '2 x pen @ 1.50 = 3.00' and end with 'TOTAL 13.00'."""
    cart = Cart()
    cart.add_item("pen", 1.50, 2)
    cart.add_item("book", 10.00)
    assert cart.receipt() == "2 x pen @ 1.50 = 3.00\n1 x book @ 10.00 = 10.00\nTOTAL 13.00"


def test_empty_cart():
    """An empty cart must give only 'TOTAL 0.00'."""
    assert Cart().receipt() == "TOTAL 0.00"


def test_two_decimals_always():
    """Every amount must have exactly 2 decimal places, also for whole numbers like 5."""
    cart = Cart()
    cart.add_item("mug", 5, 1)
    assert cart.receipt() == "1 x mug @ 5.00 = 5.00\nTOTAL 5.00"


def test_order_of_items():
    """Items must appear in the order they were added."""
    cart = Cart()
    cart.add_item("zebra", 1.00)
    cart.add_item("apple", 2.00)
    lines = cart.receipt().split("\n")
    assert lines[0].startswith("1 x zebra") and lines[1].startswith("1 x apple")


def test_no_new_line_at_the_end():
    """The receipt must not end with a new line."""
    cart = Cart()
    cart.add_item("pen", 1.50)
    assert not cart.receipt().endswith("\n")


def test_line_total_is_rounded():
    """A line total must be rounded to 2 decimal places: 3 x 0.10 is 0.30."""
    cart = Cart()
    cart.add_item("sweet", 0.10, 3)
    assert cart.receipt() == "3 x sweet @ 0.10 = 0.30\nTOTAL 0.30"
