import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from audit_analytics.api.app import create_app


class CanonicalApiSmokeTest(unittest.TestCase):
    def test_empty_engagement_can_be_created_and_read_from_served_app(self):
        with tempfile.TemporaryDirectory() as directory:
            client = TestClient(create_app(Path(directory) / "audit.db"))
            self.assertEqual(client.get("/api/health").json()["status"], "ok")
            self.assertIsNone(client.get("/api/engagement").json()["engagement"])
            created = client.post(
                "/api/engagement",
                json={"client": "Smoke Client", "period": "2025-01-01:2025-12-31", "owner": "manager"},
            )
            self.assertEqual(created.status_code, 200, created.text)
            self.assertEqual(client.get("/api/engagement").json()["engagement"]["client"], "Smoke Client")
            self.assertEqual(client.get("/").status_code, 200)
            client.close()


if __name__ == "__main__":
    unittest.main()
