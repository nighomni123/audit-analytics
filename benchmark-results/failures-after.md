# Failures After Remediation

This report records only issues still evidenced after the Phase 6 fixes. Historical defects are preserved in `failures.md` and the committed baseline report.

## CONFIRMED DEFECT

### API 404 contract was corrected

The missing reconciliation endpoint now returns 404; this item is closed, not remaining.

### Ground-truth terminology is clarified

The six-row fixture semantics are documented in `docs/GROUND_TRUTH.md`; direct/proxy/unobservable distinctions are now explicit.

## CONTROL GAP

### Direct database writers remain outside application authentication

SQLite now blocks severity mutation and protects review/status history, but a user with filesystem/database access can still alter unrelated database structures or delete the database file. The application is intentionally local-only and does not provide cryptographic database tamper evidence.

- **Evidence:** `benchmark-results/remediation/governance.json`
- **Impact:** filesystem-level tampering is outside the current threat boundary.
- **Mitigation:** use OS permissions, encrypted storage, backups, and firm controls.
- **Reason unresolved:** cryptographic database sealing is not part of the local-first MVP.
- **Next validation:** firm threat-model review and filesystem-permission test.

## PERFORMANCE LIMITATION

### Similarity remains a dense scan

The historical 100k/64-dimension run used approximately 398 MB and 17.29 seconds. The architecture remains full in-memory cosine retrieval, not ANN or paging.

- **Evidence:** `benchmark-results/performance-similarity.json`
- **Impact:** real embedding dimensions and concurrent requests can exhaust local memory/latency budgets.
- **Mitigation:** bounded model use, measured capacity planning, and pagination only where evidence supports it.
- **Reason unresolved:** ANN architecture is intentionally deferred.
- **Next validation:** representative-dimension latency/memory and retrieval-quality study.

### 250k/500k analysis remains unmeasured

Import succeeds through 500k rows, but end-to-end analysis was not run at those sizes. The application now blocks analysis above 100k on the measured profile.

- **Evidence:** `benchmark-results/performance-scale.json`, `src/audit_analytics/analytics.py`
- **Impact:** import acceptance must not be interpreted as analysis acceptance.
- **Mitigation:** explicit safety guard and separate import/analysis status.
- **Reason unresolved:** no safe measured analysis envelope for 250k/500k.
- **Next validation:** heterogeneous 250k/500k profiling and an explicit capacity decision.

## ANALYTICAL LIMITATION

### Bounded semantic candidate recall remains low

The 1k fixed-vector result remains `0.0000/0.0674/0.0997` at 1/5/10. Candidate provenance and `exhaustive: false` are preserved.

- **Evidence:** `benchmark-results/remediation/semantic.json`
- **Impact:** semantic profile metrics can omit true nearest neighbours.
- **Mitigation:** no hidden exhaustive/ANN claim; candidate IDs and limits are persisted.
- **Reason unresolved:** changing candidate generation requires labelled quality evidence.
- **Next validation:** authorized labelled retrieval benchmark before ANN/exhaustive changes.

### Model quality is unvalidated

Ollama was unavailable, so no live model digest, dimensions, latency, cache, calibration, or quality result is claimed.

- **Evidence:** `benchmark-results/baseline.json`, `benchmark-results/remediation/semantic.json`
- **Impact:** semantic layer remains laboratory-only.
- **Mitigation:** offline mechanics tests and explicit unavailability disclosure.
- **Reason unresolved:** no running local model/service or authorized labels.
- **Next validation:** fixed model/digest run on approved synthetic/authorized data.

## ENVIRONMENTAL LIMITATION

### Gitleaks was not executed

The local Docker daemon was unavailable.

- **Evidence:** `benchmark-results/security.json`
- **Impact:** no local secret-scan result is claimed.
- **Mitigation:** CI workflow is present; run it in a functioning container environment.
- **Reason unresolved:** environment service unavailable.
- **Next validation:** CI/container secret scan.

## UNVALIDATED

### Real-audit effectiveness

Synthetic detector precision/recall and seeded samples do not establish real audit effectiveness, false-positive acceptability, calibration, or fraud detection.

- **Evidence:** `benchmark-results/remediation-summary.md`
- **Impact:** readiness must remain laboratory/partial for analytical claims.
- **Mitigation:** no real-data claims; require authorized labelled benchmark.
- **Reason unresolved:** no authorized population is available in this task.
- **Next validation:** firm-approved labelled population and documented methodology.

### Broader accessibility and cross-browser coverage

The current Playwright workflow passes desktop/mobile persisted flow, but full assistive-technology, browser-matrix, and accessibility conformance testing was not completed.

- **Evidence:** `benchmark-results/baseline.json`
- **Impact:** frontend is demonstrated functionally, not accessibility-certified.
- **Mitigation:** native labels, keyboard controls, and persisted browser test.
- **Reason unresolved:** scope/tooling not available in the current environment.
- **Next validation:** browser matrix plus automated/manual accessibility review.

## INTENTIONALLY DEFERRED

- Network/multi-user authentication, SSO, TLS, CSRF, and tenancy isolation.
- Formal model validation, calibration, drift controls, and promotion.
- ANN/vector database architecture beyond measured evidence.
- Firm-specific Excel/PDF workpaper formats and digital signatures.
- 250k/500k end-to-end analysis as a supported product claim.
