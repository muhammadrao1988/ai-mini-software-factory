from shop.cart import Cart


def test_empty_cart_is_zero():
    assert Cart().total() == 0


def test_total_adds_up_items():
    cart = Cart()
    cart.add_item("pen", 1.50, 2)
    cart.add_item("book", 10.00)
    assert cart.total() == 13.00
