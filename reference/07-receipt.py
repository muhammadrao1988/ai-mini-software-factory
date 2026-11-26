"""A very small shopping cart. Prices are in a currency with two decimal places."""
from __future__ import annotations


class Cart:
    def __init__(self) -> None:
        self.items: list[tuple[str, float, int]] = []

    def add_item(self, name: str, price: float, quantity: int = 1) -> None:
        self.items.append((name, price, quantity))

    def subtotal(self) -> float:
        return round(sum(price * quantity for _, price, quantity in self.items), 2)

    def total(self) -> float:
        return self.subtotal()

    def receipt(self) -> str:
        lines = [f"{q} x {n} @ {p:.2f} = {round(p * q, 2):.2f}" for n, p, q in self.items]
        return "\n".join(lines + [f"TOTAL {self.total():.2f}"])
