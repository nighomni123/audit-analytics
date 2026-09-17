# RESUME.md — Continuation guide for Audit Analytics

> **Why this file exists.** The previous AI session (transcript: `GPT_thread.md`,
> ~7.8k lines) built this repo from the *qcom-scraping* pipeline and was cut off
> by a token/usage limit **right after** the user asked it to "write down what to
> do for resuming in future or for another ai agent." It never delivered that
> note. This file is that note. Read it instead of the 7.8k-line transcript.

---

## 1. What this repo is (one paragraph)

A **local-first journal-entry analytics tool** for Indian statutory-audit and
forensic-audit teams. It ingests GL/COA extracts, runs explainable, deterministic
risk-cue analytics, offers optional local (Ollama) semantic transaction search,
and produces reviewer-controlled, evidence-linked workpapers. It is **not** an
audit engine: it never issues an opinion, asserts fraud, or replaces professional
judgement. The original inspiration (`qcom-scraping`) supplied reusable *pipeline
principles* only — observation storage, entity baselines, event/state handling,
provenance, anomaly ranking, human review, exports. The web crawler, consumer
product semantics, pricing, and demand signals were intentionally **not** reused.

## 2. Verified current state (as of the abrupt stop)

```sh
python3 run.py --help                       # 30+ subcommands listed below
PYTHONPATH=src python3 -m pytest tests/ -q   # 25 tests, all pass
```

- `tests/test_cli_workflow.py` — full CLI integration: init → add-user →
  import-gl with exact reconciliation → acknowledge → analyze → status.
- `tests/test_engagement_workflow.py` — reconciled import → exportable review.
- `tests/test_pipeline.py` — analysis blocked until GL import is acknowledged.
- `tests/test_semantic.py` — token classifier + similarity work with **no** model
  service (semantic is an additive, optional layer).
- `tests/test_semantic_risk_core.py` — semantic lifecycle, null/sparse/zero
  clusters, malformed-vector rollback, cache reuse, embed-ledger batch.
- `tests/test_semantic_evaluation.py` — precision/recall, mismatch metrics,
  cue false positives on negatives, label validation.
- `tests/test_semantic_integration.py` — full E2E: import → acknowledge →
  profile → analyze (baseline + opt-in) → investigate → evaluate → export →
  live HTTP checks (profile/investigation/queue/400/404/stale).
- `tests/test_materiality.py` — disclosed planning labels, materiality-banded
  sampling, report sections.
- `tests/test_analytics_features.py` — fiscal-calendar trigger, taxonomy tagging.
- `tests/test_server_endpoints.py` — server import + route presence.
- `tests/test_model_registry.py`, `test_bank.py`, `test_connectors.py`,
  `test_reports_features.py` — registry, bank, connectors, reports.

All 25 pass. Nothing is half-written on disk; the MVP is functional end-to-end.

## 3. Module map (where everything lives)

```
run.py                  entrypoint → src/audit_analytics/cli.py
src/audit_analytics/
  cli.py                argparse surface; one branch per subcommand
  store.py              SQLite Store: schema, users/roles, settings, audit_log,
                         reconciliation(); the system of record
  importer.py           import_gl, import_coa, preview_gl (aliases, evidence copy,
                         SHA-256, rejected_rows, control totals)
  analytics.py          analyze(store, actor, use_isolation): deterministic cues +
                         optional isolation-style ranking (pop ≥ 256); semantic
                         run integration via analysis_signal_results
  semantic.py           token classifier + optional Ollama embeddings;
                         similar_transactions() = max(token, cosine)
  semantic_risk.py      semantic_profile, semantic_investigate,
                         _analysis_components (snapshot/legacy/unavailable);
                         k-means clustering, metrics, cues, lifecycle
  semantic_evaluation.py evaluate_semantic: offline label-based precision/recall,
                         mismatch metrics, cue FP check, report + audit log
  bank.py               import-bank, reconcile-bank (bank_statements/bank_matches)
  sampling.py           create_sample(): high-risk + top-ranked + seeded random
  reports.py            engagement_summary, export_workpaper (+ manifest),
                         write_engagement_report (HTML)
  server.py             serve(): localhost UI on :8788
  connectors.py         BaseConnector + DemoCsvConnector + run_connector
  model_registry.py     register_model/validate_model/list_models/stamp_run
tests/                  12 test files (25 tests total)
```

CLI subcommands: `init, import-gl, import-coa, preview-gl, save-mapping,
list-mappings, acknowledge-population, configure, add-user, analyze,
embed-ledger, similar, review, assign, create-sample, export, report, status,
serve, semantic-profile, semantic-investigate, semantic-evaluate,
import-account-taxonomy, set-fiscal-calendar, compare-runs, lock-reviews,
reopen-reviews, import-connector, import-bank, reconcile-bank,
register-model, validate-model, list-models`.

## 4. qcom-scraping → Audit Analytics translation (the design spine)

| Source pattern | Audit Analytics equivalent |
| --- | --- |
| Observed product w/ time, source, location | GL row w/ import version, source row, hash, evidence path |
| Entity-specific statistical baseline | Account / preparer / entity / period peer groups |
| Unknown ≠ out-of-stock | Missing/invalid financial data = coverage limitation, not a risk cue |
| Debounced state/event machine | Versioned model runs + append-only reviews + audit_log |
| Ranked demand-pressure signal | Ranked, explainable journal-entry risk cue |
| Dashboard + export + human review | Review UI + workpaper export + reviewer note/disposition |
| Additive migrations + reproducibility | Versioned imports/runs, immutable logs, no destructive rewrite |

## 5. What is DONE (MVP)

- Engagement creation, local users + roles (`manager/partner/preparer/reviewer/
  quality_reviewer`), role-guarded every mutating command.
- CSV **and** first-sheet XLSX import (stdlib only, no upload). Header aliases,
  evidence copy + SHA-256, rejected_rows with reasons, debit/credit control
  totals, optional expected-row/debit/credit reconciliation.
- **Acknowledge-before-analyze lock**: analytics is blocked until a reviewer
  acknowledges every GL import (exact match or documented override).
- Deterministic analytics: repeated-entry, round-amount, weekend/period-end,
  rare account×preparer, 30-day same-account reversals, account-peer robust
  outliers (median/MAD), Benford population check (≥100 non-zero, indicator
  only). Optional isolation-style scorer for pop ≥ 256 (disable via
  `--no-isolation`). Every exception carries reasons + peer context.
- Local semantic search (token classifier always; Ollama `embeddinggemma`
  optional; `max(token, cosine)` so semantics only *expands* candidates).
- **Semantic Risk Engine v1 (experimental, opt-in):** narration-only
  vectors (no account/label leakage), versioned `semantic_runs`,
  `semantic_profiles` (transaction/account/vendor/preparer/entity/process),
  `semantic_results` with cues/metrics/evidence, `analysis_signal_results`
  for zero-cue retention. Deterministic k-means (seed 7, k≤12, ≤512
  training, ≤64 candidates), signed cosine metrics, historical novelty,
  vendor shift, account mismatch, peer/cluster outlier cues. Lifecycle:
  digest resolve, transaction rollback on failure, stale-population
  rejection. Offline evaluation against authorised labels (precision@10,
  recall@20, mismatch precision/recall, cluster purity, FP on negatives).
  Review investigation page with Why flagged / Normal peers / Alternative
  matches / Related population / Other signals / Suggested evidence.
- Review workflow: dispositions `open|cleared|follow_up|selected_for_testing`,
  append-only `reviews` + `audit_log`. Assignments, due dates, reproducible
  sampling, CSV workpaper export + JSON manifest, HTML engagement report.
- Controls/limits documented in `README.md` (SA 230 / SA 240 framing) and
  `IMPLEMENTATION_PLAN.md` (full design, data contract, roadmap, acceptance
  checks, known MVP limits).

## 6. What is NOT done (roadmap → see IMPLEMENTATION_PLAN.md §8)

- **Release 1.1 — methodology hardening:** import-mapping preview UX + saved
  per-engagement mapping (CLI `save-mapping`/`list-mappings` *exists*, UI is not
  built); structured client control-total reconciliation *form* (currently the
  `--expected-*` flags + a note); materiality as *disclosed ranking/sampling
  threshold* (settings exist, not yet wired into scoring/sampling); account
  labels/type filters, fiscal-calendar controls, workbook/PDF workpaper output;
  model-run comparison view; formal methodology/limitations report.
- **Release 1.2 — review governance:** second-level approval for cleared
  high-severity; lock completed review set (additive reopening); reviewer queues,
  filters, search; signed export manifests.
- **Release 2 — controlled ERP connectors:** read-only adapters (SAP/Oracle/
  Tally/QuickBooks) producing the same canonical import + connector-run manifest.
  **Not before** a firm supplies authorized access + data dictionary.
- **Release 3 — expanded datasets:** vendor/customer masters, bank extracts,
  invoices, POs, related-party graphs (separate normalized evidence types).
- **Release 4 — validated advanced models:** governed model registry *only after*
  documented validation; deterministic explanations + human review always required.

## 7. How to verify / common commands

```sh
cd "/Users/Mitesh Gada/Documents/Projects/audit-analytics"
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 run.py --help
# smoke test (no client data needed):
python3 run.py init --db /tmp/demo.db --client Demo --period 2025-04-01:2026-03-31 --owner m
python3 run.py status --db /tmp/demo.db
```

## 8. Hard invariants / gotchas (do NOT break these)

- **No outbound network for client data.** Analytics, import, export are
  fully local. Ollama (`embed-ledger`/`similar`) is the *only* optional external
  service and runs on the same host. Keep it that way; add a connector only via
  Release 2's reviewed adapter interface. (`IMPLEMENTATION_PLAN.md` §9 acceptance
  check #9 — "no outbound network call … without an explicitly approved
  connector/feature.")
- **Additive schema only.** New tables/nullable columns + backfills. Never drop/
  rename raw rows, source hashes, reviewer notes, or old model-run outputs
  (`store.py` schema).
- **Acknowledge-before-analyze is a safety control**, not a formality — preserve
  it when touching `importer.py`/`cli.py`/`store.reconciliation()`.
- **Reviews + audit_log are append-only.** A disposition creates a *new* row; it
  never overwrites prior reasoning.
- **Scores are cues, not findings.** Exported text must never say "fraud",
  "exception", or "opinion" about a score (`IMPLEMENTATION_PLAN.md` §9 #8).
- **Semantic never suppresses lexical.** Final similarity = `max(token, cosine)`.
- `serve` binds `127.0.0.1` only; do not expose without Release 1.2 governance.

## 9. Open decisions to confirm with the user before building 1.1

These are product/methodology calls, not engineering unknowns — ask before
coding:

1. **Materiality wiring.** Should materiality/performance-materiality drive
   *sampling* (`create-sample`) and/or *ranking* weighting, or remain a disclosed
   threshold shown on the report only? The plan says "disclosed ranking/sampling
   thresholds" — confirm the exact behavior.
2. **Control-total reconciliation UX.** Is the current `--expected-*` +
   `--override-reconciliation` + note flow sufficient, or does the firm need a
   structured reconcile screen (imported vs supplied, line-by-line diff)?
3. **Workpaper output format.** CSV is shipped; is formatted **XLSX/PDF** needed
   for the firm's template, or is CSV + the HTML report enough for now?
4. **Account taxonomy.** Should account labels/risk taxonomy live in the firm's
   methodology DB (separate from client COA per plan §4), and who maintains it?
5. **Scope of next step.** Continue on Release 1.1 (local, no external deps) vs.
   pause engineering until firm methodology input lands.

## 10. Suggested first continuation task (when resumed)

If picking up cold, the lowest-risk, highest-value next step is **Release 1.1
materiality wiring + structured reconciliation report**, because:

- It needs no new dependencies and no external services.
- It directly strengthens the SA 230/SA 240 documentation story.
- It touches well-tested modules (`store.py`, `analytics.py`, `reports.py`,
  `cli.py`) with existing tests to extend.

Concrete entry points:
- `store.get_setting("materiality", {})` already stores `overall`/`performance`.
- `analytics.analyze()` → add a documented, optional materiality-banded flag on
  exceptions (no behaviour change when unset).
- `sampling.create_sample()` → accept a materiality parameter so the random
  coverage slice can be bounded to items above performance-materiality.
- `reports.write_engagement_report()` → include a methodology + limitations
  section and the recorded materiality settings.

Extend `tests/test_pipeline.py` / `test_cli_workflow.py` to cover the new path
(ponytail rule: non-trivial logic leaves one runnable check behind).

---

*Generated as the missing deliverable from the interrupted session. Keep this
file in sync with `IMPLEMENTATION_PLAN.md` and `README.md`; update §5/§6 as
releases land.*

**Status update (this session):** Release 1.1 materiality wiring is delivered —
exceptions now carry a disclosed `materiality_band` (`above_overall` /
`above_performance` / `below`), and `create-sample` bounds its random coverage
slice to entries at/above performance materiality (`--random-min-amount`
override). `write_engagement_report` now renders a Reconciliation table plus
Materiality and Methodology/Limitations sections. Covered by
`tests/test_materiality.py` (3 tests).

**Status update (Phase 1 semantic risk engine):** Phase 1A–1E fully delivered:
`semantic_risk.py` (narration-only vectors, k-means clustering, metrics, cues,
investigation with snapshot/legacy/unavailable components), `semantic.py`
(token classifier + Ollama transport with redirect/loopback guards),
`semantic_evaluation.py` (offline label-based precision/recall, mismatch
metrics, cue false-positive check), `analysis_signal_results` table for
zero-cue evidence retention, `examples/semantic/` fixtures with labels, and
`tests/test_semantic_risk_core.py`, `test_semantic_evaluation.py`,
`test_semantic_integration.py`. Browser verification via Playwright passes at
1440×1000 and 390×1000 (`tests/browser_review.cjs`).

**Status update (continued):** The remaining local, dependency-free work across
Releases 1.1–1.4 was delivered in one fan-out:
- **1.1** – `import-account-taxonomy` + analytics account-type tagging; `set-fiscal-calendar` + `fiscal_period_end` trigger; `compare-runs` + `/compare-runs`; methodology/limitations report section.
- **1.2** – second-level approval for cleared high-severity (enforced in `review`); `lock-reviews`/`reopen-reviews` additive milestone; reviewer/status filters (`/reviews`); SHA-256 signed export manifest (`workpaper_sha256`/`manifest_sha256`).
- **2** – `connectors.py` (`BaseConnector` + `DemoCsvConnector` + `run_connector`) producing canonical import + `connector_runs` manifest; real ERP adapters **deferred** (need firm auth + data dictionary).
- **3** – `bank.py` (`import-bank`, `reconcile-bank`, `bank_statements`/`bank_matches`); vendor/customer/PO graphs deferred.
- **4** – `model_registry.py` (`register_model`/`validate_model`/`list_models`/`stamp_run`) recording provenance/approval; actual statistical validation **deferred** (needs labelled authorised data).

Full suite passes (25/25). Deferred items require firm-only resources (SSO infra, ERP credentials, labelled validation data) and were intentionally NOT faked. See `IMPLEMENTATION_PLAN.md` §8 for the per-item delivered/deferred notes.
