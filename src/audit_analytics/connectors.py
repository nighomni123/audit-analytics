"""Demo CSV connector proving the connector interface (Release 2)."""
from __future__ import annotations

import csv
import tempfile
import time
from pathlib import Path

CANONICAL_FIELDS = ("entry_id", "posting_date", "account_code", "debit", "credit",
                    "description", "preparer", "reference", "entity", "is_manual")


class BaseConnector:
    """Connector interface: extract canonical rows from a source path."""

    name = ""
    source_system = ""

    def extract(self, path: str) -> list[dict]:
        """Return canonical rows (without signed_amount; derived as credit - debit)."""
        raise NotImplementedError


class DemoCsvConnector(BaseConnector):
    """Read CSV with case-insensitive headers; canonical headers or single amount."""

    name = "demo_csv"
    source_system = "demo_csv"

    def extract(self, path: str) -> list[dict]:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                return []
            lower = {h.lower(): h for h in reader.fieldnames}
            has_amount = "amount" in lower
            rows = []
            for raw in reader:
                g = lambda *names: next((raw[lower[n]] for n in names if n in lower), None)  # noqa: E731
                debit = g("debit") or 0
                credit = g("credit") or 0
                try:
                    debit = float(str(debit).replace(",", "").strip() or 0)
                except ValueError:
                    debit = 0.0
                try:
                    credit = float(str(credit).replace(",", "").strip() or 0)
                except ValueError:
                    credit = 0.0
                if has_amount and not debit and not credit:
                    try:
                        amt = float(str(raw[lower["amount"]]).replace(",", "").strip() or 0)
                    except ValueError:
                        amt = 0.0
                    debit, credit = (amt, 0.0) if amt >= 0 else (0.0, -amt)
                rows.append({
                    "entry_id": g("entry_id") or "",
                    "posting_date": g("posting_date") or "",
                    "account_code": g("account_code") or "",
                    "debit": debit,
                    "credit": credit,
                    "description": g("description") or "",
                    "preparer": g("preparer") or "",
                    "reference": g("reference") or "",
                    "entity": g("entity") or "",
                    "is_manual": g("is_manual") or "",
                })
            return rows


def run_connector(name: str, store, path: str, actor: str):
    """Extract via named connector, import through import_gl, record manifest."""
    if name != "demo_csv":
        raise ValueError(f"unknown connector: {name}")
    from audit_analytics.importer import import_gl
    rows = DemoCsvConnector().extract(path)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False,
                                     newline="", encoding="utf-8") as tmp:
        w = csv.DictWriter(tmp, fieldnames=list(CANONICAL_FIELDS))
        w.writeheader()
        w.writerows(rows)
        tmpcsv = tmp.name
    import_id, accepted, rejected, debits, credits = import_gl(store, tmpcsv, actor)
    now = time.time()
    store.conn.execute(
        "INSERT INTO connector_runs(connector, identity, source_system, extracted_at,"
        " record_count, control_debits, control_credits, created_at)"
        " VALUES(?,?,?,?,?,?,?,?)",
        (name, actor, "demo_csv", now, accepted, debits, credits, now))
    store.conn.commit()
    Path(tmpcsv).unlink(missing_ok=True)
    return (import_id, {"connector": name, "accepted": accepted, "record_count": accepted,
                       "control_debits": debits, "control_credits": credits})
