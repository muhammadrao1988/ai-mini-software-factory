Extend the class `ParcelTracker` in app/tracking.py. Everything from the earlier task must keep working.

Add the module-level constant `ALLOWED_STATUSES` in app/tracking.py. It is a set (or frozenset) of exactly these strings: "picked_up", "in_transit", "out_for_delivery", "failed_attempt", "delivered".

Method `add_status(tracking_number: str, status: str, place: str, time: datetime.datetime) -> None`: the courier adds a status update to a parcel. Check the input in this order:
1. If the tracking number is unknown, raise KeyError.
2. If status is not in ALLOWED_STATUSES, raise ValueError. "registered" is not allowed as an update.
3. If place is empty or only whitespace, raise ValueError.
4. If time is not a datetime.datetime object, raise TypeError.
Surrounding whitespace is removed from place before it is stored. A failed call stores nothing.

Method `get_history(tracking_number: str) -> list`: returns a new list of dicts, one per update. Each dict has exactly the keys "status", "place", "time" (time is the datetime object that was given). The list is sorted by time, oldest first. Updates with the same time stay in the order they were added. A parcel with no updates returns []. An unknown tracking number raises KeyError.

Change `get_parcel`: "status" is now the status of the last entry in the sorted history (the newest time; if several have the same time, the one added last). If there are no updates it is still "registered".
