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

import numpy as np

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


def _validate_batch(vectors, expected: int) -> list[array.array]:
    """Shared float32/finite/dimension validation. Fails closed on any malformed batch."""
    if not isinstance(vectors, list) or len(vectors) != expected:
        raise ValueError("embedding provider returned an invalid batch size")
    result = []
    dims = None
    for vector in vectors:
        if not isinstance(vector, list) or not vector or any(
            isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in vector
        ):
            raise ValueError("invalid embedding vector")
        if dims is not None and len(vector) != dims:
            raise ValueError("mixed embedding dimensions")
        dims = len(vector)
        try:
            converted = array.array('f', vector)
        except (OverflowError, TypeError) as exc:
            raise ValueError("invalid float32 embedding") from exc
        _cosine(converted, converted)
        result.append(converted)
    return result


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
        return {**matches[0], 'runtime_version': self._request('/api/version').get('version'), 'provider': 'ollama', 'provenance_kind': 'content_digest'}

    def embed(self, texts: list[str]) -> list[array.array]:
        data = self._request('/api/embed', {"model": self.model, "input": texts, "truncate": False})
        return _validate_batch(data.get("embeddings") if isinstance(data, dict) else None, len(texts))


class RemoteEmbedder:
    """OpenAI-compatible `/embeddings` transport (OpenRouter, OpenAI, vLLM, LM Studio...).

    A deliberate exception to the local-only default: enabling it sends ledger text to a third
    party. Kept as its own class so `LocalEmbedder`'s loopback guard is never weakened.
    """

    def __init__(self, base_url: str, api_key: str, model: str, referer: str = "", title: str = ""):
        if not isinstance(model, str) or not model.strip():
            raise ValueError('model name required')
        parsed = urlparse(base_url)
        try:
            local = ipaddress.ip_address(parsed.hostname or '').is_loopback
        except ValueError:
            local = False
        if not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError('provider base URL must be a plain origin without credentials, query, or fragment')
        if parsed.scheme != 'https' and not (parsed.scheme == 'http' and local):
            raise ValueError('provider base URL must use https unless it is a loopback address')
        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError('provider API key is required')
        for value in (api_key, model, referer, title):
            if not isinstance(value, str) or any(c in value for c in '\r\n'):
                raise ValueError('provider credentials, model, and headers must be single-line values')
        self.base_url, self.api_key, self.model = base_url.rstrip('/'), api_key, model
        self.referer, self.title = referer, title

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
        if self.referer:
            headers["HTTP-Referer"] = self.referer
        if self.title:
            headers["X-OpenRouter-Title"] = self.title
        return headers

    def _request(self, path, payload=None):
        body = json.dumps(payload).encode() if payload is not None else None
        request = urllib.request.Request(self.base_url + path, data=body, headers=self._headers())
        try:
            # No proxies and no redirects: a credentialed request must never be replayed elsewhere.
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect())
            with opener.open(request, timeout=180) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as exc:
            # Surface the provider's reason, never the request: it carries the API key.
            detail = ''
            try:
                detail = str(json.loads(exc.read().decode()).get('error', {}).get('message', ''))[:200]
            except Exception:  # noqa: BLE001 - provider response bodies are untrusted
                pass
            raise ValueError(f'provider request failed with HTTP {exc.code}{": " + detail if detail else ""}') from None
        except (urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
            raise ValueError('provider request failed; check the base URL, API key, and model name') from exc

    def identity(self):
        # Remote providers publish no content digest, so identity is a declared tuple. Callers that
        # compare digests still catch a mid-run settings change, but not a silent upstream model swap.
        return {'provider': 'openai_compatible', 'model': self.model, 'base_url': self.base_url,
                'digest': hashlib.sha256(f'openai_compatible|{self.base_url}|{self.model}'.encode()).hexdigest(),
                'provenance_kind': 'declared_endpoint'}

    def embed(self, texts: list[str]) -> list[array.array]:
        data = self._request('/embeddings', {"model": self.model, "input": texts, "encoding_format": "float"})
        # OpenAI/OpenRouter nest vectors under data[].embedding and may return them out of order.
        rows = data.get("data") if isinstance(data, dict) else None
        if not isinstance(rows, list):
            raise ValueError("embedding provider returned an invalid batch")
        try:
            ordered = sorted(rows, key=lambda row: row["index"])
            return _validate_batch([row["embedding"] for row in ordered], len(texts))
        except (TypeError, KeyError) as exc:
            raise ValueError("embedding provider returned a malformed batch") from exc


def resolve_embedder(store: Store, model: str | None = None):
    """The single place that decides which embedder runs. Returns (embedder, model).

    A configured, acknowledged remote provider takes precedence over `model`; the caller records
    in provenance whichever one actually ran.
    """
    config = store.semantic_provider()
    if config and config.get('enabled'):
        embedder = RemoteEmbedder(config['base_url'], store.provider_api_key(), config['model'],
                                  config.get('referer') or '', config.get('title') or '')
        return embedder, embedder.model
    return LocalEmbedder(model or 'embeddinggemma'), (model or 'embeddinggemma')


def _entries(store: Store):
    return [dict(row) for row in store.conn.execute("""SELECT l.*, c.account_name FROM ledger_entries l
        LEFT JOIN coa c ON c.account_code=l.account_code ORDER BY l.id""")]


def embed_ledger(store: Store, model=None, batch_size=64, actor="system"):
    """Backfill vectors; unchanged text is never re-embedded."""
    if isinstance(batch_size,bool) or not isinstance(batch_size,int) or batch_size<=0: raise ValueError('batch_size must be positive')
    embedder, model = resolve_embedder(store, model); todo = []
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


def similar_transactions(store: Store, query: str, limit=25, model=None):
    """Rank ledger candidates with token overlap plus optional local cosine.

    Embedding similarity can add semantically related candidates, but never
    suppresses a strong transparent token/account-head match.
    """
    if not isinstance(query, str) or not query.strip() or len(query) > 1000:
        raise ValueError("query must contain 1 to 1000 characters")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
        raise ValueError("limit must be an integer from 1 to 100")
    query_tokens = tokens(query)
    if not query_tokens:
        raise ValueError("query must contain meaningful transaction or account-head terms")
    rows = _entries(store)
    prepared = []
    for entry in rows:
        text = _text(entry)
        prepared.append((entry, text, tokens(text)))
    doc_freq = Counter(token for _, _, entry_tokens in prepared for token in entry_tokens)
    n = max(1, len(rows))
    semantic_scores = {}
    embedder, model = resolve_embedder(store, model)
    embedded = store.conn.execute("SELECT dims FROM ledger_embeddings WHERE model=? LIMIT 1", (model,)).fetchone()
    if embedded:
        dims = embedded[0]
        vector_rows = store.conn.execute(
            "SELECT ledger_id,vector FROM ledger_embeddings WHERE model=? AND dims=? ORDER BY ledger_id", (model, dims)
        ).fetchall()
        query_vector = embedder.embed([query])[0]
        if len(query_vector) != dims:
            raise ValueError("local model dimensions changed; rerun embed-ledger for this model")
        if vector_rows:
            matrix = np.vstack([np.frombuffer(row["vector"], dtype="<f4") for row in vector_rows])
            if matrix.shape[1] != dims or not np.isfinite(matrix).all():
                raise ValueError("stored embeddings contain invalid dimensions or values")
            matrix64 = matrix.astype(np.float64)
            norms = np.sqrt(np.sum(matrix64**2, axis=1))
            query_array = np.frombuffer(query_vector, dtype="<f4").astype(np.float64)
            query_norm = math.sqrt(float(np.dot(query_array, query_array)))
            if not np.isfinite(norms).all() or not math.isfinite(query_norm) or np.any(norms == 0) or query_norm == 0:
                raise ValueError("cosine requires finite nonzero norms")
            cosine = np.clip((matrix64 @ query_array) / (norms * query_norm), -1.0, 1.0)
            semantic_scores = {row["ledger_id"]: max(0.0, float(value)) for row, value in zip(vector_rows, cosine)}
    scored = []
    for entry, text, entry_tokens in prepared:
        union = query_tokens | entry_tokens
        weighted_shared = sum(math.log((n + 1) / (doc_freq[token] + 1)) + 1 for token in query_tokens & entry_tokens)
        weighted_all = sum(math.log((n + 1) / (doc_freq[token] + 1)) + 1 for token in union)
        token_score = weighted_shared / weighted_all if weighted_all else 0.0
        semantic_score = semantic_scores.get(entry["id"])
        score = max(token_score, semantic_score or 0.0)
        if score:
            scored.append({"ledger_id": entry["id"], "entry_id": entry["entry_id"], "posting_date": entry["posting_date"], "account_code": entry["account_code"], "account_name": entry.get("account_name"), "signed_amount": entry["signed_amount"], "description": entry["description"], "preparer": entry["preparer"], "reference": entry["reference"], "token_score": round(token_score, 3), "semantic_score": round(semantic_score, 3) if semantic_score is not None else None, "score": round(score, 3), "shared_tokens": sorted(query_tokens & entry_tokens), "token_classes": classify(text)})
    return sorted(scored, key=lambda r: (-r["score"], -r["token_score"], r["ledger_id"]))[:limit]
