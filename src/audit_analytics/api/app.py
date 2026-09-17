"""FastAPI adapter for audit analytics — thin layer over existing engine."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json

from audit_analytics.importer import preview_gl
from audit_analytics.model_registry import list_models
from audit_analytics.reports import compare_runs, engagement_summary
from audit_analytics.semantic import similar_transactions
from audit_analytics.semantic_risk import get_semantic_profile, semantic_investigate
from audit_analytics.store import Store

db_path = os.environ.get("AUDIT_DB", os.path.join(os.path.dirname(__file__), "..", "..", "data", "demo.db"))

from starlette.staticfiles import StaticFiles
app = FastAPI(title="Audit Analytics API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
dist_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.isdir(dist_dir):
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="static")

class ReviewBody(BaseModel):
    id: int
    reviewer: str
    disposition: str
    note: str

@app.get("/api/status")
def status():
    s = Store(db_path)
    try: return engagement_summary(s)
    finally: s.close()

@app.get("/api/exceptions")
def exceptions(run: Optional[int] = Query(None)):
    s = Store(db_path)
    try:
        raw = s.conn.execute("SELECT e.*,l.entry_id,l.posting_date,l.account_code,l.signed_amount,l.description,l.preparer,l.reference FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id WHERE (? IS NULL OR e.run_id=?) ORDER BY e.risk_score DESC,e.id", (run, run)).fetchall()
        out = []
        for r in raw:
            item = dict(r); item["reasons"] = json.loads(item.pop("reasons_json")); item["evidence"] = json.loads(item.pop("evidence_json")); out.append(item)
        return {"count": len(out), "rows": out}
    finally: s.close()

@app.get("/api/semantic-profile")
def semantic_profile(run: Optional[int] = Query(None)):
    s = Store(db_path)
    try:
        result = get_semantic_profile(s, run)
        result["available_runs"] = [dict(r) for r in s.conn.execute("SELECT id,status,started_at FROM semantic_runs ORDER BY id DESC LIMIT 100")]
        return result
    finally: s.close()

@app.get("/api/semantic-investigation")
def investigation(run: int, ledger_id: int):
    s = Store(db_path)
    try: return semantic_investigate(s, run, ledger_id)
    finally: s.close()

@app.get("/api/similar")
def similar(q: str = Query("")):
    s = Store(db_path)
    try: return {"query": q, "results": similar_transactions(s, q)}
    finally: s.close()

@app.get("/api/users")
def users():
    s = Store(db_path)
    try: return [dict(r) for r in s.conn.execute("SELECT username,role FROM users WHERE active=1 ORDER BY username")]
    finally: s.close()

@app.get("/api/mappings")
def mappings():
    s = Store(db_path)
    try: return [dict(r) for r in s.conn.execute("SELECT name,created_at,created_by FROM import_mappings ORDER BY name")]
    finally: s.close()

@app.get("/api/reviews")
def reviews(reviewer: Optional[str] = Query(None), status: Optional[str] = Query(None)):
    s = Store(db_path)
    try:
        query = """SELECT e.*, r.reviewer AS latest_reviewer, r.disposition AS latest_disposition, r.note AS latest_note, r.created_at AS latest_review_at FROM exceptions e LEFT JOIN reviews r ON r.id=(SELECT MAX(id) FROM reviews WHERE exception_id=e.id)"""
        clauses, params = [], []
        if reviewer: clauses.append("r.reviewer=?"); params.append(reviewer)
        if status: clauses.append("e.status=?"); params.append(status)
        if clauses: query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY e.risk_score DESC"
        return [dict(r) for r in s.conn.execute(query, params)]
    finally: s.close()

@app.get("/api/engagement")
def engagement():
    s = Store(db_path)
    try:
        meta = s.conn.execute("SELECT client, period_start, period_end FROM engagement WHERE id=1").fetchone()
        if meta:
            return {"client": meta["client"], "period": f"{meta['period_start']} → {meta['period_end']}", "folder": "—"}
        return {"client":"—","period":"—","folder":"—"}
    finally: s.close()

@app.post("/api/review")
def review(body: ReviewBody):
    s = Store(db_path)
    try:
        if not body.reviewer or not body.reviewer.strip(): raise HTTPException(400, "reviewer required")
        if not body.note or not body.note.strip(): raise HTTPException(400, "note required")
        if body.disposition not in {"open","cleared","follow_up","selected_for_testing"}: raise HTTPException(400, "invalid disposition")
        s.require_role(body.reviewer.strip(), {"reviewer","manager","partner","quality_reviewer"})
        if not s.conn.execute("SELECT 1 FROM exceptions WHERE id=?", (body.id,)).fetchone(): raise HTTPException(400, "exception not found")
        review_id = s.conn.execute("INSERT INTO reviews(exception_id,reviewer,disposition,note,created_at) VALUES(?,?,?,?,strftime('%s','now'))", (body.id, body.reviewer.strip(), body.disposition, body.note.strip())).lastrowid
        s.conn.execute("UPDATE exceptions SET status=? WHERE id=?", (body.disposition, body.id))
        s.log(body.reviewer, "review_exception", "exception", body.id, {"review_id": review_id, "disposition": body.disposition})
        s.conn.commit()
        return {"ok": True, "review_id": review_id}
    finally: s.close()

@app.get("/preview-gl")
def preview(file: str = Query("")):
    try: return preview_gl(file)
    except Exception as exc: raise HTTPException(400, str(exc))

@app.get("/compare-runs")
def compare(a: int = Query(...), b: int = Query(...)):
    s = Store(db_path)
    try: return compare_runs(s, a, b)
    finally: s.close()

@app.get("/models")
def models():
    s = Store(db_path)
    try: return list_models(s)
    finally: s.close()

@app.get("/bank")
def bank():
    s = Store(db_path)
    try: return [dict(r) for r in s.conn.execute("SELECT * FROM bank_statements ORDER BY rowid DESC LIMIT 200")]
    finally: s.close()

@app.get("/account-taxonomy")
def taxonomy():
    s = Store(db_path)
    try: return [dict(r) for r in s.conn.execute("SELECT * FROM account_taxonomy ORDER BY account_code")]
    finally: s.close()
