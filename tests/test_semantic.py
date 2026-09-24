import array
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from audit_analytics.semantic import classify, similar_transactions
from audit_analytics.store import Store

class SemanticTest(unittest.TestCase):
    def test_token_classes_and_similarity_work_without_a_model_service(self):
        self.assertEqual(classify("NEFT bank transfer for GST tax"), ["cash_bank", "tax"])
        with tempfile.TemporaryDirectory() as d:
            store=Store(str(Path(d)/"audit.db")); store.conn.execute("INSERT INTO engagement VALUES(1,'Client','2025-04-01','2026-03-31',0)")
            for i, desc in enumerate(("Year end GST provision manual journal", "Office rent paid", "Payroll accrual"), 1):
                store.conn.execute("""INSERT INTO imports(kind,original_name,evidence_path,sha256,imported_at,accepted_rows,rejected_rows) VALUES('gl','g.csv','g.csv','x',0,1,0)""")
                iid=store.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                store.conn.execute("""INSERT INTO ledger_entries(import_id,entry_id,posting_date,account_code,debit,credit,signed_amount,description,source_row,source_hash,raw_json)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?)""",(iid,str(i),'2026-03-31','2200',100,0,100,desc,i,'h'+str(i),'{}'))
            store.conn.commit(); rows=similar_transactions(store,"manual tax provision",limit=2)
            self.assertEqual(rows[0]['description'],"Year end GST provision manual journal")
            self.assertGreater(rows[0]['token_score'],0)
    def test_embedded_similarity_uses_one_batch_vector_query(self):
        with tempfile.TemporaryDirectory() as directory:
            store = Store(str(Path(directory) / "audit.db"))
            store.conn.execute("INSERT INTO imports(kind,original_name,evidence_path,sha256,imported_at,accepted_rows,rejected_rows) VALUES('gl','g.csv','g.csv','x',0,3,0)")
            import_id = store.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            vectors = ((1.0, 0.0), (0.8, 0.2), (0.0, 1.0))
            for index, (description, vector) in enumerate((("manual tax provision", vectors[0]), ("tax reserve", vectors[1]), ("office rent", vectors[2])), 1):
                ledger_id = store.conn.execute(
                    """INSERT INTO ledger_entries(import_id,entry_id,posting_date,account_code,debit,credit,signed_amount,description,source_row,source_hash,raw_json)
                       VALUES(?,?,'2026-03-31','6000',100,0,100,?,?,?,'{}')""",
                    (import_id, str(index), description, index, f"h{index}"),
                ).lastrowid
                store.conn.execute(
                    "INSERT INTO ledger_embeddings VALUES(?,?,?,?,?,?)",
                    (ledger_id, "fixed", 2, f"t{index}", array.array("f", vector).tobytes(), 1),
                )
            store.conn.commit()
            statements = []
            store.conn.set_trace_callback(statements.append)
            with patch("audit_analytics.semantic.LocalEmbedder.embed", return_value=[array.array("f", vectors[0])]):
                results = similar_transactions(store, "manual tax provision", limit=3, model="fixed")
            vector_reads = [sql for sql in statements if "SELECT vector FROM ledger_embeddings" in sql]
            self.assertEqual(vector_reads, [])
            batch_reads = [sql for sql in statements if "SELECT ledger_id,vector FROM ledger_embeddings" in sql]
            self.assertEqual(len(batch_reads), 1)
            self.assertEqual(results[0]["ledger_id"], 1)
            self.assertEqual(results[0]["semantic_score"], 1.0)
            with self.assertRaisesRegex(ValueError, "limit"):
                similar_transactions(store, "manual tax provision", limit=0)
            store.close()


if __name__ == "__main__":
    unittest.main()
