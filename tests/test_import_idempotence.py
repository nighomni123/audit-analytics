import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from audit_analytics.bank import import_bank
from audit_analytics.importer import DuplicateImportError, import_coa, import_gl
from audit_analytics.store import Store


class ImportIdempotenceTest(unittest.TestCase):
    def make_store(self, directory: str) -> Store:
        return Store(str(Path(directory) / "audit.db"))

    def test_gl_duplicate_is_rejected_and_explicit_reimport_is_linked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "gl.csv"
            source.write_text("entry_id,posting_date,account_code,amount\nJ1,2026-03-31,6000,100\n", encoding="utf-8")
            store = self.make_store(directory)
            first, *_ = import_gl(store, str(source))
            copy_path = root / "renamed.csv"
            copy_path.write_bytes(source.read_bytes())
            with self.assertRaises(DuplicateImportError) as caught:
                import_gl(store, str(copy_path))
            self.assertEqual(caught.exception.existing_import_id, first)
            self.assertEqual(store.conn.execute("SELECT COUNT(*) FROM ledger_entries").fetchone()[0], 1)

            second, *_ = import_gl(store, str(source), reimport=True)
            row = store.conn.execute("SELECT supersedes_import_id FROM imports WHERE id=?", (second,)).fetchone()
            self.assertEqual(row[0], first)
            self.assertEqual(store.conn.execute("SELECT COUNT(*) FROM ledger_entries").fetchone()[0], 2)
            self.assertEqual(len(list((root / "evidence").iterdir())), 1)
            store.close()

    def test_coa_and_bank_use_the_same_exact_hash_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            coa = root / "coa.csv"
            coa.write_text("account_code,account_name\n6000,Repairs\n", encoding="utf-8")
            bank = root / "bank.csv"
            bank.write_text("entry_date,narration,debit,credit,balance\n2026-03-31,Receipt,0,100,100\n", encoding="utf-8")
            store = self.make_store(directory)
            import_coa(store, str(coa))
            bank_id, *_ = import_bank(store, str(bank), "preparer")
            with self.assertRaises(DuplicateImportError):
                import_coa(store, str(coa))
            with self.assertRaises(DuplicateImportError):
                import_bank(store, str(bank), "preparer")
            reimported, *_ = import_bank(store, str(bank), "preparer", reimport=True)
            self.assertEqual(
                store.conn.execute("SELECT supersedes_import_id FROM imports WHERE id=?", (reimported,)).fetchone()[0],
                bank_id,
            )
            store.close()

    def test_source_limit_and_failed_import_leave_no_orphan_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "gl.csv"
            with source.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=["entry_id", "posting_date", "account_code", "amount"])
                writer.writeheader()
                writer.writerow({"entry_id": "J1", "posting_date": "2026-03-31", "account_code": "6000", "amount": "1"})
            store = self.make_store(directory)
            with patch("audit_analytics.importer.MAX_SOURCE_BYTES", 10):
                with self.assertRaisesRegex(ValueError, "import limit"):
                    import_gl(store, str(source))
            self.assertFalse((root / "evidence").exists())
            with patch("audit_analytics.importer._rows", side_effect=RuntimeError("parser failed")):
                with self.assertRaisesRegex(RuntimeError, "parser failed"):
                    import_gl(store, str(source))
            self.assertEqual(list((root / "evidence").iterdir()), [])
            self.assertEqual(store.conn.execute("SELECT COUNT(*) FROM imports").fetchone()[0], 0)
            store.close()


if __name__ == "__main__":
    unittest.main()
