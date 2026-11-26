# Refuse bad input

Change `add_item` in `shop/cart.py` so the cart refuses bad input.

- `quantity` must be a whole number of 1 or more. Zero or a negative number raises `ValueError`.
- A quantity that is not a whole number, like `1.5`, raises `ValueError`.
- `price` must be zero or more. A negative price raises `ValueError`. A price of zero is allowed (a free gift).
- `name` must not be empty or only spaces. Otherwise raise `ValueError`.
- When input is refused, the cart must stay exactly as it was.

Add tests for the new behaviour in `tests/test_cart.py`.
