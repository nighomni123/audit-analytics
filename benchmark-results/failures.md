# Benchmark Failures and Limitations

This is an observation report, not a remediation patch. Product source was not changed to improve benchmark results.

## Confirmed defects / control gaps

### 1. `BUG` — preceding fiscal-period days are missed

`semantic`/deterministic fixture test with fiscal date `2026-03-31` and configured window `3` detected the exact date but missed `2026-03-30`: fiscal-period precision `1.0`, recall `0.5`, F1 `0.667`. The implementation compares `posted - fiscal_date >= 0`, so it does not cover the preceding days described by the documentation.

Evidence: `benchmark-results/correctness.json` → `deterministic.detectors[fiscal_period_end]`.

### 2. `CONTROL FAILURE` — missing preparer data can create a risk cue

At 10% controlled missingness, two rows with blank `preparer` received `rare_account_preparer_pair` and risk score `20`; at 0% the same population had zero exceptions. Missing data therefore can increase deterministic risk rather than only reducing applicability. This violates the benchmark criterion that missing data must not automatically increase risk.

Evidence: `benchmark-results/correctness.json` → `missing_data.rates[1].exception_rows`.

### 3. `CONTROL FAILURE` — direct severity mutation bypasses second-review policy

The review/status invariant blocks direct `exceptions.status` divergence, but a direct SQLite update of `exceptions.severity` to `low` was allowed. A local database writer could lower severity and then clear the item without the high-severity second-review path. This is outside normal API use, but relevant to the local-file threat model and governance claims.

Evidence: `benchmark-results/governance.json` → `governance.direct_severity_mutation`.

### 4. `BUG / DATA-INTEGRITY DECISION REQUIRED` — empty amount rows are accepted as zero

Malformed input containing neither debit, credit, nor amount was accepted as a zero-value ledger row; explicit zero amount was also accepted. Invalid IDs, dates, negative debit/credit, and simultaneous debit/credit were rejected with raw JSON preserved. Whether zero-value lines are valid must be specified; under the requested malformed-input policy, the “neither populated” case is not rejected.

Evidence: `benchmark-results/correctness.json` → `malformed_import`.

### 5. `DOCUMENTATION MISMATCH` — repository ground truth and README disagree

`examples/demo-ground-truth.csv` contains six positive rows, not five. The current run detected four of six: the round-amount row and two of four `benford_vendor` rows were surfaced through other cues; `JE035690` was only a rare-pair cue, `JE035744` was missed, and `off_hours` is unobservable because the schema stores dates rather than timestamps. The label name `benford_vendor` also does not correspond to a per-entry Benford detector.

Evidence: `benchmark-results/correctness.json` → `ground_truth`; independent probe in the benchmark session.

### 6. `API CONTRACT GAP` — missing reconciliation object returns 400 rather than 404

`GET /api/imports/999/reconciliation` returns structured `400 invalid_input` while other missing objects generally return 404. The endpoint is safe and non-mutating, but the error contract is inconsistent.

Evidence: `benchmark-results/governance.json` → `api_endpoint_matrix`.

## Performance limitations

### 7. `PERFORMANCE LIMITATION` — adversarial deterministic analysis is quadratic

Same-account/same-amount populations took `3.14s` at 1k, `12.77s` at 2k, `65.04s` at 5k, and `433.61s` at 10k. The reversal comparison is bucket-squared. The 250k/500k populations were import-tested only; running analysis on them would be unsafe on this host.

Evidence: `benchmark-results/performance-adversarial.json`.

### 8. `PERFORMANCE LIMITATION` — similarity is a full dense scan

Synthetic 64-dimensional retrieval took `8.58s` / `199 MB` at 50k and `17.29s` / `398 MB` at 100k. The ordinary API similarity path inherits this cost; 10k repeated API calls measured p95 `0.574s`. Real embedding dimensions and additional columns will consume more memory. No ANN/paging result was claimed.

Evidence: `benchmark-results/performance-similarity.json` and `performance.json` → `api_latency`.

### 9. `PERFORMANCE LIMITATION` — 250k/500k import is possible but slow

Import-only measurements accepted 250,000 rows in `288.62s` (866 rows/s, 118 MB DB) and 500,000 in `795.48s` (629 rows/s, 236 MB DB) on the recorded 4-core/8 GiB host. This demonstrates ingestion capacity, not end-to-end engagement capacity.

Evidence: `benchmark-results/performance-scale.json`.

## Analytical / evaluation limitations

### 10. `ANALYTICAL LIMITATION` — bounded semantic candidate recall is very low

On the fixed-vector 1,000-row approximation fixture, candidate recall was `0.0` at 1, `0.0674` at 5, and `0.0997` at 10; the calculation took `73.15s`. The bounded sampler can omit the true nearest neighbor. This is consistent with the explicit `exhaustive: false` disclosure, but means the production semantic profile is not a population-exhaustive nearest-neighbour method.

Evidence: `benchmark-results/semantic.json` → `approximation`.

### 11. `ANALYTICAL LIMITATION` — no live model quality evidence

Ollama is installed but unavailable at `127.0.0.1:11434`; no real model digest, dimensions, latency, cache, calibration, or model-specific retrieval was measured. All semantic quality numbers above use deterministic offline vectors or lexical paths.

### 12. `ANALYTICAL LIMITATION` — semantic fusion is not uniformly beneficial

On the fixed semantic fixture, semantic-only MRR was `0.929` versus token-only `0.732`, but max-fusion MRR was `0.810` and max Recall@1 was `0.357` versus semantic-only `0.464`. `max(token, cosine)` preserves candidates but can rank a strong lexical candidate above a semantically closer candidate. The result is fixture-specific and not model validation.

Evidence: `benchmark-results/semantic.json` → `retrieval`.

### 13. `ANALYTICAL LIMITATION` — clustering evidence is weak/illustrative

The fixed fixture produced two clusters with purity `0.722`; this is not a real-model or real-audit clustering result. The 11 unlabeled ledger rows and sparse/missing cases limit denominator quality.

## Test and environment gaps

- `gitleaks` was not executed because the local Docker daemon was unavailable; this is an environmental limitation, not a passing secret scan.
- No Ollama runtime benchmark was possible; no fake model result is reported.
- The existing suite is green (38 Python tests, one upstream Starlette/httpx deprecation warning), but it does not cover real-model quality, real-client distributions, or 250k/500k analysis.
- Synthetic detector precision/recall uses deliberately constructed populations and fixed defaults; it is not an effectiveness estimate for real audit work.

## Intentionally deferred boundaries

These are not counted as defects:

- network/multi-user authentication, SSO, TLS, CSRF, and tenant isolation;
- formal statistical model validation and model promotion;
- ANN/vector database migration beyond the measured local ceiling;
- firm-specific Excel/PDF workpaper formats and digital signatures.
