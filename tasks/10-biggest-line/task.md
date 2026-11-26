# Find the most expensive line

Add two methods to `Cart` in `shop/cart.py`.

- `most_expensive()`: the name of the item whose line costs the most (price times quantity).
  - If two lines cost the same, return the one that was added first.
  - An empty cart returns `None`.
- `clear()`: removes every item. After it, the total is 0.

Add tests for the new behaviour in `tests/test_cart.py`.
