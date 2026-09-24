import sqlite3
import tempfile
import unittest
from pathlib import Path

from audit_analytics.store import Store


class OperationsTest(unittest.TestCase):
    def test_sqlite_backup_round_trip_preserves_governance_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = root / "audit.db"
            store = Store(str(database))
            store.conn.execute("INSERT INTO engagement VALUES(1,'Backup Client','2025-01-01','2025-12-31',0)")
            store.conn.execute(
                "INSERT INTO imports(kind,original_name,evidence_path,sha256,imported_at,accepted_rows,rejected_rows) VALUES('gl','gl.csv','gl.csv','hash',1,1,0)"
            )
            import_id = store.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            ledger_id = store.conn.execute(
                """INSERT INTO ledger_entries(import_id,entry_id,posting_date,account_code,debit,credit,signed_amount,source_row,source_hash,raw_json)
                   VALUES(?,'J1','2025-12-31','6000',100,0,100,2,'row','{}')""",
                (import_id,),
            ).lastrowid
            run_id = store.conn.execute(
                "INSERT INTO model_runs(started_at,configuration,population_count,status) VALUES(1,'{}',1,'complete')"
            ).lastrowid
            exception_id = store.conn.execute(
                "INSERT INTO exceptions(run_id,ledger_id,risk_score,severity,reasons_json,evidence_json) VALUES(?,?,80,'high','[]','{}')",
                (run_id, ledger_id),
            ).lastrowid
            store.conn.execute(
                "INSERT INTO reviews(exception_id,reviewer,disposition,note,created_at) VALUES(?, 'reviewer','follow_up','support requested',1)",
                (exception_id,),
            )
            store.conn.commit()
            store.close()

            backup_path = root / "audit-backup.db"
            source = sqlite3.connect(database)
            destination = sqlite3.connect(backup_path)
            try:
                source.backup(destination)
            finally:
                destination.close()
                source.close()

            restored = Store(str(backup_path))
            try:
                self.assertEqual(restored.conn.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                self.assertEqual(restored.conn.execute("SELECT client FROM engagement").fetchone()[0], "Backup Client")
                self.assertEqual(restored.conn.execute("SELECT status FROM exceptions WHERE id=?", (exception_id,)).fetchone()[0], "follow_up")
                self.assertEqual(restored.conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0], 1)
            finally:
                restored.close()


if __name__ == "__main__":
    unittest.main()
