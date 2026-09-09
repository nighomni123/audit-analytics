import csv
import tempfile
import unittest
from pathlib import Path

from audit_analytics.connectors import run_connector
from audit_analytics.store import Store


def _make_db(tmp):
    db = str(Path(tmp) / "t.db")
    store = Store(db)
    store.conn.execute("INSERT INTO engagement VALUES(1,'Client','2025-04-01','2026-03-31',0)")
    store.add_user("manager", "manager")
    store.conn.commit()
    return store


class TestConnectors(unittest.TestCase):
    def test_demo_csv_and_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            csvpath = str(Path(tmp) / "gl.csv")
            with open(csvpath, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=["entry_id", "posting_date", "account_code",
                                                  "debit", "credit", "description", "preparer",
                                                  "reference", "entity", "is_manual"])
                w.writeheader()
                w.writerow({"entry_id": "E1", "posting_date": "2025-05-01", "account_code": "1000",
                            "debit": 100, "credit": 0, "description": "d", "preparer": "p",
                            "reference": "R1", "entity": "HQ", "is_manual": "manual"})
                w.writerow({"entry_id": "E2", "posting_date": "2025-05-02", "account_code": "2000",
                            "debit": 0, "credit": 100, "description": "d2", "preparer": "p",
                            "reference": "R2", "entity": "HQ", "is_manual": ""})
            store = _make_db(tmp)
            import_id, manifest = run_connector("demo_csv", store, csvpath, "manager")
            assert import_id > 0
            row = store.conn.execute("SELECT * FROM connector_runs").fetchone()
            assert row is not None
            assert manifest["record_count"] == manifest["accepted"] == 2
            try:
                run_connector("sap", store, csvpath, "manager")
            except ValueError:
                pass
            else:
                raise AssertionError("expected ValueError")
            store.close()
