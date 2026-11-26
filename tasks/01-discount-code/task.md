# Add discount codes to the cart

Add a method `apply_discount(code)` to `Cart` in `shop/cart.py`.

- Known codes: `SAVE10` takes 10% off, `SAVE25` takes 25% off, `HALF` takes 50% off.
- Codes are not case-sensitive: `save10` works like `SAVE10`.
- An unknown code raises `ValueError`.
- Only one code can be active. Applying a second code replaces the first.
- `total()` returns the subtotal minus the discount, rounded to 2 decimal places.
- `subtotal()` does not change: it is still the price before the discount.

Add tests for the new behaviour in `tests/test_cart.py`.
