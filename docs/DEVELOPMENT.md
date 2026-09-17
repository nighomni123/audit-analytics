# Development

Audience: coding agent / maintainer.

## Rules

- Read `AGENTS.md` first (lazy, reuse, ponytail, no new abstractions, one runnable check per non-trivial logic).
- Read `docs/SEMANTIC_ENGINE.md` before touching `semantic_risk.py`, `semantic_evaluation.py`, or embedding-related modules.
- Read `docs/ARCHITECTURE.md` before touching module structure, data flow, or deployment.

## Key files

- `run.py` — CLI entrypoint.
- `src/audit_analytics/store.py` — SQLite system of record; schema changes must be additive.
- `src/audit_analytics/importer.py` — GL/COA import; preserve raw rows and rejected rows.
- `tests/` — 25 tests; extend rather than replace.

## Verification habit

Every non-trivial change leaves one runnable check (assert-based demo, one test file, or a one-line self-check). See `AGENTS.md` ponytail rules.

## Documentation updates

- User-facing changes → `README.md`.
- Architecture / module changes → `docs/ARCHITECTURE.md`.
- Semantic layer changes → `docs/SEMANTIC_ENGINE.md`.
- Master roadmap / governance → `IMPLEMENTATION_PLAN.md`.
- Do not reintroduce `V1_plan.txt` or `RESUME.md`; history lives in Git.
