"""A very small shopping cart. Prices are in a currency with two decimal places."""
from __future__ import annotations


class Cart:
    RATES = {"SAVE10": 0.10, "SAVE25": 0.25, "HALF": 0.50}

    def __init__(self) -> None:
        self.items: list[tuple[str, float, int]] = []
        self.rate = 0.0

    def add_item(self, name: str, price: float, quantity: int = 1) -> None:
        self.items.append((name, price, quantity))

    def apply_discount(self, code: str) -> None:
        if code.upper() not in self.RATES:
            raise ValueError(f"unknown code: {code}")
        self.rate = self.RATES[code.upper()]

    def subtotal(self) -> float:
        return round(sum(price * quantity for _, price, quantity in self.items), 2)

    def total(self) -> float:
        return round(self.subtotal() * (1 - self.rate), 2)
