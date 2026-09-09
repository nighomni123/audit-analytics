"""Local token classification and Ollama-backed transaction similarity."""
from __future__ import annotations

import array
import hashlib
import json
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
    denom = math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(x*x for x in b))
    return sum(x*y for x, y in zip(a, b)) / denom if denom else 0.0


class LocalEmbedder:
    """Minimal local Ollama transport. No API key and no external endpoint."""
    def __init__(self, model="embeddinggemma", base_url="http://127.0.0.1:11434"):
        self.model, self.base_url = model, base_url.rstrip("/")

    def embed(self, texts: list[str]) -> list[array.array]:
        body = json.dumps({"model": self.model, "input": texts}).encode()
        request = urllib.request.Request(self.base_url + "/api/embed", data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=180) as response: data = json.loads(response.read().decode())
        except (urllib.error.URLError, urllib.error.HTTPError) as exc:
            raise ValueError("local Ollama embedding failed; start `ollama serve` and run `ollama pull embeddinggemma` on this host") from exc
        vectors = data.get("embeddings")
        if not isinstance(vectors, list) or len(vectors) != len(texts): raise ValueError("local Ollama returned an invalid embedding batch")
        return [array.array("f", (float(x) for x in vector)) for vector in vectors]


def _entries(store: Store):
    return [dict(row) for row in store.conn.execute("""SELECT l.*, c.account_name FROM ledger_entries l
        LEFT JOIN coa c ON c.account_code=l.account_code ORDER BY l.id""")]


def embed_ledger(store: Store, model="embeddinggemma", batch_size=64, actor="system"):
    """Backfill locally generated vectors; unchanged text is never re-embedded."""
    embedder = LocalEmbedder(model); todo = []
    for entry in _entries(store):
        text = _text(entry); digest = hashlib.sha256(text.encode()).hexdigest()
        row = store.conn.execute("SELECT text_hash FROM ledger_embeddings WHERE ledger_id=? AND model=? ORDER BY embedded_at DESC LIMIT 1", (entry["id"], model)).fetchone()
        if not row or row[0] != digest: todo.append((entry["id"], text, digest))
    done = 0
    for start in range(0, len(todo), batch_size):
        group = todo[start:start + batch_size]; vectors = embedder.embed([x[1] for x in group])
        for (ledger_id, _, digest), vector in zip(group, vectors):
            store.conn.execute("DELETE FROM ledger_embeddings WHERE ledger_id=? AND model=?", (ledger_id, model))
            store.conn.execute("INSERT INTO ledger_embeddings VALUES(?,?,?,?,?,?)", (ledger_id, model, len(vector), digest, vector.tobytes(), time.time()))
            done += 1
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
