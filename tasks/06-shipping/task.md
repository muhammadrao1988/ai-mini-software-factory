# Add a shipping cost

Add shipping to the cart in `shop/cart.py`.

- Add `shipping()`: the shipping cost.
- Shipping costs 4.99.
- Shipping is free when the subtotal is 50.00 or more.
- An empty cart has no shipping cost.
- `total()` is the subtotal plus shipping.
- `subtotal()` does not change.

Add tests for the new behaviour in `tests/test_cart.py`.
