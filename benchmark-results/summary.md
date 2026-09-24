# Audit Analytics Benchmark Report

## 1. Tested Commit

```text
commit: 0dd6fda07abd028018514221ccbb592deb0b6842
branch: main
date: 2026-09-24
host: macOS 12.7.6, Intel Core i5-5250U, 4 logical CPUs, 8 GiB RAM
Python environment: 3.10.17 (uv environment; system python3 was 3.12.10)
Node: v22.23.2; npm: 10.9.8
SQLite: 3.47.1; NumPy: 2.2.6
frontend lock: package-lock.json, SHA-256 b37fe514b9aa2e4f5571fcdca611c7bc01e5b28d46688423e73dc8ef79574c95
Python lock: uv.lock, SHA-256 839877d5727602dbb8a207dca33ff26ebb60f6e2a99c4b53cd7de10a92b8a4b7
Ollama: binary present; 127.0.0.1:11434 refused connection
seed: 20260924
```

No client data was used. Generated ledgers, databases, and evidence files were temporary and synthetic.

## 2. Executive Findings

### What works

- The locked Python environment was rebuilt from scratch with `uv sync --frozen --all-extras --group dev`.
- The complete Python suite passed: **38 tests, 0 failures, 3 subtests, 1 upstream Starlette/httpx deprecation warning**.
- Frontend `npm ci`, strict TypeScript, production build, and `npm audit --audit-level=high` passed with **0 frontend vulnerabilities**.
- The checked-in React browser workflow passed end-to-end at desktop and mobile sizes: **1 Playwright test passed**, including create/import/reconcile/acknowledge/configure/analyze/dashboard/investigate/review/reload/lock/export flow.
- Import preserves source row identity and raw JSON, rejects several malformed financial rows, blocks analysis before acknowledgement, and rejects exact duplicate files unless an explicit re-import is requested.
- Domain/API governance invariants are materially stronger than the pre-remediation implementation: second review, lock state, append-only history, role checks, and status synchronization were observed working.
- Two normalized runs produced identical ledger rows, risk results, sample selection, workpaper rows, and normalized manifest content.

### What is not proven

- Analytical usefulness on real audit populations is not established. Synthetic detector precision/recall describes configured mechanics, not audit effectiveness.
- The live semantic model path was not benchmarked because Ollama was unavailable. Fixed-vector results are mechanics tests only.
- Bounded semantic candidate retrieval lost most exact neighbors in the 1k fixed-vector test.
- Full deterministic analysis is not safe for 250k/500k populations on this host: an adversarial same-account/same-amount bucket is quadratic.
- Full similarity retrieval is a dense in-memory scan; 100k at 64 dimensions consumed about 398 MB and took 17.3 seconds before any real embedding dimension is considered.
- Gitleaks was not executed because the local Docker daemon was unavailable.
- A direct SQLite writer can change `exceptions.severity` even though direct status divergence is blocked.

### Readiness classification

| Area | Classification |
|---|---|
| Local CSV ingestion and lineage | Demonstrated for bounded synthetic inputs |
| Deterministic detector mechanics | Partially demonstrated; no real-population validation |
| Semantic profile | Laboratory only; fixed-vector/offline evidence |
| Governance through domain/API | Demonstrated for tested cases; direct DB tampering remains a boundary |
| React persisted workflow | Demonstrated by one real browser E2E |
| 10k/100k heterogeneous local workflow | Partially demonstrated |
| 250k/500k end-to-end analysis | Blocked/performance-limited |
| Real audit effectiveness | Unvalidated |
| Network/multi-user deployment | Intentionally deferred |

## 3. Correctness

### Test groups

| Test group | Tests | Passed | Failed | Skipped | Duration |
|---|---:|---:|---:|---:|---:|
| Python unit/integration | 11 | 11 | 0 | 0 | 1.20s |
| API contracts | 5 | 5 | 0 | 0 | 3.34s |
| Semantic | 12 | 12 | 0 | 0 | 4.89s |
| Workflow | 9 | 9 | 0 | 0 | 3.88s |
| Operations | 1 | 1 | 0 | 0 | 0.17s |
| Frontend typecheck | command gate | pass | 0 | — | 9.32s |
| Frontend build | command gate | pass | 0 | — | 11.92s |
| Browser E2E | 1 | 1 | 0 | 0 | 23.4s |

The one Python warning is the upstream Starlette `TestClient`/httpx deprecation, not a test failure.

### Import correctness

The generated malformed fixture produced **6 accepted and 5 rejected rows**. Rejections were observed for missing ID, invalid date, negative debit, negative credit, and simultaneous debit/credit. Rejected rows retained their source row and raw JSON. A generated minimal first-sheet XLSX imported one row successfully.

Important boundary: a row with neither debit, credit, nor amount was accepted as zero, and an explicit zero amount was accepted. If the supported GL contract forbids zero/empty-value lines, this is a data-integrity bug; the current implementation does not enforce that policy.

### Idempotence and lineage

- First import: accepted.
- Exact same bytes: rejected with the existing import ID.
- Explicit re-import: created a new import with `supersedes_import_id` pointing to the prior import.
- Modified source: created a new hash/import population.
- Analysis was blocked before acknowledgement and succeeded only after the documented override/acknowledgement path.

### Reconciliation

| Case | Result |
|---|---|
| Exact totals | analysis blocked before acknowledgement, then allowed |
| 0.004 debit difference | accepted within the 0.01 tolerance |
| Material mismatch | acknowledgement rejected; analysis remained blocked |
| Material mismatch with explicit override | allowed with note |

### Deterministic detectors

The following table is from deliberately constructed positive/borderline/negative populations with fixed defaults. The all-1.0 rows are mechanics checks, not real-world effectiveness claims.

| Detector | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| duplicate/repeated entry | 2 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| round amount | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| period end | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| weekend | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| rare account/preparer pair | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| reversal within 30 days | 2 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| robust account peer outlier | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| fiscal period end | 1 | 0 | 1 | 1.000 | 0.500 | 0.667 |

The fiscal result is a confirmed preceding-window defect: the exact configured date was detected, but the preceding day was missed.

The repository ground-truth file contains six rows:

| Label | Labels | Detected through named mapping | Missed |
|---|---:|---:|---:|
| `round_amount` | 1 | 1 | 0 |
| `benford_vendor` mapped to peer-outlier proxy | 4 | 2 | 2 |
| `off_hours` | 1 | 0 | 1 |

A broader “any risk cue” view detects four of six because `JE035690` is surfaced only as a rare-pair cue. The README’s “4 of 5” statement is stale. `off_hours` is not observable with date-only posting data. `benford_vendor` is not a per-entry Benford detector in the current implementation.

On the 400-row demo, the run produced 148 exceptions, score range 20–55, mean 24.12, and severity counts of 137 low / 11 medium / 0 high. The highest observed score was below the high-severity threshold, so the demo does not demonstrate high-severity prioritization quality.

### Materiality and sampling

Materiality changed bands but did not change risk scores or severities in the boundary fixture:

```text
scores_unchanged: true
same seed + same population -> same sample: true
duplicate sample items: false
```

The sample’s `risk_count=0` path still retained automatically included high-risk items, as designed; it was not a random-only sample.

### Missing data

| Missingness | Exceptions | Semantic coverage |
|---:|---:|---:|
| 0% | 0 | 1.00 |
| 10% | 2 | 0.89 |
| 25% | 0 | 0.755 |
| 50% | 0 | 0.54 |
| 90% | 0 | 0.08 |

At 10%, the two exceptions were blank-preparer rows receiving `rare_account_preparer_pair`. Missing data therefore did not only reduce coverage; it could increase deterministic risk. This is a control/data-quality defect.

## 4. Semantic Engine

### Availability

Ollama was not running. No real model digest, dimensions, latency, cache, or model-specific quality result is reported.

### Offline fixed-vector retrieval

| Mode | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR |
|---|---:|---:|---:|---:|---:|
| Token-only | 0.321 | 0.786 | 0.857 | 0.893 | 0.732 |
| Semantic-only fixed vectors | 0.464 | 1.000 | 1.000 | 1.000 | 0.929 |
| `max(token, semantic)` | 0.357 | 0.929 | 1.000 | 1.000 | 0.810 |

The fixture contains 14 targets with expected related groups. These values are fixed-vector mechanics, not model validation. The max policy preserved candidates but did not uniformly improve ranking over semantic-only on this fixture.

### Bounded candidate accuracy

For a 1,000-entry fixed-vector population, the production bounded candidate sampler achieved:

```text
candidate Recall@1: 0.0000
candidate Recall@5: 0.0674
candidate Recall@10: 0.0997
calculation time: 73.15s
```

This is the most important semantic limitation: bounded candidate retrieval can omit the true nearest neighbor. The persisted `exhaustive: false` disclosure is accurate.

### Profile, cache, and clustering

- Profile coverage on the 26-row semantic fixture: `0.9615` with one missing narration.
- Cluster count: 2; fixed-fixture purity: `0.722`.
- First profile: 25 embedded, 0 cached.
- Identical second profile: 0 embedded, 25 cached.
- One modified narration: 1 embedded, 24 cached.
- Changed model digest: 25 embedded, 0 cached.
- The fixed-vector profile was deterministic in repeated mechanics tests; no live model quality was measured.

## 5. Performance

### Import-only scale

| Rows | Seconds | Rows/s | DB bytes |
|---:|---:|---:|---:|
| 100 | 0.24 | 417 | 4 KiB |
| 1,000 | 1.12 | 889 | 4 KiB |
| 10,000 | 12.81 | 780 | 4.7 MiB |
| 50,000 | 94.64 | 528 | 22.4 MiB |
| 100,000 | 112.30 | 890 | 45.0 MiB |
| 250,000 | 288.62 | 866 | 112.5 MiB |
| 500,000 | 795.48 | 629 | 225.0 MiB |

These are heterogeneous generated CSVs on a 4-core/8 GiB Intel MacBook Air. Ingestion capacity is demonstrated; end-to-end analysis capacity is not.

### Pipeline

| Population | Analysis | With isolation | API similar p50/p95 |
|---:|---:|---:|---:|
| 1,000 | 0.267s | 0.368s | 0.078s / 0.094s |
| 10,000 | 15.419s | 23.884s | 0.532s / 0.574s |

The generated 10k population flags all rows in this fixture, so exception insertion is also part of the measured cost.

### Similarity search

| Entries | Seconds | Peak Python bytes |
|---:|---:|---:|
| 50,000 | 8.582 | 199,265,704 |
| 100,000 | 17.286 | 397,972,340 |

The benchmark used 64 dimensions and identical synthetic vectors. A real embedding dimension, larger narratives, and concurrent requests will increase memory and latency.

### Adversarial analysis ceiling

| Same-account/same-amount rows | Analysis seconds |
|---:|---:|
| 1,000 | 3.14 |
| 2,000 | 12.77 |
| 5,000 | 65.04 |
| 10,000 | 433.61 |

The near-quadratic growth is caused by the reversal comparison bucket. The 250k/500k import-only results must not be interpreted as 250k/500k analysis support.

## 6. Governance

| Control | Domain | API | CLI | Browser |
|---|---|---|---|---|
| Analysis acknowledgement | PASS | PASS | PASS | PASS |
| Reviewer role | PASS | PASS | PASS | PASS/inherited UI |
| Required note | PASS | PASS | PASS | PASS |
| High-severity second review | PASS | PASS | PARTIAL — shared function, not separately exercised in CLI benchmark | PARTIAL — E2E used follow-up |
| Locked review rejection | PASS | PASS | PARTIAL | PASS |
| Locked assignment rejection | PASS | PASS | PARTIAL | PASS/inherited UI |
| Append-only review/audit history | PASS/direct DB | N/A | N/A | N/A |
| Direct status divergence | PASS/blocked | N/A | N/A | N/A |
| Direct severity mutation | **CONTROL GAP: allowed** | N/A | N/A | N/A |

The API endpoint matrix exercised 37 valid/invalid route cases. Structured errors were returned for invalid IDs, enums, ranges, queries, and host headers. A missing reconciliation object returned 400 rather than the more consistent 404 used by other missing-object endpoints.

Concurrency tests showed two concurrent reviews completing without lost history, and two concurrent lock attempts producing one success/one state conflict. A separate bounded writer test observed fail-loud `database is locked`; there is no retry queue or distributed coordination.

## 7. Security

- `uv lock --check`: pass.
- Clean `uv sync --frozen --all-extras --group dev`: pass.
- `pip-audit --local`: no known vulnerabilities; the local project itself is not on PyPI and is reported as skipped.
- `npm audit --audit-level=high`: 0 vulnerabilities.
- Frontend license metadata policy: pass.
- Python license gate: pass for the locked set.
- TrustedHost: invalid host returned 400.
- Wildcard CORS: no CORS allow-origin header.
- Security headers: CSP, `X-Frame-Options: DENY`, `X-Content-Type-Options`, referrer policy, and request ID observed.
- Unsupported extension upload: 400.
- Traversal-style filename: sanitized to basename; no outside artifact observed.
- Long `.csv` filename: accepted after basename sanitization; this is a usability/DoS boundary, not a demonstrated traversal escape.
- Gitleaks: **not executed** because Docker could not connect to the local daemon.
- Network authentication, CSRF, TLS, and tenant isolation remain intentionally unsupported.

## 8. Reproducibility

| Artifact | Expected deterministic? | Observed? |
|---|---|---|
| Normalized ledger | Yes | PASS |
| Deterministic risk results/reasons/evidence | Yes | PASS |
| Semantic vectors/profile mechanics | Yes for fixed config | PARTIAL; live model unavailable |
| Semantic results | Yes for fixed config | PARTIAL; fixed-vector tests only |
| Sample selection with same seed | Yes | PASS |
| Workpaper rows | Yes, excluding timestamps | PASS |
| Normalized manifest content | Yes, excluding timestamps/temp evidence paths | PASS |
| Browser state after reload | Yes for tested workflow | PASS |

The reproducibility harness excludes timestamps, generated run IDs, and temporary evidence paths. It does not claim that timestamped manifests or live model provenance are byte-identical.

## 9. Product Readiness

### A. Proven capabilities

- Bounded local CSV import with raw row/evidence lineage and explicit duplicate versioning.
- Deterministic detector mechanics and configurable materiality bands on synthetic data.
- Acknowledgement-gated analysis and shared review governance through domain/API paths.
- Persisted React workflow through investigation, review, reload, lock, and export.
- Locked install, dependency lock checks, local backup/restore procedure, and normalized reproducibility.
- Loopback-only operation with CSP, TrustedHost, upload validation, and no observed path traversal.

### B. Current limitations

- Analytical effectiveness is not validated on authorized real audit populations.
- Missing preparer data can create a risk cue; zero/empty amounts need a policy decision.
- Fiscal-period preceding days are missed.
- Direct severity mutation can bypass the high-severity review rule for a local DB writer.
- Bounded semantic retrieval has very low candidate recall on the tested 1k case.
- Live Ollama/model quality and provenance are unmeasured.
- Dense similarity and reversal analysis create hard scale ceilings.
- Gitleaks and real browser visual accessibility/cross-browser validation remain incomplete.

### C. Highest-priority engineering work

1. Correct the fiscal-period window and define/reject empty/zero financial lines.
2. Ensure missing preparer/other missing identity fields reduce applicability rather than create `rare_account_preparer_pair` cues.
3. Make severity immutable/derived or otherwise protect the high-severity control from direct database mutation.
4. Replace or bound the reversal bucket scan before supporting heterogeneous populations above the measured safe size.
5. Decide and benchmark ANN/paging for similarity only after collecting labelled retrieval quality evidence.
6. Run Ollama with a fixed model digest/dimension and evaluate token, semantic, and max retrieval on an authorized labelled set.
7. Correct the ground-truth file/README semantics and add regression cases for the observed misses.
8. Run Gitleaks in a functioning CI/container environment and add the resulting evidence to the release gate.

### D. Next benchmark

Before using this on an authorized real engagement, collect:

- a representative, permission-approved labelled ledger population with explicit detector labels and missingness strata;
- a fixed Ollama model digest, dimensions, cold/warm/cached latency, and provenance;
- token-only, semantic-only, max-fusion, and bounded-vs-exhaustive retrieval results on that population;
- 10k/50k/100k heterogeneous and adversarial performance with p50/p95 latency, memory, database size, and failure thresholds;
- direct-DB tamper tests for severity, assignment, evidence, and review state;
- a functioning Gitleaks scan and a repeatable browser/accessibility run.

Until that evidence exists, the appropriate classification is **laboratory-only for analytical/model claims and partially demonstrated for local workflow engineering**, not production audit readiness.
