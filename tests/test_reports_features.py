"""Tests for compare_runs and workpaper manifest hashes."""
import json
import tempfile
import unittest
from pathlib import Path

from audit_analytics.reports import compare_runs, export_workpaper
from audit_analytics.store import Store


def _exc(store, run_id, ledger_id, score):
    store.conn.execute(
        "INSERT INTO exceptions(run_id,ledger_id,risk_score,severity,reasons_json,evidence_json) VALUES(?,?,?,?,?,?)",
        (run_id, ledger_id, score, "high", "[]", "{}"))


class ReportsFeaturesTest(unittest.TestCase):
    def test_compare_and_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            store = Store(str(Path(d) / "t.db"))
            store.conn.execute("INSERT INTO engagement VALUES(1,'Client','2025-04-01','2026-03-31',0)")
            r1 = store.conn.execute("INSERT INTO model_runs(started_at,configuration,population_count,status) VALUES(?,?,?,?)", (1.0, "{}", 3, "complete")).lastrowid
            r2 = store.conn.execute("INSERT INTO model_runs(started_at,configuration,population_count,status) VALUES(?,?,?,?)", (2.0, "{}", 3, "complete")).lastrowid
            imp = store.conn.execute("INSERT INTO imports(kind,original_name,evidence_path,sha256,imported_at,accepted_rows,rejected_rows) VALUES(?,?,?,?,?,?,?)", ("gl", "gl.csv", "ev", "x", 1.0, 3, 0)).lastrowid
            lids = []
            for i, e in enumerate(("E1", "E2", "E3")):
                lids.append(store.conn.execute("INSERT INTO ledger_entries(import_id,entry_id,posting_date,account_code,debit,credit,signed_amount,source_row,source_hash,raw_json) VALUES(?,?,?,?,?,?,?,?,?,?)", (imp, e, "2025-05-01", "1000", 1.0, 0.0, 1.0, i, "h", "{}")).lastrowid)
            la, sh, lb = lids
            _exc(store, r1, la, 0.5)
            _exc(store, r1, sh, 0.8)
            _exc(store, r2, sh, 0.9)
            _exc(store, r2, lb, 0.2)
            store.conn.commit()
            c = compare_runs(store, r1, r2)
            self.assertIsInstance(c["only_in_a"], list)
            self.assertIsInstance(c["only_in_b"], list)
            self.assertIsInstance(c["shared"], int)
            self.assertIsInstance(c["score_deltas"], list)
            self.assertEqual(c["only_in_a"], [la])
            self.assertEqual(c["only_in_b"], [lb])
            self.assertEqual(c["shared"], 1)
            self.assertEqual(len(c["score_deltas"]), 1)
            self.assertEqual(c["score_deltas"][0]["delta"], 0.1)
            out = str(Path(d) / "wp.csv")
            _, mpath, _ = export_workpaper(store, out, "manager")
            m = json.loads(Path(mpath).read_text())
            self.assertTrue(m.get("workpaper_sha256"))
            self.assertTrue(m.get("manifest_sha256"))
            int(m["workpaper_sha256"], 16)
            int(m["manifest_sha256"], 16)


if __name__ == "__main__":
    unittest.main()
