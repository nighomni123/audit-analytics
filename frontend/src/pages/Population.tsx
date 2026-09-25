import { useEffect, useMemo, useState, type DragEvent, type FormEvent } from "react";

import { ApiError, post, put, upload } from "../lib/api";
import { navigate } from "../lib/navigation";
import type { ImportResult, PreviewResult, StatusSummary, User } from "../lib/types";
import { humanizeReason } from "../lib/workflow";
import { Button, Checkbox, Disclosure, Field, Message, Panel, Select, StatusBadge, TextArea, TextInput, formatDate, formatMoney, formatNumber, titleCase } from "../components/ui";

const requiredMappingFields = [
  ["entry_id", "Entry ID"],
  ["posting_date", "Posting date"],
  ["account_code", "Account code"],
  ["amount", "Amount / debit / credit"],
  ["description", "Narration"],
] as const;
const additionalMappingFields = [
  ["document_date", "Document date"],
  ["debit", "Debit"],
  ["credit", "Credit"],
  ["preparer", "Preparer"],
  ["reference", "Reference"],
  ["vendor", "Vendor"],
  ["entity", "Entity"],
  ["is_manual", "Manual / system flag"],
] as const;

function usersFor(users: User[], roles: string[]): User[] { return users.filter((user) => roles.includes(user.role)); }

export default function Population({ status, users, refresh, revision }: { status: StatusSummary; users: User[]; refresh: () => Promise<void>; revision: number }) {
  const importers = useMemo(() => usersFor(users, ["preparer", "reviewer", "manager", "partner"]), [users]);
  const reviewers = useMemo(() => usersFor(users, ["reviewer", "manager", "partner", "quality_reviewer"]), [users]);
  const managers = useMemo(() => usersFor(users, ["manager", "partner"]), [users]);
  const [actor, setActor] = useState("");
  const [reviewer, setReviewer] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<PreviewResult | null>(null);
  const [mapping, setMapping] = useState<Record<string, string>>({});
  const [showAdditional, setShowAdditional] = useState(false);
  const [expectedRows, setExpectedRows] = useState("");
  const [expectedDebits, setExpectedDebits] = useState("");
  const [expectedCredits, setExpectedCredits] = useState("");
  const [reimport, setReimport] = useState(false);
  const [duplicate, setDuplicate] = useState<{ id: number; message: string } | null>(null);
  const [note, setNote] = useState("");
  const [override, setOverride] = useState(false);
  const [overall, setOverall] = useState("");
  const [performance, setPerformance] = useState("");
  const [periodDays, setPeriodDays] = useState("3");
  const [includeIsolation, setIncludeIsolation] = useState(true);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => { setActor((current) => current || importers[0]?.username || ""); }, [importers]);
  useEffect(() => { setReviewer((current) => current || reviewers[0]?.username || ""); }, [reviewers]);
  useEffect(() => {
    const policy = status.settings.analysis_policy ?? {};
    const materiality = status.settings.materiality ?? {};
    setOverall(materiality.overall?.toString() ?? "");
    setPerformance(materiality.performance?.toString() ?? "");
    setPeriodDays((policy.period_end_days ?? 3).toString());
  }, [revision, status.settings]);

  const glImports = status.imports.filter((item) => item.kind === "gl");
  const latestImport = glImports[glImports.length - 1];
  const reconciliation = latestImport?.reconciliation;
  const pending = glImports.some((item) => item.acknowledged_at === null);

  function chooseFile(next: File | null) {
    setFile(next); setPreview(null); setDuplicate(null); setReimport(false); setError(""); setSuccess("");
  }
  function dropFile(event: DragEvent<HTMLLabelElement>) { event.preventDefault(); const dropped = event.dataTransfer.files?.[0]; if (dropped) chooseFile(dropped); }

  async function runPreview(event: FormEvent) {
    event.preventDefault(); if (!file) return;
    setBusy("preview"); setError(""); setSuccess("");
    const form = new FormData(); form.append("file", file);
    try {
      const result = await upload<PreviewResult>("/imports/preview", form);
      setPreview(result);
      setMapping(Object.fromEntries(Object.entries(result.mapping).filter((entry): entry is [string, string] => Boolean(entry[1]))));
    } catch (cause) { setError(cause instanceof Error ? cause.message : "The source could not be read."); }
    finally { setBusy(""); }
  }

  async function runImport() {
    if (!file) return;
    setBusy("import"); setError(""); setSuccess("");
    const form = new FormData();
    form.append("file", file); form.append("actor", actor); form.append("reimport", String(reimport));
    if (expectedRows) form.append("expected_rows", expectedRows);
    if (expectedDebits) form.append("expected_debits", expectedDebits);
    if (expectedCredits) form.append("expected_credits", expectedCredits);
    if (Object.keys(mapping).length) form.append("mapping", JSON.stringify(mapping));
    try {
      const result = await upload<ImportResult>("/imports/gl", form);
      setSuccess(`Import ${result.import_id} stored ${result.accepted} accepted and ${result.rejected} rejected rows. The original file is preserved as evidence.`);
      setFile(null); setPreview(null); setMapping({}); setDuplicate(null); setReimport(false); await refresh();
    } catch (cause) {
      if (cause instanceof ApiError && cause.code === "duplicate_import") {
        const existing = (cause.details as { existing_import_id?: number } | undefined)?.existing_import_id;
        setDuplicate({ id: existing ?? 0, message: cause.message });
      } else setError(cause instanceof Error ? cause.message : "The ledger could not be imported.");
    } finally { setBusy(""); }
  }

  async function acknowledge() {
    setBusy("acknowledge"); setError(""); setSuccess("");
    try {
      await post("/imports/acknowledge", { reviewer, note, override_reconciliation: override });
      setNote(""); setOverride(false); await refresh();
      setSuccess("Population reconciliation was recorded and analysis is unlocked.");
    } catch (cause) { setError(cause instanceof Error ? cause.message : "The population acknowledgement could not be recorded."); }
    finally { setBusy(""); }
  }

  async function saveQuickConfiguration(event: FormEvent) {
    event.preventDefault(); setBusy("configure"); setError(""); setSuccess("");
    try {
      await put("/config", { actor: managers[0]?.username || actor, materiality: overall === "" ? null : Number(overall), performance_materiality: performance === "" ? null : Number(performance), period_end_days: Number(periodDays) });
      await refresh(); setSuccess("Engagement parameters were saved.");
    } catch (cause) { setError(cause instanceof Error ? cause.message : "The planning parameters could not be saved."); }
    finally { setBusy(""); }
  }

  async function analyze() {
    setBusy("analyze"); setError(""); setSuccess("");
    try { const result = await post<{ run_id: number }>("/analysis-runs", { actor, include_isolation: includeIsolation }); await refresh(); navigate("risk", { run: result.run_id }); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Analysis could not be started."); }
    finally { setBusy(""); }
  }

  function setMapped(field: string, value: string) {
    setMapping((current) => { const next = { ...current }; if (value) next[field] = value; else delete next[field]; return next; });
  }

  return <div className="population-page"><div className="page-header"><div className="page-heading-copy"><div className="eyebrow">STEP 02 · CLIENT LEDGER</div><h1>Population</h1><p>Add the complete ledger, confirm how its fields map, and reconcile the accepted population to the client control totals.</p></div><div className="page-header-action"><h2 className="legacy-heading">Population & Configuration</h2><StatusBadge tone={status.population_acknowledged ? "success" : pending ? "warning" : "neutral"} dot>{status.population_acknowledged ? "Population acknowledged" : pending ? "Acknowledgement required" : "Awaiting ledger"}</StatusBadge></div></div>
    {error && <Message kind="error">{error}</Message>}{success && <Message kind="success">{success}</Message>}
    <div className="population-layout"><div className="population-main"><Panel className="ingestion-panel"><div className="section-heading"><div><div className="eyebrow">EVIDENCE INGESTION</div><h2>Add client ledger</h2><p className="section-description">The original upload is copied into local evidence storage and identified by its SHA-256 hash.</p></div><span className="step-chip">01</span></div><label className={`dropzone ${file ? "has-file" : ""}`} onDragOver={(event) => event.preventDefault()} onDrop={dropFile}><input key={`${file?.name ?? "empty"}-${file?.size ?? 0}`} type="file" accept=".csv,.xlsx" aria-label="CSV or bounded XLSX source" onChange={(event) => chooseFile(event.target.files?.[0] ?? null)} /><span className="dropzone-icon" aria-hidden="true">↑</span>{file ? <><strong>{file.name}</strong><span>{(file.size / 1024).toFixed(1)} KB · ready to preview</span><small>Choose a different file</small></> : <><strong>Drop your GL export here</strong><span>or choose a CSV or XLSX file</span><small>Complete line-level population · no cloud upload</small></>}</label><div className="ingestion-user-row"><Field label="Import user"><Select value={actor} onChange={(event) => setActor(event.target.value)} disabled={!importers.length}>{importers.map((user) => <option key={user.username} value={user.username}>{user.username} · {user.role}</option>)}</Select></Field><Button variant="secondary" onClick={runPreview} disabled={!file || Boolean(busy)}>{busy === "preview" ? "Reading source…" : "Preview source"}</Button></div>{preview && <div className="preview-block"><div className="preview-status-grid"><div><span className="check-mark">✓</span><strong>File readable</strong><small>{preview.file}</small></div><div><span className="check-mark">✓</span><strong>{formatNumber(preview.row_count ?? preview.sample_rows.length)} rows found</strong><small>Accepted rows are checked again on import</small></div><div><span className={preview.missing_required.length ? "warning-mark" : "check-mark"}>{preview.missing_required.length ? "!" : "✓"}</span><strong>{preview.missing_required.length ? `${preview.missing_required.length} fields need confirmation` : "Required fields detected"}</strong><small>{preview.missing_required.length ? preview.missing_required.map(humanizeReason).join(", ") : "Auto-detected concepts are marked below"}</small></div></div>{!preview.missing_required.length && <Message kind="success">All required concepts detected in {preview.file}.</Message>}<div className="mapping-heading"><div><div className="eyebrow">CONFIRM YOUR LEDGER FIELDS</div><h3>Mapping is ready to review</h3></div><StatusBadge tone="success">Auto-detected</StatusBadge></div><div className="mapping-table-wrap"><table className="mapping-table"><thead><tr><th>Audit field</th><th>Source column</th><th>Status</th></tr></thead><tbody>{requiredMappingFields.map(([field, label]) => <tr key={field}><td><strong>{label}</strong><small>{field}</small></td><td><Select aria-label={`Map ${label}`} value={mapping[field] ?? ""} onChange={(event) => setMapped(field, event.target.value)}><option value="">Not mapped</option>{preview.headers.map((header) => <option key={header} value={header}>{header}</option>)}</Select></td><td>{mapping[field] ? <span className="mapping-ok"><span>✓</span> Detected</span> : <span className="mapping-needed"><span>!</span> Confirm</span>}</td></tr>)}</tbody></table></div><button className="additional-fields-toggle" onClick={() => setShowAdditional((value) => !value)}>{showAdditional ? "Hide additional fields" : "Show additional fields"}<span>{showAdditional ? "⌃" : "⌄"}</span></button>{showAdditional && <div className="mapping-table-wrap additional-mapping"><table className="mapping-table"><thead><tr><th>Additional field</th><th>Source column</th><th>Status</th></tr></thead><tbody>{additionalMappingFields.map(([field, label]) => <tr key={field}><td><strong>{label}</strong><small>{field}</small></td><td><Select aria-label={`Map ${label}`} value={mapping[field] ?? ""} onChange={(event) => setMapped(field, event.target.value)}><option value="">Not mapped</option>{preview.headers.map((header) => <option key={header} value={header}>{header}</option>)}</Select></td><td>{mapping[field] ? <span className="mapping-ok"><span>✓</span> Detected</span> : <span className="mapping-muted">Optional</span>}</td></tr>)}</tbody></table></div>}<div className="sample-preview"><div className="sample-preview-heading"><div><div className="eyebrow">ACTUAL SOURCE SAMPLE</div><h3>First imported rows</h3></div><span>Visual check before import</span></div><div className="table-scroll"><table className="data-table"><thead><tr>{preview.headers.slice(0, 6).map((header) => <th key={header}>{header}</th>)}</tr></thead><tbody>{preview.sample_rows.slice(0, 3).map((row, index) => <tr key={index}>{preview.headers.slice(0, 6).map((header) => <td key={header}>{row[header] ?? "—"}</td>)}</tr>)}</tbody></table></div></div></div>}
      <div className="control-total-form"><div className="section-heading compact"><div><div className="eyebrow">CLIENT CONTROL TOTALS</div><h3>Reconcile the accepted population</h3></div><span className="muted-label">Optional until supplied</span></div><div className="form-grid three"><Field label="Expected rows"><TextInput type="number" min="0" value={expectedRows} onChange={(event) => setExpectedRows(event.target.value)} placeholder="e.g. 125430" /></Field><Field label="Expected debits"><TextInput type="number" step="0.01" value={expectedDebits} onChange={(event) => setExpectedDebits(event.target.value)} placeholder="e.g. 987654321.50" /></Field><Field label="Expected credits"><TextInput type="number" step="0.01" value={expectedCredits} onChange={(event) => setExpectedCredits(event.target.value)} placeholder="e.g. 987654321.50" /></Field></div></div><div className="import-actions">{duplicate && <div className="duplicate-confirm"><Message kind="warning">{duplicate.message}. This file already exists in this engagement.</Message><Button size="sm" onClick={() => { setReimport(true); setDuplicate(null); }}>Import as new version</Button></div>}<Button variant="primary" size="lg" onClick={runImport} disabled={!file || !actor || Boolean(busy) || Boolean(duplicate)}>{busy === "import" ? "Importing ledger…" : "Import ledger"}</Button><span className="form-footnote">Required fields must be confirmed before analysis.</span></div></Panel></div><aside className="population-side"><Panel className={`reconciliation-panel ${reconciliation?.matches ? "is-reconciled" : reconciliation ? "has-difference" : ""}`}><div className="section-heading"><div><div className="eyebrow">POPULATION REVIEW</div><h2>Control totals</h2></div>{reconciliation && <StatusBadge tone={reconciliation.matches ? "success" : "warning"} dot>{reconciliation.matches ? "Reconciled" : "Difference"}</StatusBadge>}</div>{latestImport ? <><div className="imported-count"><span>Imported entries</span><strong>{formatNumber(reconciliation?.accepted_rows ?? latestImport.accepted_rows)}</strong><small>{latestImport.original_name} · import #{latestImport.id}</small></div><div className="reconciliation-table"><div className="reconciliation-row reconciliation-head"><span> </span><strong>CLIENT SOURCE</strong><strong>IMPORTED</strong></div><div className="reconciliation-row"><span>Rows</span><strong>{reconciliation?.expected_rows === null || reconciliation?.expected_rows === undefined ? "—" : formatNumber(reconciliation.expected_rows)}</strong><strong>{formatNumber(reconciliation?.accepted_rows ?? latestImport.accepted_rows)} {reconciliation?.matches ? "✓" : ""}</strong></div><div className="reconciliation-row"><span>Debit</span><strong>{reconciliation?.expected_debits == null ? "—" : formatMoney(reconciliation.expected_debits, true)}</strong><strong>{formatMoney(reconciliation?.control_debits ?? 0, true)}</strong></div><div className="reconciliation-row"><span>Credit</span><strong>{reconciliation?.expected_credits == null ? "—" : formatMoney(reconciliation.expected_credits, true)}</strong><strong>{formatMoney(reconciliation?.control_credits ?? 0, true)}</strong></div></div>{reconciliation?.matches ? <div className="reconciliation-success"><span>✓</span><div><strong>RECONCILED</strong><p>The imported population agrees to the supplied client control totals.</p></div></div> : reconciliation ? <div className="reconciliation-difference"><strong>RECONCILIATION DIFFERENCE</strong><p>Source: {reconciliation.expected_rows ?? "—"} rows · Imported: {reconciliation.accepted_rows} rows</p><p>Document the intentional difference before acknowledgement.</p></div> : <div className="reconciliation-empty">Supply control totals to compare the source and imported population.</div>}</> : <div className="reconciliation-empty"><span className="empty-icon">—</span><p>No ledger imported yet.<br />Add the client's GL to begin population validation.</p></div>}</Panel><Panel className="ack-panel"><div className="section-heading"><div><div className="eyebrow">REVIEWER ACKNOWLEDGEMENT</div><h2>Unlock analysis</h2></div><span className="step-chip">02</span></div>{status.population_acknowledged ? <Message kind="success">Population acknowledged. Analysis is unlocked for this engagement.</Message> : <div className="ack-form"><Field label="Reviewer"><Select value={reviewer} onChange={(event) => setReviewer(event.target.value)} disabled={!pending || !reviewers.length}>{reviewers.map((user) => <option key={user.username} value={user.username}>{user.username} · {user.role}</option>)}</Select></Field><Field label="Acknowledgement note"><TextArea aria-label="Acknowledgement note" rows={3} value={note} onChange={(event) => setNote(event.target.value)} placeholder="State what was checked and why the population is appropriate for analysis." /></Field>{reconciliation && !reconciliation.matches && <Checkbox label="Document intentional difference" checked={override} onChange={(event) => setOverride(event.target.checked)} />}<Button variant="success" onClick={acknowledge} disabled={!pending || !reviewer || !note.trim() || Boolean(busy)}>{busy === "acknowledge" ? "Recording acknowledgement…" : "Acknowledge population"}</Button></div>}</Panel></aside></div>
    <Panel className="quick-methodology"><div className="section-heading"><div><div className="eyebrow">QUICK SETUP</div><h2>Record audit context</h2><p className="section-description">Planning thresholds provide context for review. They do not change risk scores.</p></div><Button variant="quiet" size="sm" onClick={() => navigate("methodology")}>Open full Audit setup →</Button></div><form onSubmit={saveQuickConfiguration}><div className="form-grid three"><Field label="Overall materiality"><TextInput type="number" min="0" step="0.01" value={overall} onChange={(event) => setOverall(event.target.value)} placeholder="Planning amount" /></Field><Field label="Performance materiality"><TextInput type="number" min="0" step="0.01" value={performance} onChange={(event) => setPerformance(event.target.value)} placeholder="Planning amount" /></Field><Field label="Period-end window (days)"><TextInput type="number" min="0" max="366" value={periodDays} onChange={(event) => setPeriodDays(event.target.value)} /></Field></div><Button type="submit" disabled={!managers.length || Boolean(busy)}>{busy === "configure" ? "Saving…" : "Save parameters"}</Button></form></Panel>
    <Panel className="quick-analysis"><div><div className="eyebrow">ANALYSIS EXECUTION</div><h2>Ready to prioritize review?</h2><p>Analysis stays locked until the population is acknowledged. Each run records its policy, population, and provenance.</p></div><div className="quick-analysis-actions"><Checkbox label="Include experimental isolation-style ranking" checked={includeIsolation} onChange={(event) => setIncludeIsolation(event.target.checked)} /><Button variant="primary" onClick={analyze} disabled={!status.population_acknowledged || !actor || Boolean(busy)}>{busy === "analyze" ? "Starting analysis…" : "Run analysis"}</Button></div></Panel>
    <div className="imports-history"><div className="section-heading"><div><div className="eyebrow">PRESERVED EVIDENCE</div><h2>Import history</h2></div><span className="muted-label">Source hashes remain available in the audit trail</span></div>{glImports.length ? <div className="table-scroll"><table className="data-table import-table"><thead><tr><th>Version</th><th>Source file</th><th>Accepted</th><th>Rejected</th><th>State</th><th>Source hash</th></tr></thead><tbody>{glImports.map((item) => <tr key={item.id}><td><strong>#{item.id}</strong>{item.supersedes_import_id && <small>supersedes #{item.supersedes_import_id}</small>}</td><td>{item.original_name}</td><td>{formatNumber(item.accepted_rows)}</td><td>{formatNumber(item.rejected_rows)}</td><td><StatusBadge tone={item.acknowledged_at ? "success" : "warning"} dot>{item.acknowledged_at ? "Acknowledged" : "Pending"}</StatusBadge></td><td><code>{item.sha256.slice(0, 12)}…</code></td></tr>)}</tbody></table></div> : <p className="muted-copy">No GL versions have been stored.</p>}</div>
  </div>;
}
