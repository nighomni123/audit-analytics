import csv
import json
import tempfile
import unittest
from pathlib import Path

from audit_analytics.analytics import analyze
from audit_analytics.importer import import_gl
from audit_analytics.reports import write_engagement_report
from audit_analytics.sampling import create_sample
from audit_analytics.store import Store


class MaterialityTest(unittest.TestCase):
    def _seed(self, root):
        gl = root / "gl.csv"
        with gl.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["entry_id", "posting_date", "account_code", "amount", "description", "preparer", "reference"])
            w.writeheader()
            # 12 entries: one large (1,000,000), the rest small/distinct.
            for i in range(12):
                w.writerow({"entry_id": f"J{i}", "posting_date": "2026-03-31" if i == 11 else "2026-02-01",
                            "account_code": "6000", "amount": 1000000 if i == 11 else 100 + i,
                            "description": "accrual", "preparer": "admin", "reference": f"R{i}"})
        store = Store(str(root / "audit.db"))
        store.conn.execute("INSERT INTO engagement VALUES(1,'Client','2025-04-01','2026-03-31',0)")
        store.add_user("manager", "manager"); store.add_user("reviewer", "reviewer")
        store.set_setting("materiality", {"overall": 500000, "performance": 250000}, "manager")
        store.set_setting("analysis_policy", {"round_amount_threshold": 1000, "period_end_days": 3, "outlier_robust_z": 3.5}, "manager")
        iid, accepted, rejected, _, _ = import_gl(store, str(gl), "manager")
        store.conn.execute("UPDATE imports SET acknowledged_at=1, acknowledged_by='reviewer', acknowledgement_note='agreed' WHERE id=?", (iid,))
        store.conn.commit()
        return store

    def test_exceptions_carry_materiality_band(self):
        with tempfile.TemporaryDirectory() as d:
            store = self._seed(Path(d))
            analyze(store, "manager", include_isolation=False)
            bands = {row["entry_id"]: row["materiality_band"] for row in store.conn.execute(
                "SELECT l.entry_id, e.materiality_band FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id")}
            # J11 is the only entry at/above overall materiality.
            self.assertEqual(bands["J11"], "above_overall")
            self.assertTrue(all(b == "below" for eid, b in bands.items() if eid != "J11"))

    def test_random_sample_respects_min_amount(self):
        with tempfile.TemporaryDirectory() as d:
            store = self._seed(Path(d))
            run_id = analyze(store, "manager", include_isolation=False)
            # Flatten to a pure random slice: no high-severity, risk-count 0.
            store.conn.execute("UPDATE exceptions SET severity='low', risk_score=1")
            store.conn.commit()
            _, selected = create_sample(store, "s", "reviewer", run_id, risk_count=0, random_count=5, seed=3, random_min_amount=250000)
            included = {r["entry_id"] for r in store.conn.execute(
                "SELECT l.entry_id FROM sample_items si JOIN ledger_entries l ON l.id=si.ledger_id")}
            # Only J11 (1,000,000) is >= performance materiality.
            self.assertEqual(included, {"J11"})
            self.assertEqual(selected, 1)

    def test_report_includes_materiality_and_reconciliation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); store = self._seed(root)
            analyze(store, "manager", include_isolation=False)
            out = write_engagement_report(store, str(root / "report.html"), "manager")
            text = out.read_text(encoding="utf-8")
            self.assertIn("Materiality", text)
            self.assertIn("500000", text)
            self.assertIn("Reconciliation", text)
            self.assertIn("Methodology", text)


if __name__ == "__main__":
    unittest.main()
