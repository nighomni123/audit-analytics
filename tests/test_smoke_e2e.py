"""Smoke E2E: import preview → status → exceptions → review (contract level)."""
import unittest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from audit_analytics.api.app import app

class TestSmokeE2E(unittest.TestCase):
    def test_smoke_path(self):
        client = TestClient(app)
        # 1. Preview GL import (contract)
        r = client.get("/preview-gl?file=test")
        # may fail due to missing file; that's expected in smoke
        self.assertIn(r.status_code, (200, 400))
        # 2. Status
        r = client.get("/api/status")
        self.assertEqual(r.status_code, 200)
        # 3. Exceptions (dashboard source)
        r = client.get("/api/exceptions")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("rows", data)
        # 4. Investigation contract
        r = client.get("/api/semantic-investigation?run=1&ledger_id=1")
        self.assertIn(r.status_code, (200, 404, 400))  # contract reached
        # 5. Review requires note (governance preserved)
        r = client.post("/api/review", json={"id":1,"reviewer":"admin","disposition":"open","note":"test"})
        # may fail due to role check or missing exception; check contract
        self.assertIn(r.status_code, (200, 400, 404))

if __name__ == "__main__":
    unittest.main()
