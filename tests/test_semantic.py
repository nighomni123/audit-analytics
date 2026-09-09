import tempfile
import unittest
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

if __name__ == '__main__': unittest.main()
