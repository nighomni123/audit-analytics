from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analytics import analyze
from .bank import import_bank, reconcile_bank
from .connectors import run_connector
from .importer import import_coa, import_gl, preview_gl
from .model_registry import list_models, register_model, validate_model
from .reports import compare_runs, engagement_summary, export_workpaper, write_engagement_report
from .sampling import create_sample
from .semantic import embed_ledger, similar_transactions
from .server import serve
from .store import Store

DEFAULT_ACTOR = "engagement-owner"


def _mapping(args, store):
    if getattr(args, "mapping", None):
        return json.loads(Path(args.mapping).read_text(encoding="utf-8"))
    if getattr(args, "mapping_name", None):
        row = store.conn.execute("SELECT mapping_json FROM import_mappings WHERE name=?", (args.mapping_name,)).fetchone()
        if not row:
            raise ValueError(f"mapping profile not found: {args.mapping_name}")
        return json.loads(row[0])
    return None


def _require(store, actor, roles):
    store.require_role(actor, set(roles))


def _import_account_taxonomy(store, file, actor):
    """Load firm account-type/label taxonomy. Kept separate from the client COA."""
    import csv as _csv
    n = 0
    with open(file, newline="", encoding="utf-8") as f:
        for row in _csv.DictReader(f):
            code = (row.get("account_code") or row.get("code") or "").strip()
            if not code:
                continue
            atype = (row.get("account_type") or row.get("type") or "").strip() or None
            label = (row.get("label") or row.get("name") or "").strip() or None
            raw_rw = row.get("risk_weight")
            try:
                rw = float(raw_rw) if raw_rw not in (None, "") else None
            except ValueError:
                rw = None
            store.conn.execute(
                "INSERT INTO account_taxonomy(account_code, account_type, label, risk_weight) "
                "VALUES(?,?,?,?) ON CONFLICT(account_code) DO UPDATE SET "
                "account_type=excluded.account_type, label=excluded.label, risk_weight=excluded.risk_weight",
                (code, atype, label, rw))
            n += 1
    store.log(actor, "import_account_taxonomy", "taxonomy", file, {"rows": n})
    store.conn.commit()
    return n


def _parse_fiscal_calendar(args):
    if args.file:
        data = json.loads(Path(args.file).read_text(encoding="utf-8"))
        return data if isinstance(data, list) else data.get("dates", [])
    if args.dates:
        return [d.strip() for d in args.dates.split(",") if d.strip()]
    raise ValueError("provide --dates or --file")


def main():
    p = argparse.ArgumentParser(description="Local-first journal-entry audit analytics")
    sub = p.add_subparsers(dest="cmd", required=True)
    init = sub.add_parser("init", help="create an isolated engagement")
    init.add_argument("--db", required=True); init.add_argument("--client", required=True)
    init.add_argument("--period", required=True, help="YYYY-MM-DD:YYYY-MM-DD")
    init.add_argument("--owner", default=DEFAULT_ACTOR)

    for name in ("import-gl", "import-coa"):
        command = sub.add_parser(name)
        command.add_argument("--db", required=True); command.add_argument("--file", required=True)
        command.add_argument("--actor", default=DEFAULT_ACTOR)
    gl = sub.choices["import-gl"]
    gl.add_argument("--mapping", help="JSON canonical-field to source-header mapping")
    gl.add_argument("--mapping-name")
    gl.add_argument("--expected-rows", type=int); gl.add_argument("--expected-debits", type=float)
    gl.add_argument("--expected-credits", type=float)

    preview = sub.add_parser("preview-gl", help="inspect detected source headers before import")
    preview.add_argument("--db", required=True); preview.add_argument("--file", required=True)
    preview.add_argument("--mapping")
    save_mapping = sub.add_parser("save-mapping", help="save a reviewed mapping profile")
    save_mapping.add_argument("--db", required=True); save_mapping.add_argument("--name", required=True)
    save_mapping.add_argument("--mapping", required=True); save_mapping.add_argument("--actor", default=DEFAULT_ACTOR)
    list_mappings = sub.add_parser("list-mappings"); list_mappings.add_argument("--db", required=True)

    ack = sub.add_parser("acknowledge-population", help="record reconciliation and unlock analysis")
    ack.add_argument("--db", required=True); ack.add_argument("--reviewer", required=True); ack.add_argument("--note", required=True)
    ack.add_argument("--override-reconciliation", action="store_true", help="requires a note explaining a known difference")

    configure = sub.add_parser("configure", help="set engagement methodology thresholds")
    configure.add_argument("--db", required=True); configure.add_argument("--actor", default=DEFAULT_ACTOR)
    configure.add_argument("--materiality", type=float); configure.add_argument("--performance-materiality", type=float)
    configure.add_argument("--round-amount-threshold", type=float); configure.add_argument("--period-end-days", type=int)
    configure.add_argument("--outlier-robust-z", type=float)
    user = sub.add_parser("add-user", help="add/update a local workflow user")
    user.add_argument("--db", required=True); user.add_argument("--username", required=True); user.add_argument("--role", required=True); user.add_argument("--actor", default=DEFAULT_ACTOR)

    analyze_cmd = sub.add_parser("analyze"); analyze_cmd.add_argument("--db", required=True)
    analyze_cmd.add_argument("--actor", default=DEFAULT_ACTOR); analyze_cmd.add_argument("--no-isolation", action="store_true")
    analyze_cmd.add_argument("--semantic-run", type=int, help="explicit completed semantic profile run to aggregate")
    profile = sub.add_parser("semantic-profile", help="build experimental local semantic risk profiles")
    profile.add_argument("--db", required=True); profile.add_argument("--model", default="embeddinggemma")
    profile.add_argument("--batch-size", type=int, default=64); profile.add_argument("--actor", default=DEFAULT_ACTOR)
    profile.add_argument("--config", help="JSON file of experimental semantic thresholds and clustering parameters")
    investigate = sub.add_parser("semantic-investigate", help="read stored semantic investigation evidence offline")
    investigate.add_argument("--db", required=True); investigate.add_argument("--run", type=int, required=True)
    investigate.add_argument("--ledger-id", type=int, required=True)
    evaluate = sub.add_parser("semantic-evaluate", help="evaluate a stored semantic run against authorised labels")
    evaluate.add_argument("--db", required=True); evaluate.add_argument("--run", type=int, required=True)
    evaluate.add_argument("--labels", required=True); evaluate.add_argument("--actor", default=DEFAULT_ACTOR)
    embed = sub.add_parser("embed-ledger", help="create local Ollama vectors; no data leaves this host")
    embed.add_argument("--db", required=True); embed.add_argument("--model", default="embeddinggemma")
    embed.add_argument("--batch-size", type=int, default=64); embed.add_argument("--actor", default=DEFAULT_ACTOR)
    similar = sub.add_parser("similar", help="find semantically and token-similar transactions")
    similar.add_argument("--db", required=True); similar.add_argument("--query", required=True)
    similar.add_argument("--limit", type=int, default=25); similar.add_argument("--model", default="embeddinggemma")

    review = sub.add_parser("review", help="record a reviewer disposition")
    review.add_argument("--db", required=True); review.add_argument("--exception", type=int, required=True)
    review.add_argument("--reviewer", required=True); review.add_argument("--disposition", choices=("open", "cleared", "follow_up", "selected_for_testing"), required=True); review.add_argument("--note", required=True)
    review.add_argument("--second-reviewer", help="required when clearing a high-severity exception")
    review.add_argument("--second-note", help="second reviewer's note (required with --second-reviewer)")
    assign = sub.add_parser("assign", help="assign an exception for review")
    assign.add_argument("--db", required=True); assign.add_argument("--exception", type=int, required=True)
    assign.add_argument("--assignee", required=True); assign.add_argument("--due-date"); assign.add_argument("--actor", default=DEFAULT_ACTOR)
    sample = sub.add_parser("create-sample", help="create a reproducible risk and random coverage sample")
    sample.add_argument("--db", required=True); sample.add_argument("--name", required=True); sample.add_argument("--run", type=int)
    sample.add_argument("--risk-count", type=int, default=20); sample.add_argument("--random-count", type=int, default=10)
    sample.add_argument("--seed", type=int, default=1); sample.add_argument("--actor", default=DEFAULT_ACTOR)
    sample.add_argument("--random-min-amount", type=float, default=None, help="random coverage slice limited to |amount| >= this; defaults to configured performance materiality")
    export = sub.add_parser("export", help="export exception workpaper plus evidence manifest")
    export.add_argument("--db", required=True); export.add_argument("--out", required=True); export.add_argument("--actor", default=DEFAULT_ACTOR)
    report = sub.add_parser("report", help="write an HTML engagement summary")
    report.add_argument("--db", required=True); report.add_argument("--out", required=True); report.add_argument("--actor", default=DEFAULT_ACTOR)
    status = sub.add_parser("status", help="show engagement, reconciliation, analysis, and review state"); status.add_argument("--db", required=True)
    serve_cmd = sub.add_parser("serve"); serve_cmd.add_argument("--db", required=True); serve_cmd.add_argument("--port", type=int, default=8788)

    # ---- Release 1.1: account taxonomy + fiscal calendar ----
    tax = sub.add_parser("import-account-taxonomy", help="load firm account-type/label taxonomy (separate from client COA)")
    tax.add_argument("--db", required=True); tax.add_argument("--file", required=True); tax.add_argument("--actor", default=DEFAULT_ACTOR)
    fcal = sub.add_parser("set-fiscal-calendar", help="set firm fiscal period-end dates used by analytics")
    fcal.add_argument("--db", required=True); fcal.add_argument("--actor", default=DEFAULT_ACTOR)
    fcal.add_argument("--dates", help="comma-separated YYYY-MM-DD period-end dates")
    fcal.add_argument("--file", help="JSON file with a list of YYYY-MM-DD dates")
    cmp = sub.add_parser("compare-runs", help="compare two analysis runs (new/resolved cues + score deltas)")
    cmp.add_argument("--db", required=True); cmp.add_argument("--run-a", type=int, required=True); cmp.add_argument("--run-b", type=int, required=True)

    # ---- Release 1.2: review governance ----
    lock = sub.add_parser("lock-reviews", help="record a completed-review-set milestone (additive; reopen to change)")
    lock.add_argument("--db", required=True); lock.add_argument("--actor", required=True)
    reopen = sub.add_parser("reopen-reviews", help="additively reopen a locked review set")
    reopen.add_argument("--db", required=True); reopen.add_argument("--actor", required=True)

    # ---- Release 2: connector adapters (demo only; real ERP deferred) ----
    conn = sub.add_parser("import-connector", help="import via a connector adapter (demo_csv; real ERP connectors deferred)")
    conn.add_argument("--db", required=True); conn.add_argument("--actor", default=DEFAULT_ACTOR)
    conn.add_argument("--connector", required=True); conn.add_argument("--file", required=True)

    # ---- Release 3: bank statement evidence + reconciliation ----
    ibank = sub.add_parser("import-bank", help="import a bank statement as separate evidence type")
    ibank.add_argument("--db", required=True); ibank.add_argument("--actor", default=DEFAULT_ACTOR); ibank.add_argument("--file", required=True)
    rbank = sub.add_parser("reconcile-bank", help="reconcile bank statements to ledger entries")
    rbank.add_argument("--db", required=True); rbank.add_argument("--actor", default=DEFAULT_ACTOR)
    rbank.add_argument("--tolerance", type=float, default=1.0); rbank.add_argument("--days", type=int, default=3)

    # ---- Release 4: model registry (provenance only; validation deferred) ----
    reg = sub.add_parser("register-model", help="register a model in the governed registry (provenance)")
    reg.add_argument("--db", required=True); reg.add_argument("--actor", required=True)
    reg.add_argument("--name", required=True); reg.add_argument("--type", required=True)
    reg.add_argument("--feature-schema", required=True, help="JSON object of feature schema")
    reg.add_argument("--owner", required=True)
    val = sub.add_parser("validate-model", help="record model validation/approval metadata (statistical validation deferred)")
    val.add_argument("--db", required=True); val.add_argument("--actor", required=True)
    val.add_argument("--name", required=True); val.add_argument("--approved-by", required=True)
    val.add_argument("--performance", help="JSON object of performance metrics")
    lmod = sub.add_parser("list-models", help="list registered models"); lmod.add_argument("--db", required=True)

    args = p.parse_args(); store = Store(args.db)
    try:
        if args.cmd == "init":
            start, end = args.period.split(":", 1)
            store.conn.execute("INSERT INTO engagement VALUES(1,?,?,?,strftime('%s','now'))", (args.client, start, end))
            store.add_user(args.owner, "manager", "system")
            store.set_setting("analysis_policy", {"round_amount_threshold": 1000, "period_end_days": 3, "outlier_robust_z": 3.5}, args.owner)
            store.set_setting("materiality", {}, args.owner)
            store.log(args.owner, "init", "engagement", 1, {"client": args.client}); store.conn.commit()
            print(f"created engagement for {args.client}; owner={args.owner}")
        elif args.cmd == "preview-gl":
            print(json.dumps(preview_gl(args.file, _mapping(args, store)), indent=2, default=str))
        elif args.cmd == "save-mapping":
            _require(store, args.actor, ("manager", "partner")); mapping = json.loads(Path(args.mapping).read_text(encoding="utf-8"))
            store.conn.execute("INSERT INTO import_mappings VALUES(?,?,strftime('%s','now'),?) ON CONFLICT(name) DO UPDATE SET mapping_json=excluded.mapping_json,created_at=excluded.created_at,created_by=excluded.created_by", (args.name, json.dumps(mapping, sort_keys=True), args.actor))
            store.log(args.actor, "save_mapping", "mapping", args.name, mapping); store.conn.commit(); print(f"saved mapping profile {args.name}")
        elif args.cmd == "list-mappings":
            print(json.dumps([dict(r) for r in store.conn.execute("SELECT name,created_at,created_by FROM import_mappings ORDER BY name")], indent=2))
        elif args.cmd == "import-gl":
            _require(store, args.actor, ("preparer", "reviewer", "manager", "partner"))
            iid, accepted, rejected, debits, credits = import_gl(store, args.file, args.actor, _mapping(args, store), args.expected_rows, args.expected_debits, args.expected_credits)
            print(json.dumps({"import_id": iid, "accepted": accepted, "rejected": rejected, "debits": debits, "credits": credits, "reconciliation": store.reconciliation(iid)}, indent=2))
        elif args.cmd == "import-coa":
            _require(store, args.actor, ("preparer", "reviewer", "manager", "partner")); print(f"COA import {import_coa(store, args.file, args.actor)} complete")
        elif args.cmd == "acknowledge-population":
            _require(store, args.reviewer, ("reviewer", "manager", "partner", "quality_reviewer"))
            pending = store.conn.execute("SELECT id FROM imports WHERE kind='gl' AND acknowledged_at IS NULL").fetchall()
            if not pending: raise ValueError("no unacknowledged GL imports")
            for row in pending:
                rec = store.reconciliation(row["id"])
                if not rec["matches"] and not args.override_reconciliation:
                    raise ValueError(f"import {row['id']} has no matching supplied control totals; use --override-reconciliation only with a documented difference")
                store.conn.execute("UPDATE imports SET reconciled_at=strftime('%s','now'),reconciled_by=?,reconciliation_note=?,acknowledged_at=strftime('%s','now'),acknowledged_by=?,acknowledgement_note=? WHERE id=?", (args.reviewer, args.note, args.reviewer, args.note, row["id"]))
                store.log(args.reviewer, "acknowledge_population", "import", row["id"], {"reconciliation": rec, "override": args.override_reconciliation, "note": args.note})
            store.conn.commit(); print(f"acknowledged {len(pending)} reconciled GL import(s)")
        elif args.cmd == "configure":
            _require(store, args.actor, ("manager", "partner")); policy = store.get_setting("analysis_policy", {}); materiality = store.get_setting("materiality", {})
            for value, key in ((args.round_amount_threshold, "round_amount_threshold"), (args.period_end_days, "period_end_days"), (args.outlier_robust_z, "outlier_robust_z")):
                if value is not None: policy[key] = value
            if args.materiality is not None: materiality["overall"] = args.materiality
            if args.performance_materiality is not None: materiality["performance"] = args.performance_materiality
            store.set_setting("analysis_policy", policy, args.actor); store.set_setting("materiality", materiality, args.actor)
            store.log(args.actor, "configure", "engagement", 1, {"analysis_policy": policy, "materiality": materiality}); store.conn.commit(); print(json.dumps({"analysis_policy": policy, "materiality": materiality}, indent=2))
        elif args.cmd == "add-user":
            _require(store, args.actor, ("manager", "partner")); store.add_user(args.username, args.role, args.actor); store.conn.commit(); print(f"user {args.username} is {args.role}")
        elif args.cmd == "analyze":
            _require(store, args.actor, ("preparer", "reviewer", "manager", "partner")); print(f"analysis run {analyze(store, args.actor, not args.no_isolation, args.semantic_run)} complete")
        elif args.cmd == "embed-ledger":
            _require(store, args.actor, ("preparer", "reviewer", "manager", "partner")); print(f"embedded {embed_ledger(store, args.model, args.batch_size, args.actor)} changed ledger entries locally")
        elif args.cmd == "semantic-profile":
            from .semantic_risk import semantic_profile
            _require(store, args.actor, ("preparer", "reviewer", "manager", "partner"))
            config = json.loads(Path(args.config).read_text(encoding="utf-8")) if args.config else None
            print(json.dumps(semantic_profile(store, args.model, args.batch_size, args.actor, config), indent=2, default=str))
        elif args.cmd == "semantic-investigate":
            from .semantic_risk import semantic_investigate
            print(json.dumps(semantic_investigate(store, args.run, args.ledger_id), indent=2, default=str))
        elif args.cmd == "semantic-evaluate":
            from .semantic_evaluation import evaluate_semantic
            _require(store, args.actor, ("reviewer", "manager", "partner", "quality_reviewer"))
            print(json.dumps(evaluate_semantic(store, args.run, args.labels, args.actor), indent=2, default=str))
        elif args.cmd == "similar":
            rows = similar_transactions(store, args.query, args.limit, args.model); print(json.dumps({"query": args.query, "count": len(rows), "results": rows}, indent=2))
        elif args.cmd == "review":
            _require(store, args.reviewer, ("reviewer", "manager", "partner", "quality_reviewer"))
            exc = store.conn.execute("SELECT severity FROM exceptions WHERE id=?", (args.exception,)).fetchone()
            if not exc: raise ValueError("exception not found")
            second_reviewer, second_note = None, None
            # ponytail: second-level approval is a real governance control for
            # high-severity clears; it adds a column, it never overwrites the
            # first reviewer's reasoning (reviews remain append-only).
            if args.disposition == "cleared" and exc["severity"] == "high":
                if not args.second_reviewer or not args.second_note:
                    raise ValueError("clearing a high-severity exception requires a second reviewer (--second-reviewer) and --second-note")
                if args.second_reviewer == args.reviewer:
                    raise ValueError("second reviewer must differ from the first reviewer")
                second_reviewer, second_note = args.second_reviewer, args.second_note
            review_id = store.conn.execute("INSERT INTO reviews(exception_id,reviewer,disposition,note,created_at,second_reviewer,second_note) VALUES(?,?,?,?,strftime('%s','now'),?,?)", (args.exception, args.reviewer, args.disposition, args.note, second_reviewer, second_note)).lastrowid
            store.conn.execute("UPDATE exceptions SET status=? WHERE id=?", (args.disposition, args.exception)); store.log(args.reviewer, "review_exception", "exception", args.exception, {"review_id": review_id, "disposition": args.disposition, "second_reviewer": second_reviewer}); store.conn.commit(); print(f"recorded review {review_id}")
        elif args.cmd == "assign":
            _require(store, args.actor, ("manager", "partner")); store.require_role(args.assignee, {"preparer", "reviewer", "manager", "partner", "quality_reviewer"})
            if not store.conn.execute("UPDATE exceptions SET assigned_to=?,due_date=? WHERE id=?", (args.assignee, args.due_date, args.exception)).rowcount: raise ValueError("exception not found")
            store.log(args.actor, "assign_exception", "exception", args.exception, {"assignee": args.assignee, "due_date": args.due_date}); store.conn.commit(); print(f"assigned exception {args.exception} to {args.assignee}")
        elif args.cmd == "create-sample":
            _require(store, args.actor, ("reviewer", "manager", "partner", "quality_reviewer")); sample_id, count = create_sample(store, args.name, args.actor, args.run, args.risk_count, args.random_count, args.seed, args.random_min_amount); print(f"sample set {sample_id}: {count} entries")
        elif args.cmd == "export":
            _require(store, args.actor, ("preparer", "reviewer", "manager", "partner", "quality_reviewer")); out, manifest, count = export_workpaper(store, args.out, args.actor); print(f"wrote {count} review cues to {out}; manifest={manifest}")
        elif args.cmd == "report":
            _require(store, args.actor, ("preparer", "reviewer", "manager", "partner", "quality_reviewer")); print(f"wrote engagement report to {write_engagement_report(store, args.out, args.actor)}")
        elif args.cmd == "import-account-taxonomy":
            _require(store, args.actor, ("manager", "partner")); n = _import_account_taxonomy(store, args.file, args.actor); print(f"loaded {n} account taxonomy rows")
        elif args.cmd == "set-fiscal-calendar":
            _require(store, args.actor, ("manager", "partner")); dates = _parse_fiscal_calendar(args)
            store.set_setting("fiscal_calendar", dates, args.actor); store.log(args.actor, "set_fiscal_calendar", "engagement", 1, {"dates": dates}); store.conn.commit(); print(f"fiscal calendar set: {dates}")
        elif args.cmd == "compare-runs":
            print(json.dumps(compare_runs(store, args.run_a, args.run_b), indent=2, default=str))
        elif args.cmd == "lock-reviews":
            store.set_review_lock(args.actor); print("review set locked (milestone recorded; reopen to change)")
        elif args.cmd == "reopen-reviews":
            store.clear_review_lock(args.actor); print("review set reopened (additive record kept)")
        elif args.cmd == "import-connector":
            _require(store, args.actor, ("preparer", "reviewer", "manager", "partner"))
            iid, manifest = run_connector(args.connector, store, args.file, args.actor)
            print(json.dumps({"import_id": iid, **manifest}, indent=2))
        elif args.cmd == "import-bank":
            _require(store, args.actor, ("preparer", "reviewer", "manager", "partner"))
            iid, accepted, rejected = import_bank(store, args.file, args.actor)
            print(json.dumps({"import_id": iid, "accepted": accepted, "rejected": rejected}, indent=2))
        elif args.cmd == "reconcile-bank":
            _require(store, args.actor, ("preparer", "reviewer", "manager", "partner"))
            n = reconcile_bank(store, args.actor, args.tolerance, args.days); print(f"bank reconciliation: {n} matches recorded")
        elif args.cmd == "register-model":
            mid = register_model(store, args.name, args.type, json.loads(args.feature_schema), args.owner, args.actor)
            print(f"registered model {args.name} (id {mid})")
        elif args.cmd == "validate-model":
            validate_model(store, args.name, args.actor, json.loads(args.performance) if args.performance else None, args.approved_by)
            print(f"validated model {args.name}")
        elif args.cmd == "list-models":
            print(json.dumps(list_models(store), indent=2, default=str))
        elif args.cmd == "status":
            summary = engagement_summary(store); summary["review_locked"] = store.review_locked()
            print(json.dumps(summary, indent=2, default=str))
        else:
            serve(args.db, args.port)
    except (ValueError, LookupError, OSError) as exc:
        p.exit(2, f"error: {exc}\n")
    finally:
        store.close()
