"""Customer-facing parcel lookup."""


def track(tracker, tracking_number: str) -> dict:
    """Return the customer view of a parcel. Raises KeyError if unknown.

    The shop and recipient are never included.
    """
    if not isinstance(tracking_number, str):
        raise KeyError(tracking_number)
    number = tracking_number.strip().upper()
    status = tracker.get_parcel(number)["status"]
    history = tracker.get_history(number)
    last = history[-1] if history else None
    return {
        "tracking_number": number,
        "current_status": status,
        "current_place": last["place"] if last else None,
        "last_update": last["time"] if last else None,
        "history": history,
    }
