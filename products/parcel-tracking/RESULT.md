# Parcel tracking: what the factory built

_2026-11-26. Idea in, 5 tasks planned by the planner agent, built by 5 builder agents, one after the other._

| Task | Result | Tries | Time | Cost (API price) |
|---|---|---|---|---|
| 01-core-parcel-registry | Passed | 1 | 18 s | $0.15 |
| 02-add-status-updates | Passed | 1 | 36 s | $0.20 |
| 03-customer-lookup | Passed | 1 | 19 s | $0.15 |
| 04-lock-delivered-parcels | Passed | 1 | 24 s | $0.18 |
| 05-shop-parcel-list | Passed | 1 | 22 s | $0.17 |

5 of 5 tasks passed. Total: 119 s, $0.84 at API prices (nothing is charged on a Claude subscription).

After every task, the judge ran the hidden tests of **all** tasks so far (8, then 16, 23, 30 and 38 tests), so a
new task could not quietly break an old one.

The product is in `project/`: 119 lines of Python in `app/`, and 76 tests the agents wrote for themselves.

Try it:

```bash
cd products/parcel-tracking/project
uv run --python 3.14 python -c "
from datetime import datetime
from app.tracking import ParcelTracker
from app.lookup import track
t = ParcelTracker()
n = t.register_parcel('Karachi Books', 'Ali')
t.add_status(n, 'in_transit', 'Karachi hub', datetime(2026, 11, 26, 9, 0))
print(track(t, n))"
```
