# Audit Analytics — Internal Defect Ledger (P0)

All entries verified against the working checkout at commit `dfec4a46153e5ec549e70c479cdeaa41a310b13c`.
The ledger records verified defects with severity, affected component, evidence, and intended correction.
It is a working document, not a public deliverable; it is superseded by the final engineering report.

---

## P0 — investigation context (highest priority)

| ID | Severity | Component | Evidence (line refs / behavior) | Intended correction |
|----|----------|-----------|--------------------------------|---------------------|
| D1 | Critical | `src/audit_analytics/investigation_context.py:112` | Queries non-existent table `ledger` (`SELECT COUNT(*) FROM ledger WHERE account_code=?`). Canonical schema uses `ledger_entries`. | Rewrite the peer-statistics path to read from `ledger_entries` using canonical columns (`id`, `account_code`, `signed_amount`, etc.). |
| D2 | Critical | `src/audit_analytics/investigation_context.py:134` | Queries non-existent table `review_notes` (`SELECT note,actor,created_at FROM review_notes WHERE ledger_id=?`). Canonical table is `reviews` (joined to `exceptions`). | Read reviews from `reviews` joined on `exception_id` where `exception.ledger_id = ? AND exception.run_id = ?`. |
| D3 | Critical | `src/audit_analytics/investigation_context.py:146-156` | Ledger fields referenced by wrong names: `amount`, `sha256`, `date`, `account`, `file_name`, `row_index`, `hash`. Canonical fields: `signed_amount`, `source_hash`, `posting_date`, `account_code`, `description`, `source_row`, plus `imports.original_name`. | Populate `transaction_line` from `ledger_entries` using canonical field names; expose `imports.original_name` (not absolute `evidence_path`). |
| D4 | Critical | `src/audit_analytics/investigation_context.py:74,80-82` | Delegates entirely to `semantic_risk.semantic_investigate(store, run_id, ledger_id)`, which treats the deterministic analysis run ID as a semantic run ID, requires a complete semantic run, and raises when no profile exists. Deterministic-only investigation is impossible. | Rebuild context directly from canonical records (`ledger_entries`, `exceptions`, `analysis_signal_results`, `model_runs`, `imports`, `coa/account_taxonomy`); make semantic enrichment optional and only when a valid linked semantic run exists. |
| D5 | High | `src/audit_analytics/investigation_context.py:54-71` (`_match_procedures`) | Cue-to-procedure matching is fragile underscore-token keyword splitting on `c.get("reason")`/`c.get("rule")`/`c.get("label")`. Does not use canonical cue identifiers (`possible_reversal_within_30_days`, etc.). | Replace with an explicit map keyed by canonical cue identifiers; add documented handling for unknown cues and mixed deterministic/semantic cues. |
| D6 | High | `src/audit_analytics/investigation_context.py:112-118` | "Median" is computed as `ORDER BY amount LIMIT 1 OFFSET cnt//2`, i.e. the middle element of an *unordered* set — not a median; asserts `median_approx_available: true` without ever computing a median or MAD. | Compute true `statistics.median` and MAD over the account population; report `median_available` only when a median exists and disclose MAD applicability. |
| D7 | High | `src/audit_analytics/investigation_context.py:117,135-136` | Broad `except Exception: pass` hides broken queries (wrong table/column) and silent unavailability of peer stats, reviews, materiality. | Fail visibly on implementation defects (log + raise) while returning explicit `available: false` / `status: unavailable` for genuinely optional or inapplicable evidence. |
| D8 | High | `frontend/src/pages/Investigation.tsx:57` | `ctx` typed as `Record<string, unknown> | null`; accessing `ctx.transaction_line?.amount`, `.cues`, `.related_transations` yields 10 TypeScript errors and blocks `npm run build` (baseline.json records `returncode: 2`). | Define a proper `InvestigationContext` interface in `lib/types.ts` and type the state and fetch accordingly. |
| D9 | Medium | `frontend/src/pages/Investigation.tsx:69,76-82` | Parent fetches context at line 69; child `InvestigationContextPanel` re-fetches at line 77 (duplicate request). Child is called with the same `run` used for semantic (a semantic run ID, see D4) and only when a semantic run exists; when no semantic run exists the panel receives `run` undefined and would issue `/investigation-context?run=undefined&ledger_id=N`. | One clear fetch owner (the parent); pass explicit `run_id`/`ledger_id`/optional `semantic_run_id`. |
| D10 | Medium | `src/audit_analytics/api/app.py:970-974` | Route declares overloaded `run: int` and forwards it verbatim to `investigation_context(store, run, ledger_id)`, while the UI passes a *semantic* run ID (from `semanticRunId(detail)`). No validation of run/entry membership; invalid identifiers can become silent empty responses via `setCtx(null)`. | Rename param to `run_id` (deterministic analysis run, required), add optional `semantic_run_id`; validate run exists & complete, ledger belongs to run's population, semantic run (if given) is complete/non-stale/same population; return 400/404/409 explicitly. |
| D11 | Medium | `src/audit_analytics/cli.py:257-258` | CLI `investigate` command calls `semantic_investigate` and passes `args.run` — overloaded meaning again; would silently fail for a deterministic-only run. | Add an `--investigation-context` path calling the new `investigation_context` with `--run-id`/`--ledger-id`/`--semantic-run-id`. |
| D12 | Low | `docs/BENCHMARKING.md:60` | States "The current implementation has a per-account/amount reversal scan and a full dense similarity scan." — conflicts with `docs/ARCHITECTURE.md:77` and actual `analytics.py:_reversal_matches` which use sorted date windows + a range-min index (bounded). | Correct the benchmarking doc to describe the range-min-bounded reversal implementation and its measured envelope; keep the safety warning. |
| D13 | Low | `benchmark-results/baseline.json` | Stale/broken: records frontend typecheck/build failure (TS2345/TS2339 on Investigation.tsx), npm high vulnerability, inconsistent sections and two different commit hashes. | Rebuild and replace with a fresh baseline after fixes; preserve the historical snapshot only via the tracked commit reference. |

---

## P1 — analytics & semantics (verified during analysis; fixes below)

| ID | Severity | Component | Evidence | Intended correction |
|----|----------|-----------|----------|---------------------|
| D14 | Medium | `src/audit_analytics/analytics.py:259-277` | Signal-components summary is only recorded when `semantic_run_id` is set; otherwise the deterministic `signal_components` (status, reasons, score) is never persisted. The context must fall back to `reasons_json`/`evidence_json` from `exceptions` when components are absent. | Document fallback in the context code (already done there); no schema change needed. |
| D15 | Low | `src/audit_analytics/analytics.py:190-193` | `benford_population_indicator` is written to `evidence` for every entry but never surfaced as a per-entry cue; it is population-level only. | Keep as population-level (no change); the context reports it under `population_indicators` when flagged. |
| D16 | Low | `src/audit_analytics/semantic_risk.py:307-320` | `semantic_investigate` raises `ValueError('semantic run is not complete')` but its error contract is inconsistent with FastAPI's 422/404 conventions (it propagates as an internal server error). | Add explicit exception handler mapping; keep semantics as a read-only experimental aid. (No functional change; logging only.) |

---

## Test hygiene

| ID | Severity | Component | Evidence | Intended correction |
|----|----------|-----------|----------|---------------------|
| D17 | High | `tests/test_investigation_context.py:8-33` | All five tests are placeholders: `pass`, `assertTrue(True)`, code-review claims, token-splitting test on wrong shape. | Replace with real integration tests exercising the canonical fixture (Cases A-G). |
| D18 | Medium | `frontend/src/pages/Investigation.tsx:81` | Typo `related_transations` (should be `related_transactions`); unused nested-panel component creates the duplicate-fetch problem (D9). | Rename + restructure; remove the nested panel. |

---

## Verification method

Each defect is verified by reading the cited source lines; D1-D3 are confirmed by the SQLite `SCHEMA` in `store.py` (`ledger_entries`, `reviews`, `exceptions`) which contains no `ledger` or `review_notes` table.
