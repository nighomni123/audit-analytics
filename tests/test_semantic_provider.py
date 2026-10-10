"""External embedding provider: trust boundary, secret redaction, and opt-in gating.

No network: the provider transport is exercised with a stubbed urlopen.
"""
import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from audit_analytics import semantic as sem
from audit_analytics.api.app import create_app
from audit_analytics.store import Store

BASE = "https://openrouter.ai/api/v1"
MODEL = "liquid/lfm-2.5-embedding-350m:free"
SECRET = "sk-or-v1-supersecretkey123456"


def _response(vectors):
    return {"data": [{"object": "embedding", "index": i, "embedding": v} for i, v in enumerate(vectors)],
            "model": MODEL, "usage": {"prompt_tokens": 3, "total_tokens": 3}}


class _FakeHTTP:
    """Stands in for a provider HTTP response so no test needs the network."""

    def __init__(self, payload, code=200):
        self.payload, self.code, self.captured = payload, code, None

    def read(self):
        return json.dumps(self.payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class ProviderTrustBoundaryTest(unittest.TestCase):
    def test_rejects_plaintext_and_credentialed_urls(self):
        for bad in ("http://provider.example.com/v1", "https://u:p@provider.example.com/v1",
                    "https://provider.example.com/v1?key=1", "ftp://provider.example.com/v1", ""):
            with self.subTest(base_url=bad), self.assertRaises(ValueError):
                sem.RemoteEmbedder(bad, SECRET, MODEL)

    def test_rejects_header_injection_and_missing_key(self):
        with self.assertRaises(ValueError):
            sem.RemoteEmbedder(BASE, "key\nX-Injected: 1", MODEL)
        with self.assertRaises(ValueError):
            sem.RemoteEmbedder(BASE, "", MODEL)
        with self.assertRaises(ValueError):
            sem.RemoteEmbedder(BASE, SECRET, "")

    def test_loopback_http_still_allowed_for_local_servers(self):
        self.assertEqual(sem.RemoteEmbedder("http://127.0.0.1:8000/v1", "k", MODEL).base_url, "http://127.0.0.1:8000/v1")

    def test_local_embedder_loopback_guard_is_not_weakened(self):
        # The remote provider must never become a way around the local-only default.
        for bad in ("https://openrouter.ai/api/v1", "http://10.0.0.5:11434", "http://evil.example.com"):
            with self.subTest(base_url=bad), self.assertRaises(ValueError):
                sem.LocalEmbedder("embeddinggemma", bad)

    def test_embed_sends_bearer_header_and_parses_openai_shape(self):
        embedder = sem.RemoteEmbedder(BASE, SECRET, MODEL)
        seen = {}

        def fake_open(_opener, request, timeout=None):
            seen["url"] = request.full_url
            seen["auth"] = request.headers.get("Authorization")
            seen["body"] = json.loads(request.data.decode())
            return _FakeHTTP(_response([[0.1, 0.2, 0.3]]))

        with patch("urllib.request.OpenerDirector.open", fake_open):
            vectors = embedder.embed(["hello"])
        self.assertEqual(seen["url"], f"{BASE}/embeddings")
        self.assertEqual(seen["auth"], f"Bearer {SECRET}")
        self.assertEqual(seen["body"]["model"], MODEL)
        self.assertEqual(seen["body"]["encoding_format"], "float")
        self.assertAlmostEqual(vectors[0][0], 0.1, places=5)

    def test_batch_results_are_reordered_by_index(self):
        embedder = sem.RemoteEmbedder(BASE, SECRET, MODEL)
        shuffled = {"data": [{"index": 1, "embedding": [0.0, 1.0]}, {"index": 0, "embedding": [1.0, 0.0]}]}
        with patch("urllib.request.OpenerDirector.open", lambda *a, **k: _FakeHTTP(shuffled)):
            vectors = embedder.embed(["first", "second"])
        self.assertAlmostEqual(vectors[0][0], 1.0, places=5)
        self.assertAlmostEqual(vectors[1][1], 1.0, places=5)

    def test_ollama_and_openai_response_shapes_are_not_conflated(self):
        # The two providers nest vectors differently; mixing them up silently corrupts results.
        ollama = sem.LocalEmbedder("embeddinggemma")
        with patch("urllib.request.OpenerDirector.open", lambda *a, **k: _FakeHTTP({"embeddings": [[1.0, 0.0]]})):
            self.assertAlmostEqual(ollama.embed(["x"])[0][0], 1.0, places=5)
        with patch("urllib.request.OpenerDirector.open", lambda *a, **k: _FakeHTTP({"embeddings": [[1.0, 0.0]]})):
            with self.assertRaises(ValueError):
                sem.RemoteEmbedder(BASE, SECRET, MODEL).embed(["x"])

    def test_provider_error_never_echoes_the_api_key(self):
        failure = urllib.error.HTTPError(
            f"{BASE}/embeddings", 401, "Unauthorized", {},
            io.BytesIO(json.dumps({"error": {"message": "No auth credentials"}}).encode()),
        )
        with patch("urllib.request.OpenerDirector.open", side_effect=failure):
            with self.assertRaises(ValueError) as caught:
                sem.RemoteEmbedder(BASE, SECRET, MODEL).embed(["x"])
        self.assertIn("401", str(caught.exception))
        self.assertIn("No auth credentials", str(caught.exception))
        self.assertNotIn(SECRET, str(caught.exception))


class ProviderApiTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.db = Path(self.directory.name) / "audit.db"
        self.client = TestClient(create_app(self.db))
        self.client.post("/api/engagement", json={"client": "C", "period": "2025-01-01:2025-12-31", "owner": "m"})
        store = Store(str(self.db))
        store.add_user("manager", "manager", "system")
        store.add_user("reviewer", "reviewer", "manager")
        store.conn.commit()
        store.close()

    def _enable(self, **overrides):
        body = {"actor": "manager", "enabled": True, "base_url": BASE, "api_key": SECRET,
                "model": MODEL, "acknowledge_external_transfer": True}
        body.update(overrides)
        return self.client.put("/api/semantic-provider", json=body)

    def test_defaults_to_local_when_unconfigured(self):
        self.assertEqual(self.client.get("/api/semantic-provider").json()["enabled"], False)
        store = Store(str(self.db))
        try:
            self.assertIsInstance(sem.resolve_embedder(store)[0], sem.LocalEmbedder)
        finally:
            store.close()

    def test_enabling_requires_explicit_acknowledgement(self):
        response = self._enable(acknowledge_external_transfer=False)
        self.assertEqual(response.status_code, 400, response.text)
        self.assertEqual(response.json()["error"]["code"], "acknowledgement_required")
        store = Store(str(self.db))
        try:
            self.assertIsInstance(sem.resolve_embedder(store)[0], sem.LocalEmbedder)
        finally:
            store.close()

    def test_reviewer_cannot_change_where_engagement_data_is_sent(self):
        self.assertEqual(self._enable(actor="reviewer").status_code, 403)

    def test_connection_test_uses_live_credentials_and_reports_dimensions(self):
        seen = {}

        def fake_open(_opener, request, timeout=None):
            seen["auth"] = request.headers.get("Authorization")
            seen["url"] = request.full_url
            seen["body"] = json.loads(request.data.decode())
            return _FakeHTTP(_response([[0.1, 0.2, 0.3, 0.4]]))

        body = {"actor": "manager", "base_url": BASE, "api_key": SECRET, "model": MODEL}
        with patch("urllib.request.OpenerDirector.open", fake_open):
            response = self.client.post("/api/semantic-provider/test", json=body)
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["dimensions"], 4)
        self.assertEqual(data["model"], MODEL)
        self.assertEqual(seen["auth"], f"Bearer {SECRET}")
        self.assertEqual(seen["url"], f"{BASE}/embeddings")

    def test_connection_test_uses_stored_key_when_body_omits_it(self):
        self._enable()
        body = {"actor": "manager", "base_url": BASE, "api_key": "", "model": MODEL}
        seen = {}

        def fake_open(_opener, request, timeout=None):
            seen["auth"] = request.headers.get("Authorization")
            return _FakeHTTP(_response([[0.1, 0.2]]))

        with patch("urllib.request.OpenerDirector.open", fake_open):
            response = self.client.post("/api/semantic-provider/test", json=body)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(seen["auth"], f"Bearer {SECRET}")

    def test_connection_test_surfaces_provider_failure_without_leaking_key(self):
        failure = urllib.error.HTTPError(
            f"{BASE}/embeddings", 402, "Payment Required", {},
            io.BytesIO(json.dumps({"error": {"message": "No credits"}}).encode()),
        )
        body = {"actor": "manager", "base_url": BASE, "api_key": SECRET, "model": MODEL}
        with patch("urllib.request.OpenerDirector.open", side_effect=failure):
            response = self.client.post("/api/semantic-provider/test", json=body)
        self.assertEqual(response.status_code, 400, response.text)
        self.assertIn("402", response.text)
        self.assertIn("No credits", response.text)
        self.assertNotIn(SECRET, response.text)

    def test_secret_is_never_returned_by_any_endpoint(self):
        self.assertEqual(self._enable().status_code, 200)
        for path in ("/api/semantic-provider", "/api/status", "/api/config", "/api/audit-log"):
            body = self.client.get(path).text
            with self.subTest(path=path):
                self.assertNotIn(SECRET, body)
        stored = self.client.get("/api/semantic-provider").json()
        self.assertTrue(stored["has_api_key"])
        self.assertEqual(stored["api_key_hint"], "...3456")

    def test_blank_key_keeps_the_stored_secret(self):
        self._enable()
        self.assertEqual(self._enable(api_key="").status_code, 200)
        store = Store(str(self.db))
        try:
            self.assertEqual(store.provider_api_key(), SECRET)
        finally:
            store.close()

    def test_secret_is_stored_in_env_file_never_in_the_database(self):
        self._enable()
        db_text = self.db.read_bytes()
        self.assertNotIn(SECRET.encode(), db_text)
        env = self.db.parent / ".env"
        self.assertTrue(env.exists())
        self.assertIn(SECRET, env.read_text(encoding="utf-8"))
        self.assertEqual(env.stat().st_mode & 0o777, 0o600, ".env must not be world/group readable")

    def test_env_file_preserves_unrelated_keys(self):
        env = self.db.parent / ".env"
        env.write_text('EXISTING="keep me"\nOTHER=1\n', encoding="utf-8")
        self._enable()
        self.assertIn('EXISTING="keep me"', env.read_text(encoding="utf-8"))
        self.assertIn("OTHER=1", env.read_text(encoding="utf-8"))
        self._enable(api_key="sk-or-v1-SECOND-KEY-7777")
        text = env.read_text(encoding="utf-8")
        self.assertIn('EXISTING="keep me"', text)
        self.assertIn("sk-or-v1-SECOND-KEY-7777", text)
        self.assertNotIn(SECRET, text)
        self.assertEqual(text.count("AUDIT_ANALYTICS_PROVIDER_API_KEY"), 1)

    def test_database_stores_no_secret_even_for_legacy_rows(self):
        self._enable()
        store = Store(str(self.db))
        try:
            store.conn.execute("UPDATE semantic_provider SET api_key='legacy-secret' WHERE id=1")
            store.conn.commit()
            self.assertEqual(store.provider_api_key(), SECRET, "the .env value must win over any stale column")
        finally:
            store.close()

    def test_enabled_provider_is_used_by_the_resolver(self):
        self._enable()
        store = Store(str(self.db))
        try:
            embedder, model = sem.resolve_embedder(store, "embeddinggemma")
            self.assertIsInstance(embedder, sem.RemoteEmbedder)
            self.assertEqual(model, MODEL)
            self.assertEqual(embedder.identity()["provenance_kind"], "declared_endpoint")
        finally:
            store.close()

    def test_disabling_returns_to_the_local_embedder(self):
        self._enable()
        self.assertEqual(self._enable(enabled=False).status_code, 200)
        store = Store(str(self.db))
        try:
            embedder, _ = sem.resolve_embedder(store)
            self.assertIsInstance(embedder, sem.LocalEmbedder)
        finally:
            store.close()

    def test_audit_log_records_the_decision_without_the_key(self):
        self._enable()
        log = self.client.get("/api/audit-log").text
        self.assertIn("set_semantic_provider", log)
        self.assertIn(MODEL, log)
        self.assertNotIn(SECRET, log)


class ProviderEndToEndTest(unittest.TestCase):
    """The configured provider must actually drive embed-ledger and similar, offline."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.store = Store(str(Path(self.directory.name) / "audit.db"))
        self.store.conn.execute("INSERT INTO engagement VALUES(1,'C','2025-01-01','2025-12-31',0)")
        self.store.add_user("manager", "manager", "system")
        self.store.conn.execute(
            "INSERT INTO imports(kind,original_name,evidence_path,sha256,imported_at,accepted_rows,rejected_rows,"
            "acknowledged_at,acknowledged_by) VALUES('gl','g.csv','g.csv','x',0,3,0,1,'manager')")
        iid = self.store.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        for index, (description, vector) in enumerate(
            [("rent payment office", [1.0, 0.0, 0.0]), ("office rent payment", [0.99, 0.01, 0.0]),
             ("vendor invoice steel", [0.0, 0.0, 1.0])], 1
        ):
            self.store.conn.execute(
                "INSERT INTO ledger_entries(import_id,entry_id,posting_date,account_code,debit,credit,signed_amount,"
                "description,preparer,reference,entity,source_row,source_hash,raw_json) "
                "VALUES(?,?,?,?,100,0,100,?,'p','r','HQ',?,'h','{}')",
                (iid, f"J{index}", "2025-02-01", "6000", description, index))
        self.store.conn.commit()
        self.store.set_semantic_provider({
            "provider": "openai_compatible", "base_url": BASE, "api_key": SECRET, "model": MODEL,
            "referer": "", "title": "", "enabled": True, "acknowledged_at": 1.0, "acknowledged_by": "manager",
        }, "manager")
        self.store.conn.commit()

    def _stub(self, vectors_for):
        def fake_open(_opener, request, timeout=None):
            payload = json.loads(request.data.decode())
            texts = payload["input"]
            texts = [texts] if isinstance(texts, str) else texts
            return _FakeHTTP(_response([vectors_for(t) for t in texts]))
        return patch("urllib.request.OpenerDirector.open", fake_open)

    def test_embed_ledger_stores_vectors_under_the_remote_model(self):
        vectors = {"6000 |  | rent payment office | r | HQ": [1.0, 0.0, 0.0],
                   "6000 |  | office rent payment | r | HQ": [0.99, 0.01, 0.0],
                   "6000 |  | vendor invoice steel | r | HQ": [0.0, 0.0, 1.0]}
        with self._stub(lambda text: vectors.get(text, [0.5, 0.5, 0.0])):
            self.assertEqual(sem.embed_ledger(self.store), 3)
        stored = self.store.conn.execute("SELECT DISTINCT model, dims FROM ledger_embeddings").fetchall()
        self.assertEqual([(r["model"], r["dims"]) for r in stored], [(MODEL, 3)])

    def test_similar_uses_the_remote_provider_for_the_query_vector(self):
        with self._stub(lambda text: [1.0, 0.0, 0.0]):
            sem.embed_ledger(self.store)
        with self._stub(lambda text: [1.0, 0.0, 0.0]):
            results = sem.similar_transactions(self.store, "office rent")
        top = results[0]
        self.assertEqual(top["entry_id"], "J1")
        self.assertIsNotNone(top["semantic_score"])
        self.assertAlmostEqual(top["semantic_score"], 1.0, places=3)

    def test_ledger_stays_lexical_only_when_no_embeddings_exist(self):
        results = sem.similar_transactions(self.store, "steel")
        self.assertTrue(results)
        self.assertIsNone(results[0]["semantic_score"])
