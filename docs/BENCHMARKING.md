# Benchmarking Audit Analytics

This repository includes a reproducible, synthetic-only benchmark harness. It measures the current checkout without using client data or contacting hosted services.

## Tested baseline

Record the tested commit and environment before interpreting results:

```sh
git rev-parse HEAD
git status --short --branch
git log -10 --oneline
uv lock --check
uv run python scripts/run_benchmark.py --help
```

The machine-readable environment, lock hashes, CPU/RAM, Python/Node/SQLite/NumPy versions, dataset hashes, and optional Ollama probe are recorded in `benchmark-results/baseline.json`.

## Standard run

```sh
uv sync --frozen --all-extras --group dev
npm --prefix frontend ci
uv run python scripts/run_benchmark.py \
  --sizes 100,1000,10000,50000,100000 \
  --pipeline-sizes 1000,10000 \
  --approximation-sizes 1000,10000
```

The harness uses fixed seed `20260924`. It generates temporary CSV populations and deletes their databases/evidence after measurement. Only metrics, hashes, and compact raw command evidence are written to `benchmark-results/`.

For a browser run without downloading a local browser copy, provide the approved executable:

```sh
PLAYWRIGHT_CHROMIUM=/approved/path/to/chromium \
  uv run python scripts/run_benchmark.py
```

Ollama-backed model measurements are not faked. If `http://127.0.0.1:11434/api/version` is unavailable, the artifact records the live semantic model benchmark as not executed; fixed-vector mechanics may still be measured separately.

## Scale and safety

Import-only scale can be run independently:

```sh
uv run python scripts/run_benchmark.py --only-import --sizes 250000,500000
```

Do not run deterministic analysis or full semantic profiling on adversarial 250k/500k populations without first measuring the reversal bucket and memory envelope. The current implementation has a per-account/amount reversal scan and a full dense similarity scan; those are explicit performance boundaries, not invitations to consume all host memory.

## Phases

The harness records:

- clean install, compile, full tests, frontend typecheck/build, audits, and policy checks;
- malformed import, raw-row preservation, control totals, alias mapping, and duplicate-source behavior;
- exact duplicate rejection, explicit re-import lineage, modified-source population behavior, and analysis isolation;
- exact/tolerance/material-mismatch/override reconciliation through the domain path;
- per-detector confusion matrices, repository ground-truth mapping, score distribution, precision@K, materiality bands, and seeded sampling;
- offline fixed-vector semantic retrieval, profile coverage/applicability, cache behavior, cluster purity, and bounded-candidate recall;
- acknowledgement, role/note/second-review/lock/status/append-only governance, API abuse, host/header/upload checks, concurrency, and SQLite backup/restore;
- normalized reproducibility comparisons for ledger rows, risk results, samples, workpaper rows, and manifest content;
- controlled missingness at 0/10/25/50/90 percent.

## Interpreting results

A synthetic precision/recall result describes behavior on that fixture and fixed policy. It is not evidence of real-audit effectiveness, calibration, fraud detection, or model validity. A bounded semantic candidate result must be compared with its exact reference at the same population and vector fixture. A missing Ollama service is an environment limitation, not a passing model-quality result.

Generated outputs:

- `benchmark-results/baseline.json`
- `benchmark-results/correctness.json`
- `benchmark-results/semantic.json`
- `benchmark-results/performance.json`
- `benchmark-results/performance-scale.json`
- `benchmark-results/performance-similarity.json`
- `benchmark-results/performance-adversarial.json`
- `benchmark-results/test-groups.json`
- `benchmark-results/governance.json`
- `benchmark-results/security.json`
- `benchmark-results/reproducibility.json`
- `benchmark-results/failures.json`
- `benchmark-results/summary.md`
