"""FastAPI endpoint contract tests (replaces server endpoint checks for adapter)."""
import unittest, sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from audit_analytics.api.app import app, db_path

class TestFastAPIContracts(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_status_contract(self):
        r = self.client.get("/api/status")
        self.assertEqual(r.status_code, 200)
        self.assertIn("entries", r.json())

    def test_exceptions_contract_empty_run(self):
        r = self.client.get("/api/exceptions")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("count", data)
        self.assertIn("rows", data)

    def test_users_contract(self):
        r = self.client.get("/api/users")
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.json(), list)

    def test_similar_contract(self):
        r = self.client.get("/api/similar?q=test")
        self.assertEqual(r.status_code, 200)
        self.assertIn("results", r.json())

    def test_review_requires_note_and_disposition(self):
        r = self.client.post("/api/review", json={"id":1,"reviewer":"admin","disposition":"open","note":""})
        self.assertIn(r.status_code, (400, 422))

if __name__ == "__main__":
    unittest.main()
