"""Shared application operations for CLI and FastAPI governance invariants."""
from __future__ import annotations

import math
import time
from contextlib import contextmanager
from datetime import date

from .analytics import analyze
from .store import Store


REVIEW_ROLES = {"reviewer", "manager", "partner", "quality_reviewer"}
PREPARER_ROLES = {"preparer", "reviewer", "manager", "partner"}
MANAGER_ROLES = {"manager", "partner"}
DISPOSITIONS = {"open", "cleared", "follow_up", "selected_for_testing"}


class WorkflowError(ValueError):
    def __init__(self, message: str, code: str, status: int = 400):
        super().__init__(message)
        self.code = code
        self.status = status


@contextmanager
def _write_transaction(store: Store):
    store.conn.execute("BEGIN IMMEDIATE")
    try:
        yield
    except Exception:
        store.conn.rollback()
        raise
    else:
        store.conn.commit()


def _text(value, name: str) -> str:
    result = str(value or "").strip()
    if not result:
        raise WorkflowError(f"{name} is required", "invalid_input")
    return result


def _number(value, name: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise WorkflowError(f"{name} must be a finite number", "invalid_input")
    if value < 0 or (positive and value == 0):
        raise WorkflowError(f"{name} must be {'positive' if positive else 'non-negative'}", "invalid_input")
    return float(value)


def require_role(store: Store, username: str, allowed: set[str]):
    username = _text(username, "actor")
    row = store.conn.execute("SELECT role,active FROM users WHERE username=?", (username,)).fetchone()
    if not row or not row["active"]:
        raise WorkflowError(f"unknown or inactive user: {username}", "unknown_user", 404)
    if row["role"] not in allowed:
        raise WorkflowError(
            f"{username} has role {row['role']}; required: {', '.join(sorted(allowed))}",
            "forbidden",
            403,
        )
    return username


def create_engagement(store: Store, client: str, period: str, owner: str):
    client = _text(client, "client")
    owner = _text(owner, "owner")
    try:
        start_raw, end_raw = period.split(":", 1)
        start, end = date.fromisoformat(start_raw), date.fromisoformat(end_raw)
    except (ValueError, TypeError) as exc:
        raise WorkflowError("period must be YYYY-MM-DD:YYYY-MM-DD", "invalid_input") from exc
    if start > end:
        raise WorkflowError("period start must not be after period end", "invalid_input")
    with _write_transaction(store):
        if store.engagement():
            raise WorkflowError("engagement already exists", "conflict", 409)
        store.conn.execute(
            "INSERT INTO engagement VALUES(1,?,?,?,?)", (client, start.isoformat(), end.isoformat(), time.time())
        )
        store.add_user(owner, "manager", "system")
        store.set_setting("analysis_policy", {"round_amount_threshold": 1000, "period_end_days": 3, "outlier_robust_z": 3.5}, owner)
        store.set_setting("materiality", {}, owner)
        store.log(owner, "init", "engagement", 1, {"client": client, "period_start": start.isoformat(), "period_end": end.isoformat()})
    return dict(store.engagement())


def acknowledge_population(store: Store, reviewer: str, note: str, override_reconciliation: bool = False):
    reviewer = require_role(store, reviewer, REVIEW_ROLES)
    note = _text(note, "note")
    with _write_transaction(store):
        pending = store.conn.execute(
            "SELECT id FROM imports WHERE kind='gl' AND acknowledged_at IS NULL ORDER BY id"
        ).fetchall()
        if not pending:
            raise WorkflowError("no unacknowledged GL imports", "conflict", 409)
        acknowledged = []
        for row in pending:
            rec = store.reconciliation(row["id"])
            if not rec["matches"] and not override_reconciliation:
                raise WorkflowError(
                    f"import {row['id']} has no matching supplied control totals; use the explicit override with a documented difference",
                    "reconciliation_mismatch",
                )
            store.conn.execute(
                """UPDATE imports SET reconciled_at=?,reconciled_by=?,reconciliation_note=?,
                   acknowledged_at=?,acknowledged_by=?,acknowledgement_note=? WHERE id=?""",
                (time.time(), reviewer, note, time.time(), reviewer, note, row["id"]),
            )
            store.log(
                reviewer,
                "acknowledge_population",
                "import",
                row["id"],
                {"reconciliation": rec, "override": bool(override_reconciliation), "note": note},
            )
            acknowledged.append(row["id"])
    return {"import_ids": acknowledged, "reviewer": reviewer, "override": bool(override_reconciliation)}


def configure_engagement(
    store: Store,
    actor: str,
    *,
    materiality=None,
    performance_materiality=None,
    round_amount_threshold=None,
    period_end_days=None,
    outlier_robust_z=None,
):
    actor = require_role(store, actor, MANAGER_ROLES)
    if not store.engagement():
        raise WorkflowError("engagement not found", "not_found", 404)
    policy = store.get_setting("analysis_policy", {})
    materiality_settings = store.get_setting("materiality", {})
    if materiality is not None:
        materiality_settings["overall"] = _number(materiality, "materiality")
    if performance_materiality is not None:
        materiality_settings["performance"] = _number(performance_materiality, "performance materiality")
    if round_amount_threshold is not None:
        policy["round_amount_threshold"] = _number(round_amount_threshold, "round amount threshold")
    if period_end_days is not None:
        if isinstance(period_end_days, bool) or not isinstance(period_end_days, int) or not 0 <= period_end_days <= 366:
            raise WorkflowError("period_end_days must be an integer from 0 to 366", "invalid_input")
        policy["period_end_days"] = period_end_days
    if outlier_robust_z is not None:
        policy["outlier_robust_z"] = _number(outlier_robust_z, "outlier robust z", positive=True)
    overall = materiality_settings.get("overall")
    performance = materiality_settings.get("performance")
    if overall is not None and performance is not None and performance > overall:
        raise WorkflowError("performance materiality must not exceed overall materiality", "invalid_input")
    with _write_transaction(store):
        store.set_setting("analysis_policy", policy, actor)
        store.set_setting("materiality", materiality_settings, actor)
        store.log(actor, "configure", "engagement", 1, {"analysis_policy": policy, "materiality": materiality_settings})
    return {"analysis_policy": policy, "materiality": materiality_settings}


def run_analysis(store: Store, actor: str, include_isolation: bool = True, semantic_run_id=None):
    actor = require_role(store, actor, PREPARER_ROLES)
    return {"run_id": analyze(store, actor, include_isolation, semantic_run_id)}


def assign_exception(store: Store, actor: str, exception_id: int, assignee: str, due_date=None):
    actor = require_role(store, actor, MANAGER_ROLES)
    assignee = require_role(store, assignee, REVIEW_ROLES)
    if due_date:
        try:
            date.fromisoformat(due_date)
        except (TypeError, ValueError) as exc:
            raise WorkflowError("due_date must be YYYY-MM-DD", "invalid_input") from exc
    with _write_transaction(store):
        if store.review_locked():
            raise WorkflowError("review set is locked", "review_locked", 409)
        if not store.conn.execute("SELECT 1 FROM exceptions WHERE id=?", (exception_id,)).fetchone():
            raise WorkflowError("exception not found", "not_found", 404)
        store.conn.execute(
            "UPDATE exceptions SET assigned_to=?,due_date=? WHERE id=?", (assignee, due_date, exception_id)
        )
        store.log(actor, "assign_exception", "exception", exception_id, {"assignee": assignee, "due_date": due_date})
    return {"exception_id": exception_id, "assignee": assignee, "due_date": due_date}


def record_review(
    store: Store,
    exception_id: int,
    reviewer: str,
    disposition: str,
    note: str,
    second_reviewer: str | None = None,
    second_note: str | None = None,
):
    reviewer = require_role(store, reviewer, REVIEW_ROLES)
    disposition = str(disposition or "").strip()
    note = _text(note, "note")
    if disposition not in DISPOSITIONS:
        raise WorkflowError("invalid disposition", "invalid_disposition")
    with _write_transaction(store):
        if store.review_locked():
            raise WorkflowError("review set is locked", "review_locked", 409)
        exception = store.conn.execute(
            "SELECT id,severity,status FROM exceptions WHERE id=?", (exception_id,)
        ).fetchone()
        if not exception:
            raise WorkflowError("exception not found", "not_found", 404)
        second_reviewer = second_reviewer.strip() if isinstance(second_reviewer, str) and second_reviewer.strip() else None
        second_note = second_note.strip() if isinstance(second_note, str) and second_note.strip() else None
        if disposition == "cleared" and exception["severity"] == "high":
            if not second_reviewer or not second_note:
                raise WorkflowError(
                    "clearing a high-severity exception requires a second reviewer and second note",
                    "second_review_required",
                )
            if second_reviewer.casefold() == reviewer.casefold():
                raise WorkflowError("second reviewer must differ from the first reviewer", "second_review_invalid")
            second_reviewer = require_role(store, second_reviewer, REVIEW_ROLES)
        review_id = store.conn.execute(
            """INSERT INTO reviews(exception_id,reviewer,disposition,note,created_at,second_reviewer,second_note)
               VALUES(?,?,?,?,?,?,?)""",
            (exception_id, reviewer, disposition, note, time.time(), second_reviewer, second_note),
        ).lastrowid
        store.log(
            reviewer,
            "review_exception",
            "exception",
            exception_id,
            {"review_id": review_id, "disposition": disposition, "second_reviewer": second_reviewer},
        )
        status = disposition
    return {"review_id": review_id, "exception_id": exception_id, "status": status}


def _change_review_set(store: Store, actor: str, reason: str, event: str):
    actor = require_role(store, actor, MANAGER_ROLES)
    reason = _text(reason, "reason")
    with _write_transaction(store):
        current = store.review_set_state()["locked"]
        if event == "locked" and current:
            raise WorkflowError("review set is already locked", "conflict", 409)
        if event == "reopened" and not current:
            raise WorkflowError("review set is already open", "conflict", 409)
        event_id = store.conn.execute(
            "INSERT INTO review_set_events(event,actor,reason,created_at) VALUES(?,?,?,?)",
            (event, actor, reason, time.time()),
        ).lastrowid
        store.log(actor, event, "review_set", 1, {"reason": reason, "event_id": event_id})
    return {"event_id": event_id, **store.review_set_state()}


def lock_review_set(store: Store, actor: str, reason: str):
    return _change_review_set(store, actor, reason, "locked")


def reopen_review_set(store: Store, actor: str, reason: str):
    return _change_review_set(store, actor, reason, "reopened")
