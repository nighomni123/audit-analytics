"""Local token classification and Ollama-backed transaction similarity."""
from __future__ import annotations

import array
import hashlib
import json
import ipaddress
from urllib.parse import urlparse
import math
import re
import time
import urllib.error
import urllib.request
from collections import Counter

from .store import Store

STOPWORDS = frozenset("a an and as at by for from in is of on or the to with being entry journal voucher".split())
TOKEN_CLASSES = {
    "cash_bank": frozenset("cash bank cheque chequeing transfer upi neft rtgs payment receipt deposit withdrawal".split()),
    "revenue": frozenset("revenue sales income billing invoice turnover service commission".split()),
    "expense": frozenset("expense rent utility utilities travel repair maintenance professional fee".split()),
    "payroll": frozenset("salary salaries payroll wage bonus pf esi gratuity".split()),
    "inventory": frozenset("inventory stock purchase goods material consumable cogs".split()),
    "tax": frozenset("gst tds tax cgst sgst igst vat duty".split()),
    "intercompany": frozenset("intercompany related party group affiliate reimbursement".split()),
    "fixed_asset": frozenset("asset equipment machinery computer vehicle depreciation capex".split()),
}


def tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z][a-z0-9]{1,}", (text or "").lower()) if t not in STOPWORDS}


def classify(text: str) -> list[str]:
    found = tokens(text)
    return sorted(label for label, terms in TOKEN_CLASSES.items() if found & terms)


def _text(entry: dict) -> str:
    return " | ".join(str(entry.get(k) or "") for k in ("account_code", "account_name", "description", "reference", "entity"))


def _cosine(a, b):
    if not a or len(a) != len(b): raise ValueError("cosine requires equal nonempty vector dimensions")
    if any(not math.isfinite(x) for v in (a,b) for x in v): raise ValueError("cosine requires finite vectors")
    denom = math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(x*x for x in b))
    if not denom or not math.isfinite(denom): raise ValueError("cosine requires finite nonzero norms")
    return max(-1.0, min(1.0, sum(x*y for x, y in zip(a, b)) / denom))


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("local Ollama redirects are prohibited")


class LocalEmbedder:
    """Minimal local Ollama transport. No API key and no external endpoint."""
    def __init__(self, model="embeddinggemma", base_url="http://127.0.0.1:11434"):
        parsed = urlparse(base_url)
        try: local = ipaddress.ip_address(parsed.hostname or '').is_loopback
        except ValueError: local = False
        if parsed.scheme != 'http' or not local or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ('','/'):
            raise ValueError('Ollama endpoint must be a loopback HTTP IP address')
        if not isinstance(model,str) or not model.strip(): raise ValueError('model name required')
        self.model, self.base_url = model, base_url.rstrip("/")

    def _request(self, path, payload=None):
        body = json.dumps(payload).encode() if payload is not None else None
        request = urllib.request.Request(self.base_url + path, data=body, headers={"Content-Type": "application/json"})
        try:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect())
            with opener.open(request, timeout=180) as response: return json.loads(response.read().decode())
        except (urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
            raise ValueError('local Ollama request failed; start the local service and install an authorised model separately') from exc

    def identity(self):
        data = self._request('/api/tags')
        names = {self.model, self.model + ':latest'} if ':' not in self.model else {self.model}
        matches = [m for m in data.get('models',[]) if m.get('name') in names or m.get('model') in names]
        if len(matches)!=1 or not isinstance(matches[0].get('digest'),str) or not matches[0]['digest']:
            raise ValueError('cannot resolve immutable installed Ollama model identity')
        return {**matches[0], 'runtime_version': self._request('/api/version').get('version')}

    def embed(self, texts: list[str]) -> list[array.array]:
        data = self._request('/api/embed', {"model": self.model, "input": texts, "truncate": False})
        vectors = data.get("embeddings") if isinstance(data,dict) else None
        if not isinstance(vectors, list) or len(vectors) != len(texts): raise ValueError("local Ollama returned an invalid embedding batch")
        result=[]; dims=None
        for vector in vectors:
            if not isinstance(vector,list) or not vector or any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in vector): raise ValueError('invalid embedding vector')
            if dims is not None and len(vector)!=dims: raise ValueError('mixed embedding dimensions')
            dims=len(vector)
            try: converted=array.array('f',vector)
            except (OverflowError,TypeError) as exc: raise ValueError('invalid float32 embedding') from exc
            _cosine(converted,converted); result.append(converted)
        return result


def _entries(store: Store):
    return [dict(row) for row in store.conn.execute("""SELECT l.*, c.account_name FROM ledger_entries l
        LEFT JOIN coa c ON c.account_code=l.account_code ORDER BY l.id""")]


def embed_ledger(store: Store, model="embeddinggemma", batch_size=64, actor="system"):
    """Backfill locally generated vectors; unchanged text is never re-embedded."""
    if isinstance(batch_size,bool) or not isinstance(batch_size,int) or batch_size<=0: raise ValueError('batch_size must be positive')
    embedder = LocalEmbedder(model); todo = []
    for entry in _entries(store):
        text = _text(entry); digest = hashlib.sha256(text.encode()).hexdigest()
        row = store.conn.execute("SELECT text_hash FROM ledger_embeddings WHERE ledger_id=? AND model=? ORDER BY embedded_at DESC LIMIT 1", (entry["id"], model)).fetchone()
        if not row or row[0] != digest: todo.append((entry["id"], text, digest))
    done = 0
    try:
        for start in range(0, len(todo), batch_size):
            group = todo[start:start + batch_size]; vectors = embedder.embed([x[1] for x in group])
            if len(vectors) != len(group): raise ValueError("local Ollama returned an invalid embedding batch")
            for (ledger_id, _, digest), vector in zip(group, vectors):
                store.conn.execute("DELETE FROM ledger_embeddings WHERE ledger_id=? AND model=?", (ledger_id, model))
                store.conn.execute("INSERT INTO ledger_embeddings VALUES(?,?,?,?,?,?)", (ledger_id, model, len(vector), digest, vector.tobytes(), time.time()))
                done += 1
    except Exception:
        store.conn.rollback(); raise
    store.log(actor, "embed_ledger_local", "embedding", model, {"embedded": done, "skipped": len(todo) - done, "model": model})
    store.conn.commit(); return done


def similar_transactions(store: Store, query: str, limit=25, model="embeddinggemma"):
    """Rank ledger candidates with token overlap plus optional local cosine.

    Embedding similarity can add semantically related candidates, but never
    suppresses a strong transparent token/account-head match.
    """
    query_tokens = tokens(query)
    if not query_tokens: raise ValueError("query must contain meaningful transaction or account-head terms")
    rows = _entries(store); doc_freq = Counter(t for e in rows for t in tokens(_text(e)))
    n = max(1, len(rows)); query_vector = None; dims = None
    embedded = store.conn.execute("SELECT dims FROM ledger_embeddings WHERE model=? LIMIT 1", (model,)).fetchone()
    if embedded:
        dims = embedded[0]; query_vector = LocalEmbedder(model).embed([query])[0]
        if len(query_vector) != dims: raise ValueError("local model dimensions changed; rerun embed-ledger for this model")
    scored = []
    for entry in rows:
        text = _text(entry); entry_tokens = tokens(text); union = query_tokens | entry_tokens
        weighted_shared = sum(math.log((n + 1) / (doc_freq[t] + 1)) + 1 for t in query_tokens & entry_tokens)
        weighted_all = sum(math.log((n + 1) / (doc_freq[t] + 1)) + 1 for t in union)
        token_score = weighted_shared / weighted_all if weighted_all else 0.0
        semantic_score = None
        if query_vector is not None:
            row = store.conn.execute("SELECT vector FROM ledger_embeddings WHERE ledger_id=? AND model=? AND dims=?", (entry["id"], model, dims)).fetchone()
            if row: semantic_score = max(0.0, _cosine(query_vector, array.array("f", row[0])))
        score = max(token_score, semantic_score or 0.0)
        if score:
            scored.append({"ledger_id": entry["id"], "entry_id": entry["entry_id"], "posting_date": entry["posting_date"], "account_code": entry["account_code"], "account_name": entry.get("account_name"), "signed_amount": entry["signed_amount"], "description": entry["description"], "preparer": entry["preparer"], "reference": entry["reference"], "token_score": round(token_score, 3), "semantic_score": round(semantic_score, 3) if semantic_score is not None else None, "score": round(score, 3), "shared_tokens": sorted(query_tokens & entry_tokens), "token_classes": classify(text)})
    return sorted(scored, key=lambda r: (-r["score"], -r["token_score"], r["ledger_id"]))[:limit]
