"""Reproducible risk-directed and random sample selection for review planning."""
from __future__ import annotations

import json
import random
import time

from .store import Store


def create_sample(store: Store, name: str, actor: str, run_id=None, risk_count=20, random_count=10, seed=1, random_min_amount=None):
    run_id = run_id or store.conn.execute("SELECT id FROM model_runs WHERE status='complete' ORDER BY id DESC LIMIT 1").fetchone()
    if not run_id: raise ValueError("no completed analysis run")
    run_id = run_id[0] if not isinstance(run_id, int) else run_id
    if risk_count < 0 or random_count < 0: raise ValueError("sample counts must be non-negative")
    # ponytail: bound the random coverage slice to a disclosed materiality gate.
    # Default to the configured performance materiality (0 = no bound).
    min_amt = random_min_amount if random_min_amount is not None else store.get_setting("materiality", {}).get("performance", 0) or 0
    method = {"risk_count": risk_count, "random_count": random_count, "seed": seed, "run_id": run_id, "random_min_amount": min_amt, "note": "Planning aid only; engagement team determines final sample and procedures."}
    cur = store.conn.execute("INSERT INTO sample_sets(run_id,name,method_json,created_at,created_by) VALUES(?,?,?,?,?)", (run_id, name, json.dumps(method, sort_keys=True), time.time(), actor))
    sample_id = cur.lastrowid; selected = set()
    # High risk is always retained. The risk-count cap applies to additional ranked cues.
    high = store.conn.execute("SELECT ledger_id FROM exceptions WHERE run_id=? AND severity='high' ORDER BY risk_score DESC,ledger_id", (run_id,)).fetchall()
    for row in high:
        selected.add(row[0]); store.conn.execute("INSERT INTO sample_items VALUES(?,?,?)", (sample_id, row[0], "high-risk exception"))
    ranked = store.conn.execute("SELECT ledger_id FROM exceptions WHERE run_id=? ORDER BY risk_score DESC,ledger_id", (run_id,)).fetchall()
    for row in ranked:
        if len(selected) >= len(high) + risk_count: break
        if row[0] not in selected:
            selected.add(row[0]); store.conn.execute("INSERT INTO sample_items VALUES(?,?,?)", (sample_id, row[0], "top ranked risk cue"))
    universe = [row[0] for row in store.conn.execute("SELECT id, signed_amount FROM ledger_entries") if row[0] not in selected and abs(row[1]) >= min_amt]
    rng = random.Random(seed)
    for ledger_id in rng.sample(universe, min(random_count, len(universe))):
        selected.add(ledger_id); store.conn.execute("INSERT INTO sample_items VALUES(?,?,?)", (sample_id, ledger_id, f"seeded random coverage selection (|amount|>={min_amt})"))
    store.log(actor, "create_sample", "sample_set", sample_id, {**method, "selected": len(selected)})
    store.conn.commit(); return sample_id, len(selected)
