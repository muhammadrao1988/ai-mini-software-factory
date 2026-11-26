# What the hidden tests check

The agent that builds this task never sees this list or the tests.
You can: read it, and change the tests in `hidden/test_hidden.py` if a point is not what you want.

- ALLOWED_STATUSES must contain exactly the five courier statuses.
- After an update the parcel status must be the new status.
- History must be sorted oldest first and the current status must come from the newest time.
- Updates with the same time must stay in the order they were added.
- A parcel without updates must have an empty history and status registered.
- Adding to or reading history of an unknown tracking number must raise KeyError.
- A bad status or empty place must raise ValueError, a non-datetime time must raise TypeError, and nothing must be stored.
- The place must be stored without surrounding whitespace.
