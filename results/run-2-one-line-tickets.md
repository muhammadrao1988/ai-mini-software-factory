# Run 2: the same ten tasks, each written as a one-line ticket

_2026-11-26, model: Claude Sonnet through the Claude Code sign-in, at most 3 tries per task. Same hidden tests as run 1._

| Task | Result | Tries | Time | Cost (API price) |
|---|---|---|---|---|
| 01-discount-code | Passed | 1 | 23 s | $0.17 |
| 02-remove-item | Passed | 1 | 18 s | $0.15 |
| 03-check-input | Passed | 2 | 38 s | $0.31 |
| 04-merge-lines | Passed | 2 | 33 s | $0.29 |
| 05-sales-tax | Passed | 1 | 27 s | $0.18 |
| 06-shipping | Passed | 2 | 41 s | $0.30 |
| 07-receipt | Passed | 1 | 32 s | $0.08 |
| 08-bulk-price | Passed | 1 | 23 s | $0.16 |
| 09-save-and-load | Passed | 2 | 31 s | $0.29 |
| 10-biggest-line | Passed | 1 | 18 s | $0.15 |

10 of 10 tasks passed. Total: 284 s, $2.08 at API prices (nothing is charged on a Claude subscription).

On the first try, 6 of 10 passed. In the other 4, every test the agent wrote for itself passed, but the hidden
tests found 10 wrong points. After one short note for each wrong point, all 4 passed on the second try.

| Task | The agent's own tests, try 1 | Hidden tests, try 1 | What was wrong |
|---|---|---|---|
| 03 Refuse bad input | 18 passed | 1 failed | A quantity like 1.5 was accepted |
| 04 Merge same items | 5 passed | 2 failed | The same item at a different price was accepted |
| 06 Shipping | 5 passed | 3 failed | Shipping was not charged as the hidden tests expect (below 50.00, at 49.99, empty cart) |
| 09 Save and load | 5 passed | 4 failed | Broken saved data was not refused |
