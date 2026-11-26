# What the hidden tests check

The agent that builds this task never sees this list or the tests.
You can: read it, and change the tests in `hidden/test_hidden.py` if a point is not what you want.

- A new parcel must not count as delivered.
- A parcel with a delivered update must count as delivered.
- Any update after delivery must raise ValueError and store nothing.
- An update with a time before the delivery must also raise ValueError.
- is_delivered with an unknown tracking number must raise KeyError.
- Delivering one parcel must not block updates to another parcel.
- A failed delivery attempt must still allow more updates.
