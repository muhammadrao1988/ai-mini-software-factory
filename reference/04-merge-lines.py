"""A very small shopping cart. Prices are in a currency with two decimal places."""
from __future__ import annotations


class Cart:
    def __init__(self) -> None:
        self.items: list[tuple[str, float, int]] = []

    def add_item(self, name: str, price: float, quantity: int = 1) -> None:
        for i, (n, p, q) in enumerate(self.items):
            if n == name:
                if p != price:
                    raise ValueError("this item is already in the cart at another price")
                self.items[i] = (n, p, q + quantity)
                return
        self.items.append((name, price, quantity))

    def quantity_of(self, name: str) -> int:
        return sum(q for n, _, q in self.items if n == name)

    def line_count(self) -> int:
        return len(self.items)

    def subtotal(self) -> float:
        return round(sum(price * quantity for _, price, quantity in self.items), 2)

    def total(self) -> float:
        return self.subtotal()
