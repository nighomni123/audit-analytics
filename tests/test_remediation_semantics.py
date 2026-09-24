import unittest

from audit_analytics.analytics import _calculate_signals


class RemediationSemanticsTest(unittest.TestCase):
    def test_fiscal_period_window_includes_preceding_days_and_excludes_future_days(self):
        entries = []
        for index, posted in enumerate(("2026-03-27", "2026-03-28", "2026-03-29", "2026-03-30", "2026-03-31", "2026-04-01")):
            entries.append({"id": index + 1, "account_code": "1000", "signed_amount": 100.123 + index, "posting_date": posted, "description": f"fiscal {index}", "preparer": "U1", "reference": f"F{index}"})
        reasons, _, _, _, _, _ = _calculate_signals(entries, {"round_amount_threshold": 1000, "period_end_days": 3}, __import__("datetime").date(2026, 3, 31), ["2026-03-31", "2026-09-30"], {}, False)
        self.assertNotIn("fiscal_period_end", reasons[1])
        for ledger_id in (2, 3, 4, 5):
            self.assertIn("fiscal_period_end", reasons[ledger_id])
        self.assertNotIn("fiscal_period_end", reasons[6])

    def test_missing_identity_is_not_a_rare_preparer_pair(self):
        entries = [
            {"id": index + 1, "account_code": "1000", "signed_amount": 100.123 + index, "posting_date": "2025-02-14", "description": f"known {index}", "preparer": "U1", "reference": f"K{index}"}
            for index in range(10)
        ]
        entries.extend([
            {"id": 11, "account_code": "1000", "signed_amount": 120.123, "posting_date": "2025-02-14", "description": "blank preparer", "preparer": None, "reference": "M1"},
            {"id": 12, "account_code": None, "signed_amount": 121.123, "posting_date": "2025-02-14", "description": "blank account", "preparer": "U2", "reference": "M2"},
            {"id": 13, "account_code": None, "signed_amount": 122.123, "posting_date": "2025-02-14", "description": "both missing", "preparer": None, "reference": "M3"},
        ])
        reasons, evidence, _, _, _, _ = _calculate_signals(entries, {"round_amount_threshold": 1000, "period_end_days": 3}, __import__("datetime").date(2026, 3, 31), [], {}, False)
        for ledger_id in (11, 12, 13):
            self.assertNotIn("rare_account_preparer_pair", reasons[ledger_id])
            self.assertEqual(evidence[ledger_id]["rare_account_preparer_pair_applicability"], "not_applicable_missing_identity")


if __name__ == "__main__":
    unittest.main()
