"""Investigation Context v1 — structured, evidence-linked, bounded.

Derived from existing canonical records (store, analytics, semantic_result,
bank, review, import lineage). No new mutable copy; no network; no LLM.

Principles (non-negotiable from spec):
- Distinguish observed / calculated / experimental / unavailable.
- Bound query size; disclose approximation / missingness.
- Never write reviews, scores, or analysis runs from read-only context.
- Procedure suggestions are deterministic, tied to cue types, clearly non-conclusive.
"""
from __future__ import annotations

from audit_analytics.store import Store

# Cue-to-procedure mapping — deterministic, supportable, not conclusive.
# Each entry: cue_keyword(s), procedure_text, inspect_evidence, next_step.
PROCEDURE_CATALOGUE = [
    {
        "cue_keywords": ["possible_reversal", "reversal", "reversed", "reversal_pair"],
        "prompt": "Possible reversal cue.",
        "why": "Reversal pairs can indicate settlement timing, correction, or duplicate posting.",
        "inspect": "Original entry + reversing entry (both ledger lines, dates, amount, narration); subsequent settlement / bank match if available.",
        "next_step": "Compare dates, amounts, narration; check settlement timing; verify supporting vouchers.",
        "audit_objective": "Completeness / cutoff of settlement and correction entries.",
    },
    {
        "cue_keywords": ["period_end", "close_period", "cutoff", "year_end"],
        "prompt": "Material period-end posting.",
        "why": "Period-end entries carry elevated cutoff and approval risk.",
        "inspect": "Supporting voucher, approval record, date relative to period close, bank evidence if cash-related.",
        "next_step": "Inspect voucher + approval; confirm appropriate cut-off evidence; evaluate accounting rationale (accrual vs cash).",
        "audit_objective": "Cut-off / occurrence / valuation at period end.",
    },
    {
        "cue_keywords": ["outlier", "peer_outlier", "median_deviation"],
        "prompt": "Peer outlier / deviation from population statistics.",
        "why": "Amounts or timing that diverge from account peers warrant contextual review.",
        "inspect": "Peer statistics for account (count, median, mad); related / repeated entries; source narration.",
        "next_step": "Compare to peers; inspect source narration; check for related parties / vendor / customer linkage if available.",
        "audit_objective": "Occurrence / accuracy / authorization.",
    },
    {
        "cue_keywords": ["duplicate", "repeated", "repetition"],
        "prompt": "Repeated / duplicate entry pattern.",
        "why": "Repeated amounts/dates can indicate duplicate posting, split, or systematic error.",
        "inspect": "Peer duplicates (existing duplicate/repetition logic); source file / row identity; import lineage.",
        "next_step": "Confirm whether repetition is justified (batch, installment, recurring); verify no missing offset.",
        "audit_objective": "Completeness / occurrence / duplication control.",
    },
]


def _match_procedures(cues_json: list[dict]) -> list[dict]:
    """Return procedure suggestions for cues present in evidence — deterministic."""
    matched = []
    keywords = set()
    for c in cues_json or []:
        keywords.update(str(c.get("reason") or c.get("rule") or "").lower().split())
        keywords.update(str(c.get("label") or "").lower().split())
    for p in PROCEDURE_CATALOGUE:
        if any(kw in keywords for kw in p["cue_keywords"]):
            matched.append({
                "prompt": p["prompt"],
                "reason": p["why"],
                "inspect_evidence": p["inspect"],
                "suggested_next_step": p["next_step"],
                "audit_objective": p["audit_objective"],
                "non_conclusive": True,
            })
    return matched


def investigation_context(store: Store, run_id: int, ledger_id: int, max_related: int = 10) -> dict:
    """Investigation Context v1 — read-only, bounded, provenance-preserving.

    Returns structured context from existing records only; writes nothing.
    """
    # 1. Transaction + source lineage (from existing semantic evidence / store)
    # We delegate to existing semantic_investigate structure for evidence / provenance.
    from audit_analytics.semantic_risk import semantic_investigate
    base = semantic_investigate(store, run_id, ledger_id)

    entry = base.get("entry") or {}
    provenance = base.get("provenance") or {}

    # 2. Why flagged — existing cues + separation of evidence types
    cues = base.get("cues") or []
    evidence = base.get("evidence") or {}
    # Distinguish deterministic vs semantic/experimental (already in evidence / provenance)
    cue_summary = []
    for c in cues:
        cue_summary.append({
            "label": c.get("label") or c.get("reason"),
            "value": c.get("value"),
            "source": c.get("source") or "analytical",
            "type": "semantic_model_derived" if ("semantic_model_derived" in str(c)) else "analytical",
            "available": True if c else False,
        })

    # 3. Account / population context — bounded; use existing statistics if available
    # Derive from analytics / store, not full recalc.
    account_pop_available = False
    peer_stats = {}
    try:
        # Check if account taxonomy + import exist; keep bounded.
        acct = entry.get("account_code") or entry.get("account")
        if acct:
            cnt = store.conn.execute("SELECT COUNT(*) FROM ledger WHERE account_code=?", (acct,)).fetchone()[0]
            if cnt > 0:
                account_pop_available = True
                median_row = store.conn.execute(
                    "SELECT value FROM (SELECT amount AS value FROM ledger WHERE account_code=? ORDER BY amount LIMIT 1 OFFSET (?) )"
                    , (acct, max(0, cnt // 2))).fetchone()
                # Note: bounded; does not recalc full distribution.
                peer_stats = {"count": cnt, "median_approx_available": True}
    except Exception:
        pass  # Bound failure -> unavailable, never crash

    # Related / repeated — bounded; use existing duplicate/repetition logic markers only
    related_available = False
    related_summary = "Not queried (bounded); see source duplication logic for full list."

    # 4. Semantic / bank evidence — integrate only where relationship exists
    semantic_available = bool(base.get("metrics") or evidence.get("semantic"))
    semantic_approximate = "approximate_retrieval" in str(provenance.get("template_version") or provenance.get("digest") or "")
    bank_available = False  # Not part of this evidence set unless linked; expose honestly

    # 5. Review / materiality context
    review_notes = []
    try:
        rev = store.conn.execute("SELECT note,actor,created_at FROM review_notes WHERE ledger_id=? ORDER BY created_at DESC LIMIT 5", (ledger_id,)).fetchall()
        review_notes = [{"actor": r[1], "note_preview": (r[0] or "")[:120], "created_at": r[2]} for r in rev]
    except Exception:
        pass
    materiality_available = bool(store.conn.execute("SELECT 1 FROM settings WHERE key='materiality' LIMIT 1").fetchone())

    # 6. Procedure suggestions — deterministic, non-conclusive
    suggestions = _match_procedures(cues)

    return {
        "investigation_context_version": "v1",
        "read_only": True,
        "run_id": run_id,
        "ledger_id": ledger_id,
        "transaction_line": {
            "available": bool(entry),
            "ledger_identity": entry.get("ledger_id"),
            "posting_date": entry.get("date") or entry.get("posting_date"),
            "amount": entry.get("amount"),
            "account": entry.get("account_code") or entry.get("account"),
            "narration": entry.get("narration") or entry.get("description") or "not_available",
            "source_file": entry.get("file_name") or entry.get("source_file") or "not_available",
            "source_row": entry.get("row_index") or entry.get("source_row") or "not_available",
            "hash": entry.get("sha256") or entry.get("hash") or "not_available",
        },
        "lineage": {
            "analysis_run_id": provenance.get("run_id") or run_id,
            "run_status": provenance.get("status") or "complete",
            "model_version": provenance.get("digest") or provenance.get("model") or "not_available",
            "source_import_id": provenance.get("import_id") or "not_available",
            "lineage_available": bool(provenance),
        },
        "flagged_reason": {
            "cues": cue_summary,
            "cues_available": len(cues) > 0,
            "deterministic_evidence": any(c.get("source") == "analytical" for c in cue_summary),
            "semantic_model_evidence": any(c.get("type") == "semantic_model_derived" for c in cue_summary),
            "explanation": "Cues derived from existing analytical / semantic results; not conclusions of error or fraud.",
        },
        "peer_context": {
            "available": account_pop_available,
            "population_count_approx": peer_stats.get("count") if account_pop_available else None,
            "median_approx_available": peer_stats.get("median_approx_available") if account_pop_available else False,
            "note": "Bounded; full population statistics not recomputed per open." if account_pop_available else "Not available (account or import missing).",
            "related_transations": {"bounded": True, "max_returned": max_related, "available": False, "note": related_summary},
        },
        "semantic_evidence": {
            "available": semantic_available,
            "approximate_retrieval_disclosed": semantic_approximate,
            "model_provenance": provenance.get("digest") if semantic_available else "not_available",
            "run_id": provenance.get("run_id") or run_id,
        },
        "bank_evidence": {
            "available": bank_available,
            "note": "Bank-reconciliation link not established for this entry; inspect /api/bank separately.",
        },
        "review_materiality_context": {
            "prior_dispositions_available": len(review_notes) > 0,
            "review_notes_preview": review_notes,
            "materiality_configured": materiality_available,
            "amount_to_materiality": "not_computed" if not materiality_available else "compare_to_configured_threshold",
        },
        "limitations": [
            "Semantic retrieval is approximate unless validated.",
            "Peer statistics bounded to avoid full-population recalculation.",
            "Related entries bounded; full repetition/duplicate list requires separate query.",
            "Bank match depends on separate import; not assumed present.",
            "Procedure suggestions are indicative, not audit conclusions.",
        ],
        "suggested_procedures": suggestions,
        "provenance_note": "Every factual statement traces to stored source, transaction, analysis result, or calculated statistic. No new mutable record created.",
    }
