from __future__ import annotations

import json
import math
import random
import statistics
import time
from collections import Counter, defaultdict
from datetime import date, timedelta

from .store import Store


def _median_mad(values):
    median = statistics.median(values)
    mad = statistics.median([abs(x - median) for x in values])
    return median, mad

def _benford(entries):
    numbers = [abs(e["signed_amount"]) for e in entries if abs(e["signed_amount"]) >= 1]
    if len(numbers) < 100: return {"applicable": False, "n": len(numbers), "reason": "requires at least 100 non-zero amounts"}
    observed = Counter(str(int(x)).lstrip("0")[0] for x in numbers if str(int(x)).lstrip("0"))
    expected = {str(i): math.log10(1 + 1 / i) for i in range(1, 10)}
    mad = sum(abs(observed[str(i)] / len(numbers) - expected[str(i)]) for i in range(1, 10)) / 9
    return {"applicable": True, "n": len(numbers), "mad": round(mad, 4), "flag": mad > 0.015,
            "note": "Population-level indicator only; it does not identify fraudulent entries."}

def _isolation_scores(entries, trees=40, seed=7):
    """Small deterministic isolation-style scorer; retains all data locally.

    ponytail: this is a compact random-cut forest, not a replacement for a
    governed ML platform; upgrade to a validated model registry when needed.
    """
    if len(entries) < 256: return {}
    amounts = [math.log1p(abs(e["signed_amount"])) for e in entries]
    account_counts, user_counts = Counter(e["account_code"] for e in entries), Counter(e["preparer"] or "" for e in entries)
    points = [(amounts[i], -math.log(account_counts[e["account_code"]] / len(entries)), -math.log(user_counts[e["preparer"] or ""] / len(entries))) for i, e in enumerate(entries)]
    rng = random.Random(seed); depths = [0.0] * len(entries)
    for _ in range(trees):
        active = list(range(len(entries))); depth = [0] * len(entries)
        while len(active) > 1:
            dim = rng.randrange(3); vals = [points[i][dim] for i in active]; lo, hi = min(vals), max(vals)
            if lo == hi: break
            cut = rng.uniform(lo, hi); left = [i for i in active if points[i][dim] < cut]; right = [i for i in active if points[i][dim] >= cut]
            if not left or not right: break
            for i in active: depth[i] += 1
            # Recursively isolate the smaller partition first; one cut per tree level keeps runtime bounded.
            active = left if len(left) <= len(right) else right
        for i in range(len(entries)): depths[i] += depth[i]
    max_depth = max(depths) or 1
    return {entries[i]["id"]: round(1 - depths[i] / max_depth, 3) for i in range(len(entries))}

def analyze(store: Store, actor="system", include_isolation=True, semantic_run_id=None):
    if not store.population_acknowledged(): raise ValueError("analysis blocked: acknowledge every GL import's accepted population and control totals first")
    entries = [dict(r) for r in store.conn.execute("SELECT * FROM ledger_entries ORDER BY id")]
    if not entries: raise ValueError("no GL entries imported")
    policy = store.get_setting("analysis_policy", {"round_amount_threshold": 1000, "period_end_days": 3, "outlier_robust_z": 3.5})
    cfg = {"tests": ["duplicate", "round_amount", "period_end", "weekend", "rare_account_user", "reversal", "robust_peer_outlier", "benford"], "isolation": include_isolation and len(entries) >= 256, "policy": policy, "materiality": store.get_setting("materiality", {})}
    semantic = {}
    if semantic_run_id is not None:
        from .semantic_risk import population_hash
        sr = store.conn.execute("SELECT * FROM semantic_runs WHERE id=?", (semantic_run_id,)).fetchone()
        if not sr or sr["status"] != "complete": raise ValueError("semantic run must exist and be complete")
        if sr["population_hash"] != population_hash(store): raise ValueError("semantic run is stale; rebuild the semantic profile")
        cfg["semantic"] = {"run_id": semantic_run_id, "provenance": json.loads(sr["provenance_json"]), "configuration": json.loads(sr["configuration_json"]), "score_contribution": 20}
        semantic = {r["ledger_id"]: dict(r) for r in store.conn.execute("SELECT * FROM semantic_results WHERE run_id=?", (semantic_run_id,))}
        if len(semantic) != len(entries): raise ValueError("semantic run has incomplete population results")
    run = store.conn.execute("INSERT INTO model_runs(started_at,configuration,population_count,status) VALUES(?,?,?,?)", (time.time(), json.dumps(cfg), len(entries), "running")).lastrowid
    reasons, evidence = defaultdict(list), defaultdict(dict)
    by_key = defaultdict(list); by_account = defaultdict(list); by_user_pair = Counter(); ref_key = defaultdict(list)
    for e in entries:
        amount = round(abs(e["signed_amount"]), 2); by_account[e["account_code"]].append(e)
        by_user_pair[(e["account_code"], e["preparer"] or "")]+=1
        if e["reference"]: by_key[(e["account_code"], e["reference"], amount)].append(e)
        by_key[(e["account_code"], e["posting_date"], amount, e["description"] or "")].append(e)
        ref_key[(e["account_code"], amount)].append(e)
    for group in by_key.values():
        if len(group) > 1:
            for e in group: reasons[e["id"]].append("duplicate_or_repeated_entry"); evidence[e["id"]]["duplicate_count"] = len(group)
    end = date.fromisoformat(store.engagement()["period_end"])
    fiscal_dates = []
    for d in store.get_setting("fiscal_calendar", []) or []:
        try: fiscal_dates.append(date.fromisoformat(d))
        except ValueError: continue
    window = int(policy.get("period_end_days", 3))
    try:
        taxonomy = {r["account_code"]: (r["account_type"], r["label"]) for r in store.conn.execute("SELECT account_code, account_type, label FROM account_taxonomy")}
    except Exception: taxonomy = {}
    # ponytail: fiscal match is a flat scan (calendars are tiny); taxonomy is prefetched once, failures degrade to untagged.
    for e in entries:
        eid, amount = e["id"], abs(e["signed_amount"]); posted = date.fromisoformat(e["posting_date"])
        threshold = float(policy.get("round_amount_threshold", 1000))
        if amount and amount >= threshold and amount % 1000 == 0: reasons[eid].append("round_amount")
        if posted >= end - timedelta(days=int(policy.get("period_end_days", 3))): reasons[eid].append("period_end_posting")
        if posted.weekday() >= 5: reasons[eid].append("weekend_posting")
        if by_user_pair[(e["account_code"], e["preparer"] or "")] <= 2: reasons[eid].append("rare_account_preparer_pair")
        if any(timedelta(0) <= posted - f <= timedelta(days=window) for f in fiscal_dates): reasons[eid].append("fiscal_period_end")
        try:
            if e["account_code"] in taxonomy:
                evidence[eid]["account_type"], evidence[eid]["account_label"] = taxonomy[e["account_code"]]
        except Exception: pass
        peer = [abs(x["signed_amount"]) for x in by_account[e["account_code"]]]
        if len(peer) >= 8:
            med, mad = _median_mad(peer)
            if mad and abs(amount-med)/(1.4826*mad) >= float(policy.get("outlier_robust_z", 3.5)):
                reasons[eid].append("robust_account_peer_outlier"); evidence[eid]["peer_median"] = round(med, 2); evidence[eid]["robust_z"] = round(abs(amount-med)/(1.4826*mad), 2)
        for other in ref_key[(e["account_code"], round(amount, 2))]:
            if other["id"] != eid and other["signed_amount"] * e["signed_amount"] < 0 and abs((date.fromisoformat(other["posting_date"])-posted).days) <= 30:
                reasons[eid].append("possible_reversal_within_30_days"); evidence[eid]["reversal_ledger_id"] = other["id"]; break
    benford = _benford(entries)
    if benford["applicable"] and benford["flag"]:
        for e in entries: evidence[e["id"]]["benford_population_indicator"] = benford
    isolation = _isolation_scores(entries) if cfg["isolation"] else {}
    for e in entries:
        iso = isolation.get(e["id"], 0)
        if iso >= 0.72: reasons[e["id"]].append("isolation_style_anomaly"); evidence[e["id"]]["isolation_score"] = iso
        deterministic_reasons = sorted(set(reasons[e["id"]]))
        deterministic_score = min(100, 20 * len(deterministic_reasons) + (15 if evidence[e["id"]].get("robust_z", 0) >= 5 else 0) + (15 if iso >= .85 else 0))
        semantic_cues = json.loads(semantic[e["id"]]["cues_json"]) if semantic else []
        if semantic:
            amount_mad = _median_mad([abs(x['signed_amount']) for x in by_account[e['account_code']]])[1] if len(by_account[e['account_code']]) >= 8 else 0
            signal_status = {
                'amount': 'flagged' if set(deterministic_reasons) & {'round_amount','robust_account_peer_outlier'} else 'not flagged',
                'robust_amount_peer': 'flagged' if 'robust_account_peer_outlier' in deterministic_reasons else 'not flagged' if amount_mad else 'not applicable',
                'timing': 'flagged' if set(deterministic_reasons) & {'period_end_posting','weekend_posting','fiscal_period_end'} else 'not flagged',
                'frequency': 'flagged' if 'rare_account_preparer_pair' in deterministic_reasons else 'not flagged',
            }
            reasons[e["id"]].extend(semantic_cues)
            evidence[e["id"]]["semantic"] = {"run_id": semantic_run_id, "metrics": json.loads(semantic[e["id"]]["metrics_json"]), "cues": semantic_cues, "evidence": json.loads(semantic[e["id"]]["evidence_json"])}
            evidence[e["id"]]["signal_components"] = {"status": signal_status, "deterministic_reasons": deterministic_reasons, "semantic_reasons": semantic_cues, "deterministic_score": deterministic_score, "semantic_contribution": 20 if semantic_cues else 0, "note": "Correlated semantic cues contribute once. Unflagged signals do not establish correctness."}
            store.conn.execute("INSERT OR REPLACE INTO analysis_signal_results(run_id, ledger_id, components_json) VALUES(?,?,?)", (run, e["id"], json.dumps(evidence[e["id"]]["signal_components"], sort_keys=True)))
        if not reasons[e["id"]]: continue
        score = min(100, deterministic_score + (20 if semantic_cues else 0))
        severity = "high" if score >= 70 else "medium" if score >= 40 else "low"
        # ponytail: materiality is a DISCLOSED planning label only — it never
        # changes the risk score or severity (IMPLEMENTATION_PLAN §8 1.1).
        mat = cfg["materiality"] or {}
        abs_amt = abs(e["signed_amount"])
        if not mat:
            band = "not_set"
        elif mat.get("overall") and abs_amt >= mat["overall"]:
            band = "above_overall"
        elif mat.get("performance") and abs_amt >= mat["performance"]:
            band = "above_performance"
        else:
            band = "below"
        store.conn.execute("INSERT INTO exceptions(run_id,ledger_id,risk_score,severity,reasons_json,evidence_json,materiality_band) VALUES(?,?,?,?,?,?,?)", (run, e["id"], score, severity, json.dumps(sorted(set(reasons[e["id"]]))), json.dumps(evidence[e["id"]], sort_keys=True), band))
    limitation = "Benford: " + (benford.get("note") or benford.get("reason", "not applicable"))
    if semantic_run_id is not None:
        provenance = cfg["semantic"]["provenance"]
        store.conn.execute("UPDATE model_runs SET model_name=?,validation_status=? WHERE id=?", (provenance.get("model"), provenance.get("validation_status", "unregistered"), run))
        limitation += "; Experimental semantic cues support investigation, not audit conclusions. Correlated semantic cues contribute at most 20 points."
    store.conn.execute("UPDATE model_runs SET completed_at=?,status='complete',limitation_note=? WHERE id=?", (time.time(), limitation, run))
    store.log(actor, "analyze", "model_run", run, {"population": len(entries), "benford": benford, "isolation_enabled": bool(isolation)})
    store.conn.commit(); return run
