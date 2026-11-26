"""A very small shopping cart. Prices are in a currency with two decimal places."""
from __future__ import annotations


class Cart:
    def __init__(self) -> None:
        self.items: list[tuple[str, float, int]] = []

    def add_item(self, name: str, price: float, quantity: int = 1) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must not be empty")
        if isinstance(quantity, bool) or quantity != int(quantity) or quantity < 1:
            raise ValueError("quantity must be a whole number of 1 or more")
        if price < 0:
            raise ValueError("price must be zero or more")
        self.items.append((name, price, int(quantity)))

    def subtotal(self) -> float:
        return round(sum(price * quantity for _, price, quantity in self.items), 2)

    def total(self) -> float:
        return self.subtotal()
