"""Bank-statement evidence import and ledger reconciliation."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import time
from datetime import date
from pathlib import Path


def _num(v):
    """Parse a debit/credit/balance cell to float."""
    if v in (None, ""):
        return 0.0
    return float(str(v).replace(",", "").strip() or 0)


def import_bank(store, path: str, actor: str):
    """Import a bank-statement CSV; return (import_id, accepted, rejected)."""
    source = Path(path)
    evidence = store.path.parent / "evidence"
    evidence.mkdir(exist_ok=True)
    data = source.read_bytes()
    sha256 = hashlib.sha256(data).hexdigest()
    target = evidence / f"{sha256[:12]}_{source.name}"
    if not target.exists():
        shutil.copy2(source, target)
    cur = store.conn.execute(
        "INSERT INTO imports(kind, original_name, evidence_path, sha256, imported_at,"
        " accepted_rows, rejected_rows, control_debits, control_credits)"
        " VALUES('bank', ?, ?, ?, ?, 0, 0, 0, 0)",
        (source.name, str(target), sha256, time.time()),
    )
    import_id = cur.lastrowid
    accepted = 0
    with source.open(newline="", encoding="utf-8-sig") as f:
        for line, raw in enumerate(csv.DictReader(f), 2):
            low = {(k or "").strip().lower(): v for k, v in raw.items()}
            entry_date = low.get("entry_date") or low.get("date") or ""
            narration = low.get("narration") or low.get("narrative") or low.get("description") or ""
            debit, credit, balance = _num(low.get("debit")), _num(low.get("credit")), _num(low.get("balance"))
            raw_json = json.dumps(raw, default=str, sort_keys=True)
            source_hash = hashlib.sha256(raw_json.encode()).hexdigest()
            store.conn.execute(
                "INSERT INTO bank_statements(import_id, entry_date, narration, debit, credit,"
                " balance, source_row, source_hash, raw_json) VALUES(?,?,?,?,?,?,?,?,?)",
                (import_id, str(entry_date).strip(), str(narration), debit, credit,
                 balance, line, source_hash, raw_json),
            )
            accepted += 1
    store.conn.execute("UPDATE imports SET accepted_rows=? WHERE id=?", (accepted, import_id))
    store.log(actor, "import_bank", "import", import_id, {"accepted": accepted})
    store.conn.commit()
    return import_id, accepted, 0


def reconcile_bank(store, actor: str, tolerance: float = 1.0, days: int = 3) -> int:
    """Link bank rows to ledger entries within amount/date tolerance."""
    created = 0
    banks = store.conn.execute("SELECT id, entry_date, credit, debit FROM bank_statements").fetchall()
    ledgers = store.conn.execute(
        "SELECT id, posting_date, signed_amount FROM ledger_entries").fetchall()
    for b in banks:
        if store.conn.execute("SELECT 1 FROM bank_matches WHERE bank_id=?", (b["id"],)).fetchone():
            continue
        amt = (b["credit"] or 0) - (b["debit"] or 0)
        try:
            bdate = date.fromisoformat(str(b["entry_date"]).strip())
        except ValueError:
            continue
        for led in ledgers:
            diff = led["signed_amount"] - amt
            if abs(diff) > tolerance:
                continue
            try:
                ldate = date.fromisoformat(str(led["posting_date"]).strip())
            except ValueError:
                continue
            if abs((ldate - bdate).days) > days:
                continue
            store.conn.execute(
                "INSERT INTO bank_matches(bank_id, ledger_id, match_type, amount_diff, created_at)"
                " VALUES(?,?,?,?,?)",
                (b["id"], led["id"], "exact" if abs(diff) == 0 else "approx", diff, time.time()),
            )
            created += 1
            break
    store.log(actor, "reconcile_bank", "bank_matches", created, {"created": created})
    store.conn.commit()
    return created
