"""Bank-statement evidence import and ledger reconciliation."""
from __future__ import annotations

import csv
import hashlib
import json
import time
from datetime import date
from pathlib import Path

from .importer import _cleanup_evidence, _evidence_target, _validate_source
from .store import Store


def _num(value):
    """Parse a debit/credit/balance cell to float."""
    if value in (None, ""):
        return 0.0
    return float(str(value).replace(",", "").strip() or 0)


def import_bank(store: Store, path: str, actor: str, reimport: bool = False):
    """Import a bank-statement CSV; return (import_id, accepted, rejected)."""
    source = Path(path)
    _validate_source(source)
    if source.suffix.lower() != ".csv":
        raise ValueError("bank evidence must be CSV")
    store.conn.commit()
    store.conn.execute("BEGIN IMMEDIATE")
    created = False
    try:
        digest, target, created, supersedes = _evidence_target(store, source, "bank", reimport)
        cur = store.conn.execute(
            """INSERT INTO imports(kind,original_name,evidence_path,sha256,imported_at,
               accepted_rows,rejected_rows,control_debits,control_credits,supersedes_import_id)
               VALUES('bank',?,?,?,?,0,0,0,0,?)""",
            (source.name, str(target), digest, time.time(), supersedes),
        )
        import_id = cur.lastrowid
        accepted = 0
        with source.open(newline="", encoding="utf-8-sig") as stream:
            for line, raw in enumerate(csv.DictReader(stream), 2):
                low = {(key or "").strip().lower(): value for key, value in raw.items()}
                entry_date = low.get("entry_date") or low.get("date") or ""
                narration = low.get("narration") or low.get("narrative") or low.get("description") or ""
                debit, credit, balance = _num(low.get("debit")), _num(low.get("credit")), _num(low.get("balance"))
                raw_json = json.dumps(raw, default=str, sort_keys=True)
                source_hash = hashlib.sha256(raw_json.encode()).hexdigest()
                store.conn.execute(
                    """INSERT INTO bank_statements(import_id,entry_date,narration,debit,credit,
                       balance,source_row,source_hash,raw_json) VALUES(?,?,?,?,?,?,?,?,?)""",
                    (import_id, str(entry_date).strip(), narration, debit, credit, balance, line, source_hash, raw_json),
                )
                accepted += 1
        store.conn.execute("UPDATE imports SET accepted_rows=? WHERE id=?", (accepted, import_id))
        store.log(
            actor,
            "import_bank",
            "import",
            import_id,
            {"accepted": accepted, "sha256": digest, "supersedes_import_id": supersedes},
        )
        store.conn.commit()
        return import_id, accepted, 0
    except Exception:
        store.conn.rollback()
        if "target" in locals():
            _cleanup_evidence(target, created)
        raise


def reconcile_bank(store: Store, actor: str, tolerance: float = 1.0, days: int = 3) -> int:
    """Link bank rows to ledger entries within amount/date tolerance."""
    created = 0
    banks = store.conn.execute("SELECT id, entry_date, credit, debit FROM bank_statements").fetchall()
    ledgers = store.conn.execute("SELECT id, posting_date, signed_amount FROM ledger_entries").fetchall()
    for bank in banks:
        if store.conn.execute("SELECT 1 FROM bank_matches WHERE bank_id=?", (bank["id"],)).fetchone():
            continue
        amount = (bank["credit"] or 0) - (bank["debit"] or 0)
        try:
            bank_date = date.fromisoformat(str(bank["entry_date"]).strip())
        except ValueError:
            continue
        for ledger in ledgers:
            difference = ledger["signed_amount"] - amount
            if abs(difference) > tolerance:
                continue
            try:
                ledger_date = date.fromisoformat(str(ledger["posting_date"]).strip())
            except ValueError:
                continue
            if abs((ledger_date - bank_date).days) > days:
                continue
            store.conn.execute(
                """INSERT INTO bank_matches(bank_id,ledger_id,match_type,amount_diff,created_at)
                   VALUES(?,?,?,?,?)""",
                (bank["id"], ledger["id"], "exact" if abs(difference) == 0 else "approx", difference, time.time()),
            )
            created += 1
            break
    store.log(actor, "reconcile_bank", "bank_matches", created, {"created": created})
    store.conn.commit()
    return created
