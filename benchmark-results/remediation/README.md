# Remediation Benchmark Evidence

This directory is the after-remediation evidence set for `phase-6-remediation`, compared with immutable historical evidence in the parent `benchmark-results/` directory.

## Artifacts

- `baseline.json` — remediated environment, 47-test suite, frontend build, browser E2E, audits, and policy results.
- `correctness.json` — corrected fiscal/missing-data behavior, import contracts, idempotence, reconciliation, materiality/sampling, and export integrity.
- `semantic.json` — fixed-vector mechanics, cache/profile behavior, and unchanged candidate-approximation limitation.
- `performance.json` — after pipeline/API timings plus dense adversarial analysis.
- `performance-adversarial-after.json` — 1k/2k/5k/10k/20k/50k reversal/safety measurements.
- `governance.json` — domain/API matrix, immutable severity, second review, lock, upload/host/header, concurrency, and backup checks.
- `reproducibility.json` — normalized two-run comparison.
- `security.json` — final dependency and policy checks.
- `remediation-summary.md` — required before/after readiness report.
- `failures-after.md` — remaining evidence-backed limitations.

## Measured reversal improvement

Historical dense same-account/same-amount analysis: 1k 3.14s, 2k 12.77s, 5k 65.04s, 10k 433.61s.

After indexed reversal and cached peer statistics: 1k 0.09s, 2k 0.22s, 5k 0.57s, 10k 0.94s, 20k 3.86s, 50k 15.69s on the same macOS 12.7.6 / 4 CPU / 8 GiB host.

## Scope boundary

The bounded after harness completed through 10k normal pipeline, 50k optimized adversarial analysis, fixed-vector semantic mechanics, governance, reproducibility, and browser E2E. The 10k bounded-candidate approximation calculation was run separately and remains approximately 34.7s. Live Ollama, Gitleaks, 250k/500k analysis, full accessibility, and authorized real-population validation remain unavailable/deferred as documented.
