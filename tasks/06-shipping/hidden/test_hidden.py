"""Hidden checks for task 06. The agent never sees this file. Each docstring is the short note the agent gets on a fail."""
from shop.cart import Cart


def cart_of(amount):
    cart = Cart()
    cart.add_item("thing", amount)
    return cart


def test_small_order_pays_shipping():
    """An order below 50.00 must pay 4.99 shipping."""
    cart = cart_of(20.00)
    assert cart.shipping() == 4.99
    assert cart.total() == 24.99


def test_exactly_fifty_is_free():
    """An order of exactly 50.00 must have free shipping."""
    cart = cart_of(50.00)
    assert cart.shipping() == 0
    assert cart.total() == 50.00


def test_just_below_fifty_pays():
    """An order of 49.99 must still pay shipping."""
    cart = cart_of(49.99)
    assert cart.shipping() == 4.99
    assert cart.total() == 54.98


def test_large_order_is_free():
    """An order above 50.00 must have free shipping."""
    assert cart_of(120.00).shipping() == 0


def test_empty_cart():
    """An empty cart must have no shipping cost and a total of 0."""
    cart = Cart()
    assert cart.shipping() == 0
    assert cart.total() == 0


def test_subtotal_unchanged():
    """subtotal() must not include shipping."""
    assert cart_of(20.00).subtotal() == 20.00


def test_several_items_reach_the_limit():
    """Free shipping must look at the whole order, not at one item."""
    cart = Cart()
    cart.add_item("pen", 10.00, 3)
    cart.add_item("book", 20.00)
    assert cart.shipping() == 0
