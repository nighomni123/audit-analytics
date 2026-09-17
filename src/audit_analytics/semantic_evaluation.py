"""Offline evaluation of a stored semantic run against authorised labels.

Experimental mechanics check only; never promotes registry validation or
audit conclusions.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import struct
import time
import tracemalloc

KNOWN_RISKS = {"routine", "mismatch", "vendor_shift", "novel", "outlier", "negative", "sparse"}
REVIEWER_LABELS = {"positive", "negative", "unlabelled"}
MISMATCH_RISKS = {"mismatch"}


def _json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _unpack(blob: bytes, dims: int) -> list[float]:
    if len(blob) != 4 * dims:
        raise ValueError("corrupt semantic vector dimensions")
    values = list(struct.unpack("<" + "f" * dims, blob))
    if (not values or any(isinstance(v, bool) or not isinstance(v, float | int)
                           or not math.isfinite(v) for v in values)):
        raise ValueError("semantic vector must contain finite numeric values")
    norm = math.sqrt(sum(v * v for v in values))
    if not norm or not math.isfinite(norm):
        raise ValueError("semantic vector must have finite nonzero norm")
    return values


def _cosine(a: list[float], b: list[float]) -> float:
    denom = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(x * x for x in b))
    if not denom or not math.isfinite(denom):
        raise ValueError("cosine requires finite nonzero norms")
    return max(-1.0, min(1.0, sum(x * y for x, y in zip(a, b)) / denom))


def _resolve(entries, transaction_id: str, ledger_id: str | None) -> int:
    matches = [lid for lid, entry in entries.items() if entry.get('entry_id') == transaction_id]
    if ledger_id not in (None, ''):
        try: lid = int(ledger_id)
        except ValueError: raise ValueError(f'invalid ledger_id for {transaction_id!r}')
        if lid not in matches: raise ValueError('ledger_id and transaction_id must identify the same run snapshot')
        return lid
    if not matches: raise ValueError(f'unknown transaction_id {transaction_id!r} in run snapshot')
    if len(matches)>1: raise ValueError(f'ambiguous transaction_id {transaction_id!r}: supply ledger_id')
    return matches[0]


def evaluate_semantic(store, run_id: int, labels_path: str, actor: str = "system") -> dict:
    """Evaluate a completed semantic run against a labels CSV. No registry writes."""
    if isinstance(run_id, bool) or not isinstance(run_id, int) or run_id <= 0:
        raise ValueError("run must be a positive integer")
    started = time.time()
    tracing = not tracemalloc.is_tracing()
    if tracing:
        tracemalloc.start()
    try:
        run = store.conn.execute("SELECT * FROM semantic_runs WHERE id=?", (run_id,)).fetchone()
        if not run:
            raise LookupError("semantic run not found")
        if run["status"] != "complete":
            raise ValueError("semantic run is not complete")
        config = json.loads(run["configuration_json"])
        provenance = json.loads(run["provenance_json"])
        with open(labels_path, newline="", encoding="utf-8") as fh:
            raw_text = fh.read()
        rows = list(csv.DictReader(raw_text.splitlines()))
        required = {"transaction_id", "expected_related_group", "expected_process",
                    "known_risk", "reviewer_label"}
        if not rows or not required <= set(rows[0] or {}):
            raise ValueError("labels must include transaction_id,expected_related_group,"
                             "expected_process,known_risk,reviewer_label")
        entries = {r['ledger_id']: json.loads(r['evidence_json']).get('entry', {}) for r in store.conn.execute('SELECT ledger_id,evidence_json FROM semantic_results WHERE run_id=?', (run_id,))}
        labels: dict[int, dict] = {}
        for line in rows:
            tid = (line.get("transaction_id") or "").strip()
            if not tid:
                raise ValueError("labels contain a missing transaction_id")
            lid = _resolve(entries, tid, (line.get("ledger_id") or "").strip() or None)
            if lid in labels:
                raise ValueError(f"duplicate label for ledger_id {lid}")
            risk = (line.get("known_risk") or "").strip()
            review = (line.get("reviewer_label") or "").strip()
            if risk not in KNOWN_RISKS:
                raise ValueError(f"unknown known_risk {risk!r}")
            if review not in REVIEWER_LABELS:
                raise ValueError(f"unknown reviewer_label {review!r}")
            group = [g.strip() for g in (line.get("expected_related_group") or "").split(";")
                     if g.strip()]
            labels[lid] = {"transaction_id": tid, "expected_related_group": group,
                           "expected_process": (line.get("expected_process") or "").strip(),
                           "known_risk": risk, "reviewer_label": review}
        # Resolve group members (transaction_ids -> ledger ids; unknown members rejected).
        for lid, lab in labels.items():
            members = []
            for member in lab["expected_related_group"]:
                member_id = _resolve(entries, member, None)
                if member_id != lid: members.append(member_id)
            lab["group_ids"] = sorted(set(members))
        profiles = store.conn.execute(
            "SELECT ledger_id,dims,vector,metadata_json FROM semantic_profiles"
            " WHERE run_id=? AND kind='transaction'", (run_id,)).fetchall()
        vectors: dict[int, list[float]] = {}
        for row in profiles:
            vectors[row["ledger_id"]] = _unpack(row["vector"], row["dims"])
        if not vectors:
            raise ValueError("semantic run has no transaction vectors")
        dims = {row["dims"] for row in profiles}
        if len(dims) != 1:
            raise ValueError("semantic run vectors disagree on dimensions")
        results = {r["ledger_id"]: {"cues": json.loads(r["cues_json"]),
                                    "cluster_id": r["cluster_id"],
                                    "metrics": json.loads(r["metrics_json"])}
                   for r in store.conn.execute(
                       "SELECT ledger_id,cluster_id,cues_json,metrics_json FROM semantic_results"
                       " WHERE run_id=?", (run_id,))}
        precisions, recalls, short_p = [], [], 0
        unlabelled = sum(1 for lab in labels.values()
                         if lab["reviewer_label"] == "unlabelled" or not lab["group_ids"])
        for lid, lab in labels.items():
            if not lab["group_ids"] or lab["reviewer_label"] == "unlabelled" \
                    or lid not in vectors:
                continue
            ranked = sorted(((_cosine(vectors[lid], vectors[other]), other)
                             for other in vectors if other != lid), key=lambda pair: (-pair[0], pair[1]))
            top10 = [o for _, o in ranked[:10]]
            top20 = [o for _, o in ranked[:20]]
            want = set(lab["group_ids"]) & set(vectors)
            if not want or not top10: continue
            precisions.append(len(want & set(top10)) / len(top10))
            recalls.append(len(want & set(top20)) / len(want))
            if len(top10) < 10:
                short_p += 1
        # Cue false positives on negatives.
        negatives = [lid for lid, lab in labels.items() if lab["reviewer_label"] == "negative"]
        fp = sum(1 for lid in negatives if results.get(lid, {}).get("cues"))
        # Applicable mismatch precision/recall.
        eligible_mismatch = {lid for lid, lab in labels.items() if lab['reviewer_label'] != 'unlabelled' and lid in vectors and all(results.get(lid, {}).get('metrics', {}).get(k) is not None for k in ('peer_similarity','cross_account_similarity'))}
        applicable = [lid for lid, lab in labels.items() if lid in eligible_mismatch and lab["known_risk"] in MISMATCH_RISKS]
        predicted = {lid for lid, res in results.items()
                     if lid in eligible_mismatch and "semantic_account_mismatch" in res["cues"]}
        tp = len(set(applicable) & predicted)
        mismatch = {"applicable_count": len(applicable),
                    "predicted_count": len(predicted & set(labels)),
                    "precision": (tp / len(predicted & set(labels))
                                  if predicted & set(labels) else None),
                    "recall": (tp / len(applicable) if applicable else None)}
        # Cluster purity over labelled items with a known process.
        clusters: dict[int | None, list[str]] = {}
        for lid, lab in labels.items():
            if lid not in vectors or results.get(lid, {}).get('cluster_id') is None or lab["reviewer_label"] == "unlabelled" or not lab["expected_process"]:
                continue
            clusters.setdefault(results.get(lid, {}).get("cluster_id"), []).append(
                lab["expected_process"])
        purity_num = sum(max(g.values()) for g in
                         (__import__("collections").Counter(v) for v in clusters.values()) if g)
        purity_den = sum(len(v) for v in clusters.values())
        report = {
            "run_id": run_id, "labelled_count": len(labels),
            "macro_precision_at_10": (sum(precisions) / len(precisions)
                                      if precisions else None),
            "macro_recall_at_20": sum(recalls) / len(recalls) if recalls else None,
            "retrieval_method": "Exact cosine descending, ties by ledger ID; self excluded. Precision denominator is returned top-10 count, recall denominator eligible listed relevant IDs. Unlabelled candidates remain ranked but are not presumed relevant.",
            "profile_runtime_seconds": json.loads(run['summary_json']).get('runtime_seconds'),
            "false_positive_rate": fp / len(negatives) if negatives else None,
            "precision_denominator": len(precisions),
            "recall_denominator": len(recalls),
            "short_denominator_count": short_p, "unlabelled_count": unlabelled,
            "false_positives_on_negatives": fp, "negative_count": len(negatives),
            "mismatch": mismatch,
            "cluster_purity": purity_num / purity_den if purity_den else None,
            "cluster_purity_numerator": purity_num, "cluster_purity_denominator": purity_den,
            "runtime_seconds": time.time() - started,
            "peak_python_bytes": tracemalloc.get_traced_memory()[1],
            "peak_note": "Peak Python allocation only; excludes Ollama/native memory.",
            "model_digest": provenance.get("digest"), "config": config,
            "config_hash": _sha(_json(config)), "label_hash": _sha(raw_text),
            "limitation": ("Offline mechanics check on authorised labels; "
                           "not audit validation or model quality proof."),
        }
        store.log(actor, "semantic_evaluate", "semantic_run", run_id,
                  {"label_hash": report["label_hash"], "config_hash": report["config_hash"],
                   "labelled_count": len(labels)})
        store.conn.commit()
        return report
    finally:
        if tracing:
            tracemalloc.stop()
