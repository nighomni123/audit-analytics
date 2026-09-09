import csv
import tempfile
from pathlib import Path
import unittest

from audit_analytics.bank import import_bank, reconcile_bank
from audit_analytics.store import Store


class BankTest(unittest.TestCase):
    def test_import_and_reconcile(self):
        with tempfile.TemporaryDirectory() as d:
            store = Store(str(Path(d) / "a.db"))
            store.conn.execute("INSERT INTO engagement VALUES(1,'Client','2025-04-01','2026-03-31',0)")
            store.conn.execute("INSERT INTO imports(id, kind, original_name, evidence_path, sha256, imported_at, accepted_rows, rejected_rows) VALUES(1,'gl','g.csv','p','s',0,0,0)")
            store.conn.execute(
                "INSERT INTO ledger_entries(id, import_id, entry_id, posting_date, document_date,"
                " account_code, debit, credit, signed_amount, description, preparer, reference,"
                " entity, is_manual, source_row, source_hash, raw_json)"
                " VALUES(1, 1, 'E1', '2025-05-01', NULL, '1000', 100.0, 0.0, 100.0,"
                " 'sale', NULL, NULL, NULL, 0, 2, 'h', '{}')")
            store.conn.commit()
            csv_path = Path(d) / "bank.csv"
            with csv_path.open("w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["Date", "Description", "Debit", "Credit", "Balance"])
                w.writerow(["2025-05-01", "sale receipt", "0", "100", "100"])
            import_id, accepted, rejected = import_bank(store, str(csv_path), "manager")
            self.assertEqual(accepted, 1)
            self.assertEqual(rejected, 0)
            n = reconcile_bank(store, "manager")
            self.assertEqual(n, 1)
            row = store.conn.execute("SELECT bank_id, ledger_id FROM bank_matches").fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["ledger_id"], 1)
            store.close()


if __name__ == "__main__":
    unittest.main()
