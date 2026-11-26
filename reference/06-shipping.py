"""A very small shopping cart. Prices are in a currency with two decimal places."""
from __future__ import annotations


class Cart:
    def __init__(self) -> None:
        self.items: list[tuple[str, float, int]] = []

    def add_item(self, name: str, price: float, quantity: int = 1) -> None:
        self.items.append((name, price, quantity))

    def subtotal(self) -> float:
        return round(sum(price * quantity for _, price, quantity in self.items), 2)

    def shipping(self) -> float:
        if not self.items or self.subtotal() >= 50.00:
            return 0.0
        return 4.99

    def total(self) -> float:
        return round(self.subtotal() + self.shipping(), 2)
