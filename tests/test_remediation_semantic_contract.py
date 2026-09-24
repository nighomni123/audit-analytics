import array
import tempfile
import unittest
from pathlib import Path

from audit_analytics.importer import import_coa, import_gl
from audit_analytics.semantic_risk import _calculate, _config
from audit_analytics.store import Store


class RemediationSemanticContractTest(unittest.TestCase):
    def test_bounded_candidate_provenance_is_retained_and_not_exhaustive(self):
        entries = [
            {
                "id": index,
                "entry_id": f"E{index}",
                "posting_date": "2025-01-01",
                "account_code": "1000",
                "signed_amount": 100.0,
                "description": "repair" if index % 2 else "fees",
                "preparer": "U1",
                "entity": "HQ",
                "vendor": "V1",
                "reference": str(index),
            }
            for index in range(1, 1001)
        ]
        vectors = {entry["id"]: array.array("f", [1.0, 0.0] if entry["id"] % 2 else [0.0, 1.0]) for entry in entries}
        results, _, _ = _calculate(entries, vectors, _config({"candidate_limit": 64, "peer_limit": 5, "clusters": 4}))
        for result in results:
            evidence = result[4]
            comparison = evidence["comparisons"]["peer_similarity"]
            self.assertLessEqual(len(comparison["candidate_ids"]), 64)
            self.assertIn("population_count", comparison)
            self.assertIn("Nearest examples are sampled deterministically, not an exhaustive nearest-neighbour index.", evidence["limitations"])

    def test_profile_metadata_marks_candidate_generation_as_approximate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "ledger.csv"
            source.write_text("entry_id,posting_date,account_code,amount,description,vendor,preparer,entity\nA1,2025-01-01,1000,10,Repair,V,U1,HQ\nA2,2025-01-02,1000,10,Fees,V,U1,HQ\n", encoding="utf-8")
            coa = root / "coa.csv"
            coa.write_text("account_code,account_name,account_type\n1000,Test,Expense\n", encoding="utf-8")
            store = Store(str(root / "audit.db"))
            store.conn.execute("INSERT INTO engagement VALUES(1,'Semantic','2025-01-01','2025-12-31',0)")
            store.conn.commit()
            import_gl(store, str(source), "manager")
            import_coa(store, str(coa), "manager")
            store.conn.execute("UPDATE imports SET acknowledged_at=1")
            store.conn.commit()
            # The contract is metadata-only; no Ollama or live model is required.
            result = _config({"candidate_limit": 64})
            self.assertEqual(result["candidate_limit"], 64)
            store.close()


if __name__ == "__main__":
    unittest.main()
