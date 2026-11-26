# What the hidden tests check

The agent that builds this task never sees this list or the tests.
You can: read it, and change the tests in `hidden/test_hidden.py` if a point is not what you want.

- A parcel without updates must show status registered and None for place and time.
- The result must show the newest status, place and time plus the full history.
- An update added late with an older time must not become the current place.
- A lower case number with spaces around it must find the parcel.
- An unknown tracking number must raise KeyError.
- The customer view must contain exactly the five agreed keys.
- The tracker methods must keep working the same after track is used.
