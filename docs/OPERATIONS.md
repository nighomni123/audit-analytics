# Local Operations

Audience: auditor, maintainer, or support engineer running the loopback laboratory workbench.

## Supported boundary

The supported service is a single-host, loopback-only laboratory application. Start it with the database selected for the engagement:

```sh
python3 run.py serve --db engagements/example/audit.db --port 8788
```

The API refuses to be a network authentication boundary. The user selected in the UI is a local workflow label, not a login. Do not expose Uvicorn on a LAN or internet; network deployment requires firm SSO/RBAC, TLS, session/CSRF controls, audit retention, and tenant isolation first.

## Health and logs

```sh
curl http://127.0.0.1:8788/api/health
```

A healthy response reports database connectivity, schema version, and packaged static UI readiness. Set `AUDIT_LOG_LEVEL=INFO` (or `DEBUG` temporarily) for operational logs. Logs go to stderr and contain request ID, method, route template, status, and duration. They intentionally omit query strings, narrations, file contents, and full engagement paths. The SQLite `audit_log` is business history and is separate from runtime diagnostics.

## Backup and restore

Use SQLite's online backup API so WAL state is included consistently. Do not copy only a live `.db` file while the service is writing. A minimal Python backup is:

```python
import sqlite3
source = sqlite3.connect("engagements/example/audit.db")
destination = sqlite3.connect("/secure/backup/audit.db")
try:
    source.backup(destination)
finally:
    destination.close()
    source.close()
```

Verify the copy before archiving:

```sh
sqlite3 /secure/backup/audit.db "PRAGMA integrity_check;"
```

Archive the database, hash-addressed `evidence/` directory, exports, and firm-prescribed workpapers together under the firm's retention policy. The automated round-trip check is `tests/test_operations.py`.

## Recovery checklist

1. Stop the service before restoring files.
2. Restore the database and evidence directory into an access-controlled engagement folder.
3. Run `PRAGMA integrity_check` and inspect `/api/status` and `/api/health`.
4. Confirm imports, review-set events, latest model run, and source hashes.
5. Reopen only after the evidence and database belong to the same engagement.

## Troubleshooting

- **Blank or old UI:** run `npm --prefix frontend ci` and `npm --prefix frontend run build`; confirm `src/audit_analytics/static/index.html` exists.
- **API unavailable:** verify `serve` is bound to `127.0.0.1`, inspect stderr, and call `/api/health`.
- **Import rejected as duplicate:** compare the SHA-256 and import ID; use the explicit “new version” action only when the duplicate is intentional.
- **Analysis blocked:** first verify acknowledgement/reconciliation. If the error mentions the analysis safety limit, the import is retained; split or explicitly sample the engagement rather than bypassing the guard.
- **Semantic evidence stale:** the population changed after the profile; rebuild the profile before linking a new analysis run.
- **Review locked:** use a manager/partner lock reason and the reopen event; do not edit SQLite tables directly.

## Analysis capacity boundary

Import and analysis have different limits. Imports of 250k/500k synthetic rows are supported as evidence retention, but deterministic analysis is guarded at 100,000 rows on the measured local profile. A blocked analysis leaves the import and evidence intact; it does not create a partial model run. Treat the limit as measured-host evidence, not a universal hardware guarantee.

The remediation benchmark reduced dense same-account/same-amount analysis from 433.61s at 10k rows to 0.94s, with 50k measured at 15.69s. The ordinary similarity path remains a dense in-memory scan; 100k at 64 dimensions used approximately 398 MB and 17.29 seconds. Higher-dimensional embeddings and concurrent requests require a separate capacity benchmark.

## Operational boundaries

The current benchmark harness (`scripts/benchmark_similarity.py`) measures exact batched retrieval at 10k/50k/100k synthetic entries. A 100k, 64-dimension local run completed in the measured development environment; higher-dimensional models consume more memory. The supported ceiling is a local engagement workflow, not a multi-user service. ANN/vector databases and model promotion require a separate measured decision and governance approval.

For local browser checks, reuse the approved existing Chromium executable via `PLAYWRIGHT_CHROMIUM`; CI installs its own locked browser in an ephemeral runner.
