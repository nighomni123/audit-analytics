import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CliWorkflowTest(unittest.TestCase):
    def test_first_engagement_commands_complete_with_exact_reconciliation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); db = root / "audit.db"; source = root / "gl.csv"
            with source.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["entry_id", "posting_date", "account_code", "debit", "credit", "description"])
                writer.writeheader()
                for i in range(12): writer.writerow({"entry_id": f"J{i}", "posting_date": "2026-03-31" if i == 11 else "2026-02-01", "account_code": "6000", "debit": 1000 if i == 11 else 100 + i, "credit": 0, "description": "accrual"})
            def run(*args):
                return subprocess.run([sys.executable, "run.py", *args], cwd=ROOT, text=True, capture_output=True, check=True)
            run("init", "--db", str(db), "--client", "Client", "--period", "2025-04-01:2026-03-31", "--owner", "manager")
            run("add-user", "--db", str(db), "--actor", "manager", "--username", "reviewer", "--role", "reviewer")
            total = sum([100 + i for i in range(11)] + [1000])
            imported = run("import-gl", "--db", str(db), "--actor", "manager", "--file", str(source), "--expected-rows", "12", "--expected-debits", str(total), "--expected-credits", "0")
            self.assertTrue(json.loads(imported.stdout)["reconciliation"]["matches"])
            run("acknowledge-population", "--db", str(db), "--reviewer", "reviewer", "--note", "Agreed to source control report")
            run("analyze", "--db", str(db), "--actor", "manager", "--no-isolation")
            status = json.loads(run("status", "--db", str(db)).stdout)
            self.assertTrue(status["population_acknowledged"])


if __name__ == "__main__":
    unittest.main()
