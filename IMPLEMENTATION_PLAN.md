# Audit Analytics — Implementation and Evolution Plan

## 1. Purpose and operating boundary

Audit Analytics is a local-first journal-entry analytics system for audit and
accounting firms conducting Indian external statutory audits. Its purpose is to
help engagement teams profile a ledger population, identify explainable risk
cues, select and document responsive procedures, and retain an evidence-linked
review trail.

It is deliberately **not** an automated audit engine. It must never express an
audit opinion, determine that fraud occurred, treat a risk score as a finding,
or replace the auditor's professional judgement. A flagged entry is a review
cue. A reviewer must assess the entry, obtain appropriate evidence, and record
their disposition.

The initial product boundary is general-ledger (GL) and chart-of-accounts (COA)
data. Supporting documents, OCR, bank data, vendor/customer masters,
related-party graphs, continuous controls monitoring, and ERP integrations are
future additions behind the same normalized-data boundary.

The documentation and review controls are intended to support engagement teams
working under SA 230 and SA 240. The firm remains responsible for applying the
current standards, its audit methodology, quality-management policies, and any
jurisdiction-specific legal requirements.

## 2. Design translated from qcom-scraping

The source project supplied reusable pipeline principles rather than an audit
domain model:

| Source-pipeline pattern | Audit Analytics equivalent |
| --- | --- |
| Captured observation with time, source, and location | Imported GL record with import version, source row, hash, and evidence-file path |
| Entity-specific statistical baseline | Account, preparer, entity, and period peer groups |
| Unknown is not an out-of-stock event | Missing or invalid financial data is a coverage limitation, never a suspicious transaction |
| Debounced state/event handling | Versioned model runs, reviewed exceptions, and append-only dispositions |
| Ranked demand-pressure signal | Ranked, explainable journal-entry risk cue |
| Dashboard, export, and human review | Engagement review queue, reviewer note/disposition, and workpaper export |
| Additive migrations and reproducibility | Versioned imports/runs, immutable logs, and no destructive data rewrite |

The web crawler, consumer-product semantics, pricing logic, and demand claims
are intentionally not reused. Financial data enters only through trusted,
controlled imports and future read-only connector adapters.

## 3. Delivered foundation

The current implementation is a functional local MVP.

### 3.1 Engagement and data controls

- `init` creates one engagement database with client and audit-period metadata.
- `import-gl` accepts CSV and ordinary first-sheet XLSX exports without sending
  data to an external conversion service.
- Common header aliases are mapped to a canonical GL contract. Required fields
  are entry ID, posting date, account code, and signed amount or debit/credit.
- Accepted rows retain their complete original row JSON, SHA-256 row hash,
  source row number, import identifier, and evidence-file reference.
- Each source file is copied to an engagement-local `evidence/` directory and
  hash recorded before processing.
- Invalid rows are preserved with a rejection reason rather than silently
  discarded.
- The import records accepted/rejected counts and calculated debit/credit
  control totals. Analytics is blocked until the reviewer explicitly
  acknowledges every GL import and records a note.

### 3.2 Statistical and deterministic analytics

The analysis run is versioned and stores configuration, population size,
limitations, and every exception's component evidence.

- Repeated-entry tests identify repeated account/date/amount/description and
  repeated account/reference/amount patterns.
- Amount tests identify material round-number entries.
- Timing tests identify period-end and weekend postings.
- Relationship tests identify rare account/preparer combinations and potential
  opposite-sign reversals in the same account within 30 days.
- Robust peer outliers use the account-level median and median absolute
  deviation (MAD), avoiding fragile mean/standard-deviation assumptions.
- Benford analysis runs only when at least 100 non-zero amounts exist and is
  kept as a population-level indicator, not an entry-level accusation.
- An optional local isolation-style random-cut model operates only for
  populations of at least 256 entries. It is explicitly an additional ranking
  feature, not the sole basis for an exception or audit response.

Scores are bounded and severity-labelled for prioritisation. Reasons and peer
context remain visible so the reviewer can understand why an entry appeared.

### 3.3 Local semantic transaction search

- Transaction search text combines account code, optional COA account name,
  narration, reference, and entity. It does not use a remote service.
- A transparent token classifier labels terms associated with cash/bank,
  revenue, expense, payroll, inventory, tax, intercompany, and fixed assets.
- Token search uses weighted shared terms, where uncommon terms contribute more
  than generic transaction vocabulary.
- Optional Ollama `embeddinggemma` vectors are stored in the engagement SQLite
  database, keyed by ledger ID, model, dimensions, and a source-text hash.
  Unchanged records are not re-embedded.
- Query vectors are transient and never persisted. Similarity is local cosine
  similarity; the final candidate score is `max(token_score, semantic_score)`.
  Thus semantic retrieval expands candidates but never suppresses a strong
  transparent token/account-head match.
- Search candidates are review leads, not a statement that two entries are the
  same transaction or evidence of concealment.
- Recommended default: `embeddinggemma`, a compact multilingual local model.
  `nomic-embed-text` is the fast English-language comparison baseline, while
  `mxbai-embed-large` is the higher-resource candidate for a controlled
  quality pilot. The firm must validate the selected model on authorised,
  labelled transaction pairs and record the model in its methodology.

### 3.4 Review and workpapers

- The local HTTP review UI shows entry context, score, reasons, model evidence,
  current status, and a required reviewer note.
- Supported dispositions are `open`, `cleared`, `follow_up`, and
  `selected_for_testing`.
- Each disposition creates an append-only `reviews` record and an `audit_log`
  event with actor, time, target, and structured details.
- `export` creates a CSV workpaper containing risk information, original GL
  context, reasons, and evidence. Firms can load this into their prescribed
  workpaper template.

## 4. Canonical data contract

### Required GL fields

| Canonical field | Purpose | Typical aliases |
| --- | --- | --- |
| `entry_id` | Stable journal/voucher-line identifier | journal_entry_id, voucher_no, transaction_id |
| `posting_date` | Accounting posting date | date, entry_date |
| `account_code` | GL account identifier | account, gl_code, ledger_code |
| `signed_amount` or `debit`/`credit` | Transaction value | amount, net_amount, debit_amount, credit_amount |

### Recommended optional fields

`document_date`, `description`, `preparer`, `reference`, `entity`, and
`is_manual` improve population profiling and analytical precision. Their
absence is recorded as a coverage limitation; it does not become a risk cue.

### COA contract

COA imports are optional enrichment and accept account code plus account name
and type where present. Future account-risk taxonomy mappings should be stored
separately from the raw client COA so firm methodology does not overwrite
client evidence.

## 5. Data model and lineage

The SQLite database is the engagement's system of record. Its logical flow is:

```text
evidence file -> imports -> ledger_entries / rejected_rows
                               |
                               v
                         model_runs -> exceptions -> reviews
                               \             \-> audit_log
                                \-> workpaper export
```

- `imports` stores file lineage, hash, counts, control totals, and reviewer
  acknowledgement.
- `ledger_entries` holds normalized data and immutable source identity.
- `rejected_rows` makes quality issues inspectable and countable.
- `model_runs` captures run configuration and limitations for reproducibility.
- `exceptions` links a particular run to a particular original ledger record.
- `reviews` is append-only; status changes do not erase earlier reviewer work.
- `audit_log` records administrative, import, analysis, and review actions.

Schema evolution must be additive: new tables or nullable columns plus
backfills where appropriate. Never overwrite raw rows, source hashes, reviewer
notes, or old model-run outputs.

## 6. Firm deployment and security baseline

The supported deployment baseline is an auditor-controlled laptop, server, or
private VPC. Engagement data must remain within the firm-approved environment.

- Bind the review service to `127.0.0.1` by default. A network deployment must
  add firm SSO, role-based access control, TLS, session expiry, CSRF protection,
  audit-log retention, encrypted backups, and tenancy isolation before use.
- Encrypt devices/disks and backups using firm-approved controls. Restrict the
  engagement directory to assigned team members.
- Do not route client data to hosted LLM, embedding, telemetry, spreadsheet
  conversion, or third-party model services by default.
- Preserve original import files under the firm retention policy. On engagement
  closure, archive or delete through the firm's approved records process—not a
  silent application cleanup task.
- Capture tool version, model configuration, population acknowledgement, and
  export timestamp in each formal workpaper package.

## 7. Review workflow

1. The engagement team creates the engagement and imports the GL/COA extracts.
2. The preparer reconciles accepted entry count and calculated totals to the
   client-provided population/control totals; rejected rows are investigated.
3. A reviewer acknowledges the import with a specific note. This unlocks
   analysis but does not imply audit evidence has been obtained.
4. The team runs the hybrid analytics and reviews population limitations.
5. The reviewer filters/ranks cues, obtains support as necessary, records a
   disposition and rationale, and selects substantive testing items where
   appropriate.
6. The team exports the reviewed population and dispositions into the firm's
   workpaper structure, including methodology, limitations, and conclusion by
   the responsible auditor.

## 8. Planned releases

### Release 1.1 — audit-methodology hardening

- Add import-mapping preview and a saved client/ERP field mapping per
  engagement.
- Capture external client control totals, compare them to accepted data, and
  require an explicit quantified reconciliation before acknowledgement.
- Add materiality and performance-materiality settings used only as disclosed
  ranking/sampling thresholds. **(Delivered, post-resume)** `analyze` labels
  every exception `above_overall` / `above_performance` / `below` — a disclosed
  planning label that never alters a risk score; `create-sample` bounds its
  random coverage slice to entries at/above performance materiality (override via
  `--random-min-amount`). Covered by `tests/test_materiality.py`.
- Add account labels, account-type filters, fiscal calendar controls, and
  workbook/PDF workpaper outputs. **(Delivered, post-resume)** `import-account-taxonomy`
  loads a firm taxonomy; `analyze` tags exceptions with `account_type`/`account_label`
  for filtering; `set-fiscal-calendar` plus the analytics `fiscal_period_end` trigger.
  Workbook/PDF output remains deferred (CSV + HTML report shipped).
- Add a model-run comparison view and a formal methodology/limitations report.
  **(Delivered, post-resume)** `compare-runs` CLI + `/compare-runs` endpoint; the
  HTML `report` carries a Methodology & Limitations section.

### Release 1.2 — review governance

- Add local user roles: preparer, reviewer, engagement manager, and read-only
  quality reviewer.
- Require second-level approval for cleared high-severity entries and lock a
  completed review set while allowing additive reopening records.
  **(Delivered, post-resume)** `review` enforces `--second-reviewer`/`--second-note`
  for cleared high-severity exceptions; `lock-reviews`/`reopen-reviews` record the
  milestone additively via `settings`.
- Add assignment, due date, reviewer filters, search, and reviewer sampling
  queues. **(Delivered, post-resume)** assignment/due-date existed; `/reviews`
  filters by reviewer/status; sampling queues exist.
- Add signed export manifests listing source imports, file hashes, run IDs, and
  reviewed exception counts. **(Delivered, post-resume)** `export` manifest now
  carries SHA-256 of the workpaper + manifest (`workpaper_sha256`/`manifest_sha256`).

### Release 2 — controlled ERP connectors

- Implement read-only adapter interfaces for SAP, Oracle, Tally, QuickBooks,
  and other approved systems only after a firm provides authorized access and a
  data dictionary.
- Each adapter must produce the same canonical import data and a connector-run
  manifest: authorization identity, query/version, extraction timestamp,
  record count, control totals, and source-system identifiers.
- Do not make connectors silently refresh a reviewed engagement population;
  each refresh is a new import version requiring reconciliation and
  acknowledgement.

  **(Delivered, post-resume foundation)** `connectors.py` defines `BaseConnector`
  + `DemoCsvConnector` and `run_connector()`; the demo path produces the canonical
  import and a `connector_runs` manifest. Real SAP/Oracle/Tally/QuickBooks adapters
  remain **DEFERRED** — they require firm-authorized access + a data dictionary per
  the plan; the interface is proven and ready to extend.

### Release 3 — expanded forensic and audit datasets

- Add vendor/customer masters, bank extracts, invoices, purchase orders, and
  related-party datasets as separate normalized evidence types.
- Build graph and text-similarity analysis only with explicit coverage and
  false-positive controls.

  **(Delivered, post-resume foundation)** `bank.py` adds the `bank_statements` /
  `bank_matches` evidence types, `import-bank`, and `reconcile-bank` (date + amount
  matching to ledger). Vendor/customer masters, invoices, POs, and related-party
  graphs remain deferred (separate normalized types to add later).
- Keep document ingestion separate from GL scoring; missing supporting evidence
  is a review state, not an inferred fraud feature.

### Release 4 — validated advanced models

- Replace the compact isolation-style scorer with a governed model registry
  only after documented validation across representative, authorised audit
  populations.
- Record training data provenance, version, feature schema, calibration,
  performance, drift checks, approval owner, and rollback process.

  **(Delivered, post-resume foundation)** `model_registry.py` provides
  `register_model`/`validate_model`/`list_models`/`stamp_run` recording provenance,
  feature schema, approval owner, and validation status; `model_runs` gained
  `model_name`/`validation_status`. Actual statistical validation is **DEFERRED** — it
  requires labelled, authorised audit populations and governance sign-off; the
  isolation scorer remains the only active model and is disableable.
- Continue to require deterministic explanations, human review, and sampling
  methodology independent of any model score.

## 9. Acceptance and regression checks

Every release must retain these checks:

- Valid CSV/XLSX import maps standard aliases, copies evidence, and maintains
  correct row identity even with blank spreadsheet cells.
- Invalid required fields and dates become visible rejected rows; they never
  become scored exceptions.
- No analysis is possible before all GL imports are acknowledged.
- Calculated accepted-population counts/debits/credits are visible before the
  acknowledgement action.
- Synthetic datasets verify each deterministic cue, robust outlier threshold,
  reversal matching, Benford minimum-population guard, and isolation-model
  minimum-population guard.
- Each exception traces to an import, evidence file, original source row, and
  stored raw fields.
- A review note is mandatory; the audit log retains every disposition action.
- Exported workpapers include no language treating a score as fraud, an audit
  finding, or an audit opinion.
- Static and runtime checks confirm no outbound network call is introduced for
  engagement data without an explicitly approved connector/feature.

## 10. Known MVP limits

- The first UI is local and deliberately has no multi-user authentication;
  serve it only on the controlled host until Release 1.2 governance is built.
- XLSX support targets ordinary tabular first-sheet exports; complex workbooks,
  macros, protected files, and multi-sheet mappings require the mapping preview
  work in Release 1.1.
- The current import acknowledgement captures calculated totals and a reviewer
  note; structured client-supplied control-total reconciliation is planned for
  Release 1.1.
- The isolation-style algorithm is a compact local ranking aid with a stated
  ceiling, not a validated fraud model. It can be disabled per run.
- CSV is the current workpaper export. Formatted Excel/PDF output and audit
  suite integration are planned additions.

---

## 11. Verified current state (post-resume, as of cleanup)

Extracted from the temporary session-continuation file (`RESUME.md`, now removed).

- **Tests:** 25/25 pass (`tests/test_*.py`).
- **Module map:** `cli.py` (entrypoint), `store.py` (SQLite + reconciliation, audit_log), `importer.py`, `analytics.py`, `semantic.py`, `semantic_risk.py`, `semantic_evaluation.py`, `reports.py`, `server.py` (`serve` on `127.0.0.1:8788`), `bank.py`, `sampling.py`, `connectors.py`, `model_registry.py`.
- **CLI surface:** ~34 subcommands (full list in `README.md`); key ones: `init`, `import-gl`, `import-coa`, `acknowledge-population`, `analyze`, `semantic-profile`, `semantic-investigate`, `semantic-evaluate`, `export`, `report`, `serve`, `compare-runs`, `lock-reviews`, `reopen-reviews`.
- **MVP delivered:** engagement/init; CSV + first-sheet XLSX import (evidence copy + SHA-256); acknowledge-before-analyze lock; deterministic analytics (repeated entry, round amount, weekend/period-end, rare account/preparer, 30-day reversal, MAD peer outliers, Benford indicator ≥100); optional isolation-style ranking (pop ≥ 256); local semantic search (`max(token, cosine)`); Semantic Risk Engine Phase 1A–1E (narration-only embeddings, k-means clustering, metrics, cues, investigation, offline evaluation, stale-population guard, zero-cue `analysis_signal_results`, review page); review workflow (dispositions, append-only `reviews` + `audit_log`, assignments, reproducible sampling, CSV + JSON manifest, HTML report); `serve` local server.
- **Releases 1.1–1.4 delivered post-resume:** 1.1 (materiality wiring `above_overall`/`above_performance`/`below`, fiscal-calendar + taxonomy tagging, methodology/limitations report section); 1.2 (second-level approval for cleared high-severity, `lock-reviews`/`reopen-reviews`, reviewer/status filters, signed export manifest SHA-256); 2 (connector framework `BaseConnector`/`DemoCsvConnector`; real ERP adapters deferred — need firm auth + data dictionary); 3 (`bank.py`: `import-bank`, `reconcile-bank`; vendor/customer/PO graphs deferred); 4 (`model_registry.py` provenance/stamp; validated statistical models deferred — need labelled authorised data).
- **Invariants preserved:** no outbound network for client data (only optional same-host Ollama); additive schema only (no destructive row/hash/note deletion); acknowledge-before-analyze safety control; append-only reviews; scores = cues, never findings/opinions; lexical similarity never suppressed (`max(token, cosine)`); `serve` binds `127.0.0.1` only until 1.2 governance.
- **Remaining open product decisions (before 1.1+):** materiality exact wiring (sampling ranking vs. disclosed threshold); structured reconciliation form vs. current `--expected-*` + note; workpaper output format (CSV + HTML sufficient, or need XLSX/PDF); account taxonomy source/owner; next-scope choice (continue 1.1 local work vs. pause for firm methodology input). See §8 roadmap.

(See `README.md` for CLI/reference; `docs/SEMANTIC_ENGINE.md` for Semantic Risk Engine technical design; `docs/ARCHITECTURE.md` for system structure; `docs/DEVELOPMENT.md` for agent/dev rules; `AGENTS.md` for agent rules.)
