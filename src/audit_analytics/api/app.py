"""Canonical local FastAPI service for the Audit Analytics workbench."""
from __future__ import annotations

import csv
import json
import logging
import os
import secrets
import sqlite3
import tempfile
import time
import zipfile
from contextlib import contextmanager
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, Form, Query, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from audit_analytics.importer import (
    MAX_SOURCE_BYTES,
    DuplicateImportError,
    import_gl,
    preview_gl,
)
from audit_analytics.model_registry import list_models
from audit_analytics.reports import compare_runs, engagement_summary, export_workpaper, write_engagement_report
from audit_analytics.sampling import create_sample
from audit_analytics.semantic import similar_transactions
from audit_analytics.semantic_risk import get_semantic_profile, semantic_investigate
from audit_analytics.store import Store
from audit_analytics.workflow import (
    MANAGER_ROLES,
    PREPARER_ROLES,
    REVIEW_ROLES,
    WorkflowError,
    acknowledge_population,
    assign_exception,
    configure_engagement,
    create_engagement,
    lock_review_set,
    record_review,
    reopen_review_set,
    require_role,
    run_analysis,
)


Disposition = Literal["open", "cleared", "follow_up", "selected_for_testing"]
logger = logging.getLogger("audit_analytics.api")


class StrictModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class EngagementBody(StrictModel):
    client: str = Field(min_length=1, max_length=200)
    period: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}:\d{4}-\d{2}-\d{2}$")
    owner: str = Field(min_length=1, max_length=100)


class AcknowledgeBody(StrictModel):
    reviewer: str = Field(min_length=1, max_length=100)
    note: str = Field(min_length=1, max_length=4000)
    override_reconciliation: bool = False


class ConfigBody(StrictModel):
    actor: str = Field(min_length=1, max_length=100)
    materiality: float | None = Field(default=None, ge=0)
    performance_materiality: float | None = Field(default=None, ge=0)
    round_amount_threshold: float | None = Field(default=None, ge=0)
    period_end_days: int | None = Field(default=None, ge=0, le=366)
    outlier_robust_z: float | None = Field(default=None, gt=0)


class AnalysisBody(StrictModel):
    actor: str = Field(min_length=1, max_length=100)
    include_isolation: bool = True
    semantic_run_id: int | None = Field(default=None, gt=0)


class ReviewBody(StrictModel):
    id: int = Field(gt=0)
    reviewer: str = Field(min_length=1, max_length=100)
    disposition: Disposition
    note: str = Field(min_length=1, max_length=4000)
    second_reviewer: str | None = Field(default=None, max_length=100)
    second_note: str | None = Field(default=None, max_length=4000)


class AssignmentBody(StrictModel):
    actor: str = Field(min_length=1, max_length=100)
    exception_id: int = Field(gt=0)
    assignee: str = Field(min_length=1, max_length=100)
    due_date: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")


class ReviewSetBody(StrictModel):
    actor: str = Field(min_length=1, max_length=100)
    reason: str = Field(min_length=1, max_length=2000)


class ExportBody(StrictModel):
    actor: str = Field(min_length=1, max_length=100)


class SampleSetBody(StrictModel):
    actor: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    run_id: int | None = Field(default=None, gt=0)
    risk_count: int = Field(default=20, ge=0)
    random_count: int = Field(default=10, ge=0)
    seed: int = Field(default=1)
    random_min_amount: float | None = Field(default=None, ge=0, allow_inf_nan=False)


def _error(code: str, message: str, status: int, **details):
    body = {"error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return JSONResponse(body, status_code=status)


def _mapping(value: str | None):
    if value is None or not value.strip():
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise WorkflowError("mapping must be a JSON object", "invalid_mapping") from exc
    if not isinstance(parsed, dict):
        raise WorkflowError("mapping must be a JSON object", "invalid_mapping")
    return parsed


@contextmanager
def _upload_path(upload: UploadFile):
    filename = Path(upload.filename or "").name
    suffix = Path(filename).suffix.lower()
    if not filename or suffix not in {".csv", ".xlsx"}:
        raise WorkflowError("upload a .csv or .xlsx file", "invalid_file", 400)
    if upload.size is not None and upload.size > MAX_SOURCE_BYTES:
        raise WorkflowError(f"source file exceeds the {MAX_SOURCE_BYTES}-byte import limit", "file_too_large", 413)
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    path = Path(temp.name)
    total = 0
    try:
        with temp:
            while chunk := upload.file.read(1024 * 1024):
                total += len(chunk)
                if total > MAX_SOURCE_BYTES:
                    raise WorkflowError(
                        f"source file exceeds the {MAX_SOURCE_BYTES}-byte import limit", "file_too_large", 413
                    )
                temp.write(chunk)
        yield path
    finally:
        path.unlink(missing_ok=True)
        upload.file.close()


def _decode_json(value, fallback):
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return fallback


def _decode(row):
    item = dict(row)
    for field in ("reasons_json", "evidence_json", "detail_json"):
        if field in item:
            key = field.removesuffix("_json")
            item[key] = _decode_json(item.pop(field), [] if key == "reasons" else {})
    if "configuration" in item:
        item["configuration"] = _decode_json(item["configuration"], {})
    return item


def _sample_payload(store: Store, sample_id: int, item_limit: int):
    row = store.conn.execute("SELECT * FROM sample_sets WHERE id=?", (sample_id,)).fetchone()
    if not row:
        raise LookupError("sample set not found")
    item = dict(row)
    item["method"] = _decode_json(item.pop("method_json"), {})
    item["item_count"] = store.conn.execute(
        "SELECT COUNT(*) FROM sample_items WHERE sample_set_id=?", (sample_id,)
    ).fetchone()[0]
    item["selected_count"] = item["item_count"]
    item["items"] = []
    for selected in store.conn.execute(
        """SELECT si.ledger_id,si.rationale,l.entry_id,l.posting_date,l.document_date,l.account_code,
                  c.account_name,l.debit,l.credit,l.signed_amount,l.description,l.preparer,l.reference,
                  l.entity,l.vendor,l.is_manual,l.import_id,l.source_row,l.source_hash,
                  e.id AS exception_id,e.run_id AS exception_run_id,e.risk_score AS exception_risk_score,
                  e.severity AS exception_severity,e.status AS exception_status,
                  e.materiality_band AS exception_materiality_band,e.assigned_to AS exception_assigned_to,
                  e.due_date AS exception_due_date,e.reasons_json AS exception_reasons_json,
                  e.evidence_json AS exception_evidence_json
           FROM sample_items si JOIN ledger_entries l ON l.id=si.ledger_id
           LEFT JOIN coa c ON c.account_code=l.account_code
           LEFT JOIN exceptions e ON e.ledger_id=si.ledger_id AND e.run_id=?
           WHERE si.sample_set_id=? ORDER BY si.rowid LIMIT ?""",
        (item["run_id"], sample_id, item_limit),
    ):
        entry = dict(selected)
        exception_id = entry.pop("exception_id", None)
        if exception_id is None:
            entry["exception"] = None
        else:
            entry["exception"] = {
                "id": exception_id,
                "run_id": entry.pop("exception_run_id", None),
                "risk_score": entry.pop("exception_risk_score", None),
                "severity": entry.pop("exception_severity", None),
                "status": entry.pop("exception_status", None),
                "materiality_band": entry.pop("exception_materiality_band", None),
                "assigned_to": entry.pop("exception_assigned_to", None),
                "due_date": entry.pop("exception_due_date", None),
                "reasons": _decode_json(entry.pop("exception_reasons_json", "[]"), []),
                "evidence": _decode_json(entry.pop("exception_evidence_json", "{}"), {}),
            }
        for key in (
            "exception_run_id", "exception_risk_score", "exception_severity", "exception_status",
            "exception_materiality_band", "exception_assigned_to", "exception_due_date",
            "exception_reasons_json", "exception_evidence_json",
        ):
            entry.pop(key, None)
        item["items"].append(entry)
    item["items_truncated"] = item["item_count"] > len(item["items"])
    return item


def create_app(db_path: str | Path | None = None, static_dir: str | Path | None = None) -> FastAPI:
    resolved_db = Path(db_path or os.environ.get("AUDIT_DB", Path.cwd() / "data" / "demo.db"))
    resolved_static = Path(static_dir) if static_dir else Path(__file__).resolve().parent.parent / "static"
    app = FastAPI(title="Audit Analytics API", version="1.0.0")
    app.state.db_path = str(resolved_db)
    app.state.static_dir = str(resolved_static)
    logger.setLevel(os.environ.get("AUDIT_LOG_LEVEL", "INFO").upper())
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["127.0.0.1", "localhost", "testserver"],
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        request_id = secrets.token_hex(8)
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            route = request.scope.get("route")
            route_path = getattr(route, "path", request.url.path)
            logger.exception("request_failed method=%s path=%s request_id=%s", request.method, route_path, request_id)
            raise
        route = request.scope.get("route")
        route_path = getattr(route, "path", request.url.path)
        duration_ms = (time.perf_counter() - started) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; connect-src 'self'; img-src 'self' data:; style-src 'self'; "
            "script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
        )
        logger.info(
            "request method=%s path=%s status=%s duration_ms=%.1f request_id=%s",
            request.method,
            route_path,
            response.status_code,
            duration_ms,
            request_id,
        )
        return response

    @app.exception_handler(WorkflowError)
    async def workflow_error(_request: Request, exc: WorkflowError):
        return _error(exc.code, str(exc), exc.status)

    @app.exception_handler(DuplicateImportError)
    async def duplicate_import(_request: Request, exc: DuplicateImportError):
        return _error(
            "duplicate_import",
            str(exc),
            409,
            kind=exc.kind,
            existing_import_id=exc.existing_import_id,
        )

    @app.exception_handler(LookupError)
    async def lookup_error(_request: Request, exc: LookupError):
        return _error("not_found", str(exc), 404)

    @app.exception_handler(ValueError)
    async def value_error(_request: Request, exc: ValueError):
        return _error("invalid_input", str(exc), 400)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_request: Request, exc: RequestValidationError):
        return _error("validation_error", "request validation failed", 422, fields=exc.errors())

    @app.exception_handler(StarletteHTTPException)
    async def http_error(_request: Request, exc: StarletteHTTPException):
        return _error("http_error", str(exc.detail), exc.status_code)

    @app.get("/api/health")
    def health(request: Request):
        database = Store(request.app.state.db_path)
        try:
            database.conn.execute("SELECT 1").fetchone()
            schema_version = database.schema_version()
        finally:
            database.close()
        static_ready = (Path(request.app.state.static_dir) / "index.html").is_file()
        return {
            "status": "ok" if static_ready else "degraded",
            "database": "ok",
            "schema_version": schema_version,
            "static": "ok" if static_ready else "missing",
        }

    def concrete_store(request: Request) -> Store:
        return Store(request.app.state.db_path)

    @app.get("/api/status")
    def status_route(request: Request):
        store = concrete_store(request)
        try:
            return engagement_summary(store)
        finally:
            store.close()

    @app.get("/api/engagement")
    def engagement_route(request: Request):
        store = concrete_store(request)
        try:
            row = store.engagement()
            return {"engagement": dict(row) if row else None, "folder": store.path.parent.name}
        finally:
            store.close()

    @app.post("/api/engagement")
    def engagement_create(body: EngagementBody, request: Request):
        store = concrete_store(request)
        try:
            return dict(create_engagement(store, body.client, body.period, body.owner))
        finally:
            store.close()

    @app.get("/api/users")
    def users(request: Request):
        store = concrete_store(request)
        try:
            return [dict(row) for row in store.conn.execute("SELECT username,role FROM users WHERE active=1 ORDER BY username")]
        finally:
            store.close()

    @app.post("/api/imports/preview")
    def import_preview(file: UploadFile = File(...), mapping: str | None = Form(None)):
        with _upload_path(file) as path:
            result = preview_gl(str(path), _mapping(mapping))
            result["file"] = Path(file.filename or path.name).name
            return result

    @app.post("/api/imports/gl")
    def import_gl_endpoint(
        request: Request,
        file: UploadFile = File(...),
        actor: str = Form(...),
        expected_rows: int | None = Form(None, ge=0),
        expected_debits: float | None = Form(None),
        expected_credits: float | None = Form(None),
        mapping: str | None = Form(None),
        mapping_name: str | None = Form(None),
        reimport: bool = Form(False),
    ):
        store = concrete_store(request)
        try:
            require_role(store, actor, PREPARER_ROLES)
            selected_mapping = _mapping(mapping)
            if mapping_name:
                row = store.conn.execute(
                    "SELECT mapping_json FROM import_mappings WHERE name=?", (mapping_name,)
                ).fetchone()
                if not row:
                    raise WorkflowError(f"mapping profile not found: {mapping_name}", "not_found", 404)
                selected_mapping = json.loads(row[0])
            with _upload_path(file) as path:
                import_id, accepted, rejected, debits, credits = import_gl(
                    store,
                    str(path),
                    actor,
                    selected_mapping,
                    expected_rows,
                    expected_debits,
                    expected_credits,
                    reimport,
                )
            return {
                "import_id": import_id,
                "accepted": accepted,
                "rejected": rejected,
                "debits": debits,
                "credits": credits,
                "reconciliation": store.reconciliation(import_id),
            }
        finally:
            store.close()

    @app.get("/api/imports")
    def imports(request: Request):
        store = concrete_store(request)
        try:
            rows = []
            for row in store.conn.execute("SELECT * FROM imports ORDER BY id"):
                item = dict(row)
                item["reconciliation"] = store.reconciliation(item["id"]) if item["kind"] == "gl" else None
                rows.append(item)
            return rows
        finally:
            store.close()

    @app.get("/api/imports/{import_id}/reconciliation")
    def import_reconciliation(import_id: int, request: Request):
        store = concrete_store(request)
        try:
            return store.reconciliation(import_id)
        finally:
            store.close()

    @app.post("/api/imports/acknowledge")
    def acknowledge(body: AcknowledgeBody, request: Request):
        store = concrete_store(request)
        try:
            return acknowledge_population(store, body.reviewer, body.note, body.override_reconciliation)
        finally:
            store.close()

    @app.get("/api/config")
    def config(request: Request):
        store = concrete_store(request)
        try:
            return {
                "analysis_policy": store.get_setting("analysis_policy", {}),
                "materiality": store.get_setting("materiality", {}),
            }
        finally:
            store.close()

    @app.put("/api/config")
    def update_config(body: ConfigBody, request: Request):
        store = concrete_store(request)
        try:
            return configure_engagement(
                store,
                body.actor,
                materiality=body.materiality,
                performance_materiality=body.performance_materiality,
                round_amount_threshold=body.round_amount_threshold,
                period_end_days=body.period_end_days,
                outlier_robust_z=body.outlier_robust_z,
            )
        finally:
            store.close()

    @app.get("/api/analysis-runs")
    def analysis_runs(request: Request, limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
        store = concrete_store(request)
        try:
            rows = [_decode(row) for row in store.conn.execute(
                "SELECT * FROM model_runs ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset)
            )]
            return {"rows": rows, "limit": limit, "offset": offset}
        finally:
            store.close()

    @app.post("/api/analysis-runs")
    def analysis_create(body: AnalysisBody, request: Request):
        store = concrete_store(request)
        try:
            return run_analysis(store, body.actor, body.include_isolation, body.semantic_run_id)
        finally:
            store.close()

    @app.post("/api/sample-sets")
    def sample_set_create(body: SampleSetBody, request: Request):
        store = concrete_store(request)
        try:
            try:
                require_role(store, body.actor, REVIEW_ROLES)
                sample_id, selected = create_sample(
                    store,
                    body.name,
                    body.actor,
                    body.run_id,
                    body.risk_count,
                    body.random_count,
                    body.seed,
                    body.random_min_amount,
                )
                return {"sample_set_id": sample_id, "selected": selected}
            except sqlite3.IntegrityError as exc:
                store.conn.rollback()
                if "FOREIGN KEY" in str(exc).upper():
                    raise WorkflowError("analysis run not found", "not_found", 404) from exc
                if "sample_sets" in str(exc):
                    raise WorkflowError("sample set already exists for this analysis run", "conflict", 409) from exc
                raise WorkflowError("sample set could not be created", "invalid_input", 400) from exc
            except Exception:
                store.conn.rollback()
                raise
        finally:
            store.close()

    @app.get("/api/sample-sets")
    def sample_sets(
        request: Request,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
    ):
        store = concrete_store(request)
        try:
            rows = store.conn.execute(
                "SELECT id FROM sample_sets ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset)
            ).fetchall()
            return {
                "rows": [_sample_payload(store, row["id"], 100) for row in rows],
                "limit": limit,
                "offset": offset,
            }
        finally:
            store.close()

    @app.get("/api/sample-sets/{sample_id}")
    def sample_set_detail(
        sample_id: int,
        request: Request,
        limit: int = Query(500, ge=1, le=500),
    ):
        store = concrete_store(request)
        try:
            return _sample_payload(store, sample_id, limit)
        finally:
            store.close()

    @app.get("/api/audit-log")
    def audit_log(
        request: Request,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        action: str | None = Query(None, max_length=100),
        target_type: str | None = Query(None, max_length=100),
        target_id: str | None = Query(None, min_length=1, max_length=200),
        actor: str | None = Query(None, max_length=100),
    ):
        store = concrete_store(request)
        try:
            clauses, params = ["1=1"], []
            if action is not None:
                clauses.append("action=?")
                params.append(action)
            if target_type is not None:
                clauses.append("target_type=?")
                params.append(target_type)
            if target_id is not None:
                clauses.append("target_id=?")
                params.append(target_id)
            if actor is not None:
                clauses.append("actor=?")
                params.append(actor)
            where = " AND ".join(clauses)
            rows = store.conn.execute(
                f"SELECT * FROM audit_log WHERE {where} ORDER BY id DESC LIMIT ? OFFSET ?",
                (*params, limit, offset),
            ).fetchall()
            return {"rows": [_decode(row) for row in rows], "limit": limit, "offset": offset}
        finally:
            store.close()

    @app.post("/api/demo/seed")
    def demo_seed(request: Request):
        store = concrete_store(request)
        try:
            has_data = store.conn.execute(
                "SELECT EXISTS(SELECT 1 FROM engagement) OR EXISTS(SELECT 1 FROM imports) "
                "OR EXISTS(SELECT 1 FROM ledger_entries) OR EXISTS(SELECT 1 FROM model_runs)"
            ).fetchone()[0]
            if has_data:
                raise WorkflowError("demo seed requires an empty engagement", "conflict", 409)
            fixture = Path(__file__).resolve().parents[3] / "examples" / "demo-journal-entries.csv"
            if not fixture.is_file():
                raise LookupError("demo fixture not found: examples/demo-journal-entries.csv")
            preview = preview_gl(str(fixture))
            try:
                with fixture.open(newline="", encoding="utf-8-sig") as stream:
                    fixture_rows = list(csv.DictReader(stream))
                fixture_debits = sum(
                    (Decimal(str(row.get("amount") or "0").replace(",", "").replace("₹", "").strip() or "0") for row in fixture_rows),
                    Decimal("0"),
                )
            except (OSError, csv.Error, InvalidOperation, ValueError) as exc:
                raise WorkflowError("demo fixture could not be read as the expected synthetic source", "invalid_fixture", 409) from exc
            if preview["row_count"] != 400 or preview["missing_required"] or fixture_debits != Decimal("3496407.62"):
                raise WorkflowError("demo fixture is not the expected 400-row source", "invalid_fixture", 409)
            owner = "synthetic-demo-manager"
            engagement = create_engagement(
                store,
                "Synthetic Demo Engagement (source-checkout fixture)",
                "2025-01-01:2026-03-31",
                owner,
            )
            import_id, accepted, rejected, debits, credits = import_gl(
                store,
                str(fixture),
                owner,
                expected_rows=400,
                expected_debits=3496407.62,
                expected_credits=0,
            )
            if accepted != 400 or rejected != 0 or abs(debits - 3496407.62) > 0.01 or abs(credits) > 0.01:
                raise WorkflowError("demo fixture control totals are not the expected synthetic totals", "invalid_fixture", 409)
            acknowledgement = acknowledge_population(
                store,
                owner,
                "Synthetic source-checkout fixture; no client approval or review is represented.",
            )
            configuration = configure_engagement(
                store,
                owner,
                materiality=100000,
                performance_materiality=25000,
                round_amount_threshold=1000,
                period_end_days=3,
                outlier_robust_z=3.5,
            )
            analysis_run_id = run_analysis(store, owner)["run_id"]
            exception_count = store.conn.execute("SELECT COUNT(*) FROM exceptions WHERE run_id=?", (analysis_run_id,)).fetchone()[0]
            review_count = store.conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
            return {
                "synthetic": True,
                "fixture": "examples/demo-journal-entries.csv",
                "engagement": engagement,
                "engagement_id": engagement["id"],
                "import_id": import_id,
                "accepted": accepted,
                "rejected": rejected,
                "debits": round(debits, 2),
                "credits": round(credits, 2),
                "entries": accepted,
                "run_id": analysis_run_id,
                "analysis_run_id": analysis_run_id,
                "exceptions": exception_count,
                "reviews": review_count,
                "acknowledged_import_ids": acknowledgement["import_ids"],
                "configuration": configuration,
            }
        except Exception:
            store.conn.rollback()
            raise
        finally:
            store.close()

    @app.get("/api/exceptions")
    def exceptions(
        request: Request,
        run: int | None = Query(None, gt=0),
        severity: Literal["high", "medium", "low"] | None = None,
        status_filter: Literal["open", "cleared", "follow_up", "selected_for_testing"] | None = Query(None, alias="status"),
        search: str | None = Query(None, max_length=200),
        assigned_to: str | None = Query(None, max_length=100),
        account: str | None = Query(None, max_length=100),
        preparer: str | None = Query(None, max_length=100),
        materiality_band: str | None = Query(None, max_length=50),
        signal: str | None = Query(None, max_length=100),
        date_from: date | None = Query(None),
        date_to: date | None = Query(None),
        min_amount: float | None = Query(None, allow_inf_nan=False),
        max_amount: float | None = Query(None, allow_inf_nan=False),
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
    ):
        store = concrete_store(request)
        try:
            if min_amount is not None and max_amount is not None and min_amount > max_amount:
                raise WorkflowError("min_amount must not exceed max_amount", "invalid_input")
            clauses, params = ["1=1"], []
            if run is not None:
                clauses.append("e.run_id=?")
                params.append(run)
            if severity:
                clauses.append("e.severity=?")
                params.append(severity)
            if status_filter:
                clauses.append("e.status=?")
                params.append(status_filter)
            if assigned_to is not None:
                clauses.append("e.assigned_to=?")
                params.append(assigned_to)
            if account:
                clauses.append("l.account_code=?")
                params.append(account)
            if preparer:
                clauses.append("l.preparer=?")
                params.append(preparer)
            if materiality_band:
                clauses.append("e.materiality_band=?")
                params.append(materiality_band)
            if signal:
                clauses.append("e.reasons_json LIKE ?")
                params.append(f'%"{signal}"%')
            if date_from is not None:
                clauses.append("l.posting_date>=?")
                params.append(date_from.isoformat())
            if date_to is not None:
                clauses.append("l.posting_date<=?")
                params.append(date_to.isoformat())
            if min_amount is not None:
                clauses.append("l.signed_amount>=?")
                params.append(min_amount)
            if max_amount is not None:
                clauses.append("l.signed_amount<=?")
                params.append(max_amount)
            if search:
                clauses.append("(l.entry_id LIKE ? OR l.description LIKE ? OR l.reference LIKE ? OR l.account_code LIKE ? OR l.preparer LIKE ? OR l.vendor LIKE ? OR l.entity LIKE ?)")
                pattern = f"%{search}%"
                params.extend((pattern, pattern, pattern, pattern, pattern, pattern, pattern))
            where = " AND ".join(clauses)
            join = "FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id LEFT JOIN coa c ON c.account_code=l.account_code"
            total = store.conn.execute(f"SELECT COUNT(*) {join} WHERE {where}", params).fetchone()[0]
            rows = store.conn.execute(
                f"""SELECT e.*,l.entry_id,l.posting_date,l.document_date,l.account_code,c.account_name,l.debit,l.credit,
                    l.signed_amount,l.description,l.preparer,l.reference,l.entity,l.vendor,l.is_manual,
                    l.import_id,l.source_row,l.source_hash {join} WHERE {where}
                    ORDER BY e.risk_score DESC,e.id LIMIT ? OFFSET ?""",
                (*params, limit, offset),
            ).fetchall()
            return {"count": len(rows), "total": total, "limit": limit, "offset": offset, "rows": [_decode(row) for row in rows]}
        finally:
            store.close()

    @app.get("/api/exceptions/{exception_id}")
    def exception_detail(exception_id: int, request: Request):
        store = concrete_store(request)
        try:
            row = store.conn.execute(
                """SELECT e.*,l.entry_id,l.posting_date,l.document_date,l.account_code,c.account_name,
                   l.debit,l.credit,l.signed_amount,l.description,l.preparer,l.reference,l.entity,l.vendor,
                   l.is_manual,l.import_id,l.source_row,l.source_hash,l.raw_json
                   FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id
                   LEFT JOIN coa c ON c.account_code=l.account_code WHERE e.id=?""",
                (exception_id,),
            ).fetchone()
            if not row:
                raise LookupError("exception not found")
            item = _decode(row)
            item["source_record"] = json.loads(item.pop("raw_json"))
            item["reviews"] = [
                dict(review)
                for review in store.conn.execute("SELECT * FROM reviews WHERE exception_id=? ORDER BY id", (exception_id,))
            ]
            return item
        finally:
            store.close()

    @app.post("/api/review")
    def review(body: ReviewBody, request: Request):
        store = concrete_store(request)
        try:
            return record_review(
                store, body.id, body.reviewer, body.disposition, body.note, body.second_reviewer, body.second_note
            )
        finally:
            store.close()

    @app.get("/api/reviews")
    def reviews(
        request: Request,
        reviewer: str | None = Query(None, max_length=100),
        status_filter: Literal["open", "cleared", "follow_up", "selected_for_testing"] | None = Query(None, alias="status"),
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
    ):
        store = concrete_store(request)
        try:
            clauses, params = ["1=1"], []
            if reviewer:
                clauses.append("r.reviewer=?")
                params.append(reviewer)
            if status_filter:
                clauses.append("e.status=?")
                params.append(status_filter)
            where = " AND ".join(clauses)
            rows = store.conn.execute(
                f"""SELECT e.*,r.reviewer AS latest_reviewer,r.disposition AS latest_disposition,
                    r.note AS latest_note,r.second_reviewer,r.second_note,r.created_at AS latest_review_at
                    FROM exceptions e LEFT JOIN reviews r ON r.id=(SELECT MAX(id) FROM reviews WHERE exception_id=e.id)
                    WHERE {where} ORDER BY e.risk_score DESC,e.id LIMIT ? OFFSET ?""",
                (*params, limit, offset),
            ).fetchall()
            return {"rows": [dict(row) for row in rows], "limit": limit, "offset": offset}
        finally:
            store.close()

    @app.post("/api/assignments")
    def assignment(body: AssignmentBody, request: Request):
        store = concrete_store(request)
        try:
            return assign_exception(store, body.actor, body.exception_id, body.assignee, body.due_date)
        finally:
            store.close()

    @app.get("/api/review-set")
    def review_set(request: Request):
        store = concrete_store(request)
        try:
            return {"current": store.review_set_state(), "history": store.review_set_history()}
        finally:
            store.close()

    @app.post("/api/review-set/lock")
    def review_set_lock(body: ReviewSetBody, request: Request):
        store = concrete_store(request)
        try:
            return lock_review_set(store, body.actor, body.reason)
        finally:
            store.close()

    @app.post("/api/review-set/reopen")
    def review_set_reopen(body: ReviewSetBody, request: Request):
        store = concrete_store(request)
        try:
            return reopen_review_set(store, body.actor, body.reason)
        finally:
            store.close()

    @app.get("/api/similar")
    def similar(request: Request, q: str = Query(..., min_length=1, max_length=1000), limit: int = Query(25, ge=1, le=100)):
        store = concrete_store(request)
        try:
            return {"query": q, "results": similar_transactions(store, q, limit)}
        finally:
            store.close()

    @app.get("/api/semantic-profile")
    def semantic_profile(request: Request, run: int | None = Query(None, gt=0)):
        store = concrete_store(request)
        try:
            available_runs = [
                dict(row) for row in store.conn.execute(
                    "SELECT id,status,started_at FROM semantic_runs ORDER BY id DESC LIMIT 100"
                )
            ]
            if run is not None:
                result = get_semantic_profile(store, run)
            elif available_runs:
                result = get_semantic_profile(store)
            else:
                result = {"available": False}
            result["available_runs"] = available_runs
            return result
        finally:
            store.close()

    @app.get("/api/semantic-investigation")
    def semantic_investigation(request: Request, run: int = Query(..., gt=0), ledger_id: int = Query(..., gt=0)):
        store = concrete_store(request)
        try:
            return semantic_investigate(store, run, ledger_id)
        finally:
            store.close()

    @app.get("/api/mappings")
    def mappings(request: Request):
        store = concrete_store(request)
        try:
            return [dict(row) for row in store.conn.execute("SELECT name,created_at,created_by FROM import_mappings ORDER BY name")]
        finally:
            store.close()

    @app.get("/api/compare-runs")
    def compare_runs_route(request: Request, a: int = Query(..., gt=0), b: int = Query(..., gt=0)):
        store = concrete_store(request)
        try:
            return compare_runs(store, a, b)
        finally:
            store.close()

    @app.get("/api/models")
    def models(request: Request):
        store = concrete_store(request)
        try:
            return list_models(store)
        finally:
            store.close()

    @app.get("/api/bank")
    def bank(request: Request, limit: int = Query(200, ge=1, le=1000), offset: int = Query(0, ge=0)):
        store = concrete_store(request)
        try:
            return {"rows": [dict(row) for row in store.conn.execute(
                "SELECT * FROM bank_statements ORDER BY rowid DESC LIMIT ? OFFSET ?", (limit, offset)
            )], "limit": limit, "offset": offset}
        finally:
            store.close()

    @app.get("/api/account-taxonomy")
    def taxonomy(request: Request):
        store = concrete_store(request)
        try:
            return [dict(row) for row in store.conn.execute("SELECT * FROM account_taxonomy ORDER BY account_code")]
        finally:
            store.close()

    @app.post("/api/exports/package")
    def export_package(body: ExportBody, request: Request):
        store = concrete_store(request)
        try:
            require_role(store, body.actor, PREPARER_ROLES | REVIEW_ROLES)
            with tempfile.TemporaryDirectory(prefix="audit-export-") as directory:
                root = Path(directory)
                workpaper, manifest, _ = export_workpaper(store, str(root / "workpaper.csv"), body.actor)
                report = write_engagement_report(store, str(root / "engagement-report.html"), body.actor)
                archive_path = root / "audit-analytics-workpaper.zip"
                with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
                    archive.write(workpaper, workpaper.name)
                    archive.write(manifest, manifest.name)
                    archive.write(Path(str(manifest) + ".sha256"), Path(str(manifest) + ".sha256").name)
                    archive.write(report, report.name)
                content = archive_path.read_bytes()
            return Response(
                content,
                media_type="application/zip",
                headers={"Content-Disposition": 'attachment; filename="audit-analytics-workpaper.zip"'},
            )
        finally:
            store.close()

    if (resolved_static / "index.html").is_file():
        app.mount("/", StaticFiles(directory=resolved_static, html=True), name="static")
    else:
        @app.get("/")
        def missing_static():
            return JSONResponse(
                {"error": {"code": "static_missing", "message": "frontend build is missing; run npm --prefix frontend run build"}},
                status_code=503,
            )

    return app


app = create_app()
