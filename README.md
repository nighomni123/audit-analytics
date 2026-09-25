# Audit Analytics

Local-first journal-entry analytics for Indian statutory-audit teams. It ranks
explainable risk cues for auditor review; it does not make audit conclusions or
issue an opinion.

```text
What it does
Import a client's GL → check the population → analyze the entire ledger →
surface explainable risk cues → investigate selected entries → document the review.

It does not decide whether something is fraud or an audit finding.
It helps the auditor decide what deserves attention.
```

### Architecture (one picture)

```
Client GL
   ↓
Population check (reconcile controls)
   ↓
┌──────────────┴──────────────┐
↓                             ↓
Deterministic analytics     Semantic analytics
(amount, timing, peers)     (local embeddings / similarity)
│                             │
└──────────────┬──────────────┘
               ↓
       Ranked risk cues
               ↓
      Auditor investigation
               ↓
     Workpaper / review record
```

**Risk cue:** a transaction or pattern the analytics flags as unusual enough to warrant human review. A risk cue is not a finding of error, fraud, or misstatement.

```text
Example — journal entry ₹8,240,000 to Repairs & Maintenance
Risk cues: posted at period end; unusually large for account; narration unlike normal activity
Result: placed higher in review queue
Auditor action: investigates supporting evidence
```

### Privacy first

✓ Client GL stays on the machine  
✓ SQLite engagement database is local  
✓ Evidence files remain local  
✓ Embeddings run through local Ollama (optional)  
✓ No cloud AI API required; no client ledger upload  
✓ No external service is required for core analysis

> **Local-first does not automatically mean secure in every deployment.** Engagement folders, backups, devices, and any network deployment still need the firm's approved security controls.

### Vocabulary (used consistently below)

| Term | Meaning |
| --- | --- |
| **Journal entry** | One imported GL line |
| **Risk cue** | Analytical signal worth reviewing |
| **Analysis run** | One complete deterministic/semantic pipeline execution |
| **Investigation** | Auditor examination of a selected journal entry |
| **Disposition** | Auditor's recorded review outcome |

## Usage guide (start here)

Use this as the shortest path from fresh clone to first review. Detailed
workflow notes remain in [Step-by-step: first engagement](#step-by-step-first-engagement),
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/OPERATIONS.md](docs/OPERATIONS.md),
and [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

### 1) Prerequisites and install

- Python 3.10+
- Node 22.12+

```sh
cd audit-analytics
uv sync --frozen --all-extras --group dev
source .venv/bin/activate
npm --prefix frontend ci
npm --prefix frontend run build
```

### 2) Synthetic demo (`examples/demo-journal-entries.csv`)

Run the verified sequence in [CLI / developer demo](#cli--developer-demo-synthetic-data-verified)
using `examples/demo-journal-entries.csv`:
`init` → `import-gl` → `acknowledge-population` → `analyze` → `report`.

Start the local review UI:

```sh
python3 run.py serve --db demo-engagement.db
```

Open `http://127.0.0.1:8788`.

### 3) Real engagement flow (command order)

1. `init` engagement database
2. `preview-gl` incoming file
3. Optional mapping: `preview-gl --mapping ...` and `save-mapping`
4. Import sources: `import-coa` then `import-gl`
5. Reconcile totals (`status`) and reviewer `acknowledge-population`
6. Set methodology with `configure`
7. Run analytics with `analyze`
8. Review and disposition with UI or `assign`/`review`
9. Build testing sample with `create-sample`
10. Deliver outputs with `export` and `report`

### 4) Optional local Ollama semantic search

```sh
ollama serve
ollama pull embeddinggemma
python3 run.py embed-ledger --db engagements/example-ltd-fy26/audit.db --model embeddinggemma
python3 run.py similar --db engagements/example-ltd-fy26/audit.db --query "GST liability provision" --limit 25
```

### 5) Tests

```sh
uv run pytest -q
npm --prefix frontend run typecheck
npm --prefix frontend run build
# optional browser coverage
npm --prefix frontend run test:e2e
```

### 6) Important boundary

This repository is a **local laboratory tool** for auditor review support. Risk
cues are prioritisation signals, not fraud findings and not audit opinions. Keep
engagement data local/private, and do not expose `serve` to a LAN/internet
without additional firm-approved security controls.

## CLI / developer demo (synthetic data, verified)

No client ledger? The repo ships a 400-row synthetic GL (`examples/`, generated
locally, no real client data) with a `demo-ground-truth.csv` of planted
anomalies you can check the tool against. Every command below was run
end-to-end on 2026-09-15 with Python 3.12; nothing leaves your machine.

```sh
python3 run.py init --db demo-engagement.db --client "Demo Textiles Ltd" \
  --period 2025-01-01:2026-03-31 --owner reviewer
python3 run.py import-gl --db demo-engagement.db --file examples/demo-journal-entries.csv \
  --actor reviewer --expected-rows 400 --expected-debits 3496407.62 --expected-credits 0
python3 run.py acknowledge-population --db demo-engagement.db --reviewer reviewer \
  --note "demo: synthetic 400-row GL, control totals match"
python3 run.py analyze --db demo-engagement.db --actor reviewer
python3 run.py report --db demo-engagement.db --out demo-report.html --actor reviewer
python3 run.py serve --db demo-engagement.db   # review UI on http://127.0.0.1:8788
```

What you should see: a complete end-to-end run with the synthetic dataset (400 rows, control totals match). The tool surfaces explainable risk cues — not fraud findings — for auditor review.

### Technical validation (synthetic ground-truth)
The synthetic ground-truth file contains six labelled rows. The current baseline directly detects the `round_amount` row, surfaces two `benford_vendor` rows through the `robust_account_peer_outlier` proxy, surfaces one additional `benford_vendor` row only through `rare_account_preparer_pair`, misses one `benford_vendor` row, and cannot observe `off_hours` because the schema stores posting dates rather than timestamps. These are fixture semantics and detector mappings, not a claim about real ledgers or audit effectiveness. See [`docs/GROUND_TRUTH.md`](docs/GROUND_TRUTH.md).

## See it in action (visual walkthrough)

Every image uses only the synthetic 400-row GL (`examples/demo-journal-entries.csv`). No real client data appears.

### 1. Create engagement
![Init demo DB](docs/screenshots/01-init.png)
`
python3 run.py init --db demo-engagement.db --client "Demo Textiles Ltd" ...
`

### 2. Import GL
![Import synthetic GL](docs/screenshots/02-import-gl.png)
Import and reconcile the population.

### 3. Confirm population
![Acknowledge population](docs/screenshots/03-ack.png)
A reviewer acknowledges control totals.

### 4. Review risk dashboard
![Serve web UI (desktop)](docs/screenshots/05-serve-ui.png)  
![Serve web UI (mobile 390px)](docs/screenshots/06-serve-ui-mobile.png)
Open `http://127.0.0.1:8788`; see ranked exceptions, evidence links, and dispositions.

### 5. Investigate a transaction
![Exception detail in UI](docs/screenshots/07-serve-exception-detail.png)
Each cue carries reasons and links — not a black-box verdict.

### 6. Export / document
![Generate report](docs/screenshots/05-report-html.png)
Generate a readable HTML workpaper summary.

> Earlier steps (download/clone, CLI outputs, mobile view) are in `docs/screenshots/` if you want the full sequence.

Real ledgers with non-canonical headers? Pass a header-mapping profile like
`examples/demo-mapping.json` (`--mapping examples/demo-mapping.json`) or save
one with `save-mapping` for reuse across engagements.

## Quick start (user experience)

1. Launch the workbench and choose **New Engagement** (or **Run Demo** for the synthetic onboarding path).
2. Add the client GL from **Population**; preview the detected fields, confirm the mapping, and compare the supplied control totals.
3. Open **Audit setup** to record planning materiality and the period-end window.
4. Start a versioned **Analysis** run. The workbench shows the governed checks as they progress.
5. Open **Risk cues** (Journal Entry Review), filter the queue, and select **Investigate** for the evidence and immutable review timeline.
6. Record a disposition and assignment. High-priority clearances require the independent second-review control.
7. Create a reproducible **Testing sample**, lock the review set, and generate the **Workpapers** package.
8. Use **Audit trail** for source lineage, acknowledgements, analysis runs, reviews, lock/reopen events, and exports.

The GUI binds to `localhost`; nothing uploads client data. **Run Demo** uses only the repository's synthetic fixture. See the [CLI / developer demo](#cli--developer-demo-synthetic-data-verified) for the current command-line equivalent.

## Run the workbench locally

### Recommended first run

From the repository root:

```sh
cd audit-analytics
uv sync --frozen --all-extras --group dev
npm --prefix frontend ci
npm --prefix frontend run build
mkdir -p engagements/local
uv run python run.py serve --db engagements/local/audit.db
```

Open [http://127.0.0.1:8788](http://127.0.0.1:8788), then choose **Run Demo** on
the launch screen. The demo uses only the repository's synthetic fixture. Stop
the server with `Ctrl+C`.

If you already activated the virtual environment, use this equivalent form:

```sh
source .venv/bin/activate
python3 run.py serve --db engagements/local/audit.db
```

### Create a real engagement

You can create the workspace from the UI, or initialize a local database first:

```sh
mkdir -p engagements/acme
uv run python run.py init \
  --db engagements/acme/audit.db \
  --client "Acme Ltd" \
  --period 2025-04-01:2026-03-31 \
  --owner manager

uv run python run.py serve --db engagements/acme/audit.db
```

Open `http://127.0.0.1:8788` and add the client ledger from **Population**. The
workbench supports CSV and ordinary first-sheet XLSX exports; the original file
is preserved as local evidence.

### Frontend development mode

Run the API and Vite dev server in separate terminals for hot reload.

Terminal 1:

```sh
uv run python run.py serve --db engagements/local/audit.db
```

Terminal 2:

```sh
npm --prefix frontend run dev
```

Open [http://127.0.0.1:5173](http://127.0.0.1:5173). Vite proxies `/api` requests
to port `8788`.

### Local-first notes

- The engagement database, preserved evidence, exports, and optional local model
  context remain in the selected local workspace.
- No cloud AI service is required for core analysis.
- After changing frontend source, rerun `npm --prefix frontend run build` before
  serving the production bundle.
- If port `8788` is busy, start with `--port 8790` and open
  `http://127.0.0.1:8790`.

## Step-by-step: first engagement

This guide creates a separate local database for one client and one audit
period. Run commands from this directory. Nothing in this workflow uploads the
client ledger; the only optional service is Ollama running on the same machine.

### 1. Check prerequisites and choose an engagement folder

Python 3.10+ and Node 22 are supported. The Python web extra and development
tools are installed from `uv.lock`; the React bundle is built from
`package-lock.json`. Use a firm-approved encrypted local folder or private VPC
volume and keep one database per engagement:

```sh
cd audit-analytics
uv sync --frozen --all-extras --group dev
source .venv/bin/activate
npm --prefix frontend ci
npm --prefix frontend run build
python3 run.py --help
mkdir -p engagements/example-ltd-fy26
```

Do not place the engagement database in a shared public folder. The database,
its neighbouring `evidence/` folder, exports, and backups contain client data.

### 2. Prepare the source extracts

Request a line-level GL extract and, where available, a COA extract. CSV or an
ordinary first-sheet XLSX export is accepted. Keep the received original file
unchanged; the application makes a hash-addressed evidence copy on import.

The GL needs these canonical concepts:

| Required concept | Common accepted headers |
| --- | --- |
| Entry identifier | `entry_id`, `journal_entry_id`, `voucher_no`, `voucher number`, `transaction_id` |
| Posting date | `posting_date`, `date`, `entry_date` |
| Account code | `account_code`, `account`, `gl_code`, `GL Code`, `ledger_code` |
| Amount | `amount`/`signed_amount`, or separate `debit` and `credit` columns |

Recommended fields are narration/description, preparer/user, reference or
document number, entity/cost centre, document date, and manual/system flag.
Use ISO dates (`YYYY-MM-DD`) where possible; `DD/MM/YYYY`, `DD-MM-YYYY`, and
`MM/DD/YYYY` are also accepted. Do not pre-filter “unimportant” accounts or
delete blank/malformed rows—those are population-quality evidence.

Before importing, obtain the client/source-system control totals: extracted row
count, total debit, and total credit. They are used to reconcile the accepted
population, not to infer a conclusion.

### 3. Create the engagement and local users

```sh
python3 run.py init \
  --db engagements/example-ltd-fy26/audit.db \
  --client "Example Ltd" \
  --period 2025-04-01:2026-03-31 \
  --owner engagement-manager

python3 run.py add-user --db engagements/example-ltd-fy26/audit.db \
  --actor engagement-manager --username audit-preparer --role preparer
python3 run.py add-user --db engagements/example-ltd-fy26/audit.db \
  --actor engagement-manager --username audit-reviewer --role reviewer
```

The owner starts as a local `manager`. Roles are workflow guardrails for this
local utility, not a substitute for firm SSO or access control on a shared
server. Use `manager`/`partner` for configuration and assignment;
`preparer`/`reviewer` for analytical work; and `quality_reviewer` for read and
review functions.

### 4. Preview and map the GL before import

Preview headers and the first few rows; do this before writing any engagement
data:

```sh
python3 run.py preview-gl --db engagements/example-ltd-fy26/audit.db \
  --file received/example_gl.csv
```

If `missing_required` is non-empty or an auto-detected field is wrong, create a
small JSON mapping. Values are the exact source headers:

```json
{
  "entry_id": "Voucher Number",
  "posting_date": "Posting Dt",
  "account_code": "GL Code",
  "amount": "Amount",
  "description": "Narration",
  "preparer": "Created By",
  "reference": "Document Number"
}
```

Save it as `engagements/example-ltd-fy26/gl-mapping.json`, validate with
`preview-gl --mapping ...`, then preserve the approved profile for repeat
imports:

```sh
python3 run.py save-mapping --db engagements/example-ltd-fy26/audit.db \
  --actor engagement-manager --name client-gl-v1 \
  --mapping engagements/example-ltd-fy26/gl-mapping.json
```

### 5. Import, inspect, and reconcile the population

Import the COA first if available, then the GL. Replace the example totals with
the actual totals received from the client/source system.

```sh
python3 run.py import-coa --db engagements/example-ltd-fy26/audit.db \
  --actor audit-preparer --file received/chart_of_accounts.csv

python3 run.py import-gl --db engagements/example-ltd-fy26/audit.db \
  --actor audit-preparer --file received/example_gl.csv \
  --mapping-name client-gl-v1 \
  --expected-rows 125430 \
  --expected-debits 987654321.50 \
  --expected-credits 987654321.50
# If the exact SHA-256 already exists, choose an explicit version action:
python3 run.py import-gl --db engagements/example-ltd-fy26/audit.db \
  --actor audit-preparer --file received/example_gl.csv --reimport
```

Read the JSON response and confirm accepted rows, rejected rows, calculated
debits/credits, and `reconciliation.matches`. Investigate rejected rows and
mapping errors before proceeding. Check the current state at any time:

```sh
python3 run.py status --db engagements/example-ltd-fy26/audit.db
```

An exact reconciliation can be acknowledged by an authorised reviewer:

```sh
python3 run.py acknowledge-population --db engagements/example-ltd-fy26/audit.db \
  --reviewer audit-reviewer \
  --note "Accepted row count and debit/credit totals agreed to the client GL control report dated 2026-04-12."
```

If the source totals are genuinely unavailable or a known difference remains,
the reviewer must document why it is acceptable; use the override deliberately,
never as a shortcut:

```sh
python3 run.py acknowledge-population --db engagements/example-ltd-fy26/audit.db \
  --reviewer audit-reviewer --override-reconciliation \
  --note "Client control report excludes opening-balance conversion lines; 42-line difference is documented in WP A-12."
```

The application blocks analysis until every GL import is acknowledged.

### 6. Set engagement methodology parameters

The defaults are transparent, conservative starting points. The engagement
team—not the tool—must decide whether they fit the client and methodology.

```sh
python3 run.py configure --db engagements/example-ltd-fy26/audit.db \
  --actor engagement-manager \
  --materiality 500000 \
  --performance-materiality 350000 \
  --round-amount-threshold 100000 \
  --period-end-days 3 \
  --outlier-robust-z 3.5
```

Each analysis run captures these settings. A changed policy requires a new run;
old runs remain reproducible.

Materiality settings are **disclosed planning thresholds only** — they never
change a risk score. `analyze` labels every exception `above_overall` /
`above_performance` / `below` by amount. When performance materiality is set,
`create-sample` bounds its random coverage slice to entries at or above it;
override with `--random-min-amount`.

### 7. Run analysis and understand the output

```sh
python3 run.py analyze --db engagements/example-ltd-fy26/audit.db \
  --actor audit-preparer
```

The hybrid suite includes repeated-entry patterns, round amounts, weekend and
period-end postings, rare account/preparer pairs, potential reversals, robust
account-peer outliers, and Benford applicability checks. The optional local
isolation-style scorer runs only for populations of 256+ entries; disable it
with `--no-isolation` if it is outside the approved engagement methodology.

Analysis is guarded at 100,000 rows on the measured local profile. A larger
import remains intact but is not silently analyzed; split or explicitly sample
the engagement rather than bypassing the guard. The limit is a measured local
boundary, not a universal hardware guarantee.

Each output is a risk cue with reasons and evidence. It is not a fraud finding,
an audit exception, or an audit opinion.

### 8. Review, assign, and disposition exceptions

Start the canonical local workbench (build the frontend once after checkout):

```sh
python3 run.py serve --db engagements/example-ltd-fy26/audit.db
```

Open `http://127.0.0.1:8788`. The React workbench uses the same workflow and
review invariants as the CLI; select a configured local user when saving a
disposition. The user selection is a local workflow label, not authentication.
The service is intentionally bound to localhost. For a fully documented
command-line workflow:

```sh
python3 run.py assign --db engagements/example-ltd-fy26/audit.db \
  --actor engagement-manager --exception 17 \
  --assignee audit-reviewer --due-date 2026-04-20

python3 run.py review --db engagements/example-ltd-fy26/audit.db \
  --exception 17 --reviewer audit-reviewer \
  --disposition selected_for_testing \
  --note "Selected for vouching. Obtain approval, contract, invoice, and subsequent-payment evidence."
```

Permitted dispositions are `open`, `cleared`, `follow_up`, and
`selected_for_testing`. Every review creates a new immutable review record and
audit-log entry; it does not overwrite earlier reasoning.

### 9. Create a reproducible review sample

The sample tool includes all high-risk cues, then the requested top-ranked
cues, then a seed-controlled random coverage selection. It is a sampling aid;
the engagement team documents and approves the final audit sample.

```sh
python3 run.py create-sample --db engagements/example-ltd-fy26/audit.db \
  --actor audit-reviewer --name "FY26 JE testing selection" \
  --risk-count 30 --random-count 15 --seed 20260412
```

### 10. Export the workpaper package and back up the engagement

```sh
python3 run.py export --db engagements/example-ltd-fy26/audit.db \
  --actor audit-reviewer --out engagements/example-ltd-fy26/exports/je-review.csv

python3 run.py report --db engagements/example-ltd-fy26/audit.db \
  --actor audit-reviewer --out engagements/example-ltd-fy26/exports/engagement-report.html
```

`export` writes the review CSV, a companion JSON manifest listing source
imports, hashes, run state, second-review evidence, and limitations, plus a
`<manifest>.sha256` checksum. `report` produces a readable HTML
engagement summary. The manifest is checksummed, not digitally signed. Archive
the database, `evidence/` directory, exports, and firm-prescribed workpapers
together using the firm’s approved retention and backup process.

## Local AI (optional)

Audit Analytics can use locally running embedding models to understand whether differently worded transactions are semantically similar — for example `"March GST liability provision"` ≈ `"GST payable accrued for March"`. The model helps find related or unusual transactions; it does not make an audit conclusion.

To use it: install and run Ollama locally (`ollama serve`; `ollama pull embeddinggemma`), then build the index (`python3 run.py embed-ledger`) and query (`similar --db demo/audit.db --query "..."`). Technical details (models, evaluation framework, ceilings, vector-storage notes) are in [`docs/SEMANTIC_ENGINE.md`](docs/SEMANTIC_ENGINE.md).

## Semantic Risk Engine (experimental lab)

An opt-in laboratory layer documented fully in [`docs/SEMANTIC_ENGINE.md`](docs/SEMANTIC_ENGINE.md). It uses narration-only vectors, account/vendor/preparer profiles, deterministic clusters, and peer-comparison cues — never a black-box verdict, never an external LLM call. It is designed for reproducible, explainable audit support, not automatic conclusions. Technical details (run mechanics, ceilings, model registry, evaluation framework) belong in that document.

## Supported GL fields

Headers are matched case-insensitively with common aliases. Required: entry ID,
posting date, account code, and either signed amount or debit and credit.
Optional fields include document date, description/narration, preparer/user,
reference/document number, entity, vendor/supplier, and manual/system indicator. Existing rows without vendor remain missing (no guessed backfill). COA imports
are supported through `import-coa` and enrich account labels only.

CSV and ordinary first-sheet `.xlsx` exports are supported with the standard
library; no client data is uploaded or sent to a conversion service.

## Additional commands (Releases 1.1–1.4)

These build on the first-engagement workflow above. Every command is local; none
send client data off the engagement host.

- `import-account-taxonomy --file tax.csv` — load the firm's account-type/label
  taxonomy (kept separate from the client COA). `analyze` tags each exception with
  `account_type` / `account_label` for filtering.
- `set-fiscal-calendar --dates 2026-03-31,2026-06-30` — firm period-end dates;
  `analyze` flags postings within the period-end window of any of them.
- `compare-runs --run-a N --run-b M` — new/resolved cues and score deltas between
  two analysis runs (also `/compare-runs` in the UI).
- `review --exception N --disposition cleared --note … --second-reviewer X
  --second-note …` — clearing a **high-severity** exception requires a second,
  distinct reviewer (governance control).
- `lock-reviews` / `reopen-reviews` — append immutable, reasoned review-set
  events; a locked set rejects review and assignment changes.
- `import-connector --connector demo_csv --file …` — import via a connector
  adapter that produces the same canonical import plus a `connector_runs` manifest.
  The `demo_csv` adapter is shipped to prove the interface; SAP/Oracle/Tally/
  QuickBooks adapters are deferred pending firm-authorized access + a data dictionary.
- `import-bank --file bank.csv` + `reconcile-bank` — import a bank statement as a
  separate evidence type and reconcile it to ledger entries by date + amount.
- `register-model` / `validate-model` / `list-models` — governed model registry
  for provenance/approval metadata (actual statistical validation is deferred
  until labelled, authorised populations exist).
- `export` — writes a workpaper CSV, manifest, and detached SHA-256 checksum;
  the checksum is integrity evidence, not a digital signature.

## Controls and limitations

- Every imported source file is copied into `evidence/` beside the engagement
  database and is SHA-256 hashed; each entry retains source row identity.
- Import validation separates rejected/missing data from risk cues.
- Analysis is blocked until a reviewer acknowledges the accepted population and
  control totals.
- The statistical suite includes deterministic tests, account-peer robust
  outliers, Benford population checks, reversal matching, and an optional local
  isolation-style model for populations of at least 256 entries.
- Risk scores are prioritisation cues. Reviewer dispositions and audit-log
  records are append-only; no result is labelled fraud or an audit conclusion.

The controls are designed to support documentation under SA 230 and journal
entry procedures under SA 240; the engagement team remains responsible for
audit design, evidence evaluation, and conclusions.

## Future plans (deferred; see IMPLEMENTATION_PLAN.md for full roadmap)

These are future directions, not current features. Each requires firm
approval, authorised data, or validated methodology before implementation.

- **Release 1.1 — audit-methodology hardening:** import-mapping preview
  and saved per-engagement mapping profiles; structured client control-total
  reconciliation; materiality as disclosed planning thresholds (delivered —
  `materiality_band`, `--random-min-amount`); account labels/type filters;
  fiscal-calendar controls; workbook/PDF output; model-run comparison;
  formal methodology/limitations report.
- **Release 1.2 — review governance:** local user roles (preparer,
  reviewer, engagement manager, quality reviewer); second-level approval for
  cleared high-severity exceptions; immutable lock/reopen events; checksummed
  export manifests with SHA-256 workpaper and detached manifest hashes.
- **Release 2 — controlled ERP connectors:** read-only adapters for SAP,
  Oracle, Tally, QuickBooks and approved systems, each producing a
  connector-run manifest (authorization identity, query/version,
  extraction timestamp, record count, control totals, source identifiers).
  Requires firm-authorized access + data dictionary per adapter. The
  `demo_csv` connector interface is proven and ready to extend; real
  adapters are **DEFERRED**.
- **Release 3 — expanded forensic datasets:** vendor/customer masters,
  bank extracts (delivered — `import-bank`/`reconcile-bank`), invoices,
  purchase orders, and related-party datasets as separate normalized
  evidence types. Graph and text-similarity analysis only with explicit
  coverage and false-positive controls.
- **Release 4 — validated advanced models:** governed model registry
  (delivered for provenance/approval metadata only) to replace the
  compact isolation-style scorer **only after** documented validation
  across representative, authorised audit populations. Actual statistical
  validation, calibration, drift checks, and approval workflows are
  **DEFERRED** — they require labelled, authorised audit populations and
  governance sign-off. The isolation scorer remains the only active model
  and is disableable per run.
- **Semantic Risk Engine:** Phase 1 (A–E) is delivered and documented in
  `docs/SEMANTIC_ENGINE.md`. Future phases (investigation assistant, calibrated multi-detector
  aggregation, governed feedback) are deferred and require authorised
  validation before promotion beyond laboratory use.

**Important:** This is a local-first laboratory tool, not a production
audit system. It never issues audit opinions, determines fraud, or
treats risk scores as findings. No outbound network calls are made for
engagement data without an explicitly approved connector or feature.
