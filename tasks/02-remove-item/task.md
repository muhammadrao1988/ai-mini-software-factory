# Remove an item from the cart

Add a method `remove_item(name)` to `Cart` in `shop/cart.py`.

- It removes every line with that name.
- If no line has that name, it raises `KeyError`.
- After removing, `subtotal()` and `total()` no longer count that item.

Add tests for the new behaviour in `tests/test_cart.py`.
