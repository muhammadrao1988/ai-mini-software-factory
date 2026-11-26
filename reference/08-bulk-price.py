"""A very small shopping cart. Prices are in a currency with two decimal places."""
from __future__ import annotations


class Cart:
    def __init__(self) -> None:
        self.items: list[tuple[str, float, int]] = []

    def add_item(self, name: str, price: float, quantity: int = 1) -> None:
        self.items.append((name, price, quantity))

    def subtotal(self) -> float:
        return round(sum(price * quantity for _, price, quantity in self.items), 2)

    @staticmethod
    def _line(price: float, quantity: int) -> float:
        amount = price * quantity
        return round(amount * 0.9 if quantity >= 3 else amount, 2)

    def line_total(self, name: str) -> float:
        lines = [self._line(p, q) for n, p, q in self.items if n == name]
        if not lines:
            raise KeyError(name)
        return round(sum(lines), 2)

    def total(self) -> float:
        return round(sum(self._line(p, q) for _, p, q in self.items), 2)
