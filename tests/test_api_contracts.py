import csv
import io
import tempfile
import unittest
import zipfile
from pathlib import Path

from fastapi.testclient import TestClient

from audit_analytics.api.app import create_app
from audit_analytics.store import Store


class FastAPIContractTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.db = self.root / "audit.db"
        self.client = TestClient(create_app(self.db))
        response = self.client.post(
            "/api/engagement",
            json={"client": "API Client", "period": "2025-04-01:2026-03-31", "owner": "manager"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        store = Store(str(self.db))
        store.add_user("reviewer", "reviewer", "manager")
        store.add_user("second", "quality_reviewer", "manager")
        store.conn.commit()
        store.close()
        source = self.root / "gl.csv"
        with source.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=["entry_id", "posting_date", "account_code", "amount", "description"])
            writer.writeheader()
            for index in range(12):
                writer.writerow(
                    {
                        "entry_id": f"JE{index}",
                        "posting_date": "2026-03-31" if index == 11 else "2026-02-01",
                        "account_code": "6000",
                        "amount": 1000 if index == 11 else 100 + index,
                        "description": "year-end accrual" if index == 11 else "routine repair",
                    }
                )
        self.source = source

    def tearDown(self):
        self.client.close()
        self.directory.cleanup()

    def upload(self, *, reimport=False):
        data = {
            "actor": "manager",
            "expected_rows": "12",
            "expected_debits": str(sum([100 + i for i in range(11)] + [1000])),
            "expected_credits": "0",
            "reimport": str(reimport).lower(),
        }
        return self.client.post(
            "/api/imports/gl",
            data=data,
            files={"file": (self.source.name, self.source.read_bytes(), "text/csv")},
        )

    def seed_analysis(self):
        imported = self.upload()
        self.assertEqual(imported.status_code, 200, imported.text)
        acknowledged = self.client.post(
            "/api/imports/acknowledge",
            json={"reviewer": "reviewer", "note": "agreed to source control report", "override_reconciliation": False},
        )
        self.assertEqual(acknowledged.status_code, 200, acknowledged.text)
        configured = self.client.put(
            "/api/config",
            json={"actor": "manager", "materiality": 500, "performance_materiality": 350, "period_end_days": 3},
        )
        self.assertEqual(configured.status_code, 200, configured.text)
        analyzed = self.client.post("/api/analysis-runs", json={"actor": "reviewer", "include_isolation": False})
        self.assertEqual(analyzed.status_code, 200, analyzed.text)
        return analyzed.json()["run_id"]

    def test_health_static_and_same_origin_contract(self):
        health = self.client.get("/api/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["status"], "ok")
        self.assertRegex(health.headers["x-request-id"], r"^[0-9a-f]{16}$")
        root = self.client.get("/")
        self.assertEqual(root.status_code, 200)
        self.assertIn("text/html", root.headers["content-type"])
        self.assertNotIn("access-control-allow-origin", root.headers)
        self.assertEqual(root.headers["x-frame-options"], "DENY")
        self.assertEqual(self.client.get("/api/status").status_code, 200)

    def test_preview_import_duplicate_and_reconciliation_contract(self):
        preview = self.client.post(
            "/api/imports/preview",
            files={"file": (self.source.name, self.source.read_bytes(), "text/csv")},
        )
        self.assertEqual(preview.status_code, 200, preview.text)
        self.assertEqual(preview.json()["missing_required"], [])
        self.assertEqual(preview.json()["row_count"], 12)
        first = self.upload()
        self.assertEqual(first.status_code, 200, first.text)
        self.assertTrue(first.json()["reconciliation"]["matches"])
        duplicate = self.upload()
        self.assertEqual(duplicate.status_code, 409)
        self.assertEqual(duplicate.json()["error"]["code"], "duplicate_import")
        reimport = self.upload(reimport=True)
        self.assertEqual(reimport.status_code, 200, reimport.text)
        self.assertNotEqual(first.json()["import_id"], reimport.json()["import_id"])
        missing = self.client.get("/api/imports/999999/reconciliation")
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(missing.json()["error"]["code"], "not_found")

    def test_analysis_review_lock_and_export_contract(self):
        run_id = self.seed_analysis()
        queue = self.client.get("/api/exceptions", params={"run": run_id, "severity": "high", "limit": 5})
        self.assertEqual(queue.status_code, 200, queue.text)
        self.assertGreater(queue.json()["total"], 0)
        exception_id = queue.json()["rows"][0]["id"]
        detail = self.client.get(f"/api/exceptions/{exception_id}")
        self.assertEqual(detail.status_code, 200, detail.text)
        self.assertTrue(detail.json()["entry_id"])

        missing_second = self.client.post(
            "/api/review",
            json={"id": exception_id, "reviewer": "reviewer", "disposition": "cleared", "note": "support checked"},
        )
        self.assertIn(missing_second.status_code, (400, 409))
        reviewed = self.client.post(
            "/api/review",
            json={
                "id": exception_id,
                "reviewer": "reviewer",
                "disposition": "cleared",
                "note": "support checked",
                "second_reviewer": "second",
                "second_note": "independent review",
            },
        )
        self.assertEqual(reviewed.status_code, 200, reviewed.text)
        self.assertEqual(self.client.get(f"/api/exceptions/{exception_id}").json()["status"], "cleared")

        locked = self.client.post(
            "/api/review-set/lock", json={"actor": "manager", "reason": "review set complete"}
        )
        self.assertEqual(locked.status_code, 200, locked.text)
        blocked = self.client.post(
            "/api/review",
            json={"id": exception_id, "reviewer": "reviewer", "disposition": "follow_up", "note": "late change"},
        )
        self.assertEqual(blocked.status_code, 409)
        self.assertEqual(blocked.json()["error"]["code"], "review_locked")
        reopened = self.client.post(
            "/api/review-set/reopen", json={"actor": "manager", "reason": "new evidence received"}
        )
        self.assertEqual(reopened.status_code, 200, reopened.text)

        package = self.client.post("/api/exports/package", json={"actor": "reviewer"})
        self.assertEqual(package.status_code, 200, package.text)
        self.assertEqual(package.headers["content-type"], "application/zip")
        with zipfile.ZipFile(io.BytesIO(package.content)) as archive:
            names = set(archive.namelist())
            self.assertIn("workpaper.csv", names)
            self.assertIn("workpaper.csv.manifest.json", names)
            self.assertIn("workpaper.csv.manifest.json.sha256", names)
            self.assertIn("engagement-report.html", names)

    def test_sample_audit_and_exception_filter_contract(self):
        run_id = self.seed_analysis()
        created = self.client.post(
            "/api/sample-sets",
            json={
                "actor": "reviewer",
                "name": "API planning sample",
                "run_id": run_id,
                "risk_count": 1,
                "random_count": 1,
                "seed": 17,
                "random_min_amount": 0,
            },
        )
        self.assertEqual(created.status_code, 200, created.text)
        sample_id = created.json()["sample_set_id"]
        self.assertGreater(created.json()["selected"], 0)

        listed = self.client.get("/api/sample-sets", params={"limit": 10})
        self.assertEqual(listed.status_code, 200, listed.text)
        self.assertEqual(listed.json()["rows"][0]["id"], sample_id)
        self.assertIn("method", listed.json()["rows"][0])

        detail = self.client.get(f"/api/sample-sets/{sample_id}")
        self.assertEqual(detail.status_code, 200, detail.text)
        self.assertEqual(detail.json()["item_count"], detail.json()["selected_count"])
        self.assertTrue(detail.json()["items"])
        self.assertTrue(detail.json()["items"][0]["rationale"])
        self.assertIn("exception", detail.json()["items"][0])

        duplicate = self.client.post(
            "/api/sample-sets",
            json={"actor": "reviewer", "name": "API planning sample", "run_id": run_id},
        )
        self.assertEqual(duplicate.status_code, 409, duplicate.text)
        self.assertEqual(duplicate.json()["error"]["code"], "conflict")
        self.assertEqual(self.client.get(f"/api/sample-sets/{sample_id}").status_code, 200)

        audit = self.client.get(
            "/api/audit-log",
            params={
                "action": "create_sample",
                "target_type": "sample_set",
                "target_id": str(sample_id),
                "actor": "reviewer",
                "limit": 10,
            },
        )
        self.assertEqual(audit.status_code, 200, audit.text)
        self.assertEqual(audit.json()["rows"][0]["detail"]["selected"], created.json()["selected"])
        self.assertNotIn("detail_json", audit.json()["rows"][0])

        filtered = self.client.get(
            "/api/exceptions",
            params={
                "run": run_id,
                "account": "6000",
                "date_from": "2026-01-01",
                "date_to": "2026-12-31",
                "signal": "round_amount",
                "min_amount": 0,
                "max_amount": 2000,
            },
        )
        self.assertEqual(filtered.status_code, 200, filtered.text)
        self.assertGreater(filtered.json()["total"], 0)
        self.assertTrue(all(row["account_code"] == "6000" for row in filtered.json()["rows"]))
        self.assertTrue(all("round_amount" in row["reasons"] for row in filtered.json()["rows"]))

        invalid = self.client.post(
            "/api/sample-sets",
            json={"actor": "reviewer", "name": "bad", "run_id": run_id, "risk_count": -1},
        )
        self.assertEqual(invalid.status_code, 422)
        self.assertEqual(invalid.json()["error"]["code"], "validation_error")

    def test_validation_errors_use_one_json_shape(self):
        response = self.client.post("/api/review", json={"id": 0, "reviewer": "", "disposition": "unknown", "note": ""})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "validation_error")


class DemoSeedContractTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.db = Path(self.directory.name) / "demo.db"
        self.client = TestClient(create_app(self.db))

    def tearDown(self):
        self.client.close()
        self.directory.cleanup()

    def test_demo_seed_creates_only_synthetic_workflow_state(self):
        response = self.client.post("/api/demo/seed")
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertTrue(payload["synthetic"])
        self.assertEqual(payload["accepted"], 400)
        self.assertEqual(payload["rejected"], 0)
        self.assertAlmostEqual(payload["debits"], 3496407.62, places=2)
        self.assertEqual(payload["credits"], 0)
        self.assertEqual(payload["reviews"], 0)
        self.assertGreater(payload["run_id"], 0)
        self.assertIn("Synthetic", payload["engagement"]["client"])

        store = Store(str(self.db))
        self.assertEqual(store.conn.execute("SELECT COUNT(*) FROM ledger_entries").fetchone()[0], 400)
        self.assertEqual(store.conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0], 0)
        store.close()

        repeated = self.client.post("/api/demo/seed")
        self.assertEqual(repeated.status_code, 409, repeated.text)
        self.assertEqual(repeated.json()["error"]["code"], "conflict")


if __name__ == "__main__":
    unittest.main()
