# Architecture — Canonical Local Workbench

Audience: developer / coding agent.

## Runtime stack

- Python 3.10+ with the locked `uv` environment.
- CLI entry: `run.py` → `src/audit_analytics/cli.py`; `serve` launches the canonical FastAPI application on `127.0.0.1` only.
- API: `src/audit_analytics/api/app.py`, with routes under `/api` and package-owned static assets in `src/audit_analytics/static/`.
- Frontend: React + Vite + compiled Tailwind in `frontend/`; the built artifact is tracked deliberately and included in the Python package.
- Data store: SQLite (`src/audit_analytics/store.py`), one engagement database per host workflow, WAL enabled.
- Optional embeddings: same-host Ollama over a loopback-only transport; no client data leaves the engagement host.
- Python packaging: `pyproject.toml` + `uv.lock`; web dependencies are explicit and optional at the project level.

## Module map

```text
run.py
  cli.py                 argparse surface and local serve command
  workflow.py            shared engagement/review governance operations
  store.py               additive SQLite schema, migrations, invariants
  importer.py            CSV/bounded-XLSX GL/COA evidence import
  bank.py                bank evidence and reconciliation
  connectors.py          demo connector boundary
  analytics.py           deterministic signals and experimental isolation-style ranker
  semantic.py            lexical search, local embeddings, batched cosine retrieval
  semantic_risk.py       bounded experimental semantic profiles
  semantic_evaluation.py authorised-label offline evaluation
  reports.py             summary, workpaper, report, detached manifest checksum
  model_registry.py      model provenance/approval metadata
  sampling.py            reproducible risk-directed sample
  api/app.py             canonical FastAPI routes and static serving
frontend/src/
  App.tsx                shell and hash navigation
  pages/                 engagement, population, dashboard, investigation
  components/            review and evidence views
  lib/                   relative API client, types, navigation
```

## Data flow

```text
local browser
  → same-origin FastAPI /api routes
  → shared workflow.py governance
  → importer / analytics / semantic modules
  → SQLite engagement database + hash-addressed evidence/

CSV or bounded XLSX
  → preview and explicit import
  → full SHA-256 duplicate check
  → evidence copy + immutable import/source-row lineage
  → reconciliation
  → reviewer acknowledgement
  → versioned analysis run
  → risk cues / optional semantic profile
  → investigation and governed disposition
  → checksummed workpaper/report package
```

## Governance invariants

- `reviews`, `audit_log`, and review-set events are append-only at the database layer.
- A review insert synchronizes the materialized `exceptions.status`; direct divergent status updates are rejected.
- High-severity clears require a distinct, active, authorized second reviewer and note.
- Review-set lock/reopen transitions are immutable, reasoned, role-checked events; locked sets reject review and assignment changes.
- Identical evidence is rejected by default; explicit re-imports record `supersedes_import_id`.
- Empty monetary fields are rejected; explicit zero and signed negative `amount` values follow the documented signed-amount contract.
- Missing account/preparer identity is not counted as a rare identity; it reduces applicability instead of creating a cue.
- Exception severity is immutable after analysis insertion; a changed analytical state requires a new model run.
- The browser-selected local user is a workflow label, not authentication. Network deployment remains unsupported until SSO/RBAC/TLS/CSRF/tenancy controls exist.

## Retrieval and model boundaries

- Lexical search remains transparent and uses `max(token_score, cosine_similarity)`.
- Similarity retrieval batches all vectors for the selected model/dimensions once and uses exact NumPy cosine arithmetic; no ANN/vector database is hidden in this release.
- Reversal matching uses sorted date windows plus a range-minimum index while preserving the first eligible counterpart in original ledger order. Dense same-bucket 10k analysis measured 0.94s after remediation.
- Deterministic analysis rejects populations above the measured 100,000-row local safety boundary before model-run creation; imports remain intact.
- Semantic Risk Engine candidate selection remains deterministic and bounded. Runs persist `exhaustive: false`, candidate/population counts, limits, and tie-break metadata.
- The isolation-style scorer is versioned `isolation-style-random-cut-v1`, records its seed/trees/population floor, and remains experimental. It is not a standard Isolation Forest or a validated audit model.
- Statistical validation and model promotion require authorised labelled populations and governance approval.

## Security and operations

- Same-origin production UI; Vite proxies `/api` only in development. No wildcard CORS.
- Trusted-host middleware permits loopback/test hosts; CSP and clickjacking/content-type protections are set on responses.
- Runtime logs contain request ID, method, route template, status, and duration only; narration, query strings, file contents, and full engagement paths are not logged.
- `GET /api/health` checks database/schema/static readiness without probing optional Ollama.
- Use SQLite's backup API for a consistent copy; never copy a live WAL database as a backup.
- Add raw rows, hashes, notes, and old model outputs only through additive schema changes.

## Build and verification

```sh
uv sync --frozen --all-extras --group dev
npm --prefix frontend ci
npm --prefix frontend run build
uv run python -m compileall -q src run.py
uv run pytest -q
npm --prefix frontend run typecheck
npm --prefix frontend run test:e2e
```

The browser E2E command requires the CI-installed Playwright Chromium. On a developer machine, use the approved existing browser installation rather than downloading another copy.

See `docs/SEMANTIC_ENGINE.md` for semantic methodology, `docs/OPERATIONS.md` for local operations, and `README.md` for the user workflow.
