import csv
import tempfile
import unittest
from pathlib import Path

from audit_analytics.analytics import analyze
from audit_analytics.importer import import_gl
from audit_analytics.store import Store

class PipelineTest(unittest.TestCase):
    def test_import_requires_acknowledgement_then_creates_traceable_exception(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); gl=root/'gl.csv'
            with gl.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['entry_id','posting_date','account_code','amount','description','preparer','reference']); w.writeheader()
                for i in range(12): w.writerow({'entry_id':f'J{i}','posting_date':'2026-03-31' if i==11 else '2026-02-01','account_code':'6000','amount':1000 if i==11 else 100+i,'description':'accrual','preparer':'admin','reference':f'R{i}'})
            store=Store(str(root/'audit.db')); store.conn.execute("INSERT INTO engagement VALUES(1,'Client','2025-04-01','2026-03-31',0)"); store.conn.commit()
            iid,accepted,rejected,_,_=import_gl(store,str(gl)); self.assertEqual((accepted,rejected),(12,0))
            with self.assertRaisesRegex(ValueError,'acknowledge'): analyze(store)
            store.conn.execute("UPDATE imports SET acknowledged_at=1,acknowledged_by='Auditor',acknowledgement_note='agreed' WHERE id=?",(iid,)); store.conn.commit()
            analyze(store); row=store.conn.execute("SELECT e.*,l.source_row,l.source_hash FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id WHERE l.entry_id='J11'").fetchone()
            self.assertIsNotNone(row); self.assertEqual(row['source_row'],13); self.assertTrue(row['source_hash'])
            self.assertTrue((root/'evidence').exists())

if __name__ == '__main__': unittest.main()
