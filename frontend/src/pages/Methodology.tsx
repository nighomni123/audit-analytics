import { useEffect, useMemo, useState, type FormEvent } from "react";

import { get, put } from "../lib/api";
import { navigate } from "../lib/navigation";
import type { StatusSummary, User } from "../lib/types";
import { Button, Checkbox, Disclosure, Field, Message, Panel, Select, StatusBadge, TextInput } from "../components/ui";

interface SemanticProfileResponse { available_runs?: Array<{ id: number; status: string; started_at: number }>; }

export default function Methodology({ status, users, refresh, revision }: { status: StatusSummary; users: User[]; refresh: () => Promise<void>; revision: number }) {
  const managers = useMemo(() => users.filter((user) => ["manager", "partner"].includes(user.role)), [users]);
  const [actor, setActor] = useState("");
  const [overall, setOverall] = useState("");
  const [performance, setPerformance] = useState("");
  const [periodDays, setPeriodDays] = useState("3");
  const [roundAmount, setRoundAmount] = useState("1000");
  const [robustZ, setRobustZ] = useState("3.5");
  const [includeIsolation, setIncludeIsolation] = useState(true);
  const [semanticEnabled, setSemanticEnabled] = useState(false);
  const [semanticRun, setSemanticRun] = useState("");
  const [semanticRuns, setSemanticRuns] = useState<Array<{ id: number; status: string; started_at: number }>>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => { setActor((current) => current || managers[0]?.username || ""); }, [managers]);
  useEffect(() => {
    const policy = status.settings.analysis_policy ?? {};
    const materiality = status.settings.materiality ?? {};
    setOverall(materiality.overall?.toString() ?? ""); setPerformance(materiality.performance?.toString() ?? "");
    setPeriodDays((policy.period_end_days ?? 3).toString()); setRoundAmount((policy.round_amount_threshold ?? 1000).toString()); setRobustZ((policy.outlier_robust_z ?? 3.5).toString());
  }, [revision, status.settings]);
  useEffect(() => { get<SemanticProfileResponse>("/semantic-profile").then((result) => setSemanticRuns(result.available_runs ?? [])).catch(() => setSemanticRuns([])); }, [revision]);

  async function save(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError(""); setSuccess("");
    try {
      await put("/config", { actor, materiality: overall === "" ? null : Number(overall), performance_materiality: performance === "" ? null : Number(performance), period_end_days: Number(periodDays), round_amount_threshold: roundAmount === "" ? null : Number(roundAmount), outlier_robust_z: robustZ === "" ? null : Number(robustZ) });
      await refresh(); setSuccess("Engagement parameters were saved. The next analysis run will capture this methodology.");
    } catch (cause) { setError(cause instanceof Error ? cause.message : "The audit setup could not be saved."); }
    finally { setBusy(false); }
  }

  return <div className="methodology-page"><div className="page-header"><div className="page-heading-copy"><div className="eyebrow">STEP 03 · AUDIT CONTEXT</div><h1>Audit setup</h1><p>Record the planning context that helps the team decide where to focus. Keep advanced parameters available without putting them in the main path.</p></div><div className="page-header-action"><StatusBadge tone={status.population_acknowledged ? "success" : "warning"} dot>{status.population_acknowledged ? "Ready for analysis" : "Population acknowledgement required"}</StatusBadge></div></div>{error && <Message kind="error">{error}</Message>}{success && <Message kind="success">{success}</Message>}<div className="methodology-layout"><form onSubmit={save}><Panel className="setup-basics"><div className="section-heading"><div><div className="eyebrow">PLANNING CONTEXT</div><h2>Materiality and review thresholds</h2><p className="section-description">These amounts are disclosed planning context. They help label and sample the population; they do not directly modify analytical risk scores.</p></div><span className="step-chip">03</span></div><div className="form-grid"><Field label="Overall materiality" hint="Planning threshold for the engagement."><TextInput type="number" min="0" step="0.01" value={overall} onChange={(event) => setOverall(event.target.value)} placeholder="e.g. 500000" /></Field><Field label="Performance materiality" hint="Must not exceed overall materiality."><TextInput type="number" min="0" step="0.01" value={performance} onChange={(event) => setPerformance(event.target.value)} placeholder="e.g. 350000" /></Field><Field label="Period-end window (days)" hint="Highlights postings near the engagement period end."><TextInput type="number" min="0" max="366" value={periodDays} onChange={(event) => setPeriodDays(event.target.value)} /></Field><Field label="Large amount threshold" hint="Used by the round-amount review signal."><TextInput type="number" min="0" step="0.01" value={roundAmount} onChange={(event) => setRoundAmount(event.target.value)} /></Field></div><div className="helper-strip"><span>i</span><p><strong>Materiality is context, not a conclusion.</strong> The workpaper records the thresholds used so reviewers can understand the sampling and review decisions.</p></div></Panel><Panel className="advanced-panel"><Disclosure summary="Advanced methodology" defaultOpen={false}><div className="advanced-content"><div className="form-grid"><Field label="Peer outlier robust z" hint="Technical threshold for account-peer context."><TextInput type="number" min="0.1" step="0.1" value={robustZ} onChange={(event) => setRobustZ(event.target.value)} /></Field><Field label="Configuration owner"><Select value={actor} onChange={(event) => setActor(event.target.value)}><option value="">Choose manager</option>{managers.map((user) => <option key={user.username} value={user.username}>{user.username} · {user.role}</option>)}</Select></Field></div><Checkbox label="Enable experimental isolation-style ranking for the next run" checked={includeIsolation} onChange={(event) => setIncludeIsolation(event.target.checked)} /><p className="muted-copy">This is an optional ranking aid. It is recorded in the analysis configuration and can be disabled by the engagement team.</p></div></Disclosure></Panel><div className="methodology-actions"><Button type="submit" variant="primary" size="lg" disabled={busy || !actor}>{busy ? "Saving audit setup…" : "Save audit setup"}</Button><Button type="button" variant="secondary" onClick={() => navigate("analysis")}>Continue to analysis <span>→</span></Button></div></form><aside className="methodology-side"><Panel className="semantic-setup-card"><div className="section-heading"><div><div className="eyebrow">OPTIONAL SEMANTIC ANALYSIS</div><h2>Semantic context</h2></div><StatusBadge tone="warning">Experimental</StatusBadge></div><p>Use a completed local semantic profile to add narrative and peer context to the next run. The deterministic review path remains active.</p><Checkbox label="Include available semantic context" checked={semanticEnabled} onChange={(event) => setSemanticEnabled(event.target.checked)} disabled={!semanticRuns.length} /><Field label="Semantic profile run"><Select value={semanticRun} onChange={(event) => setSemanticRun(event.target.value)} disabled={!semanticEnabled || !semanticRuns.length}><option value="">{semanticRuns.length ? "Choose completed profile" : "No completed local profile"}</option>{semanticRuns.filter((run) => run.status === "complete").map((run) => <option key={run.id} value={run.id}>Run {run.id} · completed</option>)}</Select></Field>{!semanticRuns.length && <div className="semantic-unavailable"><strong>No completed semantic profile found.</strong><span>The core analysis remains available without one. Build a local profile through the approved technical workflow when needed.</span></div>}<div className="semantic-boundary"><strong>Boundary</strong><span>Semantic context augments review and never suppresses lexical or deterministic evidence.</span></div></Panel><Panel className="methodology-checklist"><div className="eyebrow">BEFORE ANALYSIS</div><h2>Quick check</h2><ul><li className={status.population_acknowledged ? "is-done" : ""}><span>{status.population_acknowledged ? "✓" : "○"}</span>Population acknowledged</li><li className={Boolean(overall || performance) ? "is-done" : ""}><span>{overall || performance ? "✓" : "○"}</span>Planning context recorded</li><li className={status.latest_run.id ? "is-done" : ""}><span>{status.latest_run.id ? "✓" : "○"}</span>Analysis run versioned</li></ul><Button variant="secondary" size="sm" onClick={() => navigate(status.population_acknowledged ? "analysis" : "population")}>{status.population_acknowledged ? "Open analysis" : "Return to population"} →</Button></Panel></aside></div></div>;
}
