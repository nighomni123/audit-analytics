import csv
import tempfile
import unittest
from pathlib import Path

from audit_analytics.importer import import_gl
from audit_analytics.store import Store


class RemediationImportContractTest(unittest.TestCase):
    def test_empty_money_is_rejected_but_explicit_zero_and_signed_amount_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "money.csv"
            fields = ["entry_id", "posting_date", "account_code", "amount", "debit", "credit"]
            rows = [
                {"entry_id": "DEBIT", "posting_date": "2025-02-14", "account_code": "1000", "amount": "", "debit": "10", "credit": ""},
                {"entry_id": "CREDIT", "posting_date": "2025-02-14", "account_code": "1000", "amount": "", "debit": "", "credit": "10"},
                {"entry_id": "AMOUNT", "posting_date": "2025-02-14", "account_code": "1000", "amount": "10", "debit": "", "credit": ""},
                {"entry_id": "ZERO", "posting_date": "2025-02-14", "account_code": "1000", "amount": "0", "debit": "", "credit": ""},
                {"entry_id": "NEGATIVE_SIGNED", "posting_date": "2025-02-14", "account_code": "1000", "amount": "-5", "debit": "", "credit": ""},
                {"entry_id": "EMPTY", "posting_date": "2025-02-14", "account_code": "1000", "amount": "", "debit": "", "credit": ""},
                {"entry_id": "NEGATIVE_DEBIT", "posting_date": "2025-02-14", "account_code": "1000", "amount": "", "debit": "-1", "credit": ""},
                {"entry_id": "BOTH", "posting_date": "2025-02-14", "account_code": "1000", "amount": "", "debit": "1", "credit": "1"},
            ]
            with source.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            store = Store(str(root / "audit.db"))
            store.conn.execute("INSERT INTO engagement VALUES(1,'Import Contract','2025-01-01','2025-12-31',0)")
            store.conn.commit()
            result = import_gl(store, str(source), "manager")
            self.assertEqual(result[1], 5)
            self.assertEqual(result[2], 3)
            accepted = {row["entry_id"]: (row["debit"], row["credit"], row["signed_amount"]) for row in store.conn.execute("SELECT entry_id,debit,credit,signed_amount FROM ledger_entries")}
            self.assertEqual(accepted["ZERO"], (0.0, 0.0, 0.0))
            self.assertEqual(accepted["NEGATIVE_SIGNED"], (0.0, 5.0, -5.0))
            rejected = {row["source_row"]: row["reason"] for row in store.conn.execute("SELECT source_row,reason FROM rejected_rows")}
            self.assertEqual(rejected[7], "monetary amount is required")
            self.assertIn("invalid debit/credit values", rejected[8])
            self.assertIn("invalid debit/credit values", rejected[9])
            raw = store.conn.execute("SELECT raw_json FROM rejected_rows WHERE source_row=7").fetchone()[0]
            self.assertIn("EMPTY", raw)
            store.close()


if __name__ == "__main__":
    unittest.main()
