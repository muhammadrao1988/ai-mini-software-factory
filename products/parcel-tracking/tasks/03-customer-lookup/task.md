Add the module app/lookup.py with the function `track(tracker, tracking_number: str) -> dict`. `tracker` is a ParcelTracker from app/tracking.py. This is the view a customer sees. Do not change how ParcelTracker behaves.

Before the lookup, the tracking number is cleaned: surrounding whitespace is removed and letters are made upper case. So " pt00000001 " finds "PT00000001". If the cleaned number is unknown, raise KeyError.

The returned dict has exactly these keys:
- "tracking_number": the cleaned tracking number (str).
- "current_status": the same value as tracker.get_parcel(number)["status"].
- "current_place": the place of the last entry in the history, or None if there are no updates.
- "last_update": the time (datetime) of the last entry in the history, or None if there are no updates.
- "history": the full history as returned by tracker.get_history(number): a list of dicts with keys "status", "place", "time", oldest first.
The result must not show the shop or the recipient.
