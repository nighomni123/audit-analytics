"""Release 1.1 analytics features: fiscal trigger + taxonomy tagging."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from audit_analytics.analytics import analyze
from audit_analytics.importer import import_gl
from audit_analytics.store import Store


class TestAnalyticsFeatures(unittest.TestCase):
    def test_fiscal_and_taxonomy(self):
        with tempfile.TemporaryDirectory() as d:
            path = str(Path(d) / "eng.db")
            store = Store(path)
            store.conn.execute("INSERT INTO engagement VALUES(1,'Client','2025-04-01','2026-03-31',0)")
            store.add_user("manager", "manager", "system")
            store.set_setting("fiscal_calendar", ["2026-03-31"], "manager")
            store.set_setting("analysis_policy", {"round_amount_threshold": 1000, "period_end_days": 3, "outlier_robust_z": 3.5}, "manager")
            gl = Path(d) / "gl.csv"
            with gl.open("w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["entry_id", "posting_date", "account_code", "debit", "credit", "description", "preparer"])
                w.writerow(["JE1", "2026-03-31", "6000", "100", "0", "year end", "alice"])
                w.writerow(["JE2", "2026-01-05", "6000", "50", "0", "mid year", "bob"])
            iid, *_ = import_gl(store, str(gl), "manager")
            store.conn.execute("UPDATE imports SET acknowledged_at=1, acknowledged_by='reviewer', acknowledgement_note='agreed' WHERE id=?", (iid,))
            store.conn.commit()
            store.conn.execute("INSERT INTO account_taxonomy(account_code, account_type, label, risk_weight) VALUES('6000','expense','Salaries',0.5)")
            store.conn.commit()
            run = analyze(store, "manager", include_isolation=False)
            rows = store.conn.execute(
                "SELECT e.reasons_json, e.evidence_json, l.posting_date FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id WHERE e.run_id=?", (run,)).fetchall()
            self.assertTrue(rows)
            on_date = [r for r in rows if r["posting_date"] == "2026-03-31"]
            self.assertTrue(on_date)
            self.assertTrue(any("fiscal_period_end" in json.loads(r["reasons_json"]) for r in on_date))
            self.assertTrue(any("account_type" in json.loads(r["evidence_json"]) for r in rows))


if __name__ == "__main__":
    unittest.main()
