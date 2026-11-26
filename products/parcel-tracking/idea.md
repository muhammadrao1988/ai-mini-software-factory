An online parcel tracking system. A shop registers a parcel and gets a tracking number. The courier adds status updates with a place and a time. A customer looks up a tracking number and sees the current status and the full history.

Five tasks for a parcel tracking system in plain Python. The core is the class ParcelTracker in app/tracking.py, which keeps all data in memory. Each task builds on the one before it:
1. Register parcels and get tracking numbers like PT00000001.
2. Let couriers add status updates with a place and a time, and keep the history sorted by time.
3. Add a customer lookup in app/lookup.py. It accepts sloppy input such as " pt00000001 " and shows the current status and the full history.
4. Reject any new update once a parcel has been delivered.
5. Let a shop list its own parcels, with an optional status filter.
Each task has a pytest file with 7 to 8 tests. The tests only use the names given in the specs. Nothing has been run yet, so neither the tests nor the specs have been tried against real code.
