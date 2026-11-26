# Save and load a cart

Add saving and loading to the cart in `shop/cart.py`.

- Add `to_dict()`: returns the cart as a plain dictionary that can be written as JSON:
  `{"items": [{"name": "pen", "price": 1.5, "quantity": 2}]}`
- Add a class method `Cart.from_dict(data)`: builds a cart from such a dictionary.
- Loading a saved cart gives a cart with the same items, in the same order, and the same total.
- If `data` has no `"items"` key, or an item misses `name`, `price` or `quantity`, raise `ValueError`.
- Changing the dictionary after `to_dict()` must not change the cart.

Add tests for the new behaviour in `tests/test_cart.py`.
