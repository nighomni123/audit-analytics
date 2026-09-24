import sqlite3
import tempfile
import unittest
from pathlib import Path

from audit_analytics.store import Store
from audit_analytics.workflow import WorkflowError, record_review


class RemediationGovernanceTest(unittest.TestCase):
    def make_store(self, directory: str) -> tuple[Store, int]:
        store = Store(str(Path(directory) / "audit.db"))
        store.conn.execute("INSERT INTO engagement VALUES(1,'Governance','2025-01-01','2025-12-31',0)")
        store.add_user("reviewer", "reviewer", "manager")
        store.add_user("second", "quality_reviewer", "manager")
        store.conn.execute("INSERT INTO imports(kind,original_name,evidence_path,sha256,imported_at,accepted_rows,rejected_rows) VALUES('gl','gl.csv','gl.csv','h',1,1,0)")
        import_id = store.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        ledger_id = store.conn.execute("INSERT INTO ledger_entries(import_id,entry_id,posting_date,account_code,debit,credit,signed_amount,source_row,source_hash,raw_json) VALUES(?,'J1','2025-12-31','1000',100,0,100,2,'r','{}')", (import_id,)).lastrowid
        run_id = store.conn.execute("INSERT INTO model_runs(started_at,configuration,population_count,status) VALUES(1,'{}',1,'complete')").lastrowid
        exception_id = store.conn.execute("INSERT INTO exceptions(run_id,ledger_id,risk_score,severity,reasons_json,evidence_json) VALUES(?,?,80,'high','[\"test\"]','{}')", (run_id, ledger_id)).lastrowid
        store.conn.commit()
        return store, exception_id

    def test_severity_is_immutable_and_high_clear_still_requires_second_review(self):
        with tempfile.TemporaryDirectory() as directory:
            store, exception_id = self.make_store(directory)
            for target in ("low", "medium", "high", "invalid"):
                with self.subTest(target=target):
                    with self.assertRaises(sqlite3.IntegrityError):
                        store.conn.execute("UPDATE exceptions SET severity=? WHERE id=?", (target, exception_id))
                    store.conn.rollback()
            with self.assertRaises(WorkflowError):
                record_review(store, exception_id, "reviewer", "cleared", "support checked")
            result = record_review(store, exception_id, "reviewer", "cleared", "support checked", "second", "independent check")
            self.assertEqual(result["status"], "cleared")
            store.close()


if __name__ == "__main__":
    unittest.main()
