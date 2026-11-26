Change `ParcelTracker.add_status` in app/tracking.py. Once a parcel has an update with status "delivered" in its history, every later call to add_status for that parcel must raise ValueError. This applies to every status, including another "delivered", and to every time, also a time earlier than the delivery. Nothing is stored when this happens. The checks from the earlier task still run first in the same order (unknown number -> KeyError, bad status -> ValueError, empty place -> ValueError, time not a datetime -> TypeError). After those checks, check for delivery and raise ValueError.

Also add the method `is_delivered(tracking_number: str) -> bool`. It returns True if the parcel has a "delivered" update in its history, and False if not. An unknown tracking number raises KeyError.

Everything else stays the same. Other parcels are not affected.
