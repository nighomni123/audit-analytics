"""Governed model registry (provenance/approval metadata only).

Statistical validation requires labelled authorised audit populations and is deferred.
"""
from __future__ import annotations

import json
import time


def _ensure_table(store) -> None:
    store.conn.execute(
        "CREATE TABLE IF NOT EXISTS model_registry (id INTEGER PRIMARY KEY,"
        " name TEXT UNIQUE, model_type TEXT, feature_schema_json TEXT, owner TEXT,"
        " status TEXT, performance_json TEXT, approved_by TEXT,"
        " created_at REAL, created_by TEXT)"
    )


def register_model(store, name, model_type, feature_schema: dict, owner, actor) -> int:
    store.require_role(actor, {"manager", "partner"})
    _ensure_table(store)
    cur = store.conn.execute(
        "INSERT INTO model_registry(name, model_type, feature_schema_json, owner,"
        " status, created_at, created_by) VALUES(?,?,?,?,?,?,?)",
        (name, model_type, json.dumps(feature_schema), owner, "registered", time.time(), actor),
    )
    store.log(actor, "register_model", "model", name, {"model_type": model_type, "owner": owner})
    store.conn.commit()
    return cur.lastrowid


def validate_model(store, name, actor, performance: dict = None, approved_by: str = None) -> None:
    store.require_role(actor, {"manager", "partner"})
    if not approved_by:
        raise ValueError("approved_by is required")
    _ensure_table(store)
    cur = store.conn.execute(
        "UPDATE model_registry SET status='validated', performance_json=?, approved_by=? WHERE name=?",
        (json.dumps(performance) if performance is not None else None, approved_by, name),
    )
    if cur.rowcount == 0:
        raise ValueError(f"unknown model: {name}")
    store.log(actor, "validate_model", "model", name, {"approved_by": approved_by, "performance": performance})
    store.conn.commit()


def list_models(store) -> list[dict]:
    _ensure_table(store)
    return [dict(r) for r in store.conn.execute("SELECT * FROM model_registry").fetchall()]


def stamp_run(store, run_id, model_name, validation_status="pending") -> None:
    store.conn.execute(
        "UPDATE model_runs SET model_name=?, validation_status=? WHERE id=?",
        (model_name, validation_status, run_id),
    )
    store.conn.commit()
