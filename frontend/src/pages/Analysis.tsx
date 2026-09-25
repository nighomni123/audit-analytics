import { useEffect, useMemo, useState } from "react";

import { get, post } from "../lib/api";
import { navigate } from "../lib/navigation";
import type { StatusSummary, User } from "../lib/types";
import { Button, Checkbox, Disclosure, Field, Message, Panel, ProgressBar, Select, StatusBadge, TechnicalDetails, formatNumber, titleCase } from "../components/ui";

const pipeline = [
  "Population verified",
  "Duplicate detection",
  "Round amount analysis",
  "Period-end analysis",
  "Reversal analysis",
  "Account peer analysis",
  "Optional semantic context",
  "Final results",
];

interface ProfileResponse { available_runs?: Array<{ id: number; status: string }>; }

export default function Analysis({ status, users, refresh, revision }: { status: StatusSummary; users: User[]; refresh: () => Promise<void>; revision: number }) {
  const actors = useMemo(() => users.filter((user) => ["preparer", "reviewer", "manager", "partner"].includes(user.role)), [users]);
  const [actor, setActor] = useState("");
  const [includeIsolation, setIncludeIsolation] = useState(true);
  const [semanticEnabled, setSemanticEnabled] = useState(false);
  const [semanticRun, setSemanticRun] = useState("");
  const [profiles, setProfiles] = useState<ProfileResponse["available_runs"]>([]);
  const [running, setRunning] = useState(false);
  const [stage, setStage] = useState(0);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => { setActor((current) => current || actors[0]?.username || ""); }, [actors]);
  useEffect(() => { get<ProfileResponse>("/semantic-profile").then((result) => setProfiles(result.available_runs ?? [])).catch(() => setProfiles([])); }, [revision]);
  useEffect(() => {
    if (!running) return;
    const timer = window.setInterval(() => setStage((value) => Math.min(value + 1, pipeline.length - 1)), 850);
    return () => window.clearInterval(timer);
  }, [running]);

  async function run() {
    setRunning(true); setStage(0); setError(""); setNotice("");
    try {
      const result = await post<{ run_id: number }>("/analysis-runs", { actor, include_isolation: includeIsolation, semantic_run_id: semanticEnabled && semanticRun ? Number(semanticRun) : null });
      setStage(pipeline.length - 1); await refresh(); navigate("risk", { run: result.run_id });
    } catch (cause) { setError(cause instanceof Error ? cause.message : "The analysis run could not be completed."); }
    finally { setRunning(false); }
  }

  const latestComplete = status.latest_run.id && status.latest_run.status === "complete";
  return <div className="analysis-page"><div className="page-header"><div className="page-heading-copy"><div className="eyebrow">STEP 04 · GOVERNED ANALYSIS</div><h1>Analysis</h1><p>Run a reproducible analysis over the acknowledged population. The output is a ranked set of risk cues for human review.</p></div><div className="page-header-action"><StatusBadge tone={status.population_acknowledged ? "success" : "warning"} dot>{status.population_acknowledged ? "Population verified" : "Analysis locked"}</StatusBadge></div></div>{error && <Message kind="error">{error}</Message>}{notice && <Message kind="info">{notice}</Message>}{!status.population_acknowledged && <Message kind="warning">Analysis is locked until the population is acknowledged. <button className="inline-link" onClick={() => navigate("population")}>Return to population review →</button></Message>}{running ? <Panel className="analysis-progress-panel"><div className="analysis-progress-heading"><div><div className="eyebrow">ANALYSIS IN PROGRESS</div><h2>Building a review queue</h2><p>Large populations can take a little time. The original ledger and evidence remain available while this run is prepared.</p></div><div className="analysis-progress-number">{Math.round(((stage + 1) / pipeline.length) * 100)}%</div></div><ProgressBar value={((stage + 1) / pipeline.length) * 100} /><div className="pipeline-list">{pipeline.map((item, index) => <div className={`pipeline-step ${index < stage ? "is-complete" : index === stage ? "is-current" : ""}`} key={item}><span className="pipeline-marker">{index < stage ? "✓" : index === stage ? "●" : "○"}</span><span>{item}</span>{index < stage && <small>complete</small>}{index === stage && <small>working</small>}</div>)}</div><div className="technical-inline"><span>Technical details are available after the run.</span><StatusBadge tone="neutral">Local governed pipeline</StatusBadge></div></Panel> : <div className="analysis-layout"><Panel className="analysis-launch-card"><div className="section-heading"><div><div className="eyebrow">RUN A VERSIONED ANALYSIS</div><h2>Analysis setup</h2><p className="section-description">Each run captures the population, policy, model components, and limitations so later review can be reproduced.</p></div><span className="step-chip">04</span></div><div className="form-grid"><Field label="Run as"><Select value={actor} onChange={(event) => setActor(event.target.value)} disabled={!actors.length}><option value="">Choose local user</option>{actors.map((user) => <option key={user.username} value={user.username}>{user.username} · {user.role}</option>)}</Select></Field><Field label="Optional semantic profile"><Select value={semanticRun} onChange={(event) => setSemanticRun(event.target.value)} disabled={!semanticEnabled || !profiles?.length}><option value="">{profiles?.length ? "Use deterministic path only" : "No completed local profile"}</option>{profiles?.filter((profile) => profile.status === "complete").map((profile) => <option key={profile.id} value={profile.id}>Semantic run {profile.id}</option>)}</Select></Field></div><div className="analysis-options"><Checkbox label="Include experimental isolation-style ranking" checked={includeIsolation} onChange={(event) => setIncludeIsolation(event.target.checked)} /><Checkbox label="Add semantic context when a completed local profile is selected" checked={semanticEnabled} onChange={(event) => setSemanticEnabled(event.target.checked)} disabled={!profiles?.length} /></div><div className="analysis-boundary"><strong>Governance boundary</strong><span>Semantic context can augment the queue, but it never suppresses the deterministic or lexical review path.</span></div><Button variant="primary" size="lg" onClick={run} disabled={!status.population_acknowledged || !actor || !status.entries}>{status.latest_run.id ? "Run another analysis" : "Run analysis"}<span>→</span></Button></Panel><aside className="analysis-side"><Panel className="pipeline-preview"><div className="eyebrow">WHAT WILL RUN</div><h2>Transparent by design</h2><div className="mini-pipeline">{pipeline.slice(0, 7).map((item, index) => <div key={item}><span>{String(index + 1).padStart(2, "0")}</span>{item}</div>)}</div><p>Open technical details after completion to inspect policy, checks, and limitations.</p></Panel><Panel className="analysis-history-card"><div className="eyebrow">RUN HISTORY</div><h2>{status.latest_run.id ? `Run ${status.latest_run.id}` : "No run yet"}</h2>{status.latest_run.id ? <><StatusBadge tone={latestComplete ? "success" : "warning"} dot>{titleCase(status.latest_run.status ?? "unknown")}</StatusBadge><p>{formatNumber(status.latest_run.population_count ?? 0)} entries in the latest population.</p><Disclosure summary="Run configuration"><TechnicalDetails value={status.latest_run.configuration} /></Disclosure></> : <p className="muted-copy">Your first run will appear here with its complete provenance.</p>}<Button variant="secondary" size="sm" onClick={() => navigate("risk", { run: status.latest_run.id })} disabled={!status.latest_run.id}>Open review queue →</Button></Panel></aside></div>}</div>;
}
