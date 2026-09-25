# Benchmark Remediation Summary

## 1. Baseline

- baseline product commit: `0dd6fda07abd028018514221ccbb592deb0b6842`
- benchmark documentation commit: `b8d7df6de0e4a2722e52b233ad91f9d02311e3e3`
- remediation branch: `phase-6-remediation`
- host: macOS 12.7.6, Intel Core i5-5250U, 4 logical CPUs, 8 GiB RAM
- environment: Python 3.10.17, Node 22.23.2, SQLite 3.47.1, NumPy 2.2.6
- seed: `20260924`
- historical evidence: `benchmark-results/`
- after evidence: `benchmark-results/remediation/`

## 2. Defects Fixed

### Fiscal period

The detector now evaluates `fiscal_date - posted_date` within the inclusive configured window, covering the fiscal date and preceding days while excluding future dates. Synthetic recall/F1 changed from `0.5/0.667` to `1.0/1.0`.

### Missing data

Blank account/preparer identities no longer enter rare-pair frequency calculations. Missingness now reduces semantic coverage (1.00 → 0.08 from 0% to 90%) without creating positive deterministic risk rows in the controlled fixture.

### Severity integrity

SQLite now rejects updates to `exceptions.severity` after analysis insertion. Direct high→low tampering is blocked, and the high-severity second-review rule remains active.

### Monetary-line validation

Rows with no populated `amount`, `debit`, or `credit` field are rejected and retained in `rejected_rows`. Explicit zero and signed negative `amount` values remain accepted under the documented signed-amount contract.

### Ground truth/documentation

`docs/GROUND_TRUTH.md` distinguishes direct detection, proxy cues, misses, and unobservable labels. The README no longer claims five planted anomalies or treats `off_hours` as a valid date-only detector miss.

### API contract

`GET /api/imports/{id}/reconciliation` now returns the canonical structured 404 for a missing resource.

## 3. Algorithmic Changes

### Reversal detector

The old account/amount bucket scan was replaced with a sorted date-window index and range-minimum lookup. The selected counterpart remains the first eligible row in original ledger order, preserving the legacy semantic policy while avoiding the dense-bucket quadratic scan.

### Analysis safety guard

`analyze()` now rejects populations above `MAX_ANALYSIS_POPULATION = 100_000` before creating a model run. The error explicitly says import data is retained and distinguishes import acceptance from analysis safety. The 100k boundary was measured on this host; it is not a universal hardware guarantee.

### Other measured changes

- Precomputed account peer medians/MAD remove another dense-account quadratic path.
- Semantic candidate generation and `exhaustive: false` disclosure were intentionally preserved; no ANN or model-quality claim was added.
- Benchmark output now supports a separate remediation directory.

## 4. Regression Coverage

- New fiscal/missing-data semantics: `tests/test_remediation_semantics.py`
- New severity boundary and second-review preservation: `tests/test_remediation_governance.py`
- New monetary-line contract: `tests/test_remediation_import_contract.py`
- Reversal equivalence and dense-index path: `tests/test_reversal_optimization.py`
- Semantic approximation/provenance contract: `tests/test_remediation_semantic_contract.py`
- Updated API 404 regression: `tests/test_api_contracts.py`
- Existing import, workflow, operations, API, semantic, and browser tests remain.
- Full Python suite: **47 passed, 0 failures, 7 subtests, 1 upstream deprecation warning**.
- Frontend typecheck/build: passed.
- Browser workflow: **1 Playwright test passed** using the approved existing external Chromium.

## 5. Before / After Correctness

| Area | Before | After | Evidence |
|---|---:|---:|---|
| Fiscal window recall | 0.5 | 1.0 | remediation/correctness.json |
| Missing 10% identity exceptions | 2 | 0 | remediation/correctness.json |
| Direct severity mutation | Allowed | Blocked | remediation/governance.json |
| Empty monetary row | Accepted | Rejected | regression test and remediation/correctness.json |
| Reconciliation missing resource | 400 | 404 | API regression and remediation/governance.json |
| Reversal counterpart policy | Legacy first eligible | Equivalent | `tests/test_reversal_optimization.py` |

## 6. Before / After Performance

| Workload | Before | After | Change |
|---|---:|---:|---|
| Dense adversarial 1k analysis | 3.14s | 0.09s | ~35× faster |
| Dense adversarial 2k analysis | 12.77s | 0.22s | ~58× faster |
| Dense adversarial 5k analysis | 65.04s | 0.57s | ~114× faster |
| Dense adversarial 10k analysis | 433.61s | 0.94s | ~459× faster |
| Dense adversarial 50k analysis | not run | 15.69s | first measured safe point |
| Normal 10k analysis | 15.42s | 4.45s | ~3.5× faster |
| Similarity 100k/64-dim | 17.29s / 398 MB | unchanged architecture | remains dense scan |
| Import 500k | 795.48s | unchanged architecture | import-only evidence |

The after API similarity p95 at 10k was 1.216s in the bounded remediation run; it is not treated as an improvement over the historical p95 because the request populations/environment differ and the full live-model path remains unavailable.

## 7. Governance

| Control | Before | After | Evidence |
|---|---|---|---|
| High-severity second review | PASS for normal paths | PASS | remediation/governance.json |
| Direct severity tampering | Allowed | Blocked at SQLite boundary | remediation/governance.json |
| Review lock/reopen events | Persistent event history | Unchanged/pass | remediation/governance.json |
| API missing-resource consistency | 400 for reconciliation | 404 | API regression |
| Backup/restore | Pass | Pass | remediation/governance.json |
| API abuse/headers/uploads | Pass in bounded matrix | Pass in bounded matrix | remediation/governance.json |

## 8. Semantic Engine

- Fixed-vector mechanics remain available and reproducible.
- Candidate generation remains explicitly approximate: `exhaustive: false`, candidate IDs, limits, and tie-break metadata are retained.
- The 1k fixed-vector candidate recall remains `0.0000/0.0674/0.0997` at 1/5/10; this was not silently changed into an ANN or exhaustive claim.
- Live Ollama model quality, digest, dimensions, latency, cache, and calibration were not measured because Ollama was unavailable.
- No model superiority, calibration, or real-audit effectiveness claim is made.

## 9. Remaining Limitations

- Dense similarity remains a full in-memory scan and can become expensive with real embedding dimensions.
- Live semantic model quality is unvalidated.
- 250k/500k end-to-end analysis was not run; only import was measured. The 100k analysis guard is measured-host evidence, not a universal guarantee.
- Gitleaks was not run because the local Docker daemon was unavailable.
- Synthetic detector results are not real-audit effectiveness evidence.
- Network/multi-user authentication, CSRF, TLS, tenancy, formal model validation, and firm-specific formal workpaper formats remain intentionally deferred.

## 10. Current Readiness

| Area | Classification |
|---|---|
| Ingestion | DEMONSTRATED for bounded synthetic CSV/XLSX inputs |
| Lineage | DEMONSTRATED |
| Reconciliation | DEMONSTRATED |
| Deterministic analytics | PARTIALLY DEMONSTRATED |
| Missing-data handling | DEMONSTRATED for controlled fixture; real distributions unvalidated |
| Governance | DEMONSTRATED for tested domain/API/database paths |
| API | DEMONSTRATED for bounded matrix; full contract breadth still finite |
| Frontend | DEMONSTRATED by Playwright; accessibility breadth incomplete |
| Reversal scalability | DEMONSTRATED through 50k dense synthetic bucket after remediation |
| Semantic retrieval | LABORATORY ONLY |
| Live model | UNVALIDATED |
| Reproducibility | DEMONSTRATED for normalized artifacts |
| Security | PARTIALLY DEMONSTRATED; Gitleaks unavailable |
| Real audit effectiveness | UNVALIDATED |
| Network deployment | INTENTIONALLY DEFERRED |

## 11. Remaining Validation Required

- Authorized labelled audit population with explicit detector labels and missingness strata.
- Live Ollama model digest/dimensions and token/semantic/max retrieval evaluation.
- Candidate-recall study on representative vectors before considering ANN or exhaustive serving.
- Heterogeneous 250k/500k analysis or an explicit architecture decision.
- Gitleaks in a functioning CI/container environment.
- Broader accessibility and cross-browser testing.
- Firm-approved workpaper format and retention/security review.

## 12. Next Engineering Phase

Run the authorized labelled-population and live-model benchmark before changing semantic architecture; the highest unresolved risk is analytical validity, not additional feature work.
