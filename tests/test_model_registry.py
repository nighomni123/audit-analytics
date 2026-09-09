import tempfile
import time
import unittest
from pathlib import Path

from audit_analytics import model_registry
from audit_analytics.store import Store


class TestModelRegistry(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(str(Path(self.tmp.name) / "t.db"))
        self.store.conn.execute("INSERT INTO engagement VALUES(1,'Client','2025-04-01','2026-03-31',0)")

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_register_validate_stamp(self):
        mid = model_registry.register_model(
            self.store, "m1", "rules", {"f": "float"}, "owner1", "actor1")
        self.assertTrue(mid)
        model_registry.validate_model(
            self.store, "m1", "actor1", performance={"auc": 0.9}, approved_by="partner1")
        models = model_registry.list_models(self.store)
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0]["status"], "validated")
        cur = self.store.conn.execute(
            "INSERT INTO model_runs(started_at, configuration, population_count, status)"
            " VALUES(?,?,?,?)", (time.time(), "{}", 10, "done"))
        run_id = cur.lastrowid
        model_registry.stamp_run(self.store, run_id, "m1", "validated")
        row = self.store.conn.execute("SELECT * FROM model_runs WHERE id=?", (run_id,)).fetchone()
        self.assertEqual(row["model_name"], "m1")

    def test_validate_unknown(self):
        with self.assertRaises(ValueError):
            model_registry.validate_model(self.store, "nope", "actor1")


if __name__ == "__main__":
    unittest.main()
