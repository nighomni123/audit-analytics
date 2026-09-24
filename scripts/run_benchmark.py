"""Run the reproducible synthetic Audit Analytics benchmark.

This harness measures the current checkout without contacting external services or
using client data. It writes machine-readable evidence under benchmark-results/.
"""
from __future__ import annotations

import argparse
import array
import csv
import hashlib
import json
import math
import os
import platform
import random
import re
import shutil
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import threading
import time
import tracemalloc
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Any
from unittest.mock import patch

from fastapi.testclient import TestClient

from audit_analytics.analytics import _benford, analyze
from audit_analytics.api.app import create_app
from audit_analytics.importer import DuplicateImportError, import_coa, import_gl, preview_gl
from audit_analytics.reports import engagement_summary, export_workpaper, write_engagement_report
from audit_analytics.sampling import create_sample
from audit_analytics.semantic import _cosine, _entries, _text, embed_ledger, similar_transactions, tokens
from audit_analytics.semantic_risk import _calculate, _config, population_hash, semantic_profile
from audit_analytics.store import Store
from audit_analytics.workflow import (
    WorkflowError,
    acknowledge_population,
    assign_exception,
    configure_engagement,
    create_engagement,
    lock_review_set,
    record_review,
    reopen_review_set,
    run_analysis,
)

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "benchmark-results"
SEED = 20260924
PERIOD_END = "2026-03-31"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(name: str, value: Any) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / name).write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def timed(callable_):
    tracemalloc.start()
    started = time.perf_counter()
    try:
        value = callable_()
        elapsed = time.perf_counter() - started
        _, peak = tracemalloc.get_traced_memory()
        return value, {"seconds": elapsed, "peak_python_bytes": peak}
    finally:
        tracemalloc.stop()


def command(args: list[str], cwd: Path = ROOT, timeout: int = 300, env: dict[str, str] | None = None) -> dict[str, Any]:
    started = time.perf_counter()
    merged = os.environ.copy()
    merged.setdefault("UV_CACHE_DIR", "/tmp/audit-benchmark-uv")
    merged.setdefault("XDG_CACHE_HOME", "/tmp/audit-benchmark-xdg")
    merged.setdefault("npm_config_cache", "/tmp/audit-benchmark-npm")
    if env:
        merged.update(env)
    try:
        proc = subprocess.run(args, cwd=cwd, env=merged, text=True, capture_output=True, timeout=timeout)
        return {"command": args, "returncode": proc.returncode, "seconds": time.perf_counter() - started, "stdout": proc.stdout[-12000:], "stderr": proc.stderr[-12000:]}
    except Exception as exc:
        return {"command": args, "returncode": None, "seconds": time.perf_counter() - started, "error": f"{type(exc).__name__}: {exc}"}


def environment() -> dict[str, Any]:
    def run(args):
        try:
            return subprocess.run(args, text=True, capture_output=True, timeout=10).stdout.strip()
        except Exception as exc:
            return f"unavailable: {exc}"
    try:
        import numpy
        numpy_version = numpy.__version__
    except Exception:
        numpy_version = "unavailable"
    try:
        import fastapi
        fastapi_version = fastapi.__version__
    except Exception:
        fastapi_version = "unavailable"
    return {
        "commit": run(["git", "rev-parse", "HEAD"]),
        "status": run(["git", "status", "--short", "--branch"]),
        "python": sys.version,
        "python3": run(["python3", "--version"]),
        "uv": run(["uv", "--version"]),
        "node": run(["node", "--version"]),
        "npm": run(["npm", "--version"]),
        "os": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "ram_bytes": int(run(["sysctl", "-n", "hw.memsize"]) or 0) if platform.system() == "Darwin" else None,
        "sqlite": run(["python3", "-c", "import sqlite3; print(sqlite3.sqlite_version)"]),
        "numpy": numpy_version,
        "fastapi": fastapi_version,
        "frontend_lock_sha256": sha256(ROOT / "frontend/package-lock.json"),
        "uv_lock_sha256": sha256(ROOT / "uv.lock"),
        "ollama_binary": shutil.which("ollama"),
        "ollama_probe": run(["curl", "-sS", "--max-time", "2", "http://127.0.0.1:11434/api/version"]),
    }


def make_gl(path: Path, size: int, seed: int = SEED) -> dict[str, Any]:
    rng = random.Random(seed)
    fields = ["entry_id", "posting_date", "account_code", "amount", "description", "preparer", "reference", "entity"]
    total = 0.0
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for index in range(size):
            amount = round(100.123 + (index % 97) * 1.371 + rng.random() * 0.01, 2)
            total += amount
            writer.writerow({"entry_id": f"B{index + 1:07d}", "posting_date": "2025-02-15", "account_code": f"{(index % 20) + 1000}", "amount": f"{amount:.2f}", "description": f"routine synthetic operation {index % 31}", "preparer": f"U{index % 8}", "reference": f"R{index + 1}", "entity": "HQ"})
    return {"path": str(path), "size": size, "sha256": sha256(path), "control_debits": round(total, 2), "control_credits": 0.0, "seed": seed}


def seed_store(directory: Path, rows: int = 20, source: Path | None = None, owner: str = "manager") -> tuple[Store, Path]:
    store = Store(str(directory / "audit.db"))
    create_engagement(store, "Synthetic Benchmark", "2025-04-01:2026-03-31", owner)
    store.add_user("reviewer", "reviewer", owner)
    store.add_user("second", "quality_reviewer", owner)
    store.conn.commit()
    if source is None:
        source = directory / "synthetic.csv"
        make_gl(source, rows)
    import_gl(store, str(source), owner)
    return store, source



def import_benchmark(sizes: list[int]) -> dict[str, Any]:
    results = []
    for size in sizes:
        with tempfile.TemporaryDirectory(prefix=f"benchmark-import-{size}-") as directory_text:
            directory = Path(directory_text)
            source = directory / "gl.csv"
            dataset = make_gl(source, size)
            store = Store(str(directory / "audit.db"))
            create_engagement(store, "Synthetic Import", "2025-04-01:2026-03-31", "manager")
            value, timing = timed(lambda: import_gl(store, str(source), "manager"))
            results.append({"size": size, "dataset": dataset, "import_id": value[0], "accepted": value[1], "rejected": value[2], "control_debits": value[3], "control_credits": value[4], "db_bytes": (directory / "audit.db").stat().st_size, "timing": timing, "rows_per_second": value[1] / timing["seconds"] if timing["seconds"] else None})
            store.close()
    return {"seed": SEED, "results": results}


def pipeline_performance(sizes: list[int]) -> dict[str, Any]:
    results = []
    for size in sizes:
        with tempfile.TemporaryDirectory(prefix=f"benchmark-pipeline-{size}-") as directory_text:
            directory = Path(directory_text)
            source = directory / "gl.csv"
            dataset = make_gl(source, size)
            store = Store(str(directory / "audit.db"))
            create_engagement(store, "Synthetic Pipeline", "2025-04-01:2026-03-31", "manager")
            store.add_user("reviewer", "reviewer", "manager")
            imported, import_timing = timed(lambda: import_gl(store, str(source), "manager"))
            acknowledge_population(store, "reviewer", "synthetic control totals", override_reconciliation=True)
            run, analysis_timing = timed(lambda: analyze(store, "manager", False))
            sample_id, sample_count = create_sample(store, f"perf-{size}", "manager", run, risk_count=5, random_count=5, seed=SEED)
            export_value, export_timing = timed(lambda: export_workpaper(store, str(directory / "workpaper.csv"), "manager"))
            report_value, report_timing = timed(lambda: write_engagement_report(store, str(directory / "report.html"), "manager"))
            api = create_app(store.path)
            client = TestClient(api)
            request_times = []
            for path in ("/api/status", "/api/exceptions?limit=25", "/api/similar?q=routine%20synthetic"):
                started = time.perf_counter(); response = client.get(path); request_times.append({"path": path, "status": response.status_code, "seconds": time.perf_counter() - started})
            client.close()
            isolation_timing = None
            if size <= 10000:
                _, isolation_timing = timed(lambda: analyze(store, "manager", True))
            results.append({"size": size, "dataset": dataset, "import": {"accepted": imported[1], "rejected": imported[2], "timing": import_timing}, "analysis": {"run": run, "exceptions": store.conn.execute("SELECT COUNT(*) FROM exceptions WHERE run_id=?", (run,)).fetchone()[0], "timing": analysis_timing, "isolation_timing": isolation_timing}, "sampling": {"sample_id": sample_id, "count": sample_count}, "export": {"rows": export_value[2], "timing": export_timing}, "report": {"timing": report_timing}, "api_requests": request_times, "db_bytes": store.path.stat().st_size})
            store.close()
    return {"seed": SEED, "results": results}


def adversarial_analysis_probe(sizes: list[int]) -> dict[str, Any]:
    results = []
    for size in sizes:
        with tempfile.TemporaryDirectory(prefix=f"benchmark-adversarial-{size}-") as directory_text:
            directory = Path(directory_text)
            source = directory / "same-bucket.csv"
            with source.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=["entry_id", "posting_date", "account_code", "amount", "description", "preparer"])
                writer.writeheader()
                for index in range(size):
                    writer.writerow({"entry_id": f"ADV{index}", "posting_date": "2025-02-14", "account_code": "1000", "amount": "100", "description": f"same bucket {index}", "preparer": "U1"})
            store = Store(str(directory / "audit.db")); create_engagement(store, "Synthetic Adversarial", "2025-04-01:2026-03-31", "manager"); import_gl(store, str(source), "manager"); acknowledge_population(store, "manager", "synthetic override", override_reconciliation=True)
            _, timing = timed(lambda: analyze(store, "manager", False))
            results.append({"size": size, "same_account_amount_bucket": True, "timing": timing, "exceptions": store.conn.execute("SELECT COUNT(*) FROM exceptions WHERE run_id=(SELECT max(id) FROM model_runs)").fetchone()[0]})
            store.close()
    return {"note": "Adversarial same-account/same-amount bucket exposes the reversal comparison ceiling.", "results": results}


def api_latency_benchmark(sizes: list[int]) -> dict[str, Any]:
    results = []
    for size in sizes:
        with tempfile.TemporaryDirectory(prefix=f"benchmark-api-latency-{size}-") as directory_text:
            directory = Path(directory_text); source = directory / "gl.csv"; make_gl(source, size)
            store = Store(str(directory / "audit.db")); create_engagement(store, "Synthetic Latency", "2025-04-01:2026-03-31", "manager"); store.add_user("reviewer", "reviewer", "manager"); import_gl(store, str(source), "manager"); acknowledge_population(store, "reviewer", "synthetic", override_reconciliation=True); analyze(store, "manager", False)
            client = TestClient(create_app(store.path)); paths = {"status": "/api/status", "exceptions": "/api/exceptions?limit=25", "similar": "/api/similar?q=routine%20synthetic"}; samples = {name: [] for name in paths}; statuses = {name: [] for name in paths}
            for _ in range(10):
                for name, path in paths.items():
                    started = time.perf_counter(); response = client.get(path); samples[name].append(time.perf_counter() - started); statuses[name].append(response.status_code)
            client.close()
            results.append({"size": size, "latency": {name: {"p50_seconds": statistics.median(values), "p95_seconds": sorted(values)[max(0, int(len(values) * .95) - 1)], "samples": values, "statuses": statuses[name]} for name, values in samples.items()}})
            store.close()
    return {"seed": SEED, "results": results}


def malformed_import_benchmark() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="benchmark-malformed-") as directory_text:
        directory = Path(directory_text)
        path = directory / "malformed.csv"
        rows = [
            {"entry_id": "OK1", "posting_date": "2025-02-15", "account_code": "1000", "debit": "10", "credit": "0", "description": "valid"},
            {"entry_id": "", "posting_date": "2025-02-15", "account_code": "1000", "debit": "10", "credit": "0", "description": "missing id"},
            {"entry_id": "BAD-DATE", "posting_date": "not-a-date", "account_code": "1000", "debit": "10", "credit": "0", "description": "bad date"},
            {"entry_id": "NEG-D", "posting_date": "2025-02-15", "account_code": "1000", "debit": "-1", "credit": "0", "description": "negative debit"},
            {"entry_id": "NEG-C", "posting_date": "2025-02-15", "account_code": "1000", "debit": "0", "credit": "-1", "description": "negative credit"},
            {"entry_id": "BOTH", "posting_date": "2025-02-15", "account_code": "1000", "debit": "1", "credit": "1", "description": "both"},
            {"entry_id": "NEITHER", "posting_date": "2025-02-15", "account_code": "1000", "debit": "0", "credit": "0", "description": "neither"},
            {"entry_id": "ZERO", "posting_date": "2025-02-15", "account_code": "1000", "amount": "0", "description": "zero amount"},
            {"entry_id": "UNICODE", "posting_date": "2025-02-15", "account_code": "1000", "amount": "12.5", "description": "é中文 😀"},
            {"entry_id": "LONG", "posting_date": "2025-02-15", "account_code": "1000", "amount": "13.5", "description": "long " + ("描述" * 5000)},
            {"entry_id": "HUGE", "posting_date": "2025-02-15", "account_code": "1000", "amount": "999999999999.99", "description": "very large amount"},
        ]
        fields = ["entry_id", "posting_date", "account_code", "debit", "credit", "amount", "description"]
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        store = Store(str(directory / "audit.db"))
        create_engagement(store, "Synthetic Malformed", "2025-04-01:2026-03-31", "manager")
        value = import_gl(store, str(path), "manager")
        rejected = [dict(row) for row in store.conn.execute("SELECT source_row,reason,raw_json FROM rejected_rows ORDER BY source_row")]
        accepted = [dict(row) for row in store.conn.execute("SELECT entry_id,raw_json,source_hash,source_row FROM ledger_entries ORDER BY id")]
        aliases = directory / "aliases.csv"
        aliases.write_text("Voucher Number,Posting Dt,GL Code,Amount,Doc Type\nA1,2025-02-15,1000,12.5,Invoice\n", encoding="utf-8")
        mapping = {"entry_id": "Voucher Number", "posting_date": "Posting Dt", "account_code": "GL Code", "amount": "Amount", "description": "Doc Type"}
        preview = preview_gl(str(aliases), mapping)
        duplicate = directory / "duplicate.csv"
        duplicate.write_text("entry_id,posting_date,account_code,amount\nDUP,2025-02-15,1000,1\nDUP,2025-02-15,1000,1\n", encoding="utf-8")
        store2 = Store(str(directory / "second.db"))
        create_engagement(store2, "Synthetic Duplicate Rows", "2025-04-01:2026-03-31", "manager")
        dup = import_gl(store2, str(duplicate), "manager")
        duplicate_ids = [row[0] for row in store2.conn.execute("SELECT entry_id FROM ledger_entries ORDER BY id")]
        store.close(); store2.close()
        return {"import": {"accepted": value[1], "rejected": value[2], "debits": value[3], "credits": value[4]}, "rejected_rows": rejected, "accepted_rows": accepted, "aliases_preview": preview, "duplicate_source_rows": {"accepted": dup[1], "rejected": dup[2], "entry_ids": duplicate_ids}}


def idempotence_benchmark() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="benchmark-idempotence-") as directory_text:
        directory = Path(directory_text)
        source = directory / "gl.csv"
        dataset = make_gl(source, 30, SEED + 1)
        store = Store(str(directory / "audit.db"))
        create_engagement(store, "Synthetic Lineage", "2025-04-01:2026-03-31", "manager")
        store.add_user("reviewer", "reviewer", "manager")
        first = import_gl(store, str(source), "manager")
        duplicate = {"blocked": False}
        try:
            import_gl(store, str(source), "manager")
        except DuplicateImportError as exc:
            duplicate = {"blocked": True, "existing_import_id": exc.existing_import_id}
        reimport = import_gl(store, str(source), "manager", reimport=True)
        modified = directory / "modified.csv"
        modified.write_text(source.read_text(encoding="utf-8").replace("B0000001", "B0000001-CHANGED"), encoding="utf-8")
        changed = import_gl(store, str(modified), "manager")
        rows = [dict(row) for row in store.conn.execute("SELECT id,sha256,supersedes_import_id,accepted_rows FROM imports ORDER BY id")]
        # The second import is a separate population until acknowledged; run IDs
        # therefore record the lineage without collapsing versions.
        first_run = None
        blocked = None
        try:
            analyze(store, "manager", False)
        except Exception as exc:
            blocked = str(exc)
        acknowledge_population(store, "reviewer", "synthetic control totals accepted", override_reconciliation=True)
        first_run = analyze(store, "manager", False)
        store.close()
        return {"dataset": dataset, "first": {"id": first[0], "accepted": first[1]}, "duplicate": duplicate, "reimport": {"id": reimport[0], "accepted": reimport[1]}, "modified": {"id": changed[0], "accepted": changed[1]}, "lineage_rows": rows, "analysis_blocked_before_ack": blocked, "first_run": first_run}


def reconciliation_benchmark() -> dict[str, Any]:
    cases = []
    for name, expected_rows, expected_debits, override, should_analyze in [
        ("exact", 5, 15.0, False, True),
        ("tolerance", 5, 15.004, False, True),
        ("material_mismatch", 5, 99.0, False, False),
        ("override", 5, 99.0, True, True),
    ]:
        with tempfile.TemporaryDirectory(prefix=f"benchmark-recon-{name}-") as directory_text:
            directory = Path(directory_text)
            source = directory / "gl.csv"
            source.write_text("entry_id,posting_date,account_code,amount\n" + "\n".join(f"R{i},2025-02-15,1000,{3 if i < 2 else 3.0}" for i in range(5)), encoding="utf-8")
            store = Store(str(directory / "audit.db"))
            create_engagement(store, "Synthetic Reconciliation", "2025-04-01:2026-03-31", "manager")
            store.add_user("reviewer", "reviewer", "manager")
            import_gl(store, str(source), "manager", expected_rows=expected_rows, expected_debits=expected_debits, expected_credits=0)
            blocked = None
            try:
                analyze(store, "manager", False)
            except Exception as exc:
                blocked = str(exc)
            ack_error = None
            analyzed = False
            try:
                acknowledge_population(store, "reviewer", "documented synthetic reconciliation", override)
                analyzed = bool(analyze(store, "manager", False))
            except Exception as exc:
                ack_error = str(exc)
            cases.append({"case": name, "matches": store.reconciliation(1)["matches"], "analysis_blocked_before_ack": bool(blocked), "ack_error": ack_error, "analyzed": analyzed, "expected": should_analyze})
            store.close()
    return {"cases": cases}


def confusion(truth: set[str], predicted: set[str]) -> dict[str, Any]:
    tp = len(truth & predicted); fp = len(predicted - truth); fn = len(truth - predicted); tn = len(truth | predicted) - tp - fp - fn
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = 2 * precision * recall / (precision + recall) if precision is not None and recall is not None and precision + recall else None
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": precision, "recall": recall, "f1": f1}


def detector_rows(kind: str) -> tuple[list[dict[str, Any]], set[str]]:
    rows = []
    positives = set()
    for index in range(20):
        rows.append({"entry_id": f"{kind}-N{index}", "posting_date": "2025-02-14", "account_code": f"{(index % 4) + 1000}", "amount": f"{100.123 + index:.3f}", "description": f"routine {kind} {index}", "preparer": f"U{index % 4}", "reference": f"REF{index}"})
    if kind == "duplicate":
        rows.extend([{"entry_id": "duplicate-P1", "posting_date": "2025-03-01", "account_code": "2000", "amount": "222.333", "description": "same repeated entry", "preparer": "DUP", "reference": "DUP1"}, {"entry_id": "duplicate-P2", "posting_date": "2025-03-01", "account_code": "2000", "amount": "222.333", "description": "same repeated entry", "preparer": "DUP", "reference": "DUP2"}])
        positives.update({"duplicate-P1", "duplicate-P2"})
    elif kind == "round_amount":
        rows.append({"entry_id": "round-P", "posting_date": "2025-02-15", "account_code": "2000", "amount": "1000", "description": "round positive", "preparer": "U0", "reference": "ROUND"}); positives.add("round-P")
    elif kind == "period_end":
        rows.append({"entry_id": "period-P", "posting_date": PERIOD_END, "account_code": "2000", "amount": "222.333", "description": "period positive", "preparer": "U0", "reference": "PERIOD"}); positives.add("period-P")
    elif kind == "weekend":
        rows.append({"entry_id": "weekend-P", "posting_date": "2026-03-28", "account_code": "2000", "amount": "222.333", "description": "weekend positive", "preparer": "U0", "reference": "WEEKEND"}); positives.add("weekend-P")
    elif kind == "rare_account_preparer_pair":
        rows.append({"entry_id": "rare-P", "posting_date": "2025-02-15", "account_code": "9999", "amount": "222.333", "description": "rare positive", "preparer": "RAREUSER", "reference": "RARE"}); positives.add("rare-P")
    elif kind == "possible_reversal_within_30_days":
        rows.extend([{"entry_id": "reversal-P1", "posting_date": "2025-02-15", "account_code": "3000", "debit": "500", "credit": "0", "description": "reversal one", "preparer": "U1", "reference": "REV1"}, {"entry_id": "reversal-P2", "posting_date": "2025-02-20", "account_code": "3000", "debit": "0", "credit": "500", "description": "reversal two", "preparer": "U1", "reference": "REV2"}]); positives.update({"reversal-P1", "reversal-P2"})
    elif kind == "robust_account_peer_outlier":
        for index in range(8):
            rows.append({"entry_id": f"outlier-base-{index}", "posting_date": "2025-02-15", "account_code": "4000", "amount": f"{100 + index}.123", "description": "peer baseline", "preparer": "U2", "reference": f"BASE{index}"})
        rows.append({"entry_id": "outlier-P", "posting_date": "2025-02-15", "account_code": "4000", "amount": "987654.321", "description": "peer outlier", "preparer": "U2", "reference": "OUTLIER"}); positives.add("outlier-P")
    elif kind == "fiscal_period_end":
        rows.append({"entry_id": "fiscal-P", "posting_date": "2026-03-31", "account_code": "2000", "amount": "222.333", "description": "fiscal exact-date positive", "preparer": "U0", "reference": "FISCAL1"})
        rows.append({"entry_id": "fiscal-P2", "posting_date": "2026-03-30", "account_code": "2000", "amount": "222.334", "description": "fiscal preceding-day positive", "preparer": "U0", "reference": "FISCAL2"})
        positives.update({"fiscal-P", "fiscal-P2"})
    return rows, positives


def deterministic_benchmark() -> dict[str, Any]:
    detector_map = {"duplicate": "duplicate_or_repeated_entry", "round_amount": "round_amount", "period_end": "period_end_posting", "weekend": "weekend_posting", "rare_account_preparer_pair": "rare_account_preparer_pair", "possible_reversal_within_30_days": "possible_reversal_within_30_days", "robust_account_peer_outlier": "robust_account_peer_outlier", "fiscal_period_end": "fiscal_period_end"}
    results = []
    for kind, reason in detector_map.items():
        with tempfile.TemporaryDirectory(prefix=f"benchmark-detector-{kind}-") as directory_text:
            directory = Path(directory_text)
            rows, positives = detector_rows(kind)
            path = directory / "population.csv"
            fields = sorted({key for row in rows for key in row})
            with path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader(); writer.writerows(rows)
            store = Store(str(directory / "audit.db"))
            create_engagement(store, "Synthetic Detector", "2025-04-01:2026-03-31", "manager")
            store.conn.execute("INSERT INTO settings(key,value_json,updated_at,updated_by) VALUES('fiscal_calendar','[\"2026-03-31\"]',1,'manager')")
            store.conn.commit()
            import_gl(store, str(path), "manager")
            store.conn.execute("UPDATE imports SET acknowledged_at=1,acknowledged_by='manager',acknowledgement_note='synthetic'")
            store.conn.commit()
            run = analyze(store, "manager", False)
            predicted = {row[0] for row in store.conn.execute("SELECT l.entry_id FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id WHERE e.run_id=? AND e.reasons_json LIKE ?", (run, f"%{reason}%"))}
            all_ids = {row["entry_id"] for row in rows}
            metrics = confusion(positives, predicted)
            results.append({"detector": kind, "reason": reason, "population": len(all_ids), "positives": sorted(positives), "predicted": sorted(predicted), "metrics": metrics, "missed": sorted(positives - predicted), "false_positive_examples": sorted(predicted - positives)[:10]})
            store.close()
    # Benford is a population-level indicator, not an entry classifier.
    benford_inputs = [{"signed_amount": value} for value in [1, 2, 3, 4, 5, 6, 7, 8, 9] * 20]
    benford = _benford(benford_inputs)
    return {"detectors": results, "benford": {"input_n": len(benford_inputs), "result": benford, "classification": "population-level applicability/indicator; no row-level TP/FP claims"}}


def ground_truth_benchmark() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="benchmark-ground-truth-") as directory_text:
        directory = Path(directory_text)
        source = ROOT / "examples/demo-journal-entries.csv"
        store = Store(str(directory / "audit.db"))
        create_engagement(store, "Synthetic Ground Truth", "2025-04-01:2026-03-31", "manager")
        store.add_user("reviewer", "reviewer", "manager")
        value = import_gl(store, str(source), "manager")
        store.conn.execute("UPDATE imports SET acknowledged_at=1,acknowledged_by='manager',acknowledgement_note='synthetic'")
        store.conn.commit()
        run = analyze(store, "manager", False)
        labels = list(csv.DictReader((ROOT / "examples/demo-ground-truth.csv").open(newline="", encoding="utf-8")))
        mapping = {"round_amount": "round_amount", "benford_vendor": "robust_account_peer_outlier", "off_hours": None}
        by_detector = {}
        for label in labels:
            entry = label["entry_id"]; reason = mapping[label["anomaly_type"]]
            row = store.conn.execute("SELECT e.reasons_json,e.risk_score,e.severity FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id WHERE e.run_id=? AND l.entry_id=?", (run, entry)).fetchone()
            detected = bool(row and (reason is None or reason in json.loads(row[0])))
            by_detector.setdefault(label["anomaly_type"], {"labels": [], "detected": [], "missed": []})["labels"].append(entry)
            (by_detector[label["anomaly_type"]]["detected"] if detected else by_detector[label["anomaly_type"]]["missed"]).append(entry)
        for detector, item in by_detector.items():
            item["detected_count"] = len(item["detected"]); item["label_count"] = len(item["labels"])
        all_detected = {row[0] for row in store.conn.execute("SELECT l.entry_id FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id WHERE e.run_id=?", (run,))}
        score_rows = [dict(row) for row in store.conn.execute("SELECT e.risk_score,e.severity,l.entry_id FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id WHERE e.run_id=? ORDER BY e.risk_score DESC,e.id", (run,))]
        positives = {label["entry_id"] for label in labels}
        precision_at = {str(k): (len(positives & {row["entry_id"] for row in score_rows[:k]}) / min(k, len(positives)) if k else None) for k in (10, 25, 50, 100)}
        store.close()
        return {"dataset_sha256": sha256(source), "rows": value[1], "run": run, "labels": labels, "by_detector": by_detector, "detected_exception_count": len(score_rows), "precision_at_k": precision_at, "score_distribution": {"min": min((row["risk_score"] for row in score_rows), default=None), "max": max((row["risk_score"] for row in score_rows), default=None), "mean": statistics.mean(row["risk_score"] for row in score_rows) if score_rows else None, "severity_counts": dict(Counter(row["severity"] for row in score_rows))}, "off_hours_note": "The schema stores posting dates, not posting timestamps; off_hours is not observable by the current importer/detectors."}


def materiality_sampling_benchmark() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="benchmark-materiality-") as directory_text:
        directory = Path(directory_text)
        path = directory / "materiality.csv"
        amounts = [50, 100, 350, 500, 1000]
        rows = [{"entry_id": f"M{index}", "posting_date": "2025-02-15", "account_code": "1000", "amount": str(amount), "description": "materiality boundary", "preparer": "U1", "reference": f"M{index}"} for index, amount in enumerate(amounts)]
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
        store = Store(str(directory / "audit.db")); create_engagement(store, "Synthetic Materiality", "2025-04-01:2026-03-31", "manager"); store.add_user("reviewer", "reviewer", "manager")
        import_gl(store, str(path), "manager")
        store.conn.execute("UPDATE imports SET acknowledged_at=1,acknowledged_by='manager',acknowledgement_note='synthetic'"); store.conn.commit()
        base_run = analyze(store, "manager", False)
        baseline = [dict(row) for row in store.conn.execute("SELECT l.entry_id,e.risk_score,e.severity,e.materiality_band FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id WHERE e.run_id=? ORDER BY l.entry_id", (base_run,))]
        store.set_setting("materiality", {"overall": 500, "performance": 350}, "manager"); store.conn.commit()
        band_run = analyze(store, "manager", False)
        banded = [dict(row) for row in store.conn.execute("SELECT l.entry_id,e.risk_score,e.severity,e.materiality_band FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id WHERE e.run_id=? ORDER BY l.entry_id", (band_run,))]
        sample_a, count_a = create_sample(store, "same-seed-a", "manager", base_run, risk_count=0, random_count=3, seed=17)
        sample_b, count_b = create_sample(store, "same-seed-b", "manager", base_run, risk_count=0, random_count=3, seed=17)
        items_a = [row[0] for row in store.conn.execute("SELECT ledger_id FROM sample_items WHERE sample_set_id=? ORDER BY ledger_id", (sample_a,))]
        items_b = [row[0] for row in store.conn.execute("SELECT ledger_id FROM sample_items WHERE sample_set_id=? ORDER BY ledger_id", (sample_b,))]
        store.close()
        return {"amounts": amounts, "baseline": baseline, "with_materiality": banded, "scores_unchanged": {a["entry_id"]: (a["risk_score"], a["severity"]) for a in baseline} == {a["entry_id"]: (a["risk_score"], a["severity"]) for a in banded}, "sample": {"same_seed_same_items": items_a == items_b, "count_a": count_a, "count_b": count_b, "items_a": items_a, "items_b": items_b, "duplicates": len(items_a) != len(set(items_a))}}


class FixedEmbedder:
    digest = "benchmark-fixed-digest"
    def __init__(self, *args, **kwargs): pass
    def identity(self): return {"digest": self.digest, "name": "fixed", "runtime_version": "benchmark"}
    def embed(self, texts):
        result = []
        for text in texts:
            low = str(text).lower()
            if "repair" in low: result.append(array.array("f", [1.0, 0.0, 0.0, 0.0]))
            elif "fee" in low or "advis" in low: result.append(array.array("f", [0.0, 1.0, 0.0, 0.0]))
            elif "payroll" in low or "wage" in low or "salar" in low: result.append(array.array("f", [0.0, 0.0, 1.0, 0.0]))
            else: result.append(array.array("f", [0.0, 0.0, 0.0, 1.0]))
        return result


def token_rank(store: Store, query: str) -> list[dict[str, Any]]:
    rows = _entries(store); query_tokens = tokens(query); frequencies = Counter(token for row in rows for token in tokens(_text(row))); n = max(1, len(rows)); scored = []
    for row in rows:
        entry_tokens = tokens(_text(row)); union = query_tokens | entry_tokens
        shared = sum(math.log((n + 1) / (frequencies[token] + 1)) + 1 for token in query_tokens & entry_tokens)
        total = sum(math.log((n + 1) / (frequencies[token] + 1)) + 1 for token in union)
        score = shared / total if total else 0
        if score: scored.append({"ledger_id": row["id"], "score": score})
    return sorted(scored, key=lambda item: (-item["score"], item["ledger_id"]))


def missing_data_benchmark() -> dict[str, Any]:
    fields = ["description", "vendor", "preparer", "entity", "reference", "document_date", "is_manual"]
    results = []
    for rate in (0, 10, 25, 50, 90):
        with tempfile.TemporaryDirectory(prefix=f"benchmark-missing-{rate}-") as directory_text:
            directory = Path(directory_text)
            path = directory / "missing.csv"
            rng = random.Random(SEED + rate)
            rows = []
            for index in range(200):
                row = {"entry_id": f"MS{index}", "posting_date": "2025-02-14", "account_code": f"{(index % 4) + 1000}", "amount": f"{100.123 + index:.3f}", "description": "routine coverage", "vendor": "V1", "preparer": "U1", "reference": f"R{index}", "entity": "HQ", "document_date": "2025-02-01", "is_manual": "false"}
                for field in fields:
                    if rng.randrange(100) < rate:
                        row[field] = ""
                rows.append(row)
            with path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
            store = Store(str(directory / "audit.db")); create_engagement(store, "Synthetic Missingness", "2025-04-01:2026-03-31", "manager"); store.add_user("reviewer", "reviewer", "manager"); import_gl(store, str(path), "manager"); store.conn.execute("UPDATE imports SET acknowledged_at=1"); store.conn.commit(); run = analyze(store, "manager", False)
            with patch("audit_analytics.semantic_risk.LocalEmbedder", FixedEmbedder):
                profile = semantic_profile(store, "fixed", actor="manager")
            exception_rows = [dict(row) for row in store.conn.execute("SELECT l.entry_id,e.risk_score,e.reasons_json,e.severity FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id WHERE e.run_id=? ORDER BY l.entry_id", (run,))]
            result = {"missing_rate_percent": rate, "exceptions": len(exception_rows), "exception_rows": exception_rows, "semantic_coverage": profile["summary"]["coverage"], "missing_counts": {field: sum(not (row[field] or "").strip() for row in rows) for field in fields}, "semantic_retrieval_exhaustive": profile["summary"]["retrieval"]["exhaustive"]}
            store.close(); results.append(result)
    return {"seed": SEED, "rates": results, "criterion": "missing data should lower applicability/coverage, not automatically increase deterministic risk"}


def semantic_benchmark() -> dict[str, Any]:
    fixture = ROOT / "examples/semantic/ledger.csv"
    with tempfile.TemporaryDirectory(prefix="benchmark-semantic-") as directory_text:
        directory = Path(directory_text)
        store = Store(str(directory / "audit.db")); create_engagement(store, "Synthetic Semantic", "2025-01-01:2025-12-31", "manager"); store.add_user("reviewer", "reviewer", "manager")
        import_gl(store, str(fixture), "manager"); import_coa(store, str(ROOT / "examples/semantic/coa.csv"), "manager")
        store.conn.execute("UPDATE imports SET acknowledged_at=1,acknowledged_by='manager',acknowledgement_note='synthetic'"); store.conn.commit()
        with patch("audit_analytics.semantic_risk.LocalEmbedder", FixedEmbedder):
            profile = semantic_profile(store, "fixed", actor="manager")
        with patch("audit_analytics.semantic.LocalEmbedder", FixedEmbedder):
            embed_ledger(store, "fixed", actor="manager")
        labels = {row["transaction_id"]: row for row in csv.DictReader((ROOT / "examples/semantic/labels.csv").open(newline="", encoding="utf-8"))}
        entries = {row["entry_id"]: row for row in csv.DictReader(fixture.open(newline="", encoding="utf-8"))}
        retrieval = {}
        for mode in ("token", "semantic", "max"):
            hits = {1: 0, 3: 0, 5: 0, 10: 0}; reciprocal = []; examples = {"token_only": [], "semantic_only": [], "both": [], "both_fail": []}
            for target_id, label in labels.items():
                expected = {value for value in (label.get("expected_related_group") or "").split(";") if value and value in entries}
                if not expected: continue
                query = entries[target_id]["description"]
                with patch("audit_analytics.semantic.LocalEmbedder", FixedEmbedder):
                    max_results = similar_transactions(store, query, limit=100, model="fixed")
                semantic_results = [row for row in max_results if row.get("semantic_score") is not None]
                semantic_results.sort(key=lambda row: (-row["semantic_score"], row["ledger_id"]))
                token_results = token_rank(store, query)
                result_map = {"token": token_results, "semantic": semantic_results, "max": max_results}[mode]
                ranked_ids = []
                for item in result_map:
                    row = next((candidate for candidate in store.conn.execute("SELECT entry_id FROM ledger_entries WHERE id=?", (item["ledger_id"],))), None)
                    if row: ranked_ids.append(row[0])
                ranked_ids = [value for value in ranked_ids if value != target_id]
                for k in hits:
                    hits[k] += len(expected & set(ranked_ids[:k]))
                rank = next((index + 1 for index, value in enumerate(ranked_ids) if value in expected), None)
                reciprocal.append(1 / rank if rank else 0)
                if mode == "max":
                    token_ids = [next((candidate[0] for candidate in store.conn.execute("SELECT entry_id FROM ledger_entries WHERE id=?", (item["ledger_id"],)) if candidate), None) for item in token_results if item["ledger_id"] != next(row[0] for row in store.conn.execute("SELECT id FROM ledger_entries WHERE entry_id=?", (target_id,)))]
                    semantic_ids = [next((candidate[0] for candidate in store.conn.execute("SELECT entry_id FROM ledger_entries WHERE id=?", (item["ledger_id"],)) if candidate), None) for item in semantic_results if item["ledger_id"] != next(row[0] for row in store.conn.execute("SELECT id FROM ledger_entries WHERE entry_id=?", (target_id,)))]
                    token_success = bool(expected & set(token_ids[:3])); semantic_success = bool(expected & set(semantic_ids[:3]))
                    key = "both" if token_success and semantic_success else "token_only" if token_success else "semantic_only" if semantic_success else "both_fail"
                    if len(examples[key]) < 5: examples[key].append({"target": target_id, "expected": sorted(expected), "token_top3": token_ids[:3], "semantic_top3": semantic_ids[:3]})
            denominator = sum(1 for label in labels.values() if label.get("expected_related_group"))
            retrieval[mode] = {"targets": denominator, "recall_at": {str(k): hits[k] / max(1, denominator * max(1, len(set((label.get("expected_related_group") or "").split(";"))))) for k in hits}, "mrr": statistics.mean(reciprocal) if reciprocal else None, "examples": examples}
        cluster_rows = store.conn.execute("SELECT l.entry_id,e.cluster_id FROM semantic_results e JOIN ledger_entries l ON l.id=e.ledger_id WHERE e.run_id=?", (profile["run_id"],)).fetchall()
        process_by_id = {key: value.get("expected_process") for key, value in labels.items()}
        clusters = defaultdict(list)
        for row in cluster_rows:
            if process_by_id.get(row["entry_id"]): clusters[row["cluster_id"]].append(process_by_id[row["entry_id"]])
        purity = []
        for values in clusters.values():
            purity.append(max(Counter(values).values()) / len(values))
        cache = {"first": {"embedded": profile["summary"]["embedded_count"], "cached": profile["summary"]["cached_count"]}}
        with patch("audit_analytics.semantic_risk.LocalEmbedder", FixedEmbedder):
            second = semantic_profile(store, "fixed", actor="manager")
        cache["second"] = {"embedded": second["summary"]["embedded_count"], "cached": second["summary"]["cached_count"]}
        store.conn.execute("UPDATE ledger_entries SET description='changed benchmark narration' WHERE entry_id='A1'"); store.conn.commit()
        with patch("audit_analytics.semantic_risk.LocalEmbedder", FixedEmbedder):
            modified = semantic_profile(store, "fixed", actor="manager")
        cache["modified"] = {"embedded": modified["summary"]["embedded_count"], "cached": modified["summary"]["cached_count"]}
        old_digest = FixedEmbedder.digest; FixedEmbedder.digest = "benchmark-other-digest"
        with patch("audit_analytics.semantic_risk.LocalEmbedder", FixedEmbedder):
            changed_digest = semantic_profile(store, "fixed", actor="manager")
        FixedEmbedder.digest = old_digest
        cache["changed_digest"] = {"embedded": changed_digest["summary"]["embedded_count"], "cached": changed_digest["summary"]["cached_count"]}
        store.close()
        return {"fixture_sha256": sha256(fixture), "profile": {"run_id": profile["run_id"], "status": profile["status"], "coverage": profile["summary"]["coverage"], "retrieval": profile["summary"]["retrieval"], "cluster_count": len(profile["summary"]["clusters"]), "cluster_sizes": [item["member_count"] for item in profile["summary"]["clusters"]]}, "retrieval": retrieval, "cluster_purity": statistics.mean(purity) if purity else None, "cache": cache, "ollama": "not available; fixed offline vectors only"}


def approximation_benchmark(sizes: list[int]) -> dict[str, Any]:
    results = []
    for size in sizes:
        rng = random.Random(SEED + size)
        entries = [{"id": index, "entry_id": f"S{index}", "posting_date": "2025-01-01", "account_code": "1000", "signed_amount": 100 + index % 10, "description": "repair" if index % 3 == 0 else "fees" if index % 3 == 1 else "payroll", "preparer": "U", "entity": "HQ", "vendor": "V", "reference": str(index)} for index in range(1, size + 1)]
        vectors = {entry["id"]: array.array("f", FixedEmbedder().embed(["Narration: " + entry["description"]])[0]) for entry in entries}
        cfg = _config({"candidate_limit": 64, "peer_limit": 5, "training_limit": 512, "clusters": 4})
        value, timing = timed(lambda: _calculate(entries, vectors, cfg))
        candidate_hits = {1: 0, 5: 0, 10: 0}; evaluated = 0
        by_id = {entry["id"]: entry for entry in entries}
        for result in value[0]:
            ledger_id = result[0]
            comparison = result[4]["comparisons"].get("peer_similarity", {})
            candidates = set(comparison.get("candidate_ids", []))
            exact = sorted((other for other in vectors if other != ledger_id), key=lambda other: (-_cosine(vectors[ledger_id], vectors[other]), other))[:10]
            evaluated += 1
            for k in candidate_hits:
                candidate_hits[k] += len(set(exact[:k]) & candidates) / max(1, min(k, len(exact)))
        results.append({"size": size, "evaluated": evaluated, "candidate_recall_at": {str(k): value / max(1, evaluated) for k, value in candidate_hits.items()}, "timing": timing})
    return {"seed": SEED, "results": results}


def governance_benchmark() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="benchmark-governance-") as directory_text:
        directory = Path(directory_text)
        governance_rows = [{"entry_id": f"GB{index}", "posting_date": "2025-02-14", "account_code": "4000", "amount": f"{100.123 + index:.3f}", "description": "governance peer baseline", "preparer": "U2"} for index in range(8)]
        governance_rows.append({"entry_id": "G1", "posting_date": PERIOD_END, "account_code": "4000", "amount": "999999.123", "description": "governance high positive", "preparer": "RAREUSER"})
        source = directory / "governance.csv"
        with source.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(governance_rows[0])); writer.writeheader(); writer.writerows(governance_rows)
        store = Store(str(directory / "audit.db")); create_engagement(store, "Synthetic Governance", "2025-04-01:2026-03-31", "manager"); store.add_user("reviewer", "reviewer", "manager"); store.add_user("second", "quality_reviewer", "manager"); store.add_user("readonly", "read_only", "manager"); store.conn.commit()
        before = None
        try: analyze(store, "manager", False)
        except Exception as exc: before = str(exc)
        governance_total = round(sum(float(row["amount"]) for row in governance_rows), 3)
        import_gl(store, str(source), "manager", expected_rows=len(governance_rows), expected_debits=governance_total, expected_credits=0)
        exception_id = store.conn.execute("SELECT e.id FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id WHERE e.run_id=(SELECT max(id) FROM model_runs)").fetchone()
        # The first analysis is intentionally unavailable before acknowledgement.
        exception_id = None
        acknowledge_population(store, "reviewer", "synthetic totals")
        run = analyze(store, "manager", False)
        exception_id = store.conn.execute("SELECT id FROM exceptions WHERE run_id=? ORDER BY id LIMIT 1", (run,)).fetchone()[0]
        checks = {}
        for name, args in [("no_role", (exception_id, "readonly", "open", "note", None, None)), ("no_note", (exception_id, "reviewer", "open", "", None, None)), ("high_no_second", (exception_id, "reviewer", "cleared", "note", None, None)), ("same_second", (exception_id, "reviewer", "cleared", "note", "reviewer", "note")), ("bad_second_role", (exception_id, "reviewer", "cleared", "note", "readonly", "note"))]:
            try:
                record_review(store, *args); checks[name] = "unexpectedly_allowed"
            except WorkflowError as exc: checks[name] = {"blocked": True, "code": exc.code}
        allowed = record_review(store, exception_id, "reviewer", "cleared", "independent first", "second", "independent second")
        lock_review_set(store, "manager", "locked for benchmark")
        try: record_review(store, exception_id, "reviewer", "follow_up", "blocked")
        except WorkflowError as exc: checks["locked_review"] = {"blocked": True, "code": exc.code}
        try: assign_exception(store, "manager", exception_id, "reviewer")
        except WorkflowError as exc: checks["locked_assignment"] = {"blocked": True, "code": exc.code}
        direct_status = "unexpectedly_allowed"
        try: store.conn.execute("UPDATE exceptions SET status='open' WHERE id=?", (exception_id,))
        except sqlite3.IntegrityError as exc:
            direct_status = {"blocked": True, "error": str(exc)}
            store.conn.rollback()
        direct_severity = "unexpectedly_allowed"
        try:
            store.conn.execute("UPDATE exceptions SET severity='low' WHERE id=?", (exception_id,))
            direct_severity = {"allowed": True, "stored_severity": store.conn.execute("SELECT severity FROM exceptions WHERE id=?", (exception_id,)).fetchone()[0]}
            store.conn.rollback()
        except sqlite3.IntegrityError as exc:
            direct_severity = {"blocked": True, "error": str(exc)}
            store.conn.rollback()
        reopen_review_set(store, "manager", "reopened for benchmark")
        store.close()
        return {"analysis_before_ack_blocked": bool(before), "checks": checks, "valid_high_clear": allowed, "direct_status_mutation": direct_status, "direct_severity_mutation": direct_severity}


def api_endpoint_matrix() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="benchmark-api-matrix-") as directory_text:
        directory = Path(directory_text)
        app = create_app(directory / "audit.db")
        client = TestClient(app)
        client.post("/api/engagement", json={"client": "API Matrix", "period": "2025-01-01:2025-12-31", "owner": "manager"})
        store = Store(str(directory / "seed.db"))  # separate user seed is not used by the app DB
        store.close()
        # Add a reviewer and seed a valid population through the API.
        app_store = Store(str(directory / "audit.db")); app_store.add_user("reviewer", "reviewer", "manager"); app_store.conn.commit(); app_store.close()
        source = directory / "matrix.csv"; source.write_text("entry_id,posting_date,account_code,amount\nA1,2025-02-14,1000,1000\nA2,2025-02-14,1000,101.123\n", encoding="utf-8")
        imported = client.post("/api/imports/gl", data={"actor": "manager", "expected_rows": "2", "expected_debits": "1101.123", "expected_credits": "0"}, files={"file": (source.name, source.read_bytes(), "text/csv")})
        client.post("/api/imports/acknowledge", json={"reviewer": "reviewer", "note": "matrix totals"})
        analyzed = client.post("/api/analysis-runs", json={"actor": "manager", "include_isolation": False})
        run_id = analyzed.json().get("run_id")
        exception = client.get("/api/exceptions", params={"limit": 1}).json().get("rows", [{}])[0]
        matrix = []
        def record(method, path, response, label="valid"):
            body = response.json() if response.headers.get("content-type", "").startswith("application/json") else None
            matrix.append({"method": method, "path": path, "label": label, "status": response.status_code, "error_code": (body or {}).get("error", {}).get("code") if isinstance(body, dict) else None})
        record("GET", "/api/health", client.get("/api/health"))
        record("GET", "/api/status", client.get("/api/status")); record("GET", "/api/engagement", client.get("/api/engagement"))
        record("POST", "/api/engagement", client.post("/api/engagement", json={"client": "duplicate", "period": "2025-01-01:2025-12-31", "owner": "manager"}), "duplicate")
        record("GET", "/api/users", client.get("/api/users"))
        record("POST", "/api/imports/preview", client.post("/api/imports/preview", files={"file": ("matrix.csv", source.read_bytes(), "text/csv")}))
        record("POST", "/api/imports/gl", imported)
        record("GET", "/api/imports", client.get("/api/imports")); record("GET", "/api/imports/1/reconciliation", client.get("/api/imports/1/reconciliation")); record("GET", "/api/imports/999/reconciliation", client.get("/api/imports/999/reconciliation"), "missing")
        record("POST", "/api/imports/acknowledge", client.post("/api/imports/acknowledge", json={"reviewer": "reviewer", "note": "already", "override_reconciliation": True}), "repeat")
        record("GET", "/api/config", client.get("/api/config")); record("PUT", "/api/config", client.put("/api/config", json={"actor": "manager", "materiality": 1000, "performance_materiality": 500}))
        record("GET", "/api/analysis-runs", client.get("/api/analysis-runs")); record("POST", "/api/analysis-runs", analyzed)
        record("GET", "/api/exceptions", client.get("/api/exceptions")); record("GET", "/api/exceptions/999", client.get("/api/exceptions/999"), "missing")
        if exception.get("id"):
            record("GET", f"/api/exceptions/{exception['id']}", client.get(f"/api/exceptions/{exception['id']}")); record("POST", "/api/review", client.post("/api/review", json={"id": exception["id"], "reviewer": "reviewer", "disposition": "open", "note": "matrix"}))
        record("GET", "/api/reviews", client.get("/api/reviews")); record("POST", "/api/assignments", client.post("/api/assignments", json={"actor": "manager", "exception_id": exception.get("id", 1), "assignee": "reviewer"}))
        record("GET", "/api/review-set", client.get("/api/review-set")); record("POST", "/api/review-set/lock", client.post("/api/review-set/lock", json={"actor": "manager", "reason": "matrix"})); record("POST", "/api/review-set/reopen", client.post("/api/review-set/reopen", json={"actor": "manager", "reason": "matrix reopen"}))
        for path in ("/api/similar?q=matrix", "/api/semantic-profile", "/api/semantic-investigation?run=1&ledger_id=1", "/api/mappings", f"/api/compare-runs?a={run_id}&b={run_id}", "/api/models", "/api/bank", "/api/account-taxonomy"):
            record("GET", path, client.get(path))
        record("POST", "/api/exports/package", client.post("/api/exports/package", json={"actor": "manager"}))
        record("GET", "/api/semantic-profile?run=0", client.get("/api/semantic-profile?run=0"), "invalid_id")
        record("GET", "/api/similar?q=", client.get("/api/similar?q="), "empty_query")
        record("PUT", "/api/config", client.put("/api/config", json={"actor": "manager", "period_end_days": 999}), "invalid_range")
        record("POST", "/api/review", client.post("/api/review", json={"id": 0, "reviewer": "", "disposition": "bad", "note": ""}), "invalid")
        client.close()
        return {"cases": matrix, "count": len(matrix)}


def api_security_benchmark() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="benchmark-api-") as directory_text:
        directory = Path(directory_text)
        app = create_app(directory / "audit.db")
        client = TestClient(app)
        create = client.post("/api/engagement", json={"client": "API Security", "period": "2025-01-01:2025-12-31", "owner": "manager"})
        users = client.get("/api/users")
        source = directory / "upload.csv"
        source.write_text("entry_id,posting_date,account_code,amount\nA1,2025-02-15,1000,10\n", encoding="utf-8")
        results = {"health": client.get("/api/health").status_code, "create": create.status_code, "cors_header": client.get("/api/health").headers.get("access-control-allow-origin"), "security_headers": {key: client.get("/api/health").headers.get(key) for key in ("content-security-policy", "x-frame-options", "x-request-id")}}
        invalid = client.post("/api/review", json={"id": -1, "reviewer": "", "disposition": "bad", "note": ""})
        results["invalid_review"] = {"status": invalid.status_code, "body": invalid.json()}
        evil = TestClient(app, base_url="http://evil.example")
        results["trusted_host_rejection"] = evil.get("/api/status").status_code
        unsupported = client.post("/api/imports/preview", files={"file": ("../../escape.exe", b"x", "application/octet-stream")})
        results["unsupported_upload"] = {"status": unsupported.status_code, "body": unsupported.json()}
        long_name = "../" + "x" * 500 + ".csv"
        long_upload = client.post("/api/imports/preview", files={"file": (long_name, b"entry_id,posting_date,account_code,amount\nA,2025-01-01,1,1\n", "text/csv")})
        results["long_filename"] = {"status": long_upload.status_code, "body": long_upload.json(), "outside_artifacts": [str(path) for path in directory.parent.glob("escape*")]}
        results["users"] = users.json()
        client.close()
        return results


def concurrency_backup_benchmark() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="benchmark-concurrency-") as directory_text:
        directory = Path(directory_text)
        db = directory / "audit.db"; source = directory / "gl.csv"; source.write_text("entry_id,posting_date,account_code,amount\nC1,2025-02-15,1000,1000\nC2,2025-02-15,1000,101\n", encoding="utf-8")
        store = Store(str(db)); create_engagement(store, "Synthetic Concurrency", "2025-04-01:2026-03-31", "manager"); store.add_user("reviewer", "reviewer", "manager"); store.conn.commit(); import_gl(store, str(source), "manager"); store.conn.execute("UPDATE imports SET acknowledged_at=1"); store.conn.commit(); run = analyze(store, "manager", False); exception_id = store.conn.execute("SELECT id FROM exceptions LIMIT 1").fetchone()[0]; store.close()
        outcomes = []
        def review_once(index):
            connection = Store(str(db))
            try:
                record_review(connection, exception_id, "reviewer", "follow_up" if index else "open", f"concurrent {index}")
                return "ok"
            except Exception as exc:
                return f"{type(exc).__name__}: {exc}"
            finally:
                connection.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(review_once, [1, 2]))
        lock_outcomes = []
        def lock_once():
            connection = Store(str(db))
            try:
                lock_review_set(connection, "manager", "concurrent lock")
                return "ok"
            except Exception as exc:
                return f"{type(exc).__name__}: {exc}"
            finally:
                connection.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            lock_outcomes = list(pool.map(lambda _: lock_once(), [1, 2]))
        source_connection = sqlite3.connect(db); backup_path = directory / "backup.db"; destination = sqlite3.connect(backup_path); source_connection.backup(destination); destination.close(); source_connection.close()
        restored = Store(str(backup_path)); integrity = restored.conn.execute("PRAGMA integrity_check").fetchone()[0]; counts = {table: restored.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in ("imports", "ledger_entries", "model_runs", "exceptions", "reviews", "review_set_events", "audit_log")}; restored.close()
        return {"concurrent_reviews": outcomes, "concurrent_locks": lock_outcomes, "backup_integrity": integrity, "backup_counts": counts}


def reproducibility_benchmark() -> dict[str, Any]:
    source_path = ROOT / "examples/demo-journal-entries.csv"
    snapshots = []
    for index in range(2):
        with tempfile.TemporaryDirectory(prefix=f"benchmark-repro-{index}-") as directory_text:
            directory = Path(directory_text)
            store = Store(str(directory / "audit.db")); create_engagement(store, "Synthetic Reproducibility", "2025-04-01:2026-03-31", "manager"); store.add_user("reviewer", "reviewer", "manager"); import_gl(store, str(source_path), "manager", expected_rows=400, expected_debits=3496407.62, expected_credits=0); acknowledge_population(store, "reviewer", "synthetic totals"); run = analyze(store, "manager", False)
            ledger = [dict(row) for row in store.conn.execute("SELECT entry_id,posting_date,account_code,debit,credit,signed_amount,description,source_hash,source_row FROM ledger_entries ORDER BY entry_id")]
            risks = [dict(row) for row in store.conn.execute("SELECT l.entry_id,e.risk_score,e.severity,e.reasons_json,e.evidence_json FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id WHERE e.run_id=? ORDER BY l.entry_id", (run,))]
            sample_a, _ = create_sample(store, "same-seed", "manager", run, risk_count=3, random_count=3, seed=SEED)
            sample_items = [row[0] for row in store.conn.execute("SELECT ledger_id FROM sample_items WHERE sample_set_id=? ORDER BY ledger_id", (sample_a,))]
            workpaper = directory / "workpaper.csv"; manifest_path = directory / "manifest.json"; export_workpaper(store, str(workpaper), "manager")
            manifest = json.loads((directory / "workpaper.csv.manifest.json").read_text())
            manifest_sources = [{key: value for key, value in row.items() if key != "evidence_path"} for row in manifest["source_imports"]]
            snapshots.append({"ledger": ledger, "risks": risks, "sample_items": sample_items, "workpaper_rows": list(csv.DictReader(workpaper.open(newline="", encoding="utf-8"))), "manifest_core": {"source_imports": manifest_sources, "exception_count": manifest["exception_count"], "workpaper_sha256": manifest["workpaper_sha256"], "integrity": manifest["integrity"]}})
            store.close()
    return {"normalized_ledger": snapshots[0]["ledger"] == snapshots[1]["ledger"], "risk_results": snapshots[0]["risks"] == snapshots[1]["risks"], "sample_selection": snapshots[0]["sample_items"] == snapshots[1]["sample_items"], "workpaper_rows": snapshots[0]["workpaper_rows"] == snapshots[1]["workpaper_rows"], "manifest_core": snapshots[0]["manifest_core"] == snapshots[1]["manifest_core"], "timestamps_and_run_ids_excluded": True}


def test_suite_benchmark() -> dict[str, Any]:
    commands = {
        "uv_lock_check": ["uv", "lock", "--check"],
        "uv_sync": ["uv", "sync", "--frozen", "--all-extras", "--group", "dev"],
        "pytest": ["uv", "run", "pytest", "-q", "-p", "no:cacheprovider"],
        "compileall": ["uv", "run", "python", "-m", "compileall", "-q", "src", "run.py"],
        "frontend_ci": ["npm", "--prefix", "frontend", "ci", "--ignore-scripts"],
        "frontend_typecheck": ["npm", "--prefix", "frontend", "run", "typecheck"],
        "frontend_build": ["npm", "--prefix", "frontend", "run", "build"],
        "pip_audit": ["uv", "run", "pip-audit", "--local"],
        "frontend_audit": ["npm", "--prefix", "frontend", "audit", "--audit-level=high"],
        "repo_policy": ["python3", "scripts/check_repo.py"],
        "license_policy": ["python3", "scripts/check_licenses.py"],
    }
    return {name: command(args, timeout=300) for name, args in commands.items()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", default="100,1000,10000,50000,100000")
    parser.add_argument("--pipeline-sizes", default="1000,10000")
    parser.add_argument("--adversarial-sizes", default="1000,2000")
    parser.add_argument("--api-latency-sizes", default="1000,10000")
    parser.add_argument("--approximation-sizes", default="1000,10000")
    parser.add_argument("--skip-browser", action="store_true")
    parser.add_argument("--only-import", action="store_true")
    parser.add_argument("--only-adversarial", action="store_true")
    parser.add_argument("--output-dir", default="benchmark-results")
    args = parser.parse_args()
    global RESULTS
    RESULTS = Path(args.output_dir)
    if not RESULTS.is_absolute():
        RESULTS = ROOT / RESULTS
    sizes = [int(value) for value in args.sizes.split(",") if value]
    pipeline_sizes = [int(value) for value in args.pipeline_sizes.split(",") if value]
    adversarial_sizes = [int(value) for value in args.adversarial_sizes.split(",") if value]
    api_latency_sizes = [int(value) for value in args.api_latency_sizes.split(",") if value]
    approximation_sizes = [int(value) for value in args.approximation_sizes.split(",") if value]
    if args.only_import:
        write_json("performance-scale.json", {"imports": import_benchmark(sizes), "note": "Import-only scale run; analysis intentionally not attempted for unsafe sizes."})
        print(json.dumps({"commit": environment()["commit"], "results": str(RESULTS)}, indent=2))
        return
    if args.only_adversarial:
        write_json("performance-adversarial.json", adversarial_analysis_probe(adversarial_sizes))
        print(json.dumps({"commit": environment()["commit"], "results": str(RESULTS)}, indent=2))
        return
    baseline = {"benchmark_version": "1", "seed": SEED, "environment": environment(), "test_suite": test_suite_benchmark()}
    if not args.skip_browser and os.environ.get("PLAYWRIGHT_CHROMIUM"):
        baseline["browser_e2e"] = command(["npm", "--prefix", "frontend", "run", "test:e2e"], timeout=180, env={"PLAYWRIGHT_CHROMIUM": os.environ["PLAYWRIGHT_CHROMIUM"]})
    write_json("baseline.json", baseline)
    write_json("correctness.json", {"malformed_import": malformed_import_benchmark(), "idempotence": idempotence_benchmark(), "reconciliation": reconciliation_benchmark(), "deterministic": deterministic_benchmark(), "ground_truth": ground_truth_benchmark(), "materiality_and_sampling": materiality_sampling_benchmark(), "missing_data": missing_data_benchmark()})
    write_json("semantic.json", {"semantic": semantic_benchmark(), "approximation": approximation_benchmark(approximation_sizes)})
    write_json("governance.json", {"governance": governance_benchmark(), "api_endpoint_matrix": api_endpoint_matrix(), "api_security": api_security_benchmark(), "concurrency_backup": concurrency_backup_benchmark()})
    write_json("performance.json", {"imports": import_benchmark(sizes), "pipeline": pipeline_performance(pipeline_sizes), "adversarial_analysis": adversarial_analysis_probe(adversarial_sizes), "api_latency": api_latency_benchmark(api_latency_sizes)})
    write_json("reproducibility.json", reproducibility_benchmark())
    write_json("security.json", {"dependency_checks": baseline["test_suite"], "api_security": api_security_benchmark()})
    write_json("failures.json", {"failures": [], "note": "Populated by final assessment after observing command outputs."})
    (RESULTS / "README.md").write_text("# Benchmark artifacts\n\nThese files are generated from synthetic data only. See `docs/BENCHMARKING.md` and `summary.md`.\n", encoding="utf-8")
    print(json.dumps({"commit": baseline["environment"]["commit"], "results": str(RESULTS)}, indent=2))


if __name__ == "__main__":
    main()
