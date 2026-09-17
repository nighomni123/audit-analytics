"""Offline deterministic checks for semantic evaluation mechanics (fixed vectors only)."""
import csv
import json
import struct
import tempfile
import unittest
from pathlib import Path

from audit_analytics.store import Store
from audit_analytics.semantic_evaluation import evaluate_semantic

FIX = Path(__file__).resolve().parent.parent / "examples" / "semantic"


def _pack(values):
    return struct.pack("<" + "f" * len(values), *values)


def _seed(store, vectors, cues, clusters):
    now = 1.0
    imp = store.conn.execute(
        "INSERT INTO imports(kind,original_name,evidence_path,sha256,imported_at,"
        "accepted_rows,rejected_rows) VALUES('gl','g','g','h',?,?,?)",
        (now, 0, 0)).lastrowid
    with open(FIX / "ledger.csv", newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    ids = {}
    for n, row in enumerate(rows):
        amt = float(row["amount"])
        lid = store.conn.execute(
            "INSERT INTO ledger_entries(import_id,entry_id,posting_date,account_code,debit,"
            "credit,signed_amount,description,vendor,preparer,entity,source_row,source_hash,"
            "raw_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (imp, row["entry_id"], row["posting_date"], row["account_code"],
             amt if amt >= 0 else 0.0, -amt if amt < 0 else 0.0, amt, row["description"] or None,
             row["vendor"] or None, row["preparer"] or None, row["entity"] or None,
             n, "h", "{}")).lastrowid
        ids[row["entry_id"]] = lid
    run = store.conn.execute(
        "INSERT INTO semantic_runs(started_at,completed_at,actor,status,population_count,"
        "population_hash,configuration_json,provenance_json,summary_json) VALUES(?,?,?,?,?,?,?,?,?)",
        (now, now + 1, "system", "complete", len(rows), "pop", json.dumps({"seed": 7}),
         json.dumps({"digest": "d", "template_version": "narration-only-v1"}), "{}")).lastrowid
    for tid, vec in vectors.items():
        lid = ids[tid]
        store.conn.execute(
            "INSERT INTO semantic_profiles VALUES(?,?,?,?,?,?,?,?)",
            (run, "transaction", str(lid), lid, len(vec), _pack(vec), 1,
             json.dumps({"entry": {"entry_id": tid}, "text_hash": tid,
                         "template_version": "narration-only-v1"})))
    for tid in ids:
        lid = ids[tid]
        store.conn.execute(
            "INSERT INTO semantic_results VALUES(?,?,?,?,?,?)",
            (run, lid, clusters.get(tid, 1), json.dumps({'peer_similarity':0.1,'cross_account_similarity':0.9}), json.dumps(cues.get(tid, [])),
             json.dumps({"entry": {'entry_id':tid}})))
    store.conn.commit()
    return run, ids


VECTORS = {
    "R1": [1.0, 0.0, 0.0], "R2": [0.99, 0.01, 0.0], "R3": [0.98, 0.02, 0.0],
    "F1": [0.0, 1.0, 0.0], "F2": [0.0, 0.99, 0.01], "F3": [0.0, 0.98, 0.02],
    "P1": [0.0, 0.0, 1.0], "P2": [0.01, 0.0, 0.99], "P3": [0.02, 0.0, 0.98],
    "A1": [0.0, 0.9, 0.1], "V1": [0.9, 0.0, 0.1], "N1": [0.5, 0.5, 0.0],
    "C1": [0.9, 0.1, 0.0], "G1": [1.0, 0.0, 0.0], "S1": [0.0, 0.0, 1.0],
}


class EvaluationTest(unittest.TestCase):
    def test_report_metrics_and_audit_log(self):
        with tempfile.TemporaryDirectory() as d:
            store = Store(str(Path(d) / "audit.db"))
            cues = {"A1": ["semantic_account_mismatch"], "G1": ["semantic_novel_transaction"]}
            clusters = {"R1": 1, "R2": 1, "R3": 1, "F1": 2, "F2": 2, "F3": 2, "A1": 2,
                        "P1": 3, "P2": 3, "P3": 3, "S1": 3, "V1": 1, "C1": 1,
                        "N1": 4, "G1": 4}
            run, _ = _seed(store, VECTORS, cues, clusters)
            report = evaluate_semantic(store, run, str(FIX / "labels.csv"))
            self.assertEqual(report["labelled_count"], 15)
            self.assertIsNotNone(report["macro_precision_at_10"])
            self.assertIsNotNone(report["macro_recall_at_20"])
            self.assertEqual(report["mismatch"]["applicable_count"], 1)
            self.assertEqual(report["mismatch"]["recall"], 1.0)
            self.assertEqual(report["false_positives_on_negatives"], 1)
            self.assertGreaterEqual(report["peak_python_bytes"], 0)
            self.assertIn("excludes Ollama", report["peak_note"])
            log = store.conn.execute(
                "SELECT * FROM audit_log WHERE action='semantic_evaluate'").fetchall()
            self.assertEqual(len(log), 1)
            self.assertNotEqual(store.conn.execute(
                "SELECT count(*) FROM semantic_runs").fetchone()[0], 0)
            store.close()

    def test_rejects_ambiguous_duplicate_and_unknown(self):
        with tempfile.TemporaryDirectory() as d:
            store = Store(str(Path(d) / "audit.db"))
            run, ids = _seed(store, VECTORS, {}, {})
            imp = store.conn.execute("SELECT id FROM imports").fetchone()[0]
            store.conn.execute(
                "INSERT INTO ledger_entries(import_id,entry_id,posting_date,account_code,"
                "debit,credit,signed_amount,description,source_row,source_hash,raw_json)"
                " VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (imp, "R1", "2025-04-01", "6100", 10.0, 0.0, 10.0, "dup", 99, "h2", "{}"))
            store.conn.commit()
            amb = Path(d) / "amb.csv"
            amb.write_text("transaction_id,expected_related_group,expected_process,"
                           "known_risk,reviewer_label\nR1,R2,repairs,routine,positive\n")
            # A later duplicate must not change the immutable run's identity resolution.
            evaluate_semantic(store, run, str(amb))
            duplicate_id = store.conn.execute('SELECT max(id) FROM ledger_entries').fetchone()[0]
            store.conn.execute('INSERT INTO semantic_results VALUES(?,?,?,?,?,?)', (run, duplicate_id, None, '{}', '[]', json.dumps({'entry':{'entry_id':'R1'}})))
            with self.assertRaisesRegex(ValueError, 'ambiguous'):
                evaluate_semantic(store, run, str(amb))
            store.conn.execute('DELETE FROM semantic_results WHERE run_id=? AND ledger_id=?', (run,duplicate_id))
            dup = Path(d) / "dup.csv"
            dup.write_text("transaction_id,ledger_id,expected_related_group,expected_process,"
                           f"known_risk,reviewer_label\nR2,{ids['R2']},R1,repairs,routine,positive\n"
                           f"R2,{ids['R2']},R1,repairs,routine,positive\n")
            with self.assertRaisesRegex(ValueError, "duplicate"):
                evaluate_semantic(store, run, str(dup))
            amb = Path(d) / "amb2.csv"
            amb.write_text("transaction_id,expected_related_group,expected_process,"
                           "known_risk,reviewer_label\nNOPE,,repairs,routine,positive\n")
            with self.assertRaises(ValueError):
                evaluate_semantic(store, run, str(amb))
            unk = Path(d) / "unk.csv"
            unk.write_text("transaction_id,expected_related_group,expected_process,"
                           "known_risk,reviewer_label\nR1,R2,repairs,bogus,positive\n")
            with self.assertRaises(ValueError):
                evaluate_semantic(store, run, str(unk))
            store.close()

    def test_precision_ranking_and_denominator(self):
        with tempfile.TemporaryDirectory() as d:
            store=Store(str(Path(d)/'audit.db'))
            vectors={k:[-1.,0.] for k in VECTORS}
            vectors.update(R1=[1.,0.],R2=[1.,0.])
            run,_=_seed(store,vectors,{}, {})
            labels=Path(d)/'labels.csv'
            labels.write_text('transaction_id,expected_related_group,expected_process,known_risk,reviewer_label\nR1,R2,repairs,routine,positive\n')
            report=evaluate_semantic(store,run,str(labels))
            self.assertEqual(report['macro_precision_at_10'],0.1)
            self.assertEqual(report['macro_recall_at_20'],1.0)
            store.close()

    def test_rejects_incomplete_run(self):
        with tempfile.TemporaryDirectory() as d:
            store = Store(str(Path(d) / "audit.db"))
            run = store.conn.execute(
                "INSERT INTO semantic_runs(started_at,actor,status,population_count,"
                "population_hash,configuration_json,provenance_json) VALUES(?,?,?,?,?,?,?)",
                (1.0, "system", "running", 0, "p", "{}", "{}")).lastrowid
            store.conn.commit()
            with self.assertRaises(ValueError):
                evaluate_semantic(store, run, str(FIX / "labels.csv"))
            store.close()


if __name__ == "__main__":
    unittest.main()
