Add the method `list_parcels(shop: str, status: str | None = None) -> list` to `ParcelTracker` in app/tracking.py. Everything from the earlier tasks must keep working.

It returns a new list of dicts, one for each parcel of that shop. Each dict has the same form as the result of get_parcel (keys "tracking_number", "shop", "recipient", "status"). The list is sorted by tracking number, smallest first. Surrounding whitespace is removed from the shop argument before matching. After that the match is exact and case-sensitive. A shop with no parcels gives [].

If `status` is given (not None), only parcels whose current status (the same value as get_parcel's "status") equals it are returned. `status` must be "registered" or one of ALLOWED_STATUSES, otherwise raise ValueError. The dicts in the list are copies: changing them must not change the tracker.
