import csv
import tempfile
import unittest
from pathlib import Path

from audit_analytics.analytics import analyze
from audit_analytics.importer import import_gl, preview_gl
from audit_analytics.reports import engagement_summary, export_workpaper, write_engagement_report
from audit_analytics.sampling import create_sample
from audit_analytics.store import Store


class EngagementWorkflowTest(unittest.TestCase):
    def test_reconciled_import_to_exportable_review_workflow(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / "journal.csv"
            with source.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["Voucher Number", "Date", "GL Code", "Amount", "Narration", "User"])
                writer.writeheader()
                for i in range(12):
                    writer.writerow({"Voucher Number": f"V{i}", "Date": "31/03/2026" if i == 11 else "01/02/2026", "GL Code": "6000", "Amount": 1000 if i == 11 else 101 + i, "Narration": "year-end accrual", "User": "preparer"})
            preview = preview_gl(str(source))
            self.assertEqual(preview["missing_required"], [])
            store = Store(str(root / "engagement.db"))
            store.conn.execute("INSERT INTO engagement VALUES(1,'Client','2025-04-01','2026-03-31',0)")
            store.add_user("manager", "manager"); store.add_user("reviewer", "reviewer")
            store.set_setting("analysis_policy", {"round_amount_threshold": 1000, "period_end_days": 3, "outlier_robust_z": 3.5}, "manager")
            expected = sum([101 + i for i in range(11)] + [1000])
            import_id, accepted, rejected, _, _ = import_gl(store, str(source), "manager", expected_rows=12, expected_debits=expected, expected_credits=0)
            self.assertEqual((accepted, rejected), (12, 0)); self.assertTrue(store.reconciliation(import_id)["matches"])
            store.conn.execute("UPDATE imports SET acknowledged_at=1,reconciled_at=1,acknowledged_by='reviewer',reconciled_by='reviewer',acknowledgement_note='agreed',reconciliation_note='agreed' WHERE id=?", (import_id,)); store.conn.commit()
            run_id = analyze(store, "manager", include_isolation=False)
            sample_id, selected = create_sample(store, "planning sample", "reviewer", run_id, risk_count=2, random_count=2, seed=9)
            self.assertGreater(selected, 0); self.assertGreater(sample_id, 0)
            exception = store.conn.execute("SELECT id FROM exceptions ORDER BY risk_score DESC LIMIT 1").fetchone()[0]
            store.conn.execute("INSERT INTO reviews(exception_id,reviewer,disposition,note,created_at) VALUES(?,?,?,?,0)", (exception, "reviewer", "selected_for_testing", "client support requested")); store.conn.execute("UPDATE exceptions SET status='selected_for_testing' WHERE id=?", (exception,)); store.conn.commit()
            workpaper, manifest, count = export_workpaper(store, str(root / "workpaper.csv"), "manager")
            report = write_engagement_report(store, str(root / "report.html"), "manager")
            summary = engagement_summary(store)
            self.assertTrue(workpaper.exists()); self.assertTrue(manifest.exists()); self.assertTrue(report.exists())
            self.assertGreater(count, 0); self.assertTrue(summary["population_acknowledged"]); self.assertEqual(summary["imports"][0]["reconciliation"]["matches"], True)


if __name__ == "__main__":
    unittest.main()
