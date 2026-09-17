# Architecture — Actual System

Audience: developer / coding agent.

## Runtime stack

- Python 3, stdlib + minimal installed dependencies.
- CLI entry: `run.py` → `src/audit_analytics/cli.py` (`argparse`, one branch per subcommand).
- Server: `src/audit_analytics/server.py` (`http.server.BaseHTTPRequestHandler` + `ThreadingHTTPServer`), bound `127.0.0.1:8788` by default. No external web framework.
- Data store: SQLite (`src/audit_analytics/store.py` — `Store` class). System of record per engagement.
- Embedding transport: local `Ollama` (`embeddinggemma` default) via loopback; optional only; same-host.
- No React, no Vite, no FastAPI in current source. A future GUI (`Audit Workbench`) is planned but not implemented.

## Module map (actual)

```
run.py
  cli.py          argparse surface; subcommands branch
  store.py        SQLite schema + reconciliation + audit_log
  importer.py     import-gl / import-coa / preview-gl
  analytics.py     deterministic analytics + optional isolation
  semantic.py     token classifier + Ollama transport + cosine
  semantic_risk.py  profile / investigate / evaluate / lifecycle
  semantic_evaluation.py  label-based offline evaluation
  reports.py      engagement_summary / export_workpaper / HTML report
  server.py       localhost review server (:8788)
  sampling.py     create_sample()
  bank.py         import-bank / reconcile-bank
  connectors.py   BaseConnector + DemoCsvConnector
  model_registry.py  register/validate/list/stamp
```

## Data flow (actual, today)

```
source file (CSV / first-sheet XLSX)
    ↓ copy to evidence/ + SHA-256
importer.import_gl()
    ↓ canonical mapping
ledger_entries + rejected_rows
    ↓ acknowledge-population (required before analyze)
analytics.analyze()  →  exceptions + model_runs
    ↓ (optional --semantic-run ID)
semantic_risk.semantic_profile()  →  semantic_runs + profiles
    ↓
semantic_investigate()  →  investigation page (read-only)
semantic_evaluate()  →  offline label-based report
    ↓
export / report / review (append-only reviews + audit_log)
```

## Security and deployment baseline (actual)

- Local laptop / server / private VPC only.
- `serve` binds `127.0.0.1` by default; network deployment requires firm SSO, TLS, role-based access, session expiry, CSRF, audit-log retention, encrypted backups, tenancy isolation — not yet built (planned 1.2).
- No outbound network for client data; only optional same-host Ollama.
- Additive schema only; never drop/rename raw rows, hashes, notes, or old model-run outputs.

## Build / verification

```sh
PYTHONPATH=src python3 -m pytest tests/ -q      # 25 tests
python3 run.py --help                             # ~34 subcommands
python3 run.py init --db /tmp/demo.db ...        # smoke init
```

See `docs/SEMANTIC_ENGINE.md` for the semantic layer design; see `README.md` for CLI/reference; see `AGENTS.md` for agent rules.
