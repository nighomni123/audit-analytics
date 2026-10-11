"""End-to-end integration tests for Investigation Context v2.

Exercises the canonical synthetic fixture through import -> reconcile ->
acknowledge -> deterministic analysis -> (optional semantic profile) ->
investigation context, and the FastAPI contract.

Cases per the remediation plan:
  A  deterministic-only investigation
  B  semantic enrichment (with optional live Ollama fallback to injected profile)
  C  related ledger entries (duplicates, outliers, possible reversals)
  D  reviews and bank evidence
  E  unavailable / inapplicable / missing information
  F  read-only invariants (before/after table snapshots)
  G  FastAPI endpoint contract with valid and invalid inputs
"""
import csv
import json
import struct
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient
from audit_analytics.store import Store
from audit_analytics.analytics import analyze
from audit_analytics.importer import import_gl, preview_gl
from audit_analytics.workflow import acknowledge_population, configure_engagement
from audit_analytics.api.app import create_app
from audit_analytics.investigation_context import (
    _map_procedure,
    investigation_context,
    PROCEDURE_CATALOGUE,
)
from audit_analytics.semantic_risk import (
    DEFAULTS,
    TEMPLATE_VERSION,
    population_hash,
)

DETERMINISTIC_CUES = [
    "duplicate_or_repeated_entry",
    "round_amount",
    "period_end_posting",
    "weekend_posting",
    "rare_account_preparer_pair",
    "fiscal_period_end",
    "robust_account_peer_outlier",
    "possible_reversal_within_30_days",
    "isolation_style_anomaly",
]

SEMANTIC_CUES = [
    "semantic_account_mismatch",
    "semantic_novel_transaction",
    "semantic_vendor_shift",
    "semantic_cluster_outlier",
    "semantic_process_outlier",
]

FIXTURE_ROWS = [
    # Account 6000: peer population (>=8 small entries) for outlier detection.
    ("JE001", "2025-03-01", "6000", "480.00", "office services", "U001"),
    ("JE002", "2025-03-03", "6000", "520.00", "office services", "U001"),
    ("JE003", "2025-03-05", "6000", "490.00", "office services", "U001"),
    ("JE004", "2025-03-07", "6000", "510.00", "office services", "U001"),
    ("JE005", "2025-03-09", "6000", "500.00", "office services", "U001"),
    ("JE006", "2025-03-11", "6000", "530.00", "office services", "U001"),
    ("JE007", "2025-03-13", "6000", "470.00", "office services", "U001"),
    ("JE008", "2025-03-15", "6000", "500.00", "office services", "U001"),
    ("JE009", "2025-03-10", "6000", "1000.00", "year-end accrual", "U001"),  # round_amount
    ("JE010", "2025-03-29", "6000", "2500.00", "weekend posting", "U002"),  # weekend + period_end + rare
    ("JE011", "2025-03-30", "6000", "3000.00", "period-end posting", "U001"),  # weekend + period_end
    ("JE012", "2025-03-02", "6000", "500000.00", "outlier purchase", "U001"),  # robust peer outlier
    # Account 6200: duplicate + rare account/preparer pair.
    ("JE013", "2025-03-04", "6200", "500.00", "software license", "U002"),  # duplicate + rare
    ("JE014", "2025-03-06", "6200", "600.00", "software license", "U002"),  # duplicate + rare
    ("JE015", "2025-03-08", "6200", "550.00", "software license", "U002"),  # duplicate
    ("JE016", "2025-03-08", "6200", "550.00", "software license", "U002"),  # duplicate
    ("JE017", "2025-03-12", "6200", "500.00", "consulting", "U009"),  # rare pair
    ("JE018", "2025-03-14", "6200", "500.00", "consulting", "U009"),  # rare pair
    # Account 6400: routine small entries (no cues).
    ("JE019", "2025-03-01", "6400", "800.00", "repairs", "U001"),
    ("JE020", "2025-03-03", "6400", "850.00", "repairs", "U001"),
    ("JE021", "2025-03-05", "6400", "820.00", "repairs", "U001"),
    ("JE022", "2025-03-07", "6400", "0.00", "correction", "U001"),
    # Account 5100: possible reversal pair.
    ("JE023", "2025-03-01", "5100", "12000.00", "inventory purchase", "U001"),  # reversal
    ("JE024", "2025-03-05", "5100", "15000.00", "inventory purchase", "U001"),
    ("JE025", "2025-03-10", "5100", "-12000.00", "inventory reversal", "U001"),  # reversal
    # Account 6100: period-end + round + fiscal period-end.
    ("JE026", "2025-03-31", "6100", "10000.00", "fiscal close", "U001"),
    ("JE027", "2025-04-02", "6100", "200.00", "stationery", "U001"),
    ("JE028", "2025-04-04", "6100", "250.00", "stationery", "U001"),
    # Account 6300: rare account/preparer pair.
    ("JE029", "2025-03-10", "6300", "5000.00", "audit fee", "U009"),  # rare
    ("JE030", "2025-03-15", "6300", "5000.00", "advisory fee", "U009"),  # rare
]
FIXTURE_ACCOUNTS = ["5100", "6000", "6100", "6200", "6300", "6400"]


class FixtureBuilder:
    """Builds a deterministic ledger fixture in a fresh temporary store."""

    def __init__(self, work_dir: Path) -> None:
        self.work_dir = work_dir
        self.db_path = work_dir / "fixture.db"
        self.fixture_csv = work_dir / "fixture.csv"

    def build(self) -> "FixtureBuilder":
        self._write_fixture_csv()
        self.store = Store(str(self.db_path))
        self._seed()
        return self

    def _write_fixture_csv(self) -> None:
        with self.fixture_csv.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["entry_id", "posting_date", "account_code", "amount", "description", "preparer"])
            for row in FIXTURE_ROWS:
                w.writerow(row)

    def _seed(self) -> None:
        store = self.store
        store.add_user("manager", "manager")
        store.add_user("reviewer", "reviewer")
        store.add_user("quality_reviewer", "quality_reviewer")
        store.add_user("preparer", "preparer")
        for code, name, atype in zip(FIXTURE_ACCOUNTS, [
            "Cost of goods sold", "Repairs & maintenance", "Office supplies",
            "IT & software", "Professional fees", "Utilities",
        ], ["expense"] * 6):
            store.conn.execute(
                "INSERT INTO coa(account_code, account_name, account_type) VALUES(?,?,?)",
                (code, name, atype),
            )
        for code, atype, label, weight in zip(FIXTURE_ACCOUNTS, ["expense"] * 6,
                ["COGS", "Repairs", "Office", "IT", "Professional", "Utilities"],
                [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]):
            store.conn.execute(
                "INSERT INTO account_taxonomy(account_code, account_type, label, risk_weight) VALUES(?,?,?,?)",
                (code, atype, label, weight),
            )
        store.conn.execute(
            "INSERT INTO engagement VALUES(1, ?, ?, ?, ?)",
            ("Fixture Client", "2025-04-01", "2026-03-31", 0),
        )
        store.conn.commit()

    def import_and_acknowledge(self, expected_rows: int = 30) -> int:
        expected_debits = sum(float(a) for _, _, _, a, _, _ in FIXTURE_ROWS if float(a) >= 0)
        expected_credits = sum(-float(a) for _, _, _, a, _, _ in FIXTURE_ROWS if float(a) < 0)
        import_id, accepted, rejected, debits, credits = import_gl(
            self.store, str(self.fixture_csv), "manager",
            expected_rows=expected_rows,
            expected_debits=round(expected_debits, 2),
            expected_credits=round(expected_credits, 2),
        )
        assert accepted == expected_rows and rejected == 0, (accepted, rejected)
        acknowledge_population(self.store, "reviewer", "Fixture acknowledged for testing.")
        return import_id

    def configure(self) -> dict:
        return configure_engagement(
            self.store, "manager",
            materiality=500000.0,
            performance_materiality=100000.0,
            round_amount_threshold=1000.0,
            period_end_days=3,
            outlier_robust_z=3.5,
        )

    def run_analysis(self, semantic_run_id: int | None = None) -> int:
        run_id = analyze(self.store, "manager", include_isolation=False, semantic_run_id=semantic_run_id)
        assert self.store.conn.execute(
            "SELECT COUNT(*) FROM model_runs WHERE id=?", (run_id,),
        ).fetchone()[0] == 1
        return run_id

    def ledger_id_for(self, entry_id: str) -> int:
        row = self.store.conn.execute(
            "SELECT id FROM ledger_entries WHERE entry_id=?", (entry_id,),
        ).fetchone()
        assert row, f"entry {entry_id} not found in ledger"
        return row["id"]

    def fixture_entry_ids(self) -> list[str]:
        return [row[0] for row in FIXTURE_ROWS]


def _pack_vector(dims: int = 512) -> bytes:
    return struct.pack("<" + "f" * dims, *([0.0] * dims))


def _text_hash(text: str) -> str:
    import hashlib
    return hashlib.sha256(text.encode()).hexdigest()


def _inject_semantic_fixture(store: Store, ledger_ids: dict[str, int]) -> tuple[int, str]:
    """Inject a complete, self-consistent semantic profile without Ollama.

    The injected profile is validated by the same population-hash check used by
    the live engine, so a correct injection passes validation and a deliberately
    altered hash is rejected as stale. Returns (run_id, population_hash).
    """
    population_hash_value = population_hash(store)
    provenance = {
        "model": "embeddinggemma",
        "digest": "test-vector-digest-v1",
        "template_version": TEMPLATE_VERSION,
        "engine_version": "semantic-risk-v1",
        "dimensions": 512,
        "population_hash": population_hash_value,
    }
    started = 1740000000.0
    # The semantic results table must cover every ledger entry so the analysis
    # completeness check passes; only the candidate entries carry cues.
    entry_lids = [r[0] for r in store.conn.execute("SELECT id FROM ledger_entries ORDER BY id")]
    candidate_ledger_ids = set(ledger_ids.values())
    run_id = store.conn.execute(
        """INSERT INTO semantic_runs
           (started_at, actor, status, population_count, population_hash,
            configuration_json, provenance_json, summary_json, limitation_note)
           VALUES(?, 'system', 'complete', ?, ?, ?, ?, ?, ?)""",
        (started, len(entry_lids), population_hash_value,
         json.dumps({"min_peers": DEFAULTS["min_peers"], "seed": DEFAULTS["seed"],
                     "candidate_limit": DEFAULTS["candidate_limit"], "peer_limit": DEFAULTS["peer_limit"]}),
         json.dumps(provenance),
         json.dumps({
             "eligible_count": len(entry_lids),
             "inapplicable_count": 0,
             "dimensions": 512,
             "retrieval": {
                 "method": "deterministic_bounded_candidates",
                 "exhaustive": False,
                 "candidate_limit": DEFAULTS["candidate_limit"],
                 "peer_limit": DEFAULTS["peer_limit"],
                 "training_limit": DEFAULTS["training_limit"],
                 "tie_break": "score_desc_then_ledger_id",
             },
         }),
         "Experimental semantic cues are investigation aids, not audit conclusions.",
        ),
    ).lastrowid
    for entry_id, lid in ledger_ids.items():
        narration = store.conn.execute(
            "SELECT description FROM ledger_entries WHERE id=?", (lid,),
        ).fetchone()[0] or ""
        text = "Narration: " + " ".join(str(narration).split())
        text_hash = _text_hash(TEMPLATE_VERSION + "|" + text)
        store.conn.execute(
            "INSERT INTO semantic_profiles VALUES(?,?,?,?,?,?,?,?)",
            (run_id, "transaction", str(lid), lid, 512, _pack_vector(512), 1,
             json.dumps({"entry": {"entry_id": entry_id}, "text_hash": text_hash,
                         "template_version": TEMPLATE_VERSION})),
        )
    for lid in entry_lids:
        cues = ["semantic_novel_transaction", "semantic_vendor_shift"] if lid in candidate_ledger_ids else []
        store.conn.execute(
            "INSERT INTO semantic_results VALUES(?,?,?,?,?,?)",
            (run_id, lid, 0, json.dumps({}), json.dumps(cues), json.dumps({})),
        )
    store.conn.commit()
    return run_id, population_hash_value


class InvestigationIntegrationTests(unittest.TestCase):
    """Cases A-G: real integration against the canonical fixture."""

    def setUp(self) -> None:
        self.work = tempfile.mkdtemp(prefix="audit-investigation-")
        self.work_path = Path(self.work)
        self.b = FixtureBuilder(self.work_path).build()

    def tearDown(self) -> None:
        pass

    # --------------------------------------------------------------------
    # Case A -- deterministic-only investigation
    # --------------------------------------------------------------------
    def test_caseA_deterministic_only_investigation(self) -> None:
        """Import + reconcile + acknowledge + deterministic analysis, then open
        investigation context WITHOUT any semantic embeddings."""
        import_id = self.b.import_and_acknowledge()
        self.b.configure()
        run_id = self.b.run_analysis()
        peer = self.b.store.conn.execute(
            "SELECT population_count, status FROM model_runs WHERE id=?", (run_id,),
        ).fetchone()
        self.assertEqual(peer["population_count"], 30)
        self.assertEqual(peer["status"], "complete")

        # Every flagged entry must return a complete deterministic context.
        for entry_id in self.b.fixture_entry_ids():
            ledger_id = self.b.ledger_id_for(entry_id)
            ctx = investigation_context(self.b.store, run_id, ledger_id)

        self.assertEqual(ctx["investigation_context_version"], "v2")
        self.assertTrue(ctx["read_only"])
        self.assertIn("contract", ctx)
        self.assertEqual(ctx["contract"]["run_id"], run_id)

        # Open the top-of-queue exception and verify deterministic-only state.
        ex = b.store.conn.execute(
            """SELECT ledger_id, risk_score, severity, reasons_json FROM exceptions
               WHERE run_id=? ORDER BY risk_score DESC, id LIMIT 1""",
            (run_id,),
        ).fetchone()
        self.assertIsNotNone(ex)
        ctx = investigation_context(self.b.store, run_id, ex["ledger_id"])

        tx = ctx["transaction_line"]
        self.assertTrue(tx["available"])
        self.assertEqual(tx["import_id"], import_id)
        self.assertTrue(tx["source_hash"])
        self.assertEqual(tx["manual_or_system"], "not_flagged")
        self.assertIn("lineage", ctx)
        self.assertEqual(ctx["lineage"]["run_status"], "complete")
        self.assertEqual(ctx["lineage"]["model_name"], "deterministic-rules-v1")
        self.assertEqual(ctx["lineage"]["validation_status"], "rules-only")
        self.assertIsNone(ctx["lineage"]["semantic_profile_run_id"])

        reasons = ctx["why_flagged"]
        self.assertTrue(reasons["deterministic_evidence_available"])
        self.assertFalse(reasons["experimental_evidence_available"])
        self.assertIn("explanation", reasons)

        peers = ctx["population_and_peers"]
        self.assertTrue(peers["available"])
        self.assertIsInstance(peers["population_count"], int)
        peer_stats = peers["peer_statistics"]
        self.assertIsNotNone(peer_stats)
        self.assertTrue(peer_stats["median_available"])
        self.assertIn("calculation", peer_stats)
        self.assertIn("mad", peer_stats)
        self.assertIn("population_count", peer_stats)

        reviews = ctx["supporting_evidence"]["review_history"]
        self.assertFalse(reviews["available"])
        self.assertEqual(reviews["review_count"], 0)

        bank = ctx["supporting_evidence"]["bank"]
        self.assertFalse(bank["available"])
        self.assertIn("not_applicable", bank["status"])

        self.assertGreater(len(ctx["suggested_procedures"]), 0)
        for p in ctx["suggested_procedures"]:
            self.assertTrue(p["non_conclusive"])
            self.assertFalse(p["experimental"])
            self.assertFalse(p["unrecognized"])

    # --------------------------------------------------------------------
    # Case B -- semantic enrichment (live Ollama or injected profile)
    # --------------------------------------------------------------------
    def test_caseB_semantic_enrichment(self) -> None:
        """Verify deterministic + semantic enrichment, cue parsing, provenance,
        candidate details, approximation disclosure, and stale-run rejection."""
        # Isolated fixture — avoids cross-test state leakage from shared b.
        local_dir = Path(tempfile.mkdtemp())
        b = FixtureBuilder(local_dir)
        b.build()  # creates self.store
        import_id = b.import_and_acknowledge()
        b.configure()
        det_run_id = b.run_analysis()

        semantic_run_id: int
        has_ollama = (Path("/usr/local/bin/ollama").exists()
                      or Path("/usr/bin/ollama").exists())
        if has_ollama:
            from audit_analytics.semantic_risk import semantic_profile
            semantic_run_id = semantic_profile(b.store, "embeddinggemma", 64, "manager")
        else:
            semantic_run_id, _ = _inject_semantic_fixture(
                b.store,
                {b.fixture_entry_ids()[14]: b.ledger_id_for("JE015"),
                 b.fixture_entry_ids()[23]: b.ledger_id_for("JE024")},
            )

        profile = b.store.conn.execute(
            "SELECT * FROM semantic_runs WHERE id=?", (semantic_run_id,),
        ).fetchone()
        self.assertEqual(profile["status"], "complete")

        linked_run_id = b.run_analysis(semantic_run_id=semantic_run_id)
        ex = b.store.conn.execute(
            """SELECT id, ledger_id, risk_score, severity, reasons_json, evidence_json
               FROM exceptions WHERE run_id=?
               ORDER BY risk_score DESC, id LIMIT 5""",
            (linked_run_id,),
        ).fetchall()
        self.assertGreater(len(ex), 0)

        semantic_ledger_id = b.ledger_id_for("JE015")
        ctx = investigation_context(
            b.store, linked_run_id, semantic_ledger_id, semantic_run_id,
        )

        tx = ctx["transaction_line"]
        self.assertEqual(tx["ledger_identity"], semantic_ledger_id)

        lineage = ctx["lineage"]
        self.assertEqual(lineage["semantic_profile_run_id"], semantic_run_id)
        self.assertEqual(lineage["semantic_model"], "embeddinggemma")
        self.assertEqual(lineage["semantic_model_digest"], "test-vector-digest-v1")
        self.assertTrue(lineage["semantic_approximate_retrieval"])
        self.assertEqual(lineage["semantic_approximate_retrieval_note"],
                         "Semantic candidate retrieval is bounded and approximate unless validated.")

        semantic_evidence = ctx["supporting_evidence"]["semantic"]
        self.assertTrue(semantic_evidence["available"])
        self.assertEqual(semantic_evidence["status"], "complete")
        self.assertTrue(semantic_evidence["approximate_retrieval_disclosed"])
        self.assertIsNotNone(semantic_evidence["population_hash"])
        self.assertEqual(semantic_evidence["engagement_hash_matches"], True)

        semantic_cues = [c for c in ctx["cues"] if c["source"] == "semantic_model"]
        self.assertGreater(len(semantic_cues), 0)
        for c in semantic_cues:
            self.assertIn(c["cue_id"], SEMANTIC_CUES)
            self.assertTrue(c["procedure"]["non_conclusive"])
            self.assertTrue(c["procedure"].get("experimental", False))

        flagged = ctx["why_flagged"]
        self.assertTrue(flagged["experimental_evidence_available"])
        self.assertTrue(flagged["deterministic_evidence_available"])

        stale_run_id, base_hash = _inject_semantic_fixture(b.store, {})
        b.store.conn.execute(
            "UPDATE semantic_runs SET provenance_json=?, population_hash=? WHERE id=?",
            (json.dumps({**json.loads(profile["provenance_json"]), "population_hash": "stale-" + base_hash}),
             "stale-" + base_hash,
             stale_run_id),
        )
        from audit_analytics.semantic_risk import get_semantic_profile
        stale_profile = get_semantic_profile(b.store, stale_run_id)
        self.assertTrue(stale_profile["stale"])
        with self.assertRaises(LookupError):
            investigation_context(b.store, linked_run_id, semantic_ledger_id, stale_run_id)

    # --------------------------------------------------------------------
    # Case C -- related ledger entries
    # --------------------------------------------------------------------
    def test_caseC_related_ledger_entries(self) -> None:
        self.assertEqual(self.b.import_and_acknowledge(), 1)
        self.b.configure()
        run_id = self.b.run_analysis()

        def ctx_for(entry_id: str) -> dict:
            return investigation_context(
                self.b.store, run_id, self.b.ledger_id_for(entry_id),
            )

        ctx = ctx_for("JE015")
        dup = ctx["population_and_peers"]["duplicate_entries"]
        self.assertTrue(dup["available"])
        self.assertEqual(dup["count"], 1)
        members = dup["members"]
        self.assertEqual(len(members), 1)
        entry_ids = [m["entry_id"] for m in members]
        self.assertEqual(entry_ids, ["JE016"])
        self.assertEqual(members[0]["ledger_id"], self.b.ledger_id_for("JE016"))
        self.assertEqual(members[0]["signed_amount"], 550.00)
        self.assertEqual(members[0]["description"], "software license")
        self.assertEqual(members[0]["posting_date"], "2025-03-08")
        self.assertEqual(members[0]["source_row"], 17)
        self.assertTrue(members[0]["source_hash"])
        self.assertIn("matching_rationale", dup)
        self.assertIn("account", dup["matching_rationale"].lower())
        self.assertIn("date", dup["matching_rationale"].lower())
        self.assertIn("amount", dup["matching_rationale"].lower())
        self.assertIn("narration", dup["matching_rationale"].lower())

        ctx = ctx_for("JE023")
        rev = ctx["population_and_peers"]["possible_reversal"]
        self.assertTrue(rev["available"])
        self.assertEqual(rev["status"], "flagged")
        self.assertIsNotNone(rev["counterpart"])
        c = rev["counterpart"]
        self.assertEqual(c["ledger_id"], self.b.ledger_id_for("JE025"))
        self.assertEqual(c["entry_id"], "JE025")
        self.assertEqual(c["signed_amount"], -12000.00)
        self.assertEqual(c["posting_date"], "2025-03-10")
        self.assertEqual(c["narration"], "inventory reversal")
        self.assertIn("basis", rev)
        self.assertIn("30 days", rev["basis"])
        self.assertEqual(rev["days_difference"], 9)

        ctx2 = ctx_for("JE025")
        rev2 = ctx2["population_and_peers"]["possible_reversal"]
        self.assertTrue(rev2["available"])
        self.assertEqual(rev2["status"], "flagged")
        self.assertEqual(rev2["counterpart"]["entry_id"], "JE023")

        ctx = investigation_context(self.b.store, run_id,
                                    self.b.ledger_id_for("JE015"), max_related=3)
        self.assertEqual(len(ctx["population_and_peers"]["duplicate_entries"]["members"]), 1)

        ctx = ctx_for("JE012")
        ps = ctx["population_and_peers"]["peer_statistics"]
        self.assertTrue(ps["available"])
        self.assertTrue(ps["median_available"])
        self.assertTrue(ps["mad_positive"])
        self.assertGreater(ps["population_count"], 8)
        cue_ids = [c["cue_id"] for c in ctx["cues"]]
        self.assertIn("robust_account_peer_outlier", cue_ids)

    # --------------------------------------------------------------------
    # Case D -- reviews and bank evidence
    # --------------------------------------------------------------------
    def test_caseD_reviews_and_bank_evidence(self) -> None:
        self.assertEqual(self.b.import_and_acknowledge(), 1)
        self.b.configure()
        run_id = self.b.run_analysis()

        ex = b.store.conn.execute(
            "SELECT id, ledger_id FROM exceptions WHERE ledger_id=?",
            (self.b.ledger_id_for("JE009"),),
        ).fetchone()
        self.assertIsNotNone(ex)
        exception_id = ex["id"]

        ts = 1740001000.0
        self.b.store.conn.execute(
            "INSERT INTO reviews(exception_id, reviewer, disposition, note, created_at) "
            "VALUES(?,?,?,?,?)", (exception_id, "reviewer", "follow_up",
                                   "Client support requested for round amount.", ts),
        )
        self.b.store.conn.execute(
            "INSERT INTO reviews(exception_id, reviewer, disposition, note, created_at) "
            "VALUES(?,?,?,?,?)", (exception_id, "manager", "cleared",
                                   "Evidence obtained.", ts + 10),
        )

        other_ex = b.store.conn.execute(
            "SELECT id FROM exceptions WHERE ledger_id!=?", (self.b.ledger_id_for("JE009"),),
        ).fetchone()
        self.assertIsNotNone(other_ex)
        self.b.store.conn.execute(
            "INSERT INTO reviews(exception_id, reviewer, disposition, note, created_at) "
            "VALUES(?,?,?,?,?)", (other_ex["id"], "reviewer", "cleared",
                                   "Unrelated review.", ts + 100),
        )

        self.b.store.conn.execute(
            "INSERT INTO bank_statements(import_id, entry_date, narration, debit, credit, balance, source_row, source_hash, raw_json) "
            "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (1, "2025-03-10", "payment via bank", 1000.00, 0.0, 25000.00,
             45, "banksha000000000000000000000000000000000000000000000000000000000000", "{}"),
        )
        bank_id = self.b.store.conn.execute(
            "SELECT rowid FROM bank_statements WHERE narration=?", ("payment via bank",),
        ).fetchone()[0]
        self.b.store.conn.execute(
            "INSERT INTO bank_matches(bank_id, ledger_id, match_type, amount_diff, created_at) "
            "VALUES(?, ?, ?, ?, ?)",
            (bank_id, self.b.ledger_id_for("JE009"), "amount_match", 0.0, ts),
        )

        ctx = investigation_context(self.b.store, run_id, self.b.ledger_id_for("JE009"))

        reviews = ctx["supporting_evidence"]["review_history"]
        self.assertTrue(reviews["available"])
        self.assertEqual(reviews["review_count"], 2)
        dispositions = [r["disposition"] for r in reviews["history"]]
        self.assertEqual(dispositions, ["follow_up", "cleared"])
        self.assertEqual(reviews["latest_disposition"], "cleared")
        self.assertEqual(reviews["history"][0]["note"], "Client support requested for round amount.")

        bank = ctx["supporting_evidence"]["bank"]
        self.assertTrue(bank["available"])
        self.assertEqual(bank["match_type"], "amount_match")
        self.assertEqual(bank["amount_diff"], 0.0)
        be = bank["bank_entry"]
        self.assertIsNotNone(be)
        self.assertEqual(be["bank_row"], 45)
        self.assertEqual(be["bank_date"], "2025-03-10")
        self.assertEqual(be["bank_narration"], "payment via bank")
        self.assertEqual(be["bank_source_hash"][:8], "banksha0")

        self.assertIn("governance", reviews)

    # --------------------------------------------------------------------
    # Case E -- unavailable / inapplicable / missing information
    # --------------------------------------------------------------------
    def test_caseE_unavailable_information(self) -> None:
        self.assertEqual(self.b.import_and_acknowledge(), 1)
        self.b.configure()
        run_id = self.b.run_analysis()

        ctx = investigation_context(self.b.store, run_id, self.b.ledger_id_for("JE022"))
        tx = ctx["transaction_line"]
        self.assertEqual(tx["signed_amount"], 0.00)

        dq = ctx["population_and_peers"]["data_quality"]
        self.assertIsInstance(dq["missing_preparer"], bool)
        self.assertIn("missing_narration", dq)
        self.assertIn("missing_vendor", dq)

        semantic = ctx["supporting_evidence"]["semantic"]
        self.assertFalse(semantic["available"])
        self.assertEqual(semantic["status"], "unavailable")
        self.assertIn("deterministic", semantic["note"].lower())

        bank = ctx["supporting_evidence"]["bank"]
        self.assertFalse(bank["available"])
        self.assertEqual(bank["status"], "not_applicable")

        ctx = investigation_context(self.b.store, run_id, self.b.ledger_id_for("JE019"))
        peers = ctx["population_and_peers"]
        self.assertTrue(peers["available"])
        peer_stats = peers["peer_statistics"]
        self.assertIsNotNone(peer_stats)
        self.assertEqual(peer_stats["population_count"], 4)

    # --------------------------------------------------------------------
    # Case F -- read-only invariants
    # --------------------------------------------------------------------
    def test_caseF_read_only_invariants(self) -> None:
        self.assertEqual(self.b.import_and_acknowledge(), 1)
        self.b.configure()
        run_id = self.b.run_analysis()
        ex = b.store.conn.execute(
            "SELECT id, ledger_id FROM exceptions WHERE id=(SELECT id FROM exceptions LIMIT 1)",
        ).fetchone()
        ledger_id = ex["ledger_id"]
        exception_id = ex["id"]

        def snapshot() -> dict:
            c = self.b.store.conn
            return {
                "audit_log": c.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0],
                "reviews": c.execute("SELECT COUNT(*) FROM reviews").fetchone()[0],
                "exceptions": c.execute("SELECT COUNT(*) FROM exceptions").fetchone()[0],
                "analysis_signal_results": c.execute(
                    "SELECT COUNT(*) FROM analysis_signal_results",
                ).fetchone()[0],
                "sample_sets": c.execute("SELECT COUNT(*) FROM sample_sets").fetchone()[0],
                "settings": c.execute("SELECT COUNT(*) FROM settings").fetchone()[0],
                "scores": [
                    {"ledger_id": r[0], "risk_score": r[1], "severity": r[2], "status": r[3]}
                    for r in c.execute(
                        "SELECT ledger_id, risk_score, severity, status FROM exceptions"
                    )
                ],
                "run_status": [
                    {"run_id": r[0], "status": r[1]}
                    for r in c.execute("SELECT id, status FROM model_runs")
                ],
            }

        before = snapshot()
        for _ in range(3):
            investigation_context(self.b.store, run_id, ledger_id)
        investigation_context(self.b.store, run_id, ledger_id, semantic_run_id=None)
        after = snapshot()
        self.assertEqual(before["audit_log"], after["audit_log"])
        self.assertEqual(before["reviews"], after["reviews"])
        self.assertEqual(before["exceptions"], after["exceptions"])
        self.assertEqual(before["analysis_signal_results"], after["analysis_signal_results"])
        self.assertEqual(before["sample_sets"], after["sample_sets"])
        self.assertEqual(before["settings"], after["settings"])
        self.assertEqual(before["scores"], after["scores"])
        self.assertEqual(before["run_status"], after["run_status"])

        revs = self.b.store.conn.execute(
            "SELECT COUNT(*) FROM reviews WHERE exception_id=?", (exception_id,),
        ).fetchone()[0]
        self.assertEqual(revs, 0)
        row = self.b.store.conn.execute(
            "SELECT risk_score, severity, status FROM exceptions WHERE id=?",
            (exception_id,),
        ).fetchone()
        self.assertIsNotNone(row)

    # --------------------------------------------------------------------
    # Case G -- FastAPI contract
    # --------------------------------------------------------------------
    def test_caseG_api_contract(self) -> None:
        self.assertEqual(self.b.import_and_acknowledge(), 1)
        self.b.configure()
        run_id = self.b.run_analysis()
        # Ensure any open transaction is committed so concurrent Store
        # connections to the same SQLite file do not deadlock.
        try:
            self.b.store.conn.execute("COMMIT")
        except Exception:
            pass
        base = str(self.b.db_path)
        client = TestClient(create_app(base))

        ledger_id = self.b.ledger_id_for("JE015")
        res = client.get(f"/api/investigation-context?run_id={run_id}&ledger_id={ledger_id}")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["investigation_context_version"], "v2")
        self.assertTrue(data["read_only"])
        self.assertIn("contract", data)
        self.assertEqual(data["contract"]["run_id"], run_id)
        self.assertEqual(data["contract"]["ledger_id"], ledger_id)
        self.assertIsNone(data["contract"]["semantic_run_id"])
        self.assertTrue(data["why_flagged"]["deterministic_evidence_available"])
        self.assertEqual(len(data["why_flagged"]["deterministic_reasons"]), 2)

        # Valid but unflagged population member returns 200 with no cues.
        res = client.get(f"/api/investigation-context?run_id={run_id}&ledger_id={self.b.ledger_id_for('JE022')}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["why_flagged"]["deterministic_reasons"], [])

        self.assertEqual(client.get("/api/investigation-context").status_code, 422)
        self.assertEqual(client.get(f"/api/investigation-context?run_id={run_id}").status_code, 422)
        self.assertEqual(client.get(f"/api/investigation-context?run_id=-1&ledger_id={ledger_id}").status_code, 422)
        self.assertEqual(client.get(f"/api/investigation-context?run_id=0&ledger_id={ledger_id}").status_code, 422)
        self.assertEqual(client.get(f"/api/investigation-context?run_id=999999&ledger_id={ledger_id}").status_code, 404)
        self.assertEqual(client.get(f"/api/investigation-context?run_id={run_id}&ledger_id=999999").status_code, 404)
        self.assertEqual(client.get(f"/api/investigation-context?run_id={run_id}&ledger_id=12345").status_code, 404)
        self.assertEqual(client.get(f"/api/investigation-context?run_id={run_id}&ledger_id=12345").status_code, 404)

        stale_id, _ = _inject_semantic_fixture(self.b.store, {})
        self.b.store.conn.execute(
            "UPDATE semantic_runs SET provenance_json=? WHERE id=?",
            (json.dumps({**json.loads(self.b.store.conn.execute(
                "SELECT provenance_json FROM semantic_runs WHERE id=?", (stale_id,),
            ).fetchone()[0]), "population_hash": "stale-dummy"}), stale_id),
        )
        self.assertEqual(client.get(f"/api/investigation-context?run_id={run_id}&ledger_id={ledger_id}&semantic_run_id={stale_id}").status_code, 409)


class CueCatalogueTests(unittest.TestCase):
    """Procedure catalogue: canonical identifiers, unknown handling, empty/mixed."""

    def test_catalogue_keyed_by_canonical_cue_ids(self) -> None:
        self.assertIn("possible_reversal_within_30_days", PROCEDURE_CATALOGUE)
        for cue in DETERMINISTIC_CUES:
            self.assertIn(cue, PROCEDURE_CATALOGUE, cue)
        for cue in SEMANTIC_CUES:
            self.assertIn(cue, PROCEDURE_CATALOGUE, cue)
        for p in PROCEDURE_CATALOGUE.values():
            self.assertIn("cue_id", p)
            self.assertIn("suggested_next_step", p)
            self.assertIn("inspect_evidence", p)
            self.assertIn("audit_objective", p)
            self.assertTrue(p["non_conclusive"], p["cue_id"])

    def test_map_procedure_unknown_cue_returns_generic(self) -> None:
        p = _map_procedure("some_new_cue_id_not_yet_catalogued")
        self.assertTrue(p["unrecognized"])
        self.assertTrue(p["non_conclusive"])

    def test_match_procedures_empty_cues(self) -> None:
        from audit_analytics.investigation_context import _match_procedures
        self.assertEqual(_match_procedures([]), [])

    def test_procedure_fields_present(self) -> None:
        p = _map_procedure("possible_reversal_within_30_days")
        self.assertEqual(p["cue_id"], "possible_reversal_within_30_days")
        self.assertEqual(p["audit_objective"], "Completeness / cut-off.")
        self.assertIn("reversal", p["suggested_next_step"].lower())


if __name__ == "__main__":
    unittest.main()