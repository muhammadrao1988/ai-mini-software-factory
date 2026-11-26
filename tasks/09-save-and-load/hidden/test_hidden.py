"""Hidden checks for task 09. The agent never sees this file. Each docstring is the short note the agent gets on a fail."""
import json

import pytest

from shop.cart import Cart


def sample():
    cart = Cart()
    cart.add_item("pen", 1.50, 2)
    cart.add_item("book", 10.00)
    return cart


def test_shape_of_the_dictionary():
    """to_dict must return {"items": [{"name", "price", "quantity"}, ...]} in the order items were added."""
    assert sample().to_dict() == {"items": [{"name": "pen", "price": 1.5, "quantity": 2},
                                            {"name": "book", "price": 10.0, "quantity": 1}]}


def test_can_be_written_as_json():
    """The dictionary must be plain data that json.dumps accepts."""
    json.dumps(sample().to_dict())


def test_round_trip():
    """A cart loaded from its own dictionary must have the same total and the same dictionary."""
    saved = sample().to_dict()
    loaded = Cart.from_dict(json.loads(json.dumps(saved)))
    assert loaded.total() == 13.00
    assert loaded.to_dict() == saved


def test_empty_cart_round_trip():
    """An empty cart must save as {"items": []} and load again."""
    assert Cart().to_dict() == {"items": []}
    assert Cart.from_dict({"items": []}).total() == 0


def test_missing_items_key():
    """Data without an "items" key must raise ValueError."""
    with pytest.raises(ValueError):
        Cart.from_dict({})


@pytest.mark.parametrize("missing", ["name", "price", "quantity"])
def test_missing_field(missing):
    """An item that misses name, price or quantity must raise ValueError."""
    item = {"name": "pen", "price": 1.5, "quantity": 2}
    del item[missing]
    with pytest.raises(ValueError):
        Cart.from_dict({"items": [item]})


def test_dictionary_is_a_copy():
    """Changing the dictionary after to_dict must not change the cart."""
    cart = sample()
    data = cart.to_dict()
    data["items"].clear()
    assert cart.total() == 13.00


def test_loaded_cart_can_be_used():
    """A loaded cart must accept new items like any other cart."""
    cart = Cart.from_dict(sample().to_dict())
    cart.add_item("mug", 4.00)
    assert cart.total() == 17.00
