import random
import unittest
from datetime import date, timedelta

from audit_analytics.analytics import MAX_ANALYSIS_POPULATION, _check_analysis_population, _reversal_matches


def legacy_reversal_matches(entries):
    buckets = {}
    for entry in entries:
        buckets.setdefault((entry["account_code"], round(abs(entry["signed_amount"]), 2)), []).append(entry)
    matches = {}
    for entry in entries:
        for other in buckets[(entry["account_code"], round(abs(entry["signed_amount"]), 2))]:
            if other["id"] != entry["id"] and other["signed_amount"] * entry["signed_amount"] < 0 and abs((date.fromisoformat(other["posting_date"]) - date.fromisoformat(entry["posting_date"])).days) <= 30:
                matches[entry["id"]] = other["id"]
                break
    return matches


class ReversalOptimizationTest(unittest.TestCase):
    def test_analysis_safety_boundary_distinguishes_import_from_analysis(self):
        _check_analysis_population(MAX_ANALYSIS_POPULATION)
        with self.assertRaisesRegex(ValueError, "import is retained"):
            _check_analysis_population(MAX_ANALYSIS_POPULATION + 1)


        entries = [
            {"id": 1, "account_code": "A", "signed_amount": 100, "posting_date": "2025-01-01"},
            {"id": 2, "account_code": "A", "signed_amount": -100, "posting_date": "2025-01-02"},
            {"id": 3, "account_code": "A", "signed_amount": -100, "posting_date": "2025-01-03"},
            {"id": 4, "account_code": "A", "signed_amount": 100, "posting_date": "2025-02-01"},
        ]
        self.assertEqual(_reversal_matches(entries), legacy_reversal_matches(entries))
        self.assertEqual(_reversal_matches(entries)[1], 2)

    def test_indexed_lookup_matches_legacy_on_dense_randomized_fixture(self):
        rng = random.Random(17)
        entries = []
        for index in range(2000):
            entries.append({
                "id": index + 1,
                "account_code": f"A{rng.randrange(4)}",
                "signed_amount": rng.choice((-100.0, 100.0, -200.0, 200.0)),
                "posting_date": (date(2025, 1, 1) + timedelta(days=rng.randrange(70))).isoformat(),
            })
        self.assertEqual(_reversal_matches(entries), legacy_reversal_matches(entries))

    def test_large_dense_bucket_uses_indexed_path(self):
        entries = [
            {"id": index + 1, "account_code": "A", "signed_amount": 100.0 if index % 2 else -100.0, "posting_date": "2025-01-15"}
            for index in range(20000)
        ]
        matches = _reversal_matches(entries)
        self.assertEqual(len(matches), 20000)
        self.assertEqual(matches[1], 2)


if __name__ == "__main__":
    unittest.main()
