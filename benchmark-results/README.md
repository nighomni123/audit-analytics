# Audit Analytics Benchmark Artifacts

This directory contains evidence from a synthetic-only benchmark of commit `0dd6fda07abd028018514221ccbb592deb0b6842`. It contains metrics, hashes, and compact command results—not client data or generated ledgers.

## Files

- `baseline.json` — environment, lock hashes, clean install, full tests, frontend build/audit, and browser result.
- `correctness.json` — malformed import, idempotence/lineage, reconciliation, detector confusion matrices, ground truth, materiality/sampling, missingness, XLSX, and export integrity.
- `semantic.json` — fixed-vector retrieval, profile coverage, cache, cluster purity, and bounded-candidate recall.
- `governance.json` — domain/API governance, endpoint matrix, security probes, concurrency, and backup/restore.
- `performance.json` — import/pipeline/API timing, adversarial analysis, and API p50/p95.
- `performance-scale.json` — import-only 250k/500k measurements.
- `performance-similarity.json` — 50k/100k similarity measurements.
- `performance-adversarial.json` — same-account/same-amount analysis ceiling.
- `reproducibility.json` — normalized two-run comparisons.
- `security.json` — dependency checks, API security, unavailable Gitleaks/Ollama probes.
- `test-groups.json` — test counts and durations by group.
- `failures.md` — classified defects, limitations, and environmental gaps.
- `summary.md` — final readiness assessment.
- `raw/` — intentionally empty of generated data; temporary ledgers/databases are deleted after each run.

Run `uv run python scripts/run_benchmark.py --help` and see `docs/BENCHMARKING.md` for reproduction instructions.
