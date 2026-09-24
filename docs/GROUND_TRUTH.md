# Demo Ground-Truth Semantics

`examples/demo-ground-truth.csv` is a small synthetic fixture, not a claim about real-audit effectiveness. The current file contains six labelled rows. The labels are interpreted as follows.

| Label | Business meaning | Required source information | Observable with current schema? | Detector status |
|---|---|---|---|---|
| `off_hours` | Posting occurred outside normal hours | Posting timestamp/time-of-day | **No** — only `posting_date` is stored | Unobservable, not a valid missed-detector case |
| `round_amount` | Amount meets the configured round-number threshold | Amount, account context | Yes | Direct `round_amount` cue |
| `benford_vendor` | Synthetic vendor/account anomaly intended to be surfaced through peer context | Amount, account, vendor/preparer context | Partially | No per-entry Benford detector exists; two rows are `robust_account_peer_outlier` proxies, one is only a rare-pair proxy, and one is missed |

The deterministic Benford calculation is a population-level indicator. It does not identify an individual fraudulent or anomalous row. Therefore `benford_vendor` must not be reported as a directly detected Benford detector result.

On the benchmarked baseline (`0dd6fda`), one round-amount row was directly detected, two `benford_vendor` rows were peer-outlier proxies, one additional `benford_vendor` row was surfaced only as a rare-pair cue, one was missed, and the off-hours label was unobservable. The historical measurements remain in `benchmark-results/`; remediation reports use the same vocabulary.

When adding future ground truth, every label must declare:

1. business meaning;
2. required source fields;
3. whether the current schema can observe it;
4. direct detector, proxy cue, or unobservable classification;
5. expected treatment in precision/recall reporting.

A detector miss and an unobservable label must never be combined into one success rate.
