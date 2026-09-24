from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path


SCHEMA_VERSION = 1

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
  control_credits REAL, acknowledged_at REAL, acknowledged_by TEXT, acknowledgement_note TEXT,
  supersedes_import_id INTEGER REFERENCES imports(id)
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
CREATE TABLE IF NOT EXISTS review_set_events (
  id INTEGER PRIMARY KEY, event TEXT NOT NULL CHECK(event IN ('locked','reopened')),
  actor TEXT NOT NULL, reason TEXT NOT NULL, created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS review_set_events_latest ON review_set_events(id DESC);
CREATE TRIGGER IF NOT EXISTS review_set_events_no_update BEFORE UPDATE ON review_set_events
BEGIN SELECT RAISE(ABORT,'review-set events are append-only'); END;
CREATE TRIGGER IF NOT EXISTS review_set_events_no_delete BEFORE DELETE ON review_set_events
BEGIN SELECT RAISE(ABORT,'review-set events are append-only'); END;
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
CREATE TABLE IF NOT EXISTS analysis_signal_results (
  run_id INTEGER NOT NULL REFERENCES model_runs(id), ledger_id INTEGER NOT NULL REFERENCES ledger_entries(id),
  components_json TEXT NOT NULL, PRIMARY KEY(run_id, ledger_id)
);
CREATE TABLE IF NOT EXISTS exceptions (
  id INTEGER PRIMARY KEY, run_id INTEGER NOT NULL REFERENCES model_runs(id), ledger_id INTEGER NOT NULL REFERENCES ledger_entries(id),
  risk_score REAL NOT NULL, severity TEXT NOT NULL, reasons_json TEXT NOT NULL,
  evidence_json TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'open', UNIQUE(run_id, ledger_id)
);
CREATE TABLE IF NOT EXISTS reviews (
  id INTEGER PRIMARY KEY, exception_id INTEGER NOT NULL REFERENCES exceptions(id), reviewer TEXT NOT NULL,
  disposition TEXT NOT NULL CHECK(disposition IN ('open','cleared','follow_up','selected_for_testing')),
  note TEXT NOT NULL, created_at REAL NOT NULL, second_reviewer TEXT, second_note TEXT
);
CREATE INDEX IF NOT EXISTS reviews_exception_latest ON reviews(exception_id,id DESC);
CREATE TRIGGER IF NOT EXISTS reviews_sync_exception_status AFTER INSERT ON reviews
BEGIN
  UPDATE exceptions SET status=NEW.disposition WHERE id=NEW.exception_id;
END;
CREATE TRIGGER IF NOT EXISTS exceptions_status_matches_review BEFORE UPDATE OF status ON exceptions
WHEN NOT EXISTS (
  SELECT 1 FROM reviews WHERE exception_id=OLD.id AND disposition=NEW.status ORDER BY id DESC LIMIT 1
)
BEGIN
  SELECT RAISE(ABORT,'exception status must match latest review');
END;
CREATE TRIGGER IF NOT EXISTS reviews_no_update BEFORE UPDATE ON reviews
BEGIN SELECT RAISE(ABORT,'reviews are append-only'); END;
CREATE TRIGGER IF NOT EXISTS reviews_no_delete BEFORE DELETE ON reviews
BEGIN SELECT RAISE(ABORT,'reviews are append-only'); END;
CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY, created_at REAL NOT NULL, actor TEXT NOT NULL, action TEXT NOT NULL,
  target_type TEXT NOT NULL, target_id TEXT NOT NULL, detail_json TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS audit_log_no_update BEFORE UPDATE ON audit_log
BEGIN SELECT RAISE(ABORT,'audit log is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_log_no_delete BEFORE DELETE ON audit_log
BEGIN SELECT RAISE(ABORT,'audit log is append-only'); END;
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
CREATE TABLE IF NOT EXISTS model_registry (
  id INTEGER PRIMARY KEY, name TEXT UNIQUE, model_type TEXT, feature_schema_json TEXT, owner TEXT,
  status TEXT, performance_json TEXT, approved_by TEXT, created_at REAL, created_by TEXT
);
"""


class Store:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path, timeout=5.0)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript(SCHEMA)
        self._migrate()
        self.conn.commit()

    def _migrate(self):
        """Apply additive schema changes and reject partial migrations loudly."""
        current_version = self.conn.execute("PRAGMA user_version").fetchone()[0]
        if current_version > SCHEMA_VERSION:
            raise RuntimeError(f"database schema {current_version} is newer than supported schema {SCHEMA_VERSION}")
        migrations = [
            ("ledger_entries", "vendor", "TEXT"),
            ("imports", "expected_rows", "INTEGER"), ("imports", "expected_debits", "REAL"),
            ("imports", "expected_credits", "REAL"), ("imports", "reconciled_at", "REAL"),
            ("imports", "reconciled_by", "TEXT"), ("imports", "reconciliation_note", "TEXT"),
            ("imports", "supersedes_import_id", "INTEGER REFERENCES imports(id)"),
            ("exceptions", "assigned_to", "TEXT"), ("exceptions", "due_date", "TEXT"),
            ("exceptions", "materiality_band", "TEXT"),
            ("model_runs", "model_name", "TEXT"), ("model_runs", "validation_status", "TEXT"),
            ("reviews", "second_reviewer", "TEXT"), ("reviews", "second_note", "TEXT"),
        ]
        for table, column, definition in migrations:
            columns = {row["name"] for row in self.conn.execute(f"PRAGMA table_info({table})")}
            if column not in columns:
                self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

        # Keep the materialized status cache aligned with immutable review history.
        self.conn.execute("""UPDATE exceptions SET status=(
            SELECT disposition FROM reviews WHERE reviews.exception_id=exceptions.id ORDER BY reviews.id DESC LIMIT 1
        ) WHERE EXISTS(SELECT 1 FROM reviews WHERE reviews.exception_id=exceptions.id)""")

        # Older databases used a mutable settings row. Preserve that state once as history.
        legacy = self.get_setting("review_locked", None)
        has_event = self.conn.execute("SELECT 1 FROM review_set_events LIMIT 1").fetchone()
        if legacy and not has_event:
            if legacy.get("locked_at"):
                event, actor, changed_at = "locked", legacy.get("locked_by") or "legacy", legacy["locked_at"]
            elif legacy.get("reopened_at"):
                event, actor, changed_at = "reopened", legacy.get("reopened_by") or "legacy", legacy["reopened_at"]
            else:
                event = None
            if event:
                self.conn.execute(
                    "INSERT INTO review_set_events(event,actor,reason,created_at) VALUES(?,?,?,?)",
                    (event, actor, "Migrated legacy review-lock setting", changed_at),
                )
        self.conn.execute(f"PRAGMA user_version={SCHEMA_VERSION}")

    def schema_version(self) -> int:
        return self.conn.execute("PRAGMA user_version").fetchone()[0]

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

    def existing_import(self, kind: str, sha256: str):
        return self.conn.execute(
            "SELECT * FROM imports WHERE kind=? AND sha256=? ORDER BY id DESC LIMIT 1", (kind, sha256)
        ).fetchone()

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

    def review_set_state(self):
        row = self.conn.execute("SELECT * FROM review_set_events ORDER BY id DESC LIMIT 1").fetchone()
        if row is None:
            return {"locked": False, "event": None, "actor": None, "reason": None, "changed_at": None}
        return {
            "locked": row["event"] == "locked", "event": row["event"], "actor": row["actor"],
            "reason": row["reason"], "changed_at": row["created_at"],
        }

    def review_set_history(self):
        return [dict(row) for row in self.conn.execute("SELECT * FROM review_set_events ORDER BY id")]

    def review_locked(self):
        return self.review_set_state()["locked"]

    def close(self):
        self.conn.close()
