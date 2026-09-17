"""Portable workpaper exports and engagement status summaries."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import time
from pathlib import Path

from .store import Store


def compare_runs(store: Store, run_a, run_b):
    a = {r[0]: r[1] for r in store.conn.execute("SELECT ledger_id,risk_score FROM exceptions WHERE run_id=?", (run_a,))}
    b = {r[0]: r[1] for r in store.conn.execute("SELECT ledger_id,risk_score FROM exceptions WHERE run_id=?", (run_b,))}
    sa, sb = set(a), set(b)
    shared = sorted(sa & sb)
    return {"run_a": run_a, "run_b": run_b,
        "only_in_a": sorted(sa - sb), "only_in_b": sorted(sb - sa),
        "shared": len(shared),
        "score_deltas": [{"ledger_id": i, "delta": round(b[i] - a[i], 3)} for i in shared]}


def engagement_summary(store: Store):
    imports = [dict(r) for r in store.conn.execute("SELECT * FROM imports ORDER BY id")]
    return {
        "engagement": dict(store.engagement() or {}),
        "population_acknowledged": store.population_acknowledged(),
        "imports": [{**r, "reconciliation": store.reconciliation(r["id"]) if r["kind"] == "gl" else None} for r in imports],
        "entries": store.conn.execute("SELECT COUNT(*) FROM ledger_entries").fetchone()[0],
        "rejected_rows": store.conn.execute("SELECT COUNT(*) FROM rejected_rows").fetchone()[0],
        "latest_run": dict(store.conn.execute("SELECT * FROM model_runs ORDER BY id DESC LIMIT 1").fetchone() or {}),
        "exceptions": {r[0]: r[1] for r in store.conn.execute("SELECT severity,COUNT(*) FROM exceptions GROUP BY severity")},
        "review_status": {r[0]: r[1] for r in store.conn.execute("SELECT status,COUNT(*) FROM exceptions GROUP BY status")},
        "sample_sets": [dict(r) for r in store.conn.execute("SELECT * FROM sample_sets ORDER BY id DESC")],
        "settings": {r[0]: json.loads(r[1]) for r in store.conn.execute("SELECT key,value_json FROM settings ORDER BY key")},
    }


def _workpaper_rows(store: Store):
    return store.conn.execute("""WITH latest_review AS (
        SELECT r.*, ROW_NUMBER() OVER(PARTITION BY exception_id ORDER BY id DESC) n FROM reviews r
    ) SELECT e.id exception_id,e.run_id,e.risk_score,e.severity,e.status,e.assigned_to,e.due_date,
        l.entry_id,l.posting_date,l.document_date,l.account_code,c.account_name,l.debit,l.credit,l.signed_amount,
        l.description,l.preparer,l.reference,l.entity,l.is_manual,l.import_id,l.source_row,l.source_hash,
        e.reasons_json,e.evidence_json,lr.reviewer,lr.disposition,lr.note,lr.created_at review_at
        FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id LEFT JOIN coa c ON c.account_code=l.account_code
        LEFT JOIN latest_review lr ON lr.exception_id=e.id AND lr.n=1 ORDER BY e.risk_score DESC,e.id""").fetchall()


def export_workpaper(store: Store, out: str, actor="system"):
    destination = Path(out); destination.parent.mkdir(parents=True, exist_ok=True)
    rows = _workpaper_rows(store)
    fields = ["exception_id","run_id","risk_score","severity","status","assigned_to","due_date","entry_id","posting_date","document_date","account_code","account_name","debit","credit","signed_amount","description","preparer","reference","entity","is_manual","import_id","source_row","source_hash","reasons_json","evidence_json","reviewer","disposition","note","review_at"]
    with destination.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(dict(row) for row in rows)
    manifest = {"created_at": time.time(), "workpaper": str(destination), "summary": engagement_summary(store), "source_imports": [{k:r[k] for k in ("id","original_name","sha256","evidence_path")} for r in store.conn.execute("SELECT id,original_name,sha256,evidence_path FROM imports")], "exception_count": len(rows), "limitation": "Risk cues support auditor judgement; they are not findings, fraud determinations, or audit conclusions."}
    manifest["semantic_runs"] = []
    for run in store.conn.execute("SELECT id,configuration FROM model_runs ORDER BY id"):
        semantic = json.loads(run["configuration"]).get("semantic")
        if semantic: manifest["semantic_runs"].append({"analysis_run_id": run["id"], **semantic})
    manifest_path = destination.with_suffix(destination.suffix + ".manifest.json")
    manifest["workpaper_sha256"] = hashlib.sha256(destination.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    manifest["manifest_sha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    store.log(actor, "export_workpaper", "export", str(destination), {"manifest": str(manifest_path), "rows": len(rows)})
    store.conn.commit(); return destination, manifest_path, len(rows)


def write_engagement_report(store: Store, out: str, actor="system"):
    summary = engagement_summary(store); destination = Path(out); destination.parent.mkdir(parents=True, exist_ok=True)
    def cell(value): return html.escape(str(value if value is not None else "—"))
    eng = summary["engagement"] or {}
    mat = summary["settings"].get("materiality", {}) or {}
    policy = summary["settings"].get("analysis_policy", {}) or {}
    run_cfg = {}
    if summary["latest_run"] and summary["latest_run"].get("configuration"):
        try: run_cfg = json.loads(summary["latest_run"]["configuration"])
        except (TypeError, ValueError): run_cfg = {}
    import_rows = "".join(f"<tr><td>{cell(r['id'])}</td><td>{cell(r['original_name'])}</td><td>{cell(r['accepted_rows'])}</td><td>{cell(r['rejected_rows'])}</td><td>{cell((r['reconciliation'] or {}).get('matches'))}</td></tr>" for r in summary["imports"])
    recon_rows = "".join(
        f"<tr><td>{cell(r['id'])}</td><td>{cell((r['reconciliation'] or {}).get('accepted_rows'))}</td>"
        f"<td>{cell((r['reconciliation'] or {}).get('expected_rows'))}</td>"
        f"<td>{cell((r['reconciliation'] or {}).get('control_debits'))}</td>"
        f"<td>{cell((r['reconciliation'] or {}).get('expected_debits'))}</td>"
        f"<td>{cell((r['reconciliation'] or {}).get('control_credits'))}</td>"
        f"<td>{cell((r['reconciliation'] or {}).get('expected_credits'))}</td></tr>"
        for r in summary["imports"] if r["kind"] == "gl") or "<tr><td colspan=7>—</td></tr>"
    exception_rows = "".join(f"<li>{cell(k)}: {cell(v)}</li>" for k,v in summary["exceptions"].items()) or "<li>None</li>"
    tests_run = run_cfg.get("tests")
    content = f"""<!doctype html><meta charset=utf-8><title>Audit analytics engagement report</title><style>body{{font:15px system-ui;margin:2rem;max-width:960px}}table{{border-collapse:collapse}}td,th{{border:1px solid #ccc;padding:.45rem}}</style>
<h1>Audit analytics engagement report</h1>
<p><strong>Client:</strong> {cell(eng.get('client'))}<br><strong>Period:</strong> {cell(eng.get('period_start'))} to {cell(eng.get('period_end'))}</p>
<h2>Population and reconciliation</h2>
<p>Accepted ledger entries: {cell(summary['entries'])}; rejected rows: {cell(summary['rejected_rows'])}; population acknowledgement: {cell(summary['population_acknowledged'])}</p>
<table><tr><th>Import</th><th>File</th><th>Accepted</th><th>Rejected</th><th>Reconciled</th></tr>{import_rows}</table>
<h2>Reconciliation</h2>
<table><tr><th>Import</th><th>Accepted rows</th><th>Expected rows</th><th>Control debits</th><th>Expected debits</th><th>Control credits</th><th>Expected credits</th></tr>{recon_rows}</table>
<h2>Materiality (disclosed thresholds)</h2>
<p>Overall: {cell(mat.get('overall'))}; Performance: {cell(mat.get('performance'))}. These are planning thresholds only; they do not change risk scores or constitute an audit conclusion. Exceptions are labelled by band: above overall / above performance / below.</p>
<h2>Analysis</h2>
<p>Latest run: {cell(summary['latest_run'].get('id'))}; population: {cell(summary['latest_run'].get('population_count'))}; status: {cell(summary['latest_run'].get('status'))}</p>
<ul>{exception_rows}</ul>
<h2>Methodology &amp; limitations</h2>
<ul>
<li>Tests run: {cell(', '.join(tests_run) if isinstance(tests_run, list) else tests_run)}</li>
<li>Isolation-style ranking enabled: {cell(run_cfg.get('isolation'))}</li>
<li>Semantic evidence (explicit opt-in only): {cell(json.dumps(run_cfg.get('semantic', {}), sort_keys=True))}. Experimental thresholds and sampled neighbours require validation; they are not audit conclusions.</li>
<li>Robust z threshold: {cell(policy.get('outlier_robust_z'))}; round-amount threshold: {cell(policy.get('round_amount_threshold'))}; period-end window: {cell(policy.get('period_end_days'))} days</li>
<li>Risk cues support auditor judgement; they are not findings, fraud determinations, or audit conclusions. The engagement team evaluates evidence, selects procedures, and reaches conclusions under its approved methodology.</li>
</ul>"""
    destination.write_text(content, encoding="utf-8")
    store.log(actor, "write_engagement_report", "report", str(destination), {"entries": summary["entries"]})
    store.conn.commit(); return destination
