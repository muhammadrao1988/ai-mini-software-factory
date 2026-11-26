# Merge lines for the same item

Change the cart in `shop/cart.py` so the same item is kept as one line.

- Adding an item with a name that is already in the cart, at the same price, increases the quantity of that line.
- Adding an item with a name that is already in the cart, at a different price, raises `ValueError`. The cart
  stays as it was.
- Add `quantity_of(name)`: the quantity of that item, or 0 if it is not in the cart.
- Add `line_count()`: how many different items are in the cart.

Add tests for the new behaviour in `tests/test_cart.py`.
