from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path


SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS engagement (
  id INTEGER PRIMARY KEY CHECK(id=1), client TEXT NOT NULL, period_start TEXT NOT NULL,
  period_end TEXT NOT NULL, created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS imports (
  id INTEGER PRIMARY KEY, kind TEXT NOT NULL, original_name TEXT NOT NULL,
  evidence_path TEXT NOT NULL, sha256 TEXT NOT NULL, imported_at REAL NOT NULL,
  accepted_rows INTEGER NOT NULL, rejected_rows INTEGER NOT NULL, control_debits REAL,
  control_credits REAL, acknowledged_at REAL, acknowledged_by TEXT, acknowledgement_note TEXT
);
CREATE TABLE IF NOT EXISTS connector_runs (
  id INTEGER PRIMARY KEY, connector TEXT NOT NULL, identity TEXT, source_system TEXT,
  extracted_at REAL, record_count INTEGER, control_debits REAL, control_credits REAL,
  created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
  username TEXT PRIMARY KEY, role TEXT NOT NULL CHECK(role IN ('preparer','reviewer','manager','partner','quality_reviewer','read_only')),
  active INTEGER NOT NULL DEFAULT 1, created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY, value_json TEXT NOT NULL, updated_at REAL NOT NULL, updated_by TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS import_mappings (
  name TEXT PRIMARY KEY, mapping_json TEXT NOT NULL, created_at REAL NOT NULL, created_by TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS coa (
  account_code TEXT PRIMARY KEY, account_name TEXT, account_type TEXT, import_id INTEGER REFERENCES imports(id)
);
CREATE TABLE IF NOT EXISTS account_taxonomy (
  account_code TEXT PRIMARY KEY, account_type TEXT, label TEXT, risk_weight REAL,
  import_id INTEGER REFERENCES imports(id)
);
CREATE TABLE IF NOT EXISTS ledger_entries (
  id INTEGER PRIMARY KEY, import_id INTEGER NOT NULL REFERENCES imports(id), entry_id TEXT NOT NULL,
  posting_date TEXT NOT NULL, document_date TEXT, account_code TEXT NOT NULL, debit REAL NOT NULL,
  credit REAL NOT NULL, signed_amount REAL NOT NULL, description TEXT, preparer TEXT,
  reference TEXT, entity TEXT, is_manual INTEGER, source_row INTEGER NOT NULL,
  source_hash TEXT NOT NULL, raw_json TEXT NOT NULL, UNIQUE(import_id, source_row)
);
CREATE INDEX IF NOT EXISTS ledger_account_date ON ledger_entries(account_code, posting_date);
CREATE INDEX IF NOT EXISTS ledger_entry_id ON ledger_entries(entry_id);
CREATE TABLE IF NOT EXISTS rejected_rows (
  id INTEGER PRIMARY KEY, import_id INTEGER NOT NULL REFERENCES imports(id), source_row INTEGER NOT NULL,
  reason TEXT NOT NULL, raw_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS model_runs (
  id INTEGER PRIMARY KEY, started_at REAL NOT NULL, completed_at REAL, configuration TEXT NOT NULL,
  population_count INTEGER NOT NULL, status TEXT NOT NULL, limitation_note TEXT
);
CREATE TABLE IF NOT EXISTS exceptions (
  id INTEGER PRIMARY KEY, run_id INTEGER NOT NULL REFERENCES model_runs(id), ledger_id INTEGER NOT NULL REFERENCES ledger_entries(id),
  risk_score REAL NOT NULL, severity TEXT NOT NULL, reasons_json TEXT NOT NULL,
  evidence_json TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'open', UNIQUE(run_id, ledger_id)
);
CREATE TABLE IF NOT EXISTS reviews (
  id INTEGER PRIMARY KEY, exception_id INTEGER NOT NULL REFERENCES exceptions(id), reviewer TEXT NOT NULL,
  disposition TEXT NOT NULL, note TEXT NOT NULL, created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY, created_at REAL NOT NULL, actor TEXT NOT NULL, action TEXT NOT NULL,
  target_type TEXT NOT NULL, target_id TEXT NOT NULL, detail_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ledger_embeddings (
  ledger_id INTEGER NOT NULL REFERENCES ledger_entries(id), model TEXT NOT NULL,
  dims INTEGER NOT NULL, text_hash TEXT NOT NULL, vector BLOB NOT NULL,
  embedded_at REAL NOT NULL, PRIMARY KEY(ledger_id, model, dims)
);
CREATE INDEX IF NOT EXISTS ledger_embeddings_model ON ledger_embeddings(model, dims);
CREATE TABLE IF NOT EXISTS semantic_runs (
  id INTEGER PRIMARY KEY, started_at REAL NOT NULL, completed_at REAL, actor TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('running','complete','failed')),
  population_count INTEGER NOT NULL, population_hash TEXT NOT NULL,
  configuration_json TEXT NOT NULL, provenance_json TEXT NOT NULL,
  summary_json TEXT NOT NULL DEFAULT '{}', limitation_note TEXT
);
CREATE TABLE IF NOT EXISTS semantic_profiles (
  run_id INTEGER NOT NULL REFERENCES semantic_runs(id), kind TEXT NOT NULL,
  profile_key TEXT NOT NULL, ledger_id INTEGER REFERENCES ledger_entries(id),
  dims INTEGER NOT NULL CHECK(dims>0), vector BLOB NOT NULL,
  member_count INTEGER NOT NULL, metadata_json TEXT NOT NULL,
  PRIMARY KEY(run_id,kind,profile_key)
);
CREATE INDEX IF NOT EXISTS semantic_profile_ledger ON semantic_profiles(run_id,ledger_id);
CREATE TABLE IF NOT EXISTS semantic_results (
  run_id INTEGER NOT NULL REFERENCES semantic_runs(id), ledger_id INTEGER NOT NULL REFERENCES ledger_entries(id),
  cluster_id INTEGER, metrics_json TEXT NOT NULL, cues_json TEXT NOT NULL, evidence_json TEXT NOT NULL,
  PRIMARY KEY(run_id,ledger_id)
);
CREATE TABLE IF NOT EXISTS bank_statements (
  id INTEGER PRIMARY KEY, import_id INTEGER NOT NULL REFERENCES imports(id),
  entry_date TEXT, narration TEXT, debit REAL, credit REAL, balance REAL,
  source_row INTEGER NOT NULL, source_hash TEXT NOT NULL, raw_json TEXT NOT NULL,
  UNIQUE(import_id, source_row)
);
CREATE TABLE IF NOT EXISTS bank_matches (
  id INTEGER PRIMARY KEY, bank_id INTEGER REFERENCES bank_statements(id),
  ledger_id INTEGER REFERENCES ledger_entries(id), match_type TEXT,
  amount_diff REAL, created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS sample_sets (
  id INTEGER PRIMARY KEY, run_id INTEGER NOT NULL REFERENCES model_runs(id), name TEXT NOT NULL,
  method_json TEXT NOT NULL, created_at REAL NOT NULL, created_by TEXT NOT NULL, UNIQUE(run_id, name)
);
CREATE TABLE IF NOT EXISTS sample_items (
  sample_set_id INTEGER NOT NULL REFERENCES sample_sets(id), ledger_id INTEGER NOT NULL REFERENCES ledger_entries(id),
  rationale TEXT NOT NULL, PRIMARY KEY(sample_set_id, ledger_id)
);
"""


class Store:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript(SCHEMA)
        self._migrate()
        self.conn.commit()

    def _migrate(self):
        """Keep engagement databases additive as features are introduced."""
        migrations = [
            ("ledger_entries", "vendor", "TEXT"),
            ("imports", "expected_rows", "INTEGER"), ("imports", "expected_debits", "REAL"),
            ("imports", "expected_credits", "REAL"), ("imports", "reconciled_at", "REAL"),
            ("imports", "reconciled_by", "TEXT"), ("imports", "reconciliation_note", "TEXT"),
            ("exceptions", "assigned_to", "TEXT"), ("exceptions", "due_date", "TEXT"),
            ("exceptions", "materiality_band", "TEXT"),
            ("model_runs", "model_name", "TEXT"), ("model_runs", "validation_status", "TEXT"),
            ("reviews", "second_reviewer", "TEXT"), ("reviews", "second_note", "TEXT"),
        ]
        for table, column, definition in migrations:
            try: self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
            except sqlite3.OperationalError: pass

    def log(self, actor: str, action: str, target_type: str, target_id: str | int, detail: dict):
        self.conn.execute("INSERT INTO audit_log VALUES(NULL,?,?,?,?,?,?)",
                          (time.time(), actor, action, target_type, str(target_id), json.dumps(detail, sort_keys=True)))

    def engagement(self):
        return self.conn.execute("SELECT * FROM engagement WHERE id=1").fetchone()

    def set_setting(self, key: str, value, actor: str):
        self.conn.execute("INSERT INTO settings(key,value_json,updated_at,updated_by) VALUES(?,?,?,?) ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json,updated_at=excluded.updated_at,updated_by=excluded.updated_by", (key, json.dumps(value), time.time(), actor))

    def get_setting(self, key: str, default=None):
        row = self.conn.execute("SELECT value_json FROM settings WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else default

    def add_user(self, username: str, role: str, actor="system"):
        if role not in {"preparer", "reviewer", "manager", "partner", "quality_reviewer", "read_only"}: raise ValueError("invalid role")
        self.conn.execute("INSERT INTO users(username,role,active,created_at) VALUES(?,?,1,?) ON CONFLICT(username) DO UPDATE SET role=excluded.role,active=1", (username, role, time.time()))
        self.log(actor, "add_or_update_user", "user", username, {"role": role})

    def require_role(self, username: str, allowed: set[str]):
        row = self.conn.execute("SELECT role,active FROM users WHERE username=?", (username,)).fetchone()
        if not row or not row["active"]: raise ValueError(f"unknown or inactive user: {username}")
        if row["role"] not in allowed: raise ValueError(f"{username} has role {row['role']}; required: {', '.join(sorted(allowed))}")
        return row["role"]

    def reconciliation(self, import_id: int, tolerance=0.01):
        row = self.conn.execute("SELECT * FROM imports WHERE id=? AND kind='gl'", (import_id,)).fetchone()
        if not row: raise ValueError("GL import not found")
        supplied = all(row[k] is not None for k in ("expected_rows", "expected_debits", "expected_credits"))
        matches = supplied and row["accepted_rows"] == row["expected_rows"] and abs(row["control_debits"] - row["expected_debits"]) <= tolerance and abs(row["control_credits"] - row["expected_credits"]) <= tolerance
        return {"import_id": import_id, "supplied": supplied, "matches": matches, "accepted_rows": row["accepted_rows"], "expected_rows": row["expected_rows"], "control_debits": row["control_debits"], "expected_debits": row["expected_debits"], "control_credits": row["control_credits"], "expected_credits": row["expected_credits"], "reconciled_at": row["reconciled_at"]}

    def population_acknowledged(self):
        row = self.conn.execute("SELECT COUNT(*) FROM imports WHERE kind='gl' AND acknowledged_at IS NULL").fetchone()
        return row[0] == 0 and self.conn.execute("SELECT COUNT(*) FROM imports WHERE kind='gl'").fetchone()[0] > 0

    def set_review_lock(self, actor: str):
        self.set_setting("review_locked", {"locked_at": time.time(), "locked_by": actor}, actor)

    def clear_review_lock(self, actor: str):
        # Additive reopening: keep the lock's history, just mark it reopened.
        prior = self.get_setting("review_locked", {})
        prior.update({"locked_at": None, "reopened_by": actor, "reopened_at": time.time()})
        self.set_setting("review_locked", prior, actor)

    def review_locked(self):
        return bool(self.get_setting("review_locked", {}).get("locked_at"))

    def close(self):
        self.conn.close()
