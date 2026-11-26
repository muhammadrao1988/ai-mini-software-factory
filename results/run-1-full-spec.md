# Run 1: ten tasks, each with a full written spec

_2026-11-26, model: Claude Sonnet through the Claude Code sign-in, at most 3 tries per task._

| Task | Result | Tries | Time | Cost (API price) |
|---|---|---|---|---|
| 01-discount-code | Passed | 1 | 25 s | $0.17 |
| 02-remove-item | Passed | 1 | 17 s | $0.15 |
| 03-check-input | Passed | 1 | 21 s | $0.16 |
| 04-merge-lines | Passed | 1 | 22 s | $0.16 |
| 05-sales-tax | Passed | 1 | 22 s | $0.16 |
| 06-shipping | Passed | 1 | 18 s | $0.14 |
| 07-receipt | Passed | 1 | 16 s | $0.15 |
| 08-bulk-price | Passed | 1 | 28 s | $0.18 |
| 09-save-and-load | Passed | 1 | 25 s | $0.17 |
| 10-biggest-line | Passed | 1 | 19 s | $0.15 |

10 of 10 tasks passed. Total: 213 s, $1.60 at API prices (nothing is charged on a Claude subscription).

Every task passed on the first try. The retry step and the hidden tests were never needed in this run: the tasks
are small and the specs are complete, so this run says little about harder work.
