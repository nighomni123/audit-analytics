import sqlite3
import tempfile
import unittest
from pathlib import Path

from audit_analytics.store import Store
from audit_analytics.workflow import (
    WorkflowError,
    acknowledge_population,
    assign_exception,
    configure_engagement,
    create_engagement,
    lock_review_set,
    record_review,
    reopen_review_set,
)


class WorkflowTest(unittest.TestCase):
    def store(self, directory: str) -> Store:
        store = Store(str(Path(directory) / "audit.db"))
        create_engagement(store, "Client", "2025-04-01:2026-03-31", "manager")
        store.add_user("reviewer", "reviewer", "manager")
        store.add_user("second", "quality_reviewer", "manager")
        store.add_user("read-only", "read_only", "manager")
        store.conn.commit()
        return store

    @staticmethod
    def add_exception(store: Store, severity="high") -> int:
        store.conn.execute(
            "INSERT INTO imports(kind,original_name,evidence_path,sha256,imported_at,accepted_rows,rejected_rows,control_debits,control_credits) VALUES('gl','gl.csv','gl.csv','hash',1,1,0,100,0)"
        )
        import_id = store.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        ledger_id = store.conn.execute(
            """INSERT INTO ledger_entries(import_id,entry_id,posting_date,account_code,debit,credit,signed_amount,source_row,source_hash,raw_json)
               VALUES(?, 'JE-1', '2026-03-31', '6000', 100, 0, 100, 2, 'row', '{}')""",
            (import_id,),
        ).lastrowid
        run_id = store.conn.execute(
            "INSERT INTO model_runs(started_at,configuration,population_count,status) VALUES(1,'{}',1,'complete')"
        ).lastrowid
        exception_id = store.conn.execute(
            "INSERT INTO exceptions(run_id,ledger_id,risk_score,severity,reasons_json,evidence_json) VALUES(?,?,?,?,?,?)",
            (run_id, ledger_id, 90, severity, '["test"]', "{}"),
        ).lastrowid
        store.conn.commit()
        return exception_id

    def test_review_rules_are_atomic_and_shared(self):
        with tempfile.TemporaryDirectory() as directory:
            store = self.store(directory)
            low = self.add_exception(store, "low")
            high = self.add_exception(store, "high")
            result = record_review(store, low, "reviewer", "cleared", "support checked")
            self.assertEqual(result["status"], "cleared")
            self.assertEqual(store.conn.execute("SELECT status FROM exceptions WHERE id=?", (low,)).fetchone()[0], "cleared")

            for second_reviewer, second_note in ((None, None), ("reviewer", "same person"), ("read-only", "not authorized")):
                with self.subTest(second_reviewer=second_reviewer):
                    with self.assertRaises(WorkflowError):
                        record_review(store, high, "reviewer", "cleared", "first note", second_reviewer, second_note)
            self.assertEqual(store.conn.execute("SELECT COUNT(*) FROM reviews WHERE exception_id=?", (high,)).fetchone()[0], 0)
            result = record_review(store, high, "reviewer", "cleared", "first note", "second", "independent note")
            self.assertEqual(result["status"], "cleared")
            review = store.conn.execute("SELECT second_reviewer,second_note FROM reviews WHERE exception_id=?", (high,)).fetchone()
            self.assertEqual(tuple(review), ("second", "independent note"))
            store.close()

    def test_lock_events_persist_and_block_review_and_assignment(self):
        with tempfile.TemporaryDirectory() as directory:
            store = self.store(directory)
            exception_id = self.add_exception(store, "low")
            locked = lock_review_set(store, "manager", "review set complete")
            self.assertTrue(locked["locked"])
            store.close()

            store = Store(str(Path(directory) / "audit.db"))
            self.assertTrue(store.review_locked())
            with self.assertRaisesRegex(WorkflowError, "locked"):
                record_review(store, exception_id, "reviewer", "follow_up", "late change")
            with self.assertRaisesRegex(WorkflowError, "locked"):
                assign_exception(store, "manager", exception_id, "reviewer")
            reopened = reopen_review_set(store, "manager", "evidence received")
            self.assertFalse(reopened["locked"])
            record_review(store, exception_id, "reviewer", "follow_up", "late change")
            self.assertEqual([row["event"] for row in store.review_set_history()], ["locked", "reopened"])
            store.close()

    def test_database_enforces_append_only_history_and_status_consistency(self):
        with tempfile.TemporaryDirectory() as directory:
            store = self.store(directory)
            exception_id = self.add_exception(store, "low")
            review_id = record_review(store, exception_id, "reviewer", "follow_up", "reason")["review_id"]
            with self.assertRaises(sqlite3.IntegrityError):
                store.conn.execute("UPDATE exceptions SET status='cleared' WHERE id=?", (exception_id,))
            with self.assertRaises(sqlite3.IntegrityError):
                store.conn.execute("UPDATE reviews SET note='changed' WHERE id=?", (review_id,))
            with self.assertRaises(sqlite3.IntegrityError):
                store.conn.execute("DELETE FROM reviews WHERE id=?", (review_id,))
            with self.assertRaises(sqlite3.IntegrityError):
                store.conn.execute("DELETE FROM audit_log")
            store.conn.rollback()
            store.close()

    def test_acknowledgement_configuration_and_legacy_lock_migration(self):
        with tempfile.TemporaryDirectory() as directory:
            store = self.store(directory)
            import_id = self.add_exception(store, "low")
            store.conn.execute("UPDATE imports SET expected_rows=1,expected_debits=100,expected_credits=0 WHERE id=?", (import_id,))
            store.conn.commit()
            result = acknowledge_population(store, "reviewer", "agreed to source totals")
            self.assertEqual(result["import_ids"], [import_id])
            config = configure_engagement(
                store,
                "manager",
                materiality=500,
                performance_materiality=350,
                period_end_days=3,
                outlier_robust_z=3.5,
            )
            self.assertEqual(config["materiality"]["overall"], 500)
            with self.assertRaises(WorkflowError):
                configure_engagement(store, "manager", performance_materiality=600)
            store.set_setting("review_locked", {"locked_at": 123.0, "locked_by": "manager"}, "manager")
            store.conn.commit()
            store.close()

            store = Store(str(Path(directory) / "audit.db"))
            self.assertTrue(store.review_locked())
            self.assertEqual(store.review_set_history()[0]["reason"], "Migrated legacy review-lock setting")
            store.close()


if __name__ == "__main__":
    unittest.main()
