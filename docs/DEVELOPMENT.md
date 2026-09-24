# Development

Audience: coding agent / maintainer.

## Rules

- Read `AGENTS.md` first (lazy, reuse, ponytail, no new abstractions, one runnable check per non-trivial logic).
- Read `docs/ARCHITECTURE.md` before changing module boundaries, persistence, or deployment.
- Read `docs/SEMANTIC_ENGINE.md` before touching `semantic_risk.py`, `semantic_evaluation.py`, or embedding-related modules.
- Preserve immutable evidence, review history, audit history, source lineage, and additive schema migrations.

## Canonical commands

```sh
uv sync --frozen --all-extras --group dev
source .venv/bin/activate
npm --prefix frontend ci
npm --prefix frontend run typecheck
npm --prefix frontend run build
uv run pytest -q
```

For the real browser workflow, install the approved Playwright Chromium in the environment used by CI. When reusing an existing approved browser locally, pass its executable through `PLAYWRIGHT_CHROMIUM`; do not add a personal absolute module path to repository code.

## Key files

- `run.py` — source-checkout CLI shim; the installed console command is `audit-analytics`.
- `src/audit_analytics/cli.py` — argparse surface; `serve` is the only web entrypoint.
- `src/audit_analytics/api/app.py` — canonical API factory, error contract, static serving, health, and export package.
- `src/audit_analytics/workflow.py` — shared governance operations; do not duplicate review rules in routes or CLI branches.
- `src/audit_analytics/store.py` — SQLite system of record and schema invariants.
- `src/audit_analytics/importer.py` — GL/COA import, source limits, hash lineage, and duplicate policy.
- `frontend/src/` — typed React workflow; API calls are relative `/api` paths.
- `tests/` — unit, API, semantic, browser, operations, and repository checks; extend rather than replace.

## Verification habit

Every non-trivial change leaves one runnable check. Use synthetic fixtures and temporary databases. A network outage must not be required for semantic tests; mock the local embedder at the boundary.

## Documentation updates

- User-facing changes → `README.md`.
- Architecture / module changes → `docs/ARCHITECTURE.md`.
- Semantic layer changes → `docs/SEMANTIC_ENGINE.md`.
- Operations / backup / health → `docs/OPERATIONS.md`.
- Governance and roadmap → `IMPLEMENTATION_PLAN.md`.
- Do not reintroduce `GPT_thread.md`, `V1_plan.txt`, or `RESUME.md`; Git history is the archive.
