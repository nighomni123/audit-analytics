import { useEffect, useMemo, useState } from "react";

import { download, post } from "../lib/api";
import { navigate, type Screen } from "../lib/navigation";
import type { StatusSummary, User } from "../lib/types";
import { Button, Checkbox, Disclosure, Field, Message, Panel, Select, StatusBadge, formatDate, formatNumber, titleCase } from "../components/ui";

export default function Workpapers({ status, users, refresh }: { status: StatusSummary; users: User[]; refresh: () => Promise<void> }) {
  const managers = useMemo(() => users.filter((user) => ["manager", "partner"].includes(user.role)), [users]);
  const [actor, setActor] = useState("");
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [exported, setExported] = useState(false);
  useEffect(() => { setActor((current) => current || managers[0]?.username || ""); }, [managers]);
  const checklist: Array<{ label: string; done: boolean; screen: Screen }> = [
    { label: "Engagement created", done: Boolean(status.engagement), screen: "engagement" },
    { label: "Population reconciled", done: status.population_acknowledged, screen: "population" },
    { label: "Methodology recorded", done: Boolean(status.settings.materiality?.overall || status.settings.materiality?.performance), screen: "methodology" },
    { label: "Analysis completed", done: status.latest_run.status === "complete", screen: "analysis" },
    { label: "Risk review completed", done: Boolean(status.latest_run.id && !status.review_status?.open), screen: "risk" },
    { label: "Sample created", done: Boolean(status.sample_sets?.length), screen: "sample" },
    { label: "Review set locked", done: status.review_set.locked, screen: "workpapers" },
  ];
  const complete = checklist.filter((item) => item.done).length;
  const readyToExport = status.population_acknowledged && status.latest_run.status === "complete" && status.review_set.locked;

  async function changeLock(action: "lock" | "reopen") {
    setBusy(true); setError(""); setNotice("");
    try { await post(`/review-set/${action}`, { actor, reason }); setReason(""); await refresh(); setNotice(action === "lock" ? "Review set locked." : "Review set reopened."); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "The review-set event could not be recorded."); }
    finally { setBusy(false); }
  }
  async function generate() {
    setBusy(true); setError(""); setNotice("");
    try { await download("exports/package", { actor }, "audit-analytics-workpaper.zip"); setExported(true); setNotice("Final workpaper package generated and downloaded."); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "The final package could not be generated."); }
    finally { setBusy(false); }
  }

  return <div className="workpapers-page"><div className="page-header"><div className="page-heading-copy"><div className="eyebrow">STEP 07 · FINALIZE</div><h1>Workpapers</h1><p>Close the engagement with a clear checklist, a locked review set, and a reproducible document package.</p></div><div className="page-header-action"><StatusBadge tone={status.review_set.locked ? "success" : "indigo"} dot>{status.review_set.locked ? "Review set locked" : "Closeout in progress"}</StatusBadge></div></div>{error && <Message kind="error">{error}</Message>}{notice && <Message kind="success">{notice}</Message>}<div className="closeout-layout"><Panel className="closeout-checklist"><div className="section-heading"><div><div className="eyebrow">COMPLETION CHECKLIST</div><h2>{complete} of {checklist.length} closeout steps complete</h2><p className="section-description">A locked review set is the governance milestone before final package generation.</p></div><span className="step-chip">07</span></div><div className="closeout-list">{checklist.map((item) => <button key={item.label} className={`closeout-row ${item.done ? "is-done" : ""}`} onClick={() => navigate(item.screen)}><span className="closeout-check">{item.done ? "✓" : "○"}</span><span><strong>{item.label}</strong><small>{item.done ? "Recorded in engagement history" : "Open this stage to continue"}</small></span><span className="closeout-arrow">→</span></button>)}</div></Panel><Panel className="lock-panel"><div className="section-heading"><div><div className="eyebrow">REVIEW SET GOVERNANCE</div><h2>{status.review_set.locked ? "Review set is locked" : "Lock the review set"}</h2></div><StatusBadge tone={status.review_set.locked ? "success" : "warning"} dot>{status.review_set.locked ? "Immutable milestone" : "Action required"}</StatusBadge></div>{status.review_set.locked ? <div className="locked-state"><div className="locked-icon">▣</div><p>{status.review_set.reason || "The review set was locked by the engagement team."}</p><small>Locked by {status.review_set.actor ?? "local manager"} · {formatDate(new Date((status.review_set.changed_at ?? 0) * 1000).toISOString().slice(0, 10))}</small></div> : <div className="lock-form"><p>Record a reason before creating the append-only lock event. Reopening requires a new reasoned event.</p><Field label="Manager"><Select value={actor} onChange={(event) => setActor(event.target.value)}><option value="">Choose manager</option>{managers.map((user) => <option key={user.username} value={user.username}>{user.username} · {user.role}</option>)}</Select></Field><Field label="Reason"><input className="input" value={reason} onChange={(event) => setReason(event.target.value)} placeholder="e.g. Risk cue review complete; sample selected." /></Field><Button variant="primary" onClick={() => changeLock("lock")} disabled={!actor || !reason.trim() || busy}>Lock review set</Button></div>}{status.review_set.locked && <div className="reopen-form"><Field label="Reason to reopen"><input className="input" value={reason} onChange={(event) => setReason(event.target.value)} placeholder="e.g. New evidence received." /></Field><Button variant="secondary" onClick={() => changeLock("reopen")} disabled={!actor || !reason.trim() || busy}>Reopen review set</Button></div>}</Panel></div><Panel className={`package-panel ${exported ? "is-complete" : ""}`}><div className="package-heading"><div><div className="eyebrow">DOCUMENT PACKAGE</div><h2>{exported ? "Package generated" : "Generate final package"}</h2><p>One portable archive for the review CSV, engagement report, evidence manifest, and detached checksum.</p></div><div className="package-illustration" aria-hidden="true"><span>CSV</span><span>HTML</span><span>SHA</span></div></div><div className="package-items"><div><span className="package-check">✓</span><span><strong>Journal-entry review CSV</strong><small>Ranked cues, dispositions, notes, and source lineage</small></span></div><div><span className="package-check">✓</span><span><strong>Engagement report</strong><small>Population, methodology, analysis, and limitations</small></span></div><div><span className="package-check">✓</span><span><strong>Evidence manifest</strong><small>Source imports, hashes, run configuration, and provenance</small></span></div><div><span className="package-check">✓</span><span><strong>SHA-256 checksum</strong><small>Integrity evidence; not a digital signature</small></span></div></div><div className="package-footer"><div className="package-readiness"><span className={readyToExport ? "status-dot" : "status-dot warning-dot"} />{readyToExport ? "Ready to generate" : "Complete the checklist and lock the review set first"}</div><Button variant="primary" size="lg" onClick={generate} disabled={!readyToExport || !actor || busy}>{busy ? "Generating package…" : "Generate final package"}</Button></div></Panel><div className="workpaper-bottom"><Panel><div className="eyebrow">TRACEABILITY</div><h2>Every decision has a trail.</h2><p>Open the audit trail to inspect imports, acknowledgements, analysis runs, reviews, lock events, and exports.</p><Button variant="secondary" onClick={() => navigate("activity")}>Open audit trail →</Button></Panel><Panel><div className="eyebrow">PACKAGE NOTES</div><h2>Keep the evidence with the workpaper.</h2><p>Store the generated archive with the local database and preserved evidence according to your firm’s retention process.</p><Disclosure summary="Technical package details"><ul className="simple-list"><li>Archive includes a detached manifest checksum.</li><li>Semantic provenance is included when a semantic run was used.</li><li>Export is a local download; no cloud service receives the package.</li></ul></Disclosure></Panel></div></div>;
}
