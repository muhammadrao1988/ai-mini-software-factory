# Add sales tax

Add sales tax to the cart in `shop/cart.py`.

- `Cart(tax_rate=0.0)`: the tax rate is given when the cart is made. `0.075` means 7.5%. The default is no tax.
- A negative tax rate raises `ValueError`.
- Add `tax()`: the tax on the subtotal, rounded to 2 decimal places.
- Rounding is **half up**, the way a shop does it on paper: 35.00 x 0.075 = 2.625, and the tax is 2.63.
- `total()` is the subtotal plus the tax.
- `subtotal()` does not change.

Add tests for the new behaviour in `tests/test_cart.py`.
