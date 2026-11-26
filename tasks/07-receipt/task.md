# Print a receipt

Add a method `receipt()` to `Cart` in `shop/cart.py`. It returns the receipt as one text.

- One line for each item, in the order the items were added:
  `2 x pen @ 1.50 = 3.00`
- The last line is the total: `TOTAL 13.00`
- All amounts have exactly 2 decimal places.
- Lines are separated by a new line. There is no new line at the end.
- An empty cart gives only `TOTAL 0.00`.

Add tests for the new behaviour in `tests/test_cart.py`.
