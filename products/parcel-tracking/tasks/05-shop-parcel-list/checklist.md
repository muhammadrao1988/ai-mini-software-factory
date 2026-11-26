# What the hidden tests check

The agent that builds this task never sees this list or the tests.
You can: read it, and change the tests in `hidden/test_hidden.py` if a point is not what you want.

- A shop must see only its own parcels, sorted by tracking number.
- A shop without parcels must get an empty list.
- The shop name must match after trimming spaces, but upper and lower case must count.
- The status filter must return only parcels with that current status.
- The filter must use the newest status, not an older one.
- An unknown status filter must raise ValueError.
- Changing a listed dict must not change the stored parcel.
- Registering and delivery locking must still work after adding the list.
