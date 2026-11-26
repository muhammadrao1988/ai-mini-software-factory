# What the hidden tests check

The agent that builds this task never sees this list or the tests.
You can: read it, and change the tests in `hidden/test_hidden.py` if a point is not what you want.

- The first registered parcel must get the tracking number PT00000001.
- Tracking numbers must count up by one for each new parcel.
- get_parcel must return the shop, recipient and the status registered.
- An unknown tracking number must raise KeyError.
- An empty or whitespace-only shop or recipient must raise ValueError.
- A failed registration must not use up a tracking number.
- Names must be stored without surrounding whitespace and each tracker must count on its own.
- Changing the dict from get_parcel must not change the stored parcel.
