import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from audit_analytics.api.app import create_app
from audit_analytics.importer import import_gl, preview_gl
from audit_analytics.store import Store


class ImportDataQualityTest(unittest.TestCase):
    def test_parenthesized_amount_imports_as_credit(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "gl.csv"
            source.write_text(
                "entry_id,posting_date,account_code,amount\n"
                "J1,2026-03-31,6000,(750.50)\n"
                "J2,2026-03-31,6000,1000\n",
                encoding="utf-8",
            )
            store = Store(str(Path(directory) / "audit.db"))
            import_gl(store, str(source))
            rows = {r["entry_id"]: dict(r) for r in store.conn.execute(
                "SELECT entry_id,debit,credit,signed_amount FROM ledger_entries")}
            self.assertEqual(rows["J1"]["credit"], 750.50)
            self.assertEqual(rows["J1"]["debit"], 0.0)
            self.assertEqual(rows["J1"]["signed_amount"], -750.50)
            self.assertEqual(rows["J2"]["debit"], 1000.0)
            store.close()

    def test_parenthesized_debit_column_is_rejected_not_silently_flipped(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "gl.csv"
            source.write_text(
                "entry_id,posting_date,account_code,debit,credit\nJ1,2026-03-31,6000,(500),0\n",
                encoding="utf-8",
            )
            store = Store(str(Path(directory) / "audit.db"))
            _, accepted, rejected, *_ = import_gl(store, str(source))
            self.assertEqual((accepted, rejected), (0, 1))
            reason = store.conn.execute("SELECT reason FROM rejected_rows").fetchone()[0]
            self.assertIn("invalid debit/credit values", reason)
            self.assertIn("(500)", reason)
            store.close()

    def test_preview_reports_ambiguous_slash_dates_only(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "gl.csv"
            source.write_text(
                "entry_id,posting_date,account_code,amount\n"
                "J1,04/03/2025,6000,100\n"
                "J2,25/03/2025,6000,100\n"
                "J3,2025-03-04,6000,100\n",
                encoding="utf-8",
            )
            result = preview_gl(str(source))
            self.assertEqual(result["row_count"], 3)
            self.assertEqual(result["ambiguous_date_rows"], 1)
            self.assertEqual(result["date_format_assumed"], "DD/MM/YYYY")

            iso = Path(directory) / "iso.csv"
            iso.write_text("entry_id,posting_date,account_code,amount\nJ1,2025-03-04,6000,100\n", encoding="utf-8")
            clean = preview_gl(str(iso))
            self.assertEqual(clean["ambiguous_date_rows"], 0)
            self.assertIsNone(clean["date_format_assumed"])

    def test_missing_db_path_fails_loudly_for_non_init_commands(self):
        from audit_analytics.cli import main
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "typo.db"
            with self.assertRaises(SystemExit) as caught:
                main(["status", "--db", str(missing)])
            self.assertEqual(caught.exception.code, 2)
            self.assertFalse(missing.exists())

    def test_rejected_rows_endpoint_returns_reasons(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "audit.db"
            store = Store(str(db))
            store.close()
            client = TestClient(create_app(db))
            source = Path(directory) / "gl.csv"
            source.write_text(
                "entry_id,posting_date,account_code,amount\n"
                "J1,not-a-date,6000,100\n"
                "J2,2026-03-31,6000,100\n",
                encoding="utf-8",
            )
            import_gl(Store(str(db)), str(source))
            response = client.get("/api/imports/1/rejected")
            self.assertEqual(response.status_code, 200)
            body = response.json()
            self.assertEqual(body["total"], 1)
            self.assertEqual(body["rows"][0]["source_row"], 2)
            self.assertIn("invalid posting date: 'not-a-date'", body["rows"][0]["reason"])
            self.assertEqual(body["rows"][0]["raw"]["entry_id"], "J1")

            self.assertEqual(client.get("/api/imports/999/rejected").status_code, 404)


if __name__ == "__main__":
    unittest.main()
