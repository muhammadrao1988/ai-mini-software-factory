"""A very small shopping cart. Prices are in a currency with two decimal places."""
from __future__ import annotations


from decimal import ROUND_HALF_UP, Decimal


class Cart:
    def __init__(self, tax_rate: float = 0.0) -> None:
        if tax_rate < 0:
            raise ValueError("tax rate must be zero or more")
        self.tax_rate = tax_rate
        self.items: list[tuple[str, float, int]] = []

    def add_item(self, name: str, price: float, quantity: int = 1) -> None:
        self.items.append((name, price, quantity))

    def subtotal(self) -> float:
        return round(sum(price * quantity for _, price, quantity in self.items), 2)

    def tax(self) -> float:
        amount = Decimal(str(self.subtotal())) * Decimal(str(self.tax_rate))
        return float(amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    def total(self) -> float:
        return round(self.subtotal() + self.tax(), 2)
