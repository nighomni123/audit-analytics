"""Tests for compare_runs and workpaper manifest hashes."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from audit_analytics.reports import compare_runs, export_workpaper, verify_manifest
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
            reviewed = store.conn.execute("SELECT id FROM exceptions WHERE run_id=? AND ledger_id=?", (r1, sh)).fetchone()[0]
            store.conn.execute(
                """INSERT INTO reviews(exception_id,reviewer,disposition,note,created_at,second_reviewer,second_note)
                   VALUES(?,?,?,?,?,?,?)""",
                (reviewed, "reviewer", "cleared", "support checked", 1.0, "second", "independent check"),
            )
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
            self.assertNotIn("manifest_sha256", m)
            self.assertEqual(m["integrity"]["algorithm"], "SHA-256")
            int(m["workpaper_sha256"], 16)
            self.assertTrue(verify_manifest(mpath))
            with Path(out).open(newline="", encoding="utf-8") as stream:
                fields = next(csv.DictReader(stream)).keys()
            self.assertIn("second_reviewer", fields)
            self.assertIn("second_note", fields)
            Path(mpath).write_text(Path(mpath).read_text() + "tampered", encoding="utf-8")
            self.assertFalse(verify_manifest(mpath))


if __name__ == "__main__":
    unittest.main()
