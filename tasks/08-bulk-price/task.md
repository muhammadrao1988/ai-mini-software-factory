# Lower price for buying many

Add a bulk price to the cart in `shop/cart.py`.

- When a line has a quantity of 3 or more, that line gets 10% off.
- Add `line_total(name)`: the amount for that item after any bulk price, rounded to 2 decimal places.
  If the item is not in the cart, raise `KeyError`.
- `total()` is the sum of all line totals.
- `subtotal()` does not change: it is still the amount before the bulk price.
- The bulk price looks at one line only. Two different items with 2 units each get no bulk price.

Add tests for the new behaviour in `tests/test_cart.py`.
