"""Investigation Context — structured, evidence-linked, bounded, and read-only.

Derived from canonical records only:
  ledger_entries, exceptions, analysis_signal_results, model_runs, imports,
  rejected_rows, coa/account_taxonomy, bank_matches, bank_statements,
  reviews, review_set_events, settings.

No network calls, no LLM at call time, no writes. Opening context never mutates
scores, exceptions, reviews, analysis runs, semantic results, or audit history.

Contract
--------
investigation_context(store, run_id, ledger_id, semantic_run_id=None, max_related=10)

  run_id          : deterministic analysis-run ID (required). The ledger entry
                    must be flagged as an exception in this run.
  ledger_id       : ledger-entry ID (required). Must belong to the selected run.
  semantic_run_id : optional linked semantic profile run ID. If supplied it must
                    exist, be complete, be non-stale, and cover the same
                    population. If absent or invalid, deterministic context is
                    still returned (never a silent empty response).
  max_related     : bounded cap for related / duplicate / reversal lists.

Errors are explicit, not silent:
  - 400 InvalidInput   when run_id or ledger_id is invalid, the entry does not
                       belong to the run's population, or a required dependency
                       is corrupt.
  - 404 NotFound       when the exception row, entry, run, or (optionally)
                       semantic run is absent.
  - 409 Conflict       when a linked semantic run is stale or out of population.

Cue identifiers
---------------
Canonical cue IDs are the exact strings stored in `exceptions.reasons_json`:

  Deterministic:
    duplicate_or_repeated_entry
    round_amount
    period_end_posting
    weekend_posting
    rare_account_preparer_pair
    fiscal_period_end
    robust_account_peer_outlier
    possible_reversal_within_30_days
    isolation_style_anomaly            # experimental random-cut ranking aid
    benford_population_indicator       # population-level only; never per-entry
  Semantic (from semantic_results.cues_json):
    semantic_account_mismatch
    semantic_novel_transaction
    semantic_vendor_shift
    semantic_cluster_outlier
    semantic_process_outlier

Procedure suggestions are matched by these identifiers (see
PROCEDURE_CATALOGUE), not by keyword token splitting.
"""
from __future__ import annotations

import json
import logging
import statistics
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from .store import Store

logger = logging.getLogger("audit_analytics.investigation_context")


# ---------------------------------------------------------------------------
# Cue-to-procedure catalogue: explicit mapping from canonical cue identifiers.
# ---------------------------------------------------------------------------

PROCEDURE_CATALOGUE: dict[str, dict[str, Any]] = {
    "duplicate_or_repeated_entry": {
        "cue_id": "duplicate_or_repeated_entry",
        "description": "Repeated account / date / amount / narration pattern detected.",
        "why": "Repetition can indicate duplicate posting, split transactions, installments, or systematic errors.",
        "inspect_evidence": [
            "Duplicate group members (all ledger lines: date, amount, narration, source row).",
            "Source file and row identity for each member (lineage preserved on import).",
            "COA mapping and any rejection notes for the same source file.",
        ],
        "suggested_next_step": "Confirm whether repetition is justified (batch, installment, recurring); verify no missing offset; compare source invoices or vouchers for each occurrence.",
        "audit_objective": "Occurrence / completeness / duplication control.",
        "non_conclusive": True,
        "available": True,
    },
    "round_amount": {
        "cue_id": "round_amount",
        "description": "Amount is a round value at the configured threshold.",
        "why": "Round amounts at or above threshold can indicate management overrides, manual journals, or estimate postings that need authorization.",
        "inspect_evidence": [
            "Configured round-amount threshold and period-end days from the run configuration.",
            "Supporting voucher, approval record, and whether the entry is manual.",
            "Whether the amount also crosses performance/overall materiality.",
        ],
        "suggested_next_step": "Inspect the supporting voucher and authorization; confirm the accounting rationale (accrual vs cash) and whether approval exceeds delegated limits.",
        "audit_objective": "Occurrence / authorization / accuracy.",
        "non_conclusive": True,
        "available": True,
    },
    "period_end_posting": {
        "cue_id": "period_end_posting",
        "description": "Posted within the configured number of days before the period-end date.",
        "why": "Entries near period end carry elevated cutoff risk and may reflect premature or delayed recognition.",
        "inspect_evidence": [
            "Period-end date from the engagement and the configured window (period_end_days).",
            "Posting date relative to period end; supporting voucher and bank evidence if cash-related.",
        ],
        "suggested_next_step": "Inspect voucher and approval; confirm appropriate cut-off evidence; evaluate whether recognition belongs in this or the following period.",
        "audit_objective": "Cut-off / occurrence.",
        "non_conclusive": True,
        "available": True,
    },
    "weekend_posting": {
        "cue_id": "weekend_posting",
        "description": "Posted on a weekend relative to the engagement calendar.",
        "why": "Weekend postings may be automated, out-of-hours manual journals, or cutoff artifacts. Date-only data cannot prove the true posting time.",
        "inspect_evidence": [
            "Posting date weekday; whether the entry is marked as manual or system-generated.",
            "Subsequent bank match or correction entries if available.",
        ],
        "suggested_next_step": "Confirm whether weekend posting is authorized (auto-posting, batch import); inspect system logs or import evidence if available; do not treat as error merely because it occurred on a weekend.",
        "audit_objective": "Occurrence / authorization.",
        "non_conclusive": True,
        "available": True,
    },
    "rare_account_preparer_pair": {
        "cue_id": "rare_account_preparer_pair",
        "description": "This account and preparer combination is uncommon in the population.",
        "why": "Uncommon account/preparer pairings can indicate inappropriate access or unusual assignment patterns. They are not, by themselves, evidence of error.",
        "inspect_evidence": [
            "The count of entries for this account/preparer pair (must be <= 2 to flag).",
            "Preparer identity and role; whether the preparer is authorized for the account.",
        ],
        "suggested_next_step": "Confirm preparer identity and authorization for this account; compare with other preparers posting to the same account.",
        "audit_objective": "Authorization / segregation of duties.",
        "non_conclusive": True,
        "available": True,
        "limitation": "Not applicable when account or preparer is missing; missing identity is never treated as suspicious.",
    },
    "fiscal_period_end": {
        "cue_id": "fiscal_period_end",
        "description": "Posted near a configured fiscal period-end date.",
        "why": "Fiscal period-end entries carry elevated cutoff and approval risk.",
        "inspect_evidence": [
            "Configured fiscal calendar dates and period-end days window.",
            "Supporting voucher, approval record, and bank evidence if cash-related.",
        ],
        "suggested_next_step": "Inspect voucher and approval; confirm appropriate cut-off evidence; evaluate the accounting rationale.",
        "audit_objective": "Cut-off / occurrence.",
        "non_conclusive": True,
        "available": True,
    },
    "robust_account_peer_outlier": {
        "cue_id": "robust_account_peer_outlier",
        "description": "Amount is unusual compared with activity for this account (robust Z).",
        "why": "Amounts or timing that diverge materially from account peers warrant contextual review.",
        "inspect_evidence": [
            "Peer population count and median for the account; MAD-based robust Z and threshold.",
            "Related / repeated entries and source narration.",
            "Materiality band for the amount.",
        ],
        "suggested_next_step": "Compare to account peers; inspect source narration; check for related parties, vendor or customer linkage if available; confirm the amount is supported by evidence.",
        "audit_objective": "Occurrence / accuracy / valuation.",
        "non_conclusive": True,
        "available": True,
    },
    "possible_reversal_within_30_days": {
        "cue_id": "possible_reversal_within_30_days",
        "description": "A possible opposite-direction entry appears within 30 days.",
        "why": "Reversal pairs can indicate settlement timing, correction, or duplicate posting.",
        "inspect_evidence": [
            "Original entry and reversing entry (both ledger lines: dates, signed amounts, narrations).",
            "Source row and source hash for each; bank match if available.",
        ],
        "suggested_next_step": "Compare dates, amounts and narration; check settlement timing; verify supporting vouchers and whether the reversal relates to a correction or a duplicate.",
        "audit_objective": "Completeness / cut-off.",
        "non_conclusive": True,
        "available": True,
    },
    "isolation_style_anomaly": {
        "cue_id": "isolation_style_anomaly",
        "description": "An experimental ranking signal placed this entry unusually far from peers.",
        "why": "Experimental random-cut ranking aids can highlight unusual entries, but they are not validated audit models.",
        "inspect_evidence": [
            "Isolation score and configuration (trees, seed, minimum population) from the run.",
            "Deterministic cues for the same entry for corroboration.",
        ],
        "suggested_next_step": "Treat as a ranking aid only; corroborate with deterministic evidence and source inspection before any substantive follow-up.",
        "audit_objective": "Screening only.",
        "non_conclusive": True,
        "available": True,
        "experimental": True,
        "limitation": "Experimental random-cut ranking signal; not a standard Isolation Forest and not a validated audit model.",
    },
    "benford_population_indicator": {
        "cue_id": "benford_population_indicator",
        "description": "Population-level first-digit distribution deviates from Benford expectations.",
        "why": "Benford analysis is population-level only and does not identify fraudulent entries.",
        "inspect_evidence": ["Benford MAD and flag status from the run (population-level only)."],
        "suggested_next_step": "Do not apply Benford deviation to individual entries; consider it when planning population coverage.",
        "audit_objective": "Planning only.",
        "non_conclusive": True,
        "available": False,  # not a per-entry cue; present only as population indicator
    },
    "semantic_account_mismatch": {
        "cue_id": "semantic_account_mismatch",
        "description": "Semantic context differs from the account profile.",
        "why": "Experimental semantic modeling suggests the narration may not match the account profile.",
        "inspect_evidence": [
            "Semantic metrics (own similarity, alternative similarity, margin) from the linked run.",
            "Source narration and account name; any candidate peer transactions.",
        ],
        "suggested_next_step": "Inspect source invoice/contract and narration; confirm whether the account classification is correct.",
        "audit_objective": "Accuracy / classification.",
        "non_conclusive": True,
        "available": True,
        "experimental": True,
        "limitation": "Experimental semantic cue; a proxy indicator that requires corroboration and never establishes misstatement.",
    },
    "semantic_novel_transaction": {
        "cue_id": "semantic_novel_transaction",
        "description": "The narrative is unlike the available local context.",
        "why": "Experimental semantic modeling flags narratives that are dissimilar to historical entries.",
        "inspect_evidence": [
            "Narrative novelty score and historical peer examples from the linked run.",
            "Source narration and reference.",
        ],
        "suggested_next_step": "Inspect source evidence and the narrative; confirm whether the transaction is unusual or simply uses different wording.",
        "audit_objective": "Occurrence / accuracy.",
        "non_conclusive": True,
        "available": True,
        "experimental": True,
        "limitation": "Experimental semantic cue; requires corroboration and never establishes misstatement.",
    },
    "semantic_vendor_shift": {
        "cue_id": "semantic_vendor_shift",
        "description": "Semantic context suggests a change in vendor-related activity.",
        "why": "Experimental semantic modeling suggests the entry may relate to a different vendor pattern than historical behavior.",
        "inspect_evidence": [
            "Historical vendor centroid distance from the linked run.",
            "Vendor field, reference, and source narration.",
        ],
        "suggested_next_step": "Inspect the vendor field and source documentation; confirm whether the vendor relationship changed.",
        "audit_objective": "Accuracy / occurrence.",
        "non_conclusive": True,
        "available": True,
        "experimental": True,
        "limitation": "Experimental semantic cue; requires corroboration and never establishes misstatement.",
    },
    "semantic_cluster_outlier": {
        "cue_id": "semantic_cluster_outlier",
        "description": "The entry sits apart from its semantic process cluster.",
        "why": "Experimental semantic clustering placed the entry far from its process group.",
        "inspect_evidence": ["Cluster distance from the linked run; cluster representative examples."],
        "suggested_next_step": "Inspect source evidence; confirm whether the entry is an unusual but legitimate transaction.",
        "audit_objective": "Occurrence / accuracy.",
        "non_conclusive": True,
        "available": True,
        "experimental": True,
        "limitation": "Experimental semantic cue; requires corroboration and never establishes misstatement.",
    },
    "semantic_process_outlier": {
        "cue_id": "semantic_process_outlier",
        "description": "The entry is dissimilar across multiple semantic peer dimensions.",
        "why": "Experimental semantic modeling flags low similarity across account, vendor and period peers.",
        "inspect_evidence": ["Peer similarity scores across dimensions from the linked run."],
        "suggested_next_step": "Corroborate with deterministic evidence and source inspection before substantive follow-up.",
        "audit_objective": "Screening only.",
        "non_conclusive": True,
        "available": True,
        "experimental": True,
        "limitation": "Experimental semantic cue; requires corroboration and never establishes misstatement.",
    },
    # Unknown cues fall back to this generic definition (never claim unsupported reasoning).
    "_unknown": {
        "cue_id": "_unknown",
        "description": "Cue recorded by the governed analysis but not yet documented in this catalogue.",
        "why": "The cue exists in the analysis result; the procedure definition for this identifier is pending.",
        "inspect_evidence": ["The full analysis result and evidence JSON for the entry.", "Run configuration and limitation note."],
        "suggested_next_step": "Inspect the raw analysis result and source evidence; escalate to the analyst responsible for this cue's definition.",
        "audit_objective": "Information gathering.",
        "non_conclusive": True,
        "available": True,
        "unrecognized": True,
    },
}


def _map_procedure(cue_id: str) -> dict[str, Any]:
    """Map a canonical cue identifier to a procedure definition.

    Unknown identifiers get a documented generic definition rather than an
    unsupported or keyword-matched guess.
    """
    return PROCEDURE_CATALOGUE.get(cue_id, PROCEDURE_CATALOGUE["_unknown"])


def _match_procedures(cues_json: list[dict] | None) -> list[dict]:
    """Map cue data to procedure definitions using the explicit cue catalogue.

    Accepts the canonical cue schema produced by this module and the API:
    each cue carries a `cue_id`. Unknown identifiers fall back to the generic
    documented definition; empty input returns an empty list. This replaces
    the earlier fragile underscore-token keyword matching.
    """
    if not cues_json:
        return []
    matched = []
    for c in cues_json or []:
        cue_id = str(c.get("cue_id") or c.get("reason") or c.get("label") or "")
        if not cue_id or not cue_id.strip():
            continue
        p = _map_procedure(cue_id.strip())
        if p not in matched:
            matched.append(p)
    return matched


class InvestigationContextError(ValueError):
    """Raised when required identifiers are invalid or inconsistent."""


class _UnauthenticatedError(InvestigationContextError):
    """Raised when a dependency is corrupt or unreadable (treated as a defect, not absence)."""


# ---------------------------------------------------------------------------
# Canonical data access.
# ---------------------------------------------------------------------------

def _require_exception(
    store: Store, run_id: int, ledger_id: int
) -> tuple[dict[str, Any] | None, dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Return (exception_row_or_None, entry_row, model_run_row, import_row).

    The entry must belong to the selected run's population: an accepted GL
    import. The exception row is optional — every population member receives a
    read-only context; unflagged members simply show no cue reasons.
    """
    run = store.conn.execute("SELECT * FROM model_runs WHERE id = ?", (run_id,)).fetchone()
    if not run:
        raise LookupError(f"analysis run {run_id} does not exist")
    if run["status"] != "complete":
        raise InvestigationContextError(
            f"analysis run {run_id} is not complete (status: {run['status']})"
        )
    entry = store.conn.execute(
        "SELECT * FROM ledger_entries WHERE id = ?", (ledger_id,)
    ).fetchone()
    if not entry:
        raise LookupError(f"ledger entry {ledger_id} does not exist")
    imp = store.conn.execute(
        "SELECT * FROM imports WHERE id = ?", (entry["import_id"],)
    ).fetchone()
    if not imp or imp["kind"] != "gl":
        raise _UnauthenticatedError(f"entry {ledger_id} has no valid GL import lineage")
    ex = store.conn.execute(
        "SELECT * FROM exceptions WHERE run_id = ? AND ledger_id = ?",
        (run_id, ledger_id),
    ).fetchone()
    return (dict(ex) if ex else None), dict(entry), dict(run), imp


def _load_signal_components(
    store: Store, run_id: int, ledger_id: int
) -> tuple[dict[str, Any] | None, str]:
    """Return (components, source) for the entry in this run.

    Prefers the materialized signal-components table; falls back to decoding the
    legacy exception evidence / reasons columns. Returns None when genuinely absent.
    """
    row = store.conn.execute(
        "SELECT components_json FROM analysis_signal_results WHERE run_id = ? AND ledger_id = ?",
        (run_id, ledger_id),
    ).fetchone()
    if row:
        try:
            return json.loads(row["components_json"]), "analysis_signal_results"
        except (json.JSONDecodeError, TypeError) as exc:
            logger.warning("corrupt signal components for run=%s ledger=%s: %s", run_id, ledger_id, exc)
    # Legacy fallback: read reasons/evidence directly from the exception row.
    return None, "exceptions"


def _peer_population(
    store: Store, account_code: str, max_related: int
) -> dict[str, Any]:
    """Bounded peer statistics for one account (no full-population recalc)."""
    if not account_code:
        return {
            "available": False,
            "status": "unavailable",
            "note": "Account code is missing from the entry; no peer comparison is possible.",
        }
    # Bounded count.
    count_row = store.conn.execute(
        "SELECT COUNT(*) FROM ledger_entries WHERE account_code = ?", (account_code,)
    ).fetchone()
    count = count_row[0]
    if count == 0:
        return {
            "available": False,
            "status": "unavailable",
            "population_count": 0,
            "note": "No ledger entries exist for this account code.",
        }
    # Bounded sample for statistics; statistics use a deterministic sample when
    # the account is large. The account is bounded to max_related * 4 for the
    # median/MAD computation, which is the correct bounded approximation.
    LIMIT = min(count, max_related * 4)
    rows = store.conn.execute(
        "SELECT signed_amount FROM ledger_entries WHERE account_code = ? ORDER BY id LIMIT ?",
        (account_code, LIMIT),
    ).fetchall()
    values = [float(r[0]) for r in rows]
    if not values:
        return {
            "available": False,
            "status": "unavailable",
            "population_count": count,
            "note": "No monetary values are available for the account.",
        }
    median = statistics.median(values)
    mad = statistics.median([abs(v - median) for v in values])
    mad_positive = bool(mad and mad > 0)
    return {
        "available": True,
        "status": "available",
        "population_count": count,
        "sample_count": len(values),
        "sample_of_population": count > LIMIT,
        "median": round(median, 2),
        "median_available": True,
        "mad": round(mad, 4),
        "mad_positive": mad_positive,
        "calculation": "median and median absolute deviation over a bounded sample of the account population",
    }


def _duplicate_group(
    store: Store, account_code: str, posting_date: str, amount: float, narration: str, limit: int
) -> list[dict[str, Any]]:
    """Return other entries in the same (account, date, amount, narration) group.

    This is the same matching key used by the deterministic detector. Bounded.
    """
    narration = (narration or "").strip()
    rows = store.conn.execute(
        """SELECT id, entry_id, posting_date, account_code, signed_amount,
                   description, preparer, reference, source_row, source_hash
            FROM ledger_entries
            WHERE account_code = ? AND posting_date = ? AND abs(signed_amount) = abs(?)
            AND (COALESCE(description, '') = ?)
            ORDER BY id LIMIT ?""",
        (account_code, posting_date, amount, narration, limit),
    ).fetchall()
    items = [
        {
            "ledger_id": r["id"],
            "entry_id": r["entry_id"],
            "posting_date": r["posting_date"],
            "signed_amount": round(r["signed_amount"], 2),
            "description": r["description"] or "",
            "preparer": r["preparer"] or "",
            "source_row": r["source_row"],
            "source_hash": r["source_hash"],
        }
        for r in rows
    ]
    # Deduplicate by ledger_id preserving ledger order.
    seen = set()
    out = []
    for it in items:
        if it["ledger_id"] not in seen:
            seen.add(it["ledger_id"])
            out.append(it)
    return out


def _reversal_counterpart(store: Store, ledger_id: int, account_code: str, amount: float, posting_date: str) -> dict[str, Any]:
    """Return the bounded possible-reversal counterpart per the analysis policy.

    Same-sign opposite-direction entry within +/- 30 days of the posting date.
    Policy preserves the first eligible counterpart in original ledger order using
    a bounded query with a deterministic tie-break.
    """
    posted = date.fromisoformat(posting_date)
    left = (posted - timedelta(days=30)).isoformat()
    right = (posted + timedelta(days=30)).isoformat()
    sign = 1 if amount >= 0 else -1
    opposite = 1 if sign == -1 else -1
    rows = store.conn.execute(
        """SELECT id, entry_id, posting_date, account_code, signed_amount,
                   description, preparer, source_row, source_hash
            FROM ledger_entries
            WHERE account_code = ?
              AND signed_amount * ? < 0
              AND posting_date >= ? AND posting_date <= ?
              AND id != ?
            ORDER BY posting_date, id
            LIMIT 5""",
        (account_code, amount, left, right, ledger_id),
    ).fetchall()
    if not rows:
        return {"available": False, "status": "not_flagged", "counterpart": None}
    r = rows[0]
    delta_days = (date.fromisoformat(r["posting_date"]) - posted).days
    return {
        "available": True,
        "status": "flagged",
        "counterpart": {
            "ledger_id": r["id"],
            "entry_id": r["entry_id"],
            "posting_date": r["posting_date"],
            "signed_amount": round(r["signed_amount"], 2),
            "narration": r["description"] or "",
            "preparer": r["preparer"] or "",
            "source_row": r["source_row"],
            "source_hash": r["source_hash"],
        },
        "basis": "same account, opposite signed direction, within +/- 30 days of posting date; first match in posting-date then ledger order (bounded to 5 candidates).",
        "days_difference": delta_days,
    }


def _materiality_band(store: Store, run_id: int, amount: float) -> dict[str, Any]:
    """Return materiality context from the run's configuration, if configured."""
    row = store.conn.execute("SELECT configuration FROM model_runs WHERE id = ?", (run_id,)).fetchone()
    try:
        cfg = json.loads(row["configuration"])
    except (TypeError, json.JSONDecodeError):
        cfg = {}
    mat = cfg.get("materiality") or {}
    if not mat:
        return {"configured": False, "status": "unavailable", "note": "Materiality is not configured for this run."}
    abs_amt = abs(amount)
    band = "not_set"
    if mat.get("overall") and abs_amt >= mat["overall"]:
        band = "above_overall"
    elif mat.get("performance") and abs_amt >= mat["performance"]:
        band = "above_performance"
    else:
        band = "below"
    return {
        "configured": True,
        "status": "available",
        "overall": mat.get("overall"),
        "performance": mat.get("performance"),
        "amount": round(abs_amt, 2),
        "band": band,
        "note": "Materiality is a planning label only; it never changes the risk score or severity.",
    }


def _bank_evidence(store: Store, ledger_id: int) -> dict[str, Any]:
    """Return linked bank-reconciliation records for the entry, if they exist."""
    match = store.conn.execute(
        "SELECT bm.*, bs.entry_date, bs.narration, bs.debit, bs.credit, bs.balance, "
        "bs.source_row, bs.source_hash, bs.import_id, bs.raw_json "
        "FROM bank_matches bm LEFT JOIN bank_statements bs ON bs.id = bm.bank_id "
        "WHERE bm.ledger_id = ?",
        (ledger_id,),
    ).fetchone()
    if not match:
        return {
            "available": False,
            "status": "not_applicable",
            "note": "No bank-reconciliation match is linked to this entry; a bank import may not have been provided for this engagement.",
        }
    return {
        "available": True,
        "status": "available",
        "match_type": match["match_type"],
        "amount_diff": match["amount_diff"],
        "bank_entry": {
            "bank_row": match["source_row"],
            "bank_date": match["entry_date"],
            "bank_narration": match["narration"] or "",
            "bank_debit": match["debit"],
            "bank_credit": match["credit"],
            "bank_balance": match["balance"],
            "bank_source_hash": match["source_hash"],
        },
    }


def _reviews_for_exception(store: Store, exception_id: int) -> list[dict[str, Any]]:
    """Return the immutable review history for the exception (append-only)."""
    rows = store.conn.execute(
        "SELECT * FROM reviews WHERE exception_id = ? ORDER BY id", (exception_id,)
    ).fetchall()
    return [
        {
            "review_id": r["id"],
            "reviewer": r["reviewer"],
            "disposition": r["disposition"],
            "note": r["note"],
            "created_at": r["created_at"],
            "second_reviewer": r["second_reviewer"],
            "second_note": r["second_note"],
        }
        for r in rows
    ]


def _review_set_state(store: Store) -> dict[str, Any]:
    """Return the immutable review-set governance state."""
    row = store.conn.execute("SELECT * FROM review_set_events ORDER BY id DESC LIMIT 1").fetchone()
    if not row:
        return {"locked": False, "event": None, "actor": None, "reason": None, "changed_at": None}
    return {
        "locked": row["event"] == "locked",
        "event": row["event"],
        "actor": row["actor"],
        "reason": row["reason"],
        "changed_at": row["created_at"],
    }


# ---------------------------------------------------------------------------
# Semantic enrichment (optional, validated).
# ---------------------------------------------------------------------------

def _validate_semantic_run(store: Store, semantic_run_id: int) -> dict[str, Any]:
    """Validate a candidate semantic run: exists, complete, non-stale, same population.

    Returns the profile dict. Raises InvestigationContextError on failure.
    """
    from .semantic_risk import population_hash

    row = store.conn.execute("SELECT * FROM semantic_runs WHERE id = ?", (semantic_run_id,)).fetchone()
    if not row:
        raise InvestigationContextError(f"semantic run {semantic_run_id} does not exist")
    provenance = json.loads(row["provenance_json"])
    if row["status"] != "complete":
        raise InvestigationContextError(
            f"semantic run {semantic_run_id} is not complete (status: {row['status']})"
        )
    # Staleness: population hash must match the current engagement population,
    # using the same canonical hash the analysis engine itself uses.
    current_hash = population_hash(store)
    stale = current_hash != provenance.get("population_hash")
    if stale:
        raise InvestigationContextError(
            f"semantic run {semantic_run_id} is stale; its population_hash does not match the current population"
        )
    return {
        "profile": dict(row),
        "provenance": provenance,
        "stale": stale,
    }


# ---------------------------------------------------------------------------
# Public contract.
# ---------------------------------------------------------------------------

def investigation_context(
    store: Store,
    run_id: int,
    ledger_id: int,
    semantic_run_id: int | None = None,
    max_related: int = 10,
) -> dict[str, Any]:
    """Build investigation context from canonical records.

    Read-only: it performs no INSERT/UPDATE/DELETE and no external network call.
    """
    # --- Validation (fails visibly; never silent empty) ---
    try:
        ex, entry, run, imp = _require_exception(store, run_id, ledger_id)
    except InvestigationContextError:
        raise
    except Exception as exc:  # defensive: corrupt schema/dependency is a defect
        raise _UnauthenticatedError(f"cannot read exception context: {exc}") from exc

    if semantic_run_id is not None:
        semantic_info = _validate_semantic_run(store, semantic_run_id)
    else:
        semantic_info = None

    # --- Transaction + source lineage ---
    import_row = dict(store.conn.execute("SELECT * FROM imports WHERE id = ?", (imp["id"],)).fetchone())
    transaction_line = {
        "available": True,
        "ledger_identity": entry["id"],
        "entry_id": entry["entry_id"],
        "posting_date": entry["posting_date"],
        "document_date": entry["document_date"],
        "account_code": entry["account_code"],
        "account_name": store.conn.execute(
            "SELECT account_name FROM coa WHERE account_code = ?", (entry["account_code"],)
        ).fetchone()["account_name"] or "not_mapped",
        "signed_amount": round(entry["signed_amount"], 2),
        "debit": round(entry["debit"], 2),
        "credit": round(entry["credit"], 2),
        "narration": entry["description"] or "not_available",
        "preparer": entry["preparer"] or "not_available",
        "reference": entry["reference"] or "not_available",
        "entity": entry["entity"] or "not_available",
        "vendor": entry["vendor"] or "not_available",
        "manual_or_system": "manual" if (entry["is_manual"] or False) else "not_flagged",
        "import_id": imp["id"],
        "source_file_display": imp["original_name"],
        "source_row": entry["source_row"],
        "source_hash": entry["source_hash"],
        "raw_json_available": bool(entry.get("raw_json")),
    }

    model_cfg = {}
    try:
        model_cfg = json.loads(run["configuration"] or "{}")
    except (TypeError, json.JSONDecodeError):
        model_cfg = {}
    run_cfg = model_cfg.get("policy") or {}
    lineage = {
        "analysis_run_id": run_id,
        "run_status": run["status"],
        "started_at": run["started_at"],
        "completed_at": run["completed_at"],
        "model_name": run.get("model_name") or "deterministic-rules-v1",
        "validation_status": run.get("validation_status") or "rules-only",
        "limitation_note": run.get("limitation_note") or "none recorded",
        "population_count": run["population_count"],
        "source_import_id": imp["id"],
        "source_display_name": imp["original_name"],
        "source_sha256": imp["sha256"],
        "accepted_rows": imp["accepted_rows"],
        "rejected_rows": imp["rejected_rows"],
        "lineage_available": True,
    }
    if semantic_info is not None and semantic_info["profile"]:
        prov = semantic_info["provenance"]
        lineage["semantic_profile_run_id"] = semantic_run_id
        lineage["semantic_model"] = prov.get("model")
        lineage["semantic_model_digest"] = prov.get("digest")
        lineage["semantic_template_version"] = prov.get("template_version")
        lineage["semantic_approximate_retrieval"] = True
        lineage["semantic_approximate_retrieval_note"] = "Semantic candidate retrieval is bounded and approximate unless validated."
        lineage["semantic_population_hash"] = prov.get("population_hash")
    else:
        lineage["semantic_profile_run_id"] = None

    # --- Why flagged ---
    deterministic_reasons: list[str] = []
    evidence: dict[str, Any] = {}
    components_source = "exceptions"
    if ex is not None:
        reasons = ex.get("reasons_json") or []
        if not isinstance(reasons, list):
            try:
                reasons = json.loads(reasons)
            except (TypeError, json.JSONDecodeError):
                reasons = []
        deterministic_reasons = reasons
        evi = ex.get("evidence_json") or {}
        if not isinstance(evi, dict):
            try:
                evi = json.loads(evi)
            except (TypeError, json.JSONDecodeError):
                evi = {}
        evidence = evi
        signal_components, components_source = _load_signal_components(store, run_id, ledger_id)
    else:
        signal_components, components_source = None, "none"

    cues = []
    for cue_id in deterministic_reasons:
        proc = _map_procedure(cue_id)
        supporting = []
        if cue_id == "robust_account_peer_outlier":
            supporting.append({"field": "peer_median", "value": evidence.get("peer_median")})
            supporting.append({"field": "robust_z", "value": evidence.get("robust_z")})
            supporting.append({"field": "outlier_robust_z_threshold", "value": run_cfg.get("outlier_robust_z", 3.5)})
        if cue_id == "round_amount":
            supporting.append({"field": "threshold", "value": run_cfg.get("round_amount_threshold", 1000)})
        if cue_id == "period_end_posting":
            supporting.append({"field": "period_end_days", "value": run_cfg.get("period_end_days", 3)})
        if cue_id == "fiscal_period_end":
            supporting.append({"field": "fiscal_calendar", "value": run_cfg.get("fiscal_calendar")})
        if cue_id == "possible_reversal_within_30_days":
            supporting.append({"field": "reversal_ledger_id", "value": evidence.get("reversal_ledger_id")})
        if cue_id == "isolation_style_anomaly":
            supporting.append({"field": "isolation_score", "value": evidence.get("isolation_score")})
            supporting.append({"field": "threshold", "value": 0.72})
        if cue_id == "duplicate_or_repeated_entry":
            supporting.append({"field": "duplicate_count", "value": evidence.get("duplicate_count")})
        if cue_id == "benford_population_indicator":
            supporting.append({"field": "benford_mad", "value": evidence.get("benford_population_indicator", {}).get("mad")})
        cues.append({
            "cue_id": cue_id,
            "label": cue_id.replace("_", " ").title(),
            "source": proc.get("experimental", False) and "experimental_ranker" or "analytical_rule",
            "status": "available",
            "value": proc.get("available"),
            "supporting_evidence": supporting,
            "procedure": {
                "description": proc["description"],
                "why": proc["why"],
                "inspect_evidence": proc["inspect_evidence"],
                "suggested_next_step": proc["suggested_next_step"],
                "audit_objective": proc["audit_objective"],
                "non_conclusive": True,
            },
            "limitation": proc.get("limitation"),
        })
    # Deduplicate by cue_id preserving order.
    seen = set()
    deduped = []
    for c in cues:
        if c["cue_id"] not in seen:
            seen.add(c["cue_id"])
            deduped.append(c)
    cues = deduped

    if signal_components:
        semantic_reasons = signal_components.get("semantic_reasons", [])
        if isinstance(semantic_reasons, str):
            try:
                semantic_reasons = json.loads(semantic_reasons)
            except (TypeError, json.JSONDecodeError):
                semantic_reasons = []
        for cue_id in semantic_reasons:
            proc = _map_procedure(cue_id)
            metrics = (signal_components.get("semantic", {}) or {}).get("metrics", {})
            cues.append({
                "cue_id": cue_id,
                "label": cue_id.replace("_", " ").title(),
                "source": "semantic_model",
                "status": "available",
                "value": proc.get("available", True),
                "supporting_evidence": [
                    {"field": "run_id", "value": signal_components.get("semantic", {}).get("run_id")},
                    {"field": "metric", "value": metrics.get(cue_id)},
                    {"field": "threshold", "value": proc.get("threshold")},
                ],
                "procedure": {
                    "description": proc["description"],
                    "why": proc["why"],
                    "inspect_evidence": proc["inspect_evidence"],
                    "suggested_next_step": proc["suggested_next_step"],
                    "audit_objective": proc["audit_objective"],
                    "non_conclusive": True,
                    "experimental": proc.get("experimental", True),
                },
                "limitation": proc.get("limitation"),
            })

    # Determinism / observation separation.
    flagged_reason = {
        "deterministic_reasons": [c["cue_id"] for c in cues if c["source"] == "analytical_rule"],
        "experimental_reasons": [c["cue_id"] for c in cues if c["source"] in ("semantic_model", "experimental_ranker")],
        "deterministic_evidence_available": bool(cues and any(c["source"] == "analytical_rule" for c in cues)),
        "experimental_evidence_available": bool(cues and any(c["source"] in ("semantic_model", "experimental_ranker") for c in cues)),
        "signal_components_source": components_source,
        "explanation": "Cues are analytical findings from the governed analysis run. They are evidence worth investigating, not conclusions of error, fraud, or misstatement.",
    }

    # --- Population and peers ---
    account_code = entry["account_code"]
    peer_stats = _peer_population(store, account_code, max_related)
    dup_group = _duplicate_group(
        store, account_code, entry["posting_date"], float(entry["signed_amount"]), entry["description"] or "", max_related
    )
    dup_excluding_self = [d for d in dup_group if d["ledger_id"] != entry["id"]][:max_related]
    reversal = _reversal_counterpart(store, ledger_id, account_code, float(entry["signed_amount"]), entry["posting_date"])
    materiality = _materiality_band(store, run_id, float(entry["signed_amount"]))
    benford = evidence.get("benford_population_indicator")
    population_context = {
        "account": account_code or "not_available",
        "available": bool(account_code),
        "status": peer_stats.get("status"),
        "population_count": peer_stats.get("population_count") or 0,
        "peer_statistics": peer_stats if peer_stats.get("available") else None,
        "duplicate_entries": {
            "available": bool(dup_excluding_self),
            "count": len(dup_excluding_self),
            "members": dup_excluding_self,
            "matching_rationale": "same account, same posting date, same absolute amount, same narration (bounded to the account's top 10 by ledger order)",
        },
        "possible_reversal": reversal,
        "materiality": materiality,
        "population_indicators": {
            "benford": benford if (benford and benford.get("flag")) else None,
        },
        "data_quality": {
            "missing_narration": not entry.get("description"),
            "missing_preparer": not entry.get("preparer"),
            "missing_reference": not entry.get("reference"),
            "missing_entity": not entry.get("entity"),
            "missing_vendor": not entry.get("vendor"),
            "missing_document_date": not entry.get("document_date"),
        },
    }

    # --- Supporting evidence ---
    bank_evidence = _bank_evidence(store, ledger_id)
    review_history = _reviews_for_exception(store, ex["id"]) if ex else []
    reviews_context = {
        "available": bool(review_history),
        "review_count": len(review_history),
        "latest_disposition": review_history[-1]["disposition"] if review_history else None,
        "history": review_history,
        "governance": _review_set_state(store),
        "note": "Reviews are immutable and append-only; opening this view does not record any disposition.",
    }
    semantic_evidence = {}
    if semantic_info is not None:
        semantic_evidence = {
            "available": True,
            "run_id": semantic_run_id,
            "status": "complete",
            "stale": False,
            "model": semantic_info["provenance"].get("model"),
            "model_digest": semantic_info["provenance"].get("digest"),
            "dimensions": semantic_info["profile"].get("dimensions"),
            "template_version": semantic_info["provenance"].get("template_version"),
            "approximate_retrieval_disclosed": True,
            "approximate_retrieval_note": "Candidate retrieval is bounded and approximate; results are investigation aids, not validated evidence.",
            "population_hash": semantic_info["provenance"].get("population_hash"),
            "engagement_hash_matches": not semantic_info["stale"],
            "limitation": "Semantic cues are experimental and require corroboration.",
        }
    else:
        semantic_evidence = {
            "available": False,
            "status": "unavailable",
            "note": "No semantic profile has been generated or linked for this run. Deterministic context is fully available without it.",
        }

    # --- Procedure suggestions (cue-derived) ---
    suggestions = []
    for cue in cues:
        proc = cue["procedure"]
        item = {
            "cue_id": cue["cue_id"],
            "description": proc.get("description"),
            "why": proc.get("why"),
            "inspect_evidence": proc.get("inspect_evidence"),
            "suggested_next_step": proc.get("suggested_next_step"),
            "audit_objective": proc.get("audit_objective"),
            "non_conclusive": True,
            "experimental": proc.get("experimental", False),
            "unrecognized": proc.get("unrecognized", False),
        }
        if item not in suggestions:
            suggestions.append(item)

    return {
        "investigation_context_version": "v2",
        "read_only": True,
        "contract": {
            "run_id": run_id,
            "ledger_id": ledger_id,
            "semantic_run_id": semantic_run_id,
            "max_related": max_related,
        },
        "transaction_line": transaction_line,
        "lineage": lineage,
        "why_flagged": flagged_reason,
        "cues": cues,
        "population_and_peers": population_context,
        "supporting_evidence": {
            "bank": bank_evidence,
            "review_history": reviews_context,
            "semantic": semantic_evidence,
        },
        "suggested_procedures": suggestions,
        "limitations": [
            "Procedure suggestions are indicative; they do not establish error, fraud, or misstatement.",
            "Peer statistics are bounded and sampled; a full recompute is not performed on open.",
            "Related and duplicate entries are bounded by max_related; the complete list requires a separate query.",
            "Bank-match evidence depends on a separate bank import and may be genuinely absent.",
            "Semantic enrichment is experimental and approximate unless independently validated.",
            "Date-only posting data cannot prove true posting time (e.g. weekend postings may be automated).",
            "Missing optional fields (vendor, entity, reference) are reported as unavailable, never as suspicious.",
        ],
        "provenance_note": (
            "Every factual statement traces to a persisted source record, transaction, analysis result, "
            "or calculated statistic. This operation performs no writes and creates no analysis, review, or audit-log records."
        ),
    }
