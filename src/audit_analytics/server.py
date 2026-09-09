from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .importer import preview_gl
from .model_registry import list_models
from .reports import compare_runs, engagement_summary
from .semantic import similar_transactions
from .store import Store

PAGE = """<!doctype html><meta charset=utf-8><title>Audit Analytics Review</title>
<style>body{font:14px system-ui;margin:2rem;max-width:1300px;color:#18212b}table{border-collapse:collapse;width:100%;margin:.5rem 0 2rem}th,td{border:1px solid #d7dce2;padding:.55rem;text-align:left;vertical-align:top}th{background:#f2f5f8}.high{color:#a00;font-weight:700}.medium{color:#9a5b00;font-weight:700}textarea{width:100%;height:3.5rem}input,select,button{font:inherit;padding:.35rem;margin:.15rem}section{margin:1.5rem 0;padding:1rem;background:#fafbfc;border:1px solid #e0e5ea}.small{font-size:.85em;color:#506070}#semantic-results li{margin:.5rem 0}</style>
<h1>Journal-entry review</h1><p id=summary>Loading engagement state…</p>
<section><h2>Reviewer session</h2><label>Reviewer <input id=reviewer list=users placeholder="Select configured reviewer"></label><datalist id=users></datalist><span class=small>Local workflow role checks apply when a disposition is saved.</span></section>
<section><h2>Semantic transaction search</h2><label>Transaction type, narration, or account-head phrase <input id=query size=52 placeholder="manual year-end tax provision"></label><button onclick=searchSimilar()>Find similar transactions</button><p class=small>Token matching always runs. Local vector similarity is included only after an approved Ollama model has indexed the ledger.</p><ol id=semantic-results></ol></section>
<section><h2>Exception review queue</h2><table><thead><tr><th>Risk</th><th>Entry</th><th>Context</th><th>Reasons / evidence</th><th>Disposition</th></tr></thead><tbody id=rows></tbody></table></section>
<script>
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const options=(current)=>['open','cleared','follow_up','selected_for_testing'].map(v=>`<option ${v===current?'selected':''}>${v}</option>`).join('');
async function load(){let [queue,status,users]=await Promise.all([fetch('/api/exceptions').then(r=>r.json()),fetch('/api/status').then(r=>r.json()),fetch('/api/users').then(r=>r.json())]);let state=`${queue.count} review cues · ${status.entries} accepted entries · population acknowledgement: ${status.population_acknowledged?'yes':'NO'}`;document.querySelector('#summary').textContent=state;document.querySelector('#users').innerHTML=users.filter(u=>['reviewer','manager','partner','quality_reviewer'].includes(u.role)).map(u=>`<option value="${esc(u.username)}">${esc(u.role)}</option>`).join('');let body=document.querySelector('#rows');body.innerHTML=queue.rows.map(r=>`<tr><td class="${esc(r.severity)}">${esc(r.risk_score)} (${esc(r.severity)})<br>${esc(r.status)}${r.assigned_to?'<br>Assigned: '+esc(r.assigned_to):''}</td><td>${esc(r.entry_id)}<br>${esc(r.posting_date)}<br>${esc(r.account_code)}: ${esc(r.signed_amount)}</td><td>${esc(r.description)}<br>Preparer: ${esc(r.preparer||'—')}<br>Ref: ${esc(r.reference||'—')}</td><td>${r.reasons.map(esc).join('<br>')}<hr><small>${esc(JSON.stringify(r.evidence))}</small></td><td><select id=s${r.id}>${options(r.status)}</select><textarea id=n${r.id} placeholder="Audit rationale / evidence requested"></textarea><button onclick="review(${r.id})">Save</button></td></tr>`).join('')}
async function review(id){let reviewer=document.querySelector('#reviewer').value.trim();let disposition=document.querySelector('#s'+id).value,note=document.querySelector('#n'+id).value.trim();if(!reviewer){alert('Enter a configured reviewer');return}if(!note){alert('A review note is required');return}let r=await fetch('/api/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id,reviewer,disposition,note})});let body=await r.json();if(!r.ok)alert(body.error||'Could not save review');else load()}
async function searchSimilar(){let q=document.querySelector('#query').value.trim();if(!q)return;let r=await fetch('/api/similar?q='+encodeURIComponent(q)),data=await r.json();let out=document.querySelector('#semantic-results');if(!r.ok){out.innerHTML='<li>'+esc(data.error||'Search failed')+'</li>';return}out.innerHTML=data.results.map(x=>`<li><strong>${esc(x.score)}</strong> · ${esc(x.entry_id)} · ${esc(x.account_code)} · ${esc(x.description)}<br><span class=small>token ${esc(x.token_score)}; semantic ${esc(x.semantic_score??'not indexed')}; shared: ${esc(x.shared_tokens.join(', ')||'—')}; classes: ${esc(x.token_classes.join(', ')||'—')}</span></li>`).join('')||'<li>No matching candidates.</li>'}
load();</script>"""


def serve(db_path: str, port=8788):
    class Handler(BaseHTTPRequestHandler):
        def _json(self, value, status=200):
            payload = json.dumps(value, default=str).encode()
            self.send_response(status); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload))); self.end_headers(); self.wfile.write(payload)

        def do_GET(self):
            path = urlparse(self.path)
            if path.path == "/":
                payload = PAGE.encode(); self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(payload))); self.end_headers(); self.wfile.write(payload); return
            if path.path == "/api/exceptions":
                s = Store(db_path)
                try:
                    rows = s.conn.execute("""SELECT e.*,l.entry_id,l.posting_date,l.account_code,l.signed_amount,l.description,l.preparer,l.reference
                    FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id ORDER BY e.risk_score DESC""").fetchall()
                    out = []
                    for row in rows:
                        item = dict(row); item["reasons"] = json.loads(item.pop("reasons_json")); item["evidence"] = json.loads(item.pop("evidence_json")); out.append(item)
                    self._json({"count": len(out), "rows": out})
                finally: s.close()
                return
            if path.path == "/api/status":
                s = Store(db_path)
                try: self._json(engagement_summary(s))
                finally: s.close()
                return
            if path.path == "/api/users":
                s = Store(db_path)
                try: self._json([dict(row) for row in s.conn.execute("SELECT username,role FROM users WHERE active=1 ORDER BY username")])
                finally: s.close()
                return
            if path.path == "/api/similar":
                query = parse_qs(path.query).get("q", [""])[0]
                try:
                    s = Store(db_path)
                    try: self._json({"query": query, "results": similar_transactions(s, query)})
                    finally: s.close()
                except ValueError as exc: self._json({"error": str(exc)}, 400)
                return
            if path.path == "/preview-gl":
                qs = parse_qs(path.query)
                try:
                    self._json(preview_gl(qs.get("file", [""])[0]))
                except (ValueError, FileNotFoundError) as exc: self._json({"error": str(exc)}, 400)
                except Exception as exc: self._json({"error": str(exc)}, 500)
                return
            if path.path == "/mappings":
                s = Store(db_path)
                try: self._json([dict(row) for row in s.conn.execute("SELECT name,created_at,created_by FROM import_mappings ORDER BY name")])
                finally: s.close()
                return
            if path.path == "/compare-runs":
                qs = parse_qs(path.query)
                try:
                    s = Store(db_path)
                    try: self._json(compare_runs(s, int(qs.get("a", [""])[0]), int(qs.get("b", [""])[0])))
                    finally: s.close()
                except (ValueError, TypeError) as exc: self._json({"error": str(exc)}, 400)
                return
            if path.path == "/account-taxonomy":
                s = Store(db_path)
                try: self._json([dict(row) for row in s.conn.execute("SELECT * FROM account_taxonomy ORDER BY account_code")])
                finally: s.close()
                return
            if path.path == "/bank":
                s = Store(db_path)
                try: self._json([dict(row) for row in s.conn.execute("SELECT * FROM bank_statements ORDER BY rowid DESC LIMIT 200")])
                finally: s.close()
                return
            if path.path == "/reviews":
                qs = parse_qs(path.query)
                reviewer, status = qs.get("reviewer", [None])[0], qs.get("status", [None])[0]
                s = Store(db_path)
                try:
                    query = """SELECT e.*, r.reviewer AS latest_reviewer, r.disposition AS latest_disposition, r.note AS latest_note, r.created_at AS latest_review_at
                    FROM exceptions e LEFT JOIN reviews r ON r.id=(SELECT MAX(id) FROM reviews WHERE exception_id=e.id)"""
                    clauses, params = [], []
                    if reviewer: clauses.append("r.reviewer=?"); params.append(reviewer)
                    if status: clauses.append("e.status=?"); params.append(status)
                    if clauses: query += " WHERE " + " AND ".join(clauses)
                    query += " ORDER BY e.risk_score DESC"
                    self._json([dict(row) for row in s.conn.execute(query, params)])
                finally: s.close()
                return
            if path.path == "/models":
                s = Store(db_path)
                try: self._json(list_models(s))
                finally: s.close()
                return
            self._json({"error": "not found"}, 404)

        def do_POST(self):
            if urlparse(self.path).path != "/api/review": self._json({"error": "not found"}, 404); return
            try:
                data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
                if not all(isinstance(data.get(key), str) and data[key].strip() for key in ("reviewer", "disposition", "note")): raise ValueError("reviewer, disposition, and note are required")
                if data["disposition"] not in {"open", "cleared", "follow_up", "selected_for_testing"}: raise ValueError("invalid disposition")
                s = Store(db_path)
                try:
                    s.require_role(data["reviewer"].strip(), {"reviewer", "manager", "partner", "quality_reviewer"})
                    if not s.conn.execute("SELECT 1 FROM exceptions WHERE id=?", (data.get("id"),)).fetchone(): raise ValueError("exception not found")
                    review_id = s.conn.execute("INSERT INTO reviews(exception_id,reviewer,disposition,note,created_at) VALUES(?,?,?,?,strftime('%s','now'))", (data["id"], data["reviewer"].strip(), data["disposition"], data["note"].strip())).lastrowid
                    s.conn.execute("UPDATE exceptions SET status=? WHERE id=?", (data["disposition"], data["id"])); s.log(data["reviewer"], "review_exception", "exception", data["id"], {"review_id": review_id, "disposition": data["disposition"]}); s.conn.commit()
                finally: s.close()
                self._json({"ok": True})
            except (ValueError, json.JSONDecodeError) as exc: self._json({"error": str(exc)}, 400)

        def log_message(self, *args): pass

    print(f"Audit review UI: http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
