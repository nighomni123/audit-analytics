from __future__ import annotations

import json
import math
import random
import statistics
import time
from collections import Counter, defaultdict
from datetime import date, timedelta

from .store import Store


ISOLATION_VERSION = "isolation-style-random-cut-v1"
ISOLATION_SEED = 7
ISOLATION_TREES = 40
ISOLATION_MIN_POPULATION = 256


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

def _isolation_scores(entries, trees=ISOLATION_TREES, seed=ISOLATION_SEED):
    """Small deterministic isolation-style scorer; retains all data locally.

    ponytail: this is a compact random-cut forest, not a replacement for a
    governed ML platform; upgrade to a validated model registry when needed.
    """
    if len(entries) < ISOLATION_MIN_POPULATION: return {}
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

def _calculate_signals(entries, policy, period_end, fiscal_calendar, taxonomy, include_isolation):
    """Calculate deterministic evidence without reading or writing persistence."""
    reasons, evidence = defaultdict(list), defaultdict(dict)
    by_key = defaultdict(list)
    by_account = defaultdict(list)
    by_user_pair = Counter()
    ref_key = defaultdict(list)
    for entry in entries:
        amount = round(abs(entry["signed_amount"]), 2)
        by_account[entry["account_code"]].append(entry)
        if entry["account_code"] and entry["preparer"]:
            by_user_pair[(entry["account_code"], entry["preparer"])] += 1
        if entry["reference"]:
            by_key[(entry["account_code"], entry["reference"], amount)].append(entry)
        by_key[(entry["account_code"], entry["posting_date"], amount, entry["description"] or "")].append(entry)
        ref_key[(entry["account_code"], amount)].append(entry)
    for group in by_key.values():
        if len(group) > 1:
            for entry in group:
                reasons[entry["id"]].append("duplicate_or_repeated_entry")
                evidence[entry["id"]]["duplicate_count"] = len(group)
    fiscal_dates = []
    for value in fiscal_calendar or []:
        try:
            fiscal_dates.append(date.fromisoformat(value))
        except ValueError:
            continue
    window = int(policy.get("period_end_days", 3))
    for entry in entries:
        ledger_id = entry["id"]
        amount = abs(entry["signed_amount"])
        posted = date.fromisoformat(entry["posting_date"])
        threshold = float(policy.get("round_amount_threshold", 1000))
        if amount and amount >= threshold and amount % 1000 == 0:
            reasons[ledger_id].append("round_amount")
        if posted >= period_end - timedelta(days=int(policy.get("period_end_days", 3))):
            reasons[ledger_id].append("period_end_posting")
        if posted.weekday() >= 5:
            reasons[ledger_id].append("weekend_posting")
        if not entry["account_code"] or not entry["preparer"]:
            evidence[ledger_id]["rare_account_preparer_pair_applicability"] = "not_applicable_missing_identity"
        elif by_user_pair[(entry["account_code"], entry["preparer"])] <= 2:
            reasons[ledger_id].append("rare_account_preparer_pair")
        if any(timedelta(0) <= fiscal_date - posted <= timedelta(days=window) for fiscal_date in fiscal_dates):
            reasons[ledger_id].append("fiscal_period_end")
        if entry["account_code"] in taxonomy:
            evidence[ledger_id]["account_type"], evidence[ledger_id]["account_label"] = taxonomy[entry["account_code"]]
        peer = [abs(peer_entry["signed_amount"]) for peer_entry in by_account[entry["account_code"]]]
        if len(peer) >= 8:
            median, mad = _median_mad(peer)
            if mad and abs(amount - median) / (1.4826 * mad) >= float(policy.get("outlier_robust_z", 3.5)):
                reasons[ledger_id].append("robust_account_peer_outlier")
                evidence[ledger_id]["peer_median"] = round(median, 2)
                evidence[ledger_id]["robust_z"] = round(abs(amount - median) / (1.4826 * mad), 2)
        for other in ref_key[(entry["account_code"], round(amount, 2))]:
            if other["id"] != ledger_id and other["signed_amount"] * entry["signed_amount"] < 0 and abs((date.fromisoformat(other["posting_date"]) - posted).days) <= 30:
                reasons[ledger_id].append("possible_reversal_within_30_days")
                evidence[ledger_id]["reversal_ledger_id"] = other["id"]
                break
    benford = _benford(entries)
    if benford["applicable"] and benford["flag"]:
        for entry in entries:
            evidence[entry["id"]]["benford_population_indicator"] = benford
    isolation = _isolation_scores(entries) if include_isolation else {}
    for entry in entries:
        score = isolation.get(entry["id"], 0)
        if score >= 0.72:
            reasons[entry["id"]].append("isolation_style_anomaly")
            evidence[entry["id"]]["isolation_score"] = score
    return reasons, evidence, benford, isolation, by_account


def analyze(store: Store, actor="system", include_isolation=True, semantic_run_id=None):
    if not store.population_acknowledged(): raise ValueError("analysis blocked: acknowledge every GL import's accepted population and control totals first")
    entries = [dict(r) for r in store.conn.execute("SELECT * FROM ledger_entries ORDER BY id")]
    if not entries: raise ValueError("no GL entries imported")
    policy = store.get_setting("analysis_policy", {"round_amount_threshold": 1000, "period_end_days": 3, "outlier_robust_z": 3.5})
    isolation_enabled = bool(include_isolation and len(entries) >= ISOLATION_MIN_POPULATION)
    cfg = {
        "tests": ["duplicate", "round_amount", "period_end", "weekend", "rare_account_user", "reversal", "robust_peer_outlier", "benford"],
        "isolation": isolation_enabled,
        "model_components": {
            "deterministic_rules": {"version": "deterministic-rules-v1"},
            "isolation_style": {
                "version": ISOLATION_VERSION,
                "enabled": isolation_enabled,
                "seed": ISOLATION_SEED,
                "trees": ISOLATION_TREES,
                "minimum_population": ISOLATION_MIN_POPULATION,
                "validation_status": "experimental",
            },
        },
        "policy": policy,
        "materiality": store.get_setting("materiality", {}),
    }
    semantic = {}
    if semantic_run_id is not None:
        from .semantic_risk import population_hash
        sr = store.conn.execute("SELECT * FROM semantic_runs WHERE id=?", (semantic_run_id,)).fetchone()
        if not sr or sr["status"] != "complete": raise ValueError("semantic run must exist and be complete")
        if sr["population_hash"] != population_hash(store): raise ValueError("semantic run is stale; rebuild the semantic profile")
        semantic_summary = json.loads(sr["summary_json"] or "{}")
        cfg["semantic"] = {"run_id": semantic_run_id, "provenance": json.loads(sr["provenance_json"]), "configuration": json.loads(sr["configuration_json"]), "retrieval": semantic_summary.get("retrieval"), "score_contribution": 20}
        semantic = {r["ledger_id"]: dict(r) for r in store.conn.execute("SELECT * FROM semantic_results WHERE run_id=?", (semantic_run_id,))}
        if len(semantic) != len(entries): raise ValueError("semantic run has incomplete population results")
    run = store.conn.execute("INSERT INTO model_runs(started_at,configuration,population_count,status) VALUES(?,?,?,?)", (time.time(), json.dumps(cfg), len(entries), "running")).lastrowid
    try:
        taxonomy = {row["account_code"]: (row["account_type"], row["label"]) for row in store.conn.execute("SELECT account_code, account_type, label FROM account_taxonomy")}
    except Exception:
        taxonomy = {}
    reasons, evidence, benford, isolation, by_account = _calculate_signals(
        entries,
        policy,
        date.fromisoformat(store.engagement()["period_end"]),
        store.get_setting("fiscal_calendar", []),
        taxonomy,
        isolation_enabled,
    )
    for e in entries:
        iso = isolation.get(e["id"], 0)
        deterministic_reasons = sorted(set(reasons[e["id"]]))
        deterministic_score = min(100, 20 * len(deterministic_reasons) + (15 if evidence[e["id"]].get("robust_z", 0) >= 5 else 0) + (15 if iso >= .85 else 0))
        semantic_cues = json.loads(semantic[e["id"]]["cues_json"]) if semantic else []
        if semantic:
            amount_mad = _median_mad([abs(x['signed_amount']) for x in by_account[e['account_code']]])[1] if len(by_account[e['account_code']]) >= 8 else 0
            signal_status = {
                'amount': 'flagged' if set(deterministic_reasons) & {'round_amount','robust_account_peer_outlier'} else 'not flagged',
                'robust_amount_peer': 'flagged' if 'robust_account_peer_outlier' in deterministic_reasons else 'not flagged' if amount_mad else 'not applicable',
                'timing': 'flagged' if set(deterministic_reasons) & {'period_end_posting','weekend_posting','fiscal_period_end'} else 'not flagged',
                'frequency': 'not applicable' if (not e['account_code'] or not e['preparer']) else 'flagged' if 'rare_account_preparer_pair' in deterministic_reasons else 'not flagged',
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
        model_name = provenance.get("model") or "semantic-risk-v1"
        validation_status = provenance.get("validation_status", "unregistered")
        limitation += "; Experimental semantic cues support investigation, not audit conclusions. Correlated semantic cues contribute at most 20 points."
    elif isolation_enabled:
        model_name = ISOLATION_VERSION
        validation_status = "experimental"
    else:
        model_name = "deterministic-rules-v1"
        validation_status = "rules-only"
    if isolation_enabled:
        limitation += f"; {ISOLATION_VERSION} is an experimental random-cut ranking aid, not a standard Isolation Forest or validated audit model."
    store.conn.execute(
        """UPDATE model_runs SET completed_at=?,status='complete',limitation_note=?,model_name=?,validation_status=?
           WHERE id=?""",
        (time.time(), limitation, model_name, validation_status, run),
    )
    store.log(actor, "analyze", "model_run", run, {"population": len(entries), "benford": benford, "isolation_enabled": bool(isolation), "model_name": model_name, "validation_status": validation_status})
    store.conn.commit()
    return run
