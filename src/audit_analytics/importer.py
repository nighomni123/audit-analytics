from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

from .store import Store

ALIASES = {
    "entry_id": ("entry_id", "journal_entry_id", "voucher_no", "voucher_number", "transaction_id", "document_id"),
    "posting_date": ("posting_date", "date", "entry_date", "postingdate"),
    "document_date": ("document_date", "doc_date", "voucher_date"),
    "account_code": ("account_code", "account", "gl_code", "ledger_code", "account_number"),
    "debit": ("debit", "dr", "debit_amount"), "credit": ("credit", "cr", "credit_amount"),
    "amount": ("amount", "signed_amount", "net_amount", "value"),
    "description": ("description", "narration", "memo", "particulars"),
    "preparer": ("preparer", "user", "created_by", "posted_by"),
    "reference": ("reference", "reference_no", "document_no", "invoice_no", "voucher_no"),
    "entity": ("entity", "company", "cost_center", "branch"),
    "is_manual": ("is_manual", "manual", "source_type"),
}


def _key(s): return "".join(c.lower() for c in (s or "") if c.isalnum())

def _number(value):
    if value in (None, ""): return 0.0
    return float(str(value).replace(",", "").replace("₹", "").strip().strip("()") or 0)

def _date(value):
    if isinstance(value, (int, float)) or (str(value).replace(".", "", 1).isdigit() and float(value) > 20000):
        return (datetime(1899, 12, 30) + __import__('datetime').timedelta(days=float(value))).date().isoformat()
    raw = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try: return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError: pass
    raise ValueError("invalid posting date")

def _rows(path: Path):
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as f:
            yield from csv.DictReader(f)
        return
    if path.suffix.lower() == ".xlsx":
        ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
        with zipfile.ZipFile(path) as book:
            shared = []
            if "xl/sharedStrings.xml" in book.namelist():
                root = ET.fromstring(book.read("xl/sharedStrings.xml"))
                shared = ["".join(node.itertext()) for node in root.findall(f"{ns}si")]
            sheets = sorted(n for n in book.namelist() if n.startswith("xl/worksheets/sheet") and n.endswith(".xml"))
            if not sheets: raise ValueError("XLSX contains no worksheet")
            parsed = []
            for row in ET.fromstring(book.read(sheets[0])).iter(f"{ns}row"):
                values = []
                for cell in row.findall(f"{ns}c"):
                    letters = "".join(c for c in cell.get("r", "") if c.isalpha())
                    col = 0
                    for letter in letters: col = col * 26 + ord(letter.upper()) - 64
                    while len(values) < max(0, col - 1): values.append("")
                    val = cell.find(f"{ns}v"); text = "" if val is None else val.text or ""
                    if cell.get("t") == "s" and text: text = shared[int(text)]
                    elif cell.get("t") == "inlineStr": text = "".join(cell.itertext())
                    values.append(text)
                parsed.append(values)
        if not parsed: return
        headers = [str(x or "") for x in parsed[0]]
        for values in parsed[1:]: yield dict(zip(headers, values))
        return
    raise ValueError("only .csv and .xlsx files are supported")

def _canonical(row, mapping=None):
    indexed = {_key(k): v for k, v in row.items()}
    out = {}
    for field, aliases in ALIASES.items():
        explicit = (mapping or {}).get(field)
        if explicit and _key(explicit) in indexed:
            out[field] = indexed[_key(explicit)]
        else:
            out[field] = next((indexed[_key(a)] for a in aliases if _key(a) in indexed), None)
    return out

def preview_gl(filename: str, mapping=None, sample_size=10):
    source = Path(filename)
    iterator = _rows(source)
    sample = []
    for _ in range(sample_size):
        try: sample.append(next(iterator))
        except StopIteration: break
    headers = list(sample[0]) if sample else []
    inferred = {}
    for field, aliases in ALIASES.items():
        explicit = (mapping or {}).get(field)
        inferred[field] = explicit or next((h for h in headers if _key(h) in {_key(a) for a in aliases}), None)
    missing = [field for field in ("entry_id", "posting_date", "account_code") if not inferred[field]]
    if not inferred["amount"] and not (inferred["debit"] and inferred["credit"]): missing.append("amount or debit+credit")
    return {"file": source.name, "headers": headers, "mapping": inferred, "missing_required": missing, "sample_rows": sample}


def import_gl(store: Store, filename: str, actor="system", mapping=None, expected_rows=None, expected_debits=None, expected_credits=None):
    source = Path(filename)
    if not source.is_file(): raise ValueError(f"source file not found: {source}")
    evidence = store.path.parent / "evidence"; evidence.mkdir(exist_ok=True)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    target = evidence / f"{digest[:12]}_{source.name}"
    if not target.exists(): shutil.copy2(source, target)
    cur = store.conn.execute("""INSERT INTO imports(kind,original_name,evidence_path,sha256,imported_at,accepted_rows,rejected_rows,expected_rows,expected_debits,expected_credits)
        VALUES('gl',?,?,?,?,?,?,?,?,?)""", (source.name, str(target), digest, __import__('time').time(), 0, 0, expected_rows, expected_debits, expected_credits))
    import_id = cur.lastrowid; accepted = rejected = 0; debits = credits = 0.0
    for line, raw in enumerate(_rows(source), 2):
        try:
            r = _canonical(raw, mapping); entry_id = str(r["entry_id"] or "").strip(); account = str(r["account_code"] or "").strip()
            if not entry_id or not account: raise ValueError("missing entry ID or account code")
            posting = _date(r["posting_date"])
            debit, credit = _number(r["debit"]), _number(r["credit"])
            if not debit and not credit:
                amount = _number(r["amount"])
                debit, credit = (amount, 0.0) if amount >= 0 else (0.0, -amount)
            if debit < 0 or credit < 0 or (debit and credit): raise ValueError("invalid debit/credit values")
            manual = str(r["is_manual"] or "").lower() in ("1", "true", "yes", "manual")
            raw_json = json.dumps(raw, default=str, sort_keys=True); row_hash = hashlib.sha256(raw_json.encode()).hexdigest()
            store.conn.execute("""INSERT INTO ledger_entries(import_id,entry_id,posting_date,document_date,account_code,debit,credit,signed_amount,description,preparer,reference,entity,is_manual,source_row,source_hash,raw_json)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (import_id, entry_id, posting, _date(r["document_date"]) if r["document_date"] else None, account, debit, credit, debit-credit, r["description"], r["preparer"], r["reference"], r["entity"], int(manual), line, row_hash, raw_json))
            accepted += 1; debits += debit; credits += credit
        except (ValueError, TypeError) as e:
            rejected += 1; store.conn.execute("INSERT INTO rejected_rows(import_id,source_row,reason,raw_json) VALUES(?,?,?,?)", (import_id, line, str(e), json.dumps(raw, default=str)))
    store.conn.execute("UPDATE imports SET accepted_rows=?,rejected_rows=?,control_debits=?,control_credits=? WHERE id=?", (accepted, rejected, debits, credits, import_id))
    store.log(actor, "import_gl", "import", import_id, {"accepted": accepted, "rejected": rejected, "sha256": digest, "mapping": mapping or {}, "expected_rows": expected_rows, "expected_debits": expected_debits, "expected_credits": expected_credits})
    store.conn.commit(); return import_id, accepted, rejected, debits, credits

def import_coa(store: Store, filename: str, actor="system"):
    source = Path(filename); rows = list(_rows(source)); digest = hashlib.sha256(source.read_bytes()).hexdigest()
    evidence = store.path.parent / "evidence"; evidence.mkdir(exist_ok=True); target = evidence / f"{digest[:12]}_{source.name}"
    if not target.exists(): shutil.copy2(source, target)
    cur = store.conn.execute("INSERT INTO imports(kind,original_name,evidence_path,sha256,imported_at,accepted_rows,rejected_rows) VALUES('coa',?,?,?,?,?,?)", (source.name, str(target), digest, __import__('time').time(), 0, 0)); iid = cur.lastrowid
    for raw in rows:
        r = {_key(k): v for k, v in raw.items()}; code = r.get("account_code") or r.get("account") or r.get("gl_code")
        if code: store.conn.execute("INSERT OR REPLACE INTO coa VALUES(?,?,?,?)", (str(code), r.get("account_name") or r.get("name"), r.get("account_type") or r.get("type"), iid))
    store.conn.execute("UPDATE imports SET accepted_rows=? WHERE id=?", (len(rows), iid)); store.log(actor, "import_coa", "import", iid, {"rows": len(rows)}); store.conn.commit(); return iid
