"""In-memory parcel tracking."""

import datetime

ALLOWED_STATUSES = frozenset(
    {"picked_up", "in_transit", "out_for_delivery", "failed_attempt", "delivered"}
)


class ParcelTracker:
    """Keeps parcels in memory. Each instance has its own data and counter."""

    def __init__(self):
        self._parcels = {}
        self._counter = 0
        self._updates = {}

    def register_parcel(self, shop: str, recipient: str) -> str:
        shop = shop.strip() if isinstance(shop, str) else ""
        recipient = recipient.strip() if isinstance(recipient, str) else ""
        if not shop or not recipient:
            raise ValueError("shop and recipient must not be empty")
        self._counter += 1
        tracking_number = f"PT{self._counter:08d}"
        self._parcels[tracking_number] = {
            "tracking_number": tracking_number,
            "shop": shop,
            "recipient": recipient,
            "status": "registered",
        }
        self._updates[tracking_number] = []
        return tracking_number

    def get_parcel(self, tracking_number: str) -> dict:
        self._check_known(tracking_number)
        result = dict(self._parcels[tracking_number])
        history = self._sorted_updates(tracking_number)
        if history:
            result["status"] = history[-1]["status"]
        return result

    def add_status(
        self, tracking_number: str, status: str, place: str, time: datetime.datetime
    ) -> None:
        self._check_known(tracking_number)
        if not isinstance(status, str) or status not in ALLOWED_STATUSES:
            raise ValueError(f"invalid status: {status!r}")
        place = place.strip() if isinstance(place, str) else ""
        if not place:
            raise ValueError("place must not be empty")
        if not isinstance(time, datetime.datetime):
            raise TypeError("time must be a datetime.datetime")
        if self._has_delivered(tracking_number):
            raise ValueError("parcel is already delivered")
        self._updates[tracking_number].append(
            {"status": status, "place": place, "time": time}
        )

    def get_history(self, tracking_number: str) -> list:
        self._check_known(tracking_number)
        return [dict(u) for u in self._sorted_updates(tracking_number)]

    def list_parcels(self, shop: str, status: str | None = None) -> list:
        if status is not None and not (
            isinstance(status, str)
            and (status == "registered" or status in ALLOWED_STATUSES)
        ):
            raise ValueError(f"invalid status: {status!r}")
        if not isinstance(shop, str):
            return []
        shop = shop.strip()
        numbers = sorted(
            (n for n, p in self._parcels.items() if p["shop"] == shop),
            key=lambda n: int(n[2:]),
        )
        result = [self.get_parcel(n) for n in numbers]
        if status is not None:
            result = [p for p in result if p["status"] == status]
        return result

    def is_delivered(self, tracking_number: str) -> bool:
        self._check_known(tracking_number)
        return self._has_delivered(tracking_number)

    def _has_delivered(self, tracking_number) -> bool:
        return any(u["status"] == "delivered" for u in self._updates[tracking_number])

    def _check_known(self, tracking_number) -> None:
        try:
            known = tracking_number in self._parcels
        except TypeError:
            known = False
        if not known:
            raise KeyError(tracking_number)

    def _sorted_updates(self, tracking_number) -> list:
        # sorted() is stable, so updates with equal times keep insertion order.
        return sorted(self._updates[tracking_number], key=lambda u: u["time"])
