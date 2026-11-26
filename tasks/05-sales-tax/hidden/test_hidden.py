"""Hidden checks for task 05. The agent never sees this file. Each docstring is the short note the agent gets on a fail."""
import pytest

from shop.cart import Cart


def cart_of(amount, rate):
    cart = Cart(tax_rate=rate)
    cart.add_item("thing", amount)
    return cart


def test_no_tax_by_default():
    """Without a tax rate, total() must equal subtotal()."""
    cart = Cart()
    cart.add_item("thing", 20.00)
    assert cart.tax() == 0
    assert cart.total() == 20.00


def test_simple_tax():
    """10% tax on 200.00 must be 20.00, and the total 220.00."""
    cart = cart_of(200.00, 0.10)
    assert cart.tax() == 20.00
    assert cart.total() == 220.00


def test_half_rounds_up():
    """Tax must round half up: 35.00 at 7.5% is 2.625, so the tax is 2.63, not 2.62."""
    cart = cart_of(35.00, 0.075)
    assert cart.tax() == 2.63
    assert cart.total() == 37.63


def test_half_rounds_up_again():
    """Tax must round half up: 0.50 at 5% is 0.025, so the tax is 0.03."""
    assert cart_of(0.50, 0.05).tax() == 0.03


def test_below_half_rounds_down():
    """Tax below half a cent must round down: 10.10 at 2% is 0.202, so the tax is 0.20."""
    assert cart_of(10.10, 0.02).tax() == 0.20


def test_negative_rate():
    """A negative tax rate must raise ValueError."""
    with pytest.raises(ValueError):
        Cart(tax_rate=-0.01)


def test_subtotal_unchanged():
    """subtotal() must stay the price before tax."""
    assert cart_of(100.00, 0.20).subtotal() == 100.00


def test_empty_cart():
    """An empty cart with a tax rate must have tax 0 and total 0."""
    cart = Cart(tax_rate=0.2)
    assert cart.tax() == 0
    assert cart.total() == 0
