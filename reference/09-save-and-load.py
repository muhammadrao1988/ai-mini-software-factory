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

    def to_dict(self) -> dict:
        return {"items": [{"name": n, "price": p, "quantity": q} for n, p, q in self.items]}

    @classmethod
    def from_dict(cls, data: dict) -> "Cart":
        if not isinstance(data, dict) or "items" not in data:
            raise ValueError('data has no "items"')
        cart = cls()
        for item in data["items"]:
            try:
                cart.add_item(item["name"], item["price"], item["quantity"])
            except (KeyError, TypeError) as problem:
                raise ValueError(f"bad item: {item!r}") from problem
        return cart
