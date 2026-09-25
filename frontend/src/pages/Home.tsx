import { useEffect, useState, type FormEvent } from "react";

import { post } from "../lib/api";
import { navigate } from "../lib/navigation";
import type { StatusSummary } from "../lib/types";
import { Button, Message, Panel, StatusBadge } from "../components/ui";

interface DemoResponse { run_id: number; accepted: number; exceptions: number; }

export default function Home({ status, refresh }: { status: StatusSummary; refresh: () => Promise<void> }) {
  const [demoBusy, setDemoBusy] = useState(false);
  const [demoMessage, setDemoMessage] = useState("");
  const [error, setError] = useState("");
  const [setupError, setSetupError] = useState("");
  const [client, setClient] = useState("");
  const [period, setPeriod] = useState("2025-04-01:2026-03-31");
  const [owner, setOwner] = useState("manager");
  const [saving, setSaving] = useState(false);
  const [recent, setRecent] = useState<Array<{ client: string; period: string }>>([]);

  useEffect(() => {
    try { setRecent(JSON.parse(localStorage.getItem("audit-analytics-recent") ?? "[]") as Array<{ client: string; period: string }>); } catch { setRecent([]); }
  }, []);

  const hasEngagement = Boolean(status.engagement && Object.keys(status.engagement).length > 0);

  async function runDemo() {
    setDemoBusy(true); setError(""); setDemoMessage("Preparing the synthetic local engagement…");
    try {
      const result = await post<DemoResponse>("/demo/seed");
      setDemoMessage(`Synthetic engagement ready · ${result.accepted} entries · ${result.exceptions} risk cues.`);
      await refresh();
      navigate("risk", { run: result.run_id });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "The synthetic demo could not be prepared.");
      setDemoMessage("");
    } finally { setDemoBusy(false); }
  }

  async function createEngagement(event: FormEvent) {
    event.preventDefault(); setSaving(true); setSetupError("");
    try {
      await post("/engagement", { client, period, owner });
      remember(client, period);
      await refresh();
      navigate("population");
    } catch (cause) { setSetupError(cause instanceof Error ? cause.message : "The engagement could not be created."); }
    finally { setSaving(false); }
  }

  function remember(client: string, period: string) {
    const next = [{ client, period }, ...recent.filter((item) => item.client !== client)].slice(0, 4);
    localStorage.setItem("audit-analytics-recent", JSON.stringify(next));
  }

  return <div className="launch-page">
    <div className="launch-topline"><div className="launch-brand"><div className="brand-mark">AA</div><div><strong>AUDIT ANALYTICS</strong><span>Professional journal-entry workbench</span></div></div><StatusBadge tone="success" dot>LOCAL ENGAGEMENT · DATA STAYS ON THIS COMPUTER</StatusBadge></div>
    <section className="launch-hero"><div className="hero-copy"><div className="eyebrow">YOUR AUDIT WORKBENCH</div><h1>Analyze. Investigate. Document.</h1><p>Bring the client ledger into a calm, evidence-led workspace. See what deserves attention, understand why it surfaced, and record the workpaper trail.</p><div className="hero-actions"><Button variant="primary" size="lg" onClick={() => navigate("engagement")}>New Engagement</Button>{hasEngagement ? <Button size="lg" onClick={() => navigate("engagement")}>Open Engagement</Button> : <Button size="lg" onClick={() => navigate("engagement")} disabled>Open Engagement</Button>}<Button variant="quiet" size="lg" onClick={runDemo} disabled={demoBusy || hasEngagement}>{demoBusy ? "Preparing demo…" : "Run Demo"}</Button></div>{demoMessage && <div className="hero-note"><span className="status-dot" />{demoMessage}</div>}{error && <Message kind="error">{error}</Message>}</div><div className="hero-orbit" aria-hidden="true"><div className="orbit-ring orbit-ring-one" /><div className="orbit-ring orbit-ring-two" /><div className="orbit-core"><span>JE</span><small>REVIEW</small></div><div className="orbit-tag orbit-tag-one">Evidence</div><div className="orbit-tag orbit-tag-two">Population</div><div className="orbit-tag orbit-tag-three">Traceability</div></div></section>
    <section className="home-onboarding"><div className="home-onboarding-copy"><div className="eyebrow">START HERE</div><h2>Start a workspace</h2><p>Set the local workspace context in under a minute. You can begin with the synthetic demo or bring your own ledger next.</p><div className="home-onboarding-note"><span className="status-dot" />No command line required</div></div><form onSubmit={createEngagement}><div className="form-grid"><label className="field"><span className="field-label">Client name</span><input className="input" value={client} onChange={(event) => setClient(event.target.value)} placeholder="e.g. Northstar Industries Ltd" required /></label><label className="field"><span className="field-label">Audit period</span><input className="input" value={period} onChange={(event) => setPeriod(event.target.value)} required pattern="\d{4}-\d{2}-\d{2}:\d{4}-\d{2}-\d{2}" /></label></div><label className="field home-owner-field"><span className="field-label">Local owner</span><input className="input" value={owner} onChange={(event) => setOwner(event.target.value)} required /></label>{setupError && <Message kind="error">{setupError}</Message>}<Button type="submit" variant="primary" disabled={saving}>{saving ? "Creating…" : "Create engagement"}</Button></form></section>
    <section className="launch-grid"><Panel className="launch-card launch-card-wide"><div className="card-kicker">ENGAGEMENT</div><h2>Engagement</h2><p>One guided path from ledger to workpaper. Each stage keeps the next action visible while technical provenance remains one click away.</p><div className="launch-flow"><div><span>01</span><strong>Population</strong><small>Import and reconcile</small></div><div><span>02</span><strong>Analysis</strong><small>Prioritize cues</small></div><div><span>03</span><strong>Investigation</strong><small>Review evidence</small></div><div><span>04</span><strong>Finalize</strong><small>Export package</small></div></div></Panel><Panel className="launch-card"><div className="card-kicker">PRIVACY BY DEFAULT</div><h2>Local-first means visible.</h2><p>The engagement database, source evidence, and optional local model context remain on this computer. No cloud AI is required for core analysis.</p><button className="text-link" onClick={() => navigate("engagement")}>Learn about the workspace <span>→</span></button></Panel><Panel className="launch-card recent-card"><div className="card-kicker">RECENT ENGAGEMENTS</div>{recent.length ? <div className="recent-list">{recent.map((item) => <button key={item.client} onClick={() => navigate("engagement")}><strong>{item.client}</strong><span>{item.period}</span></button>)}</div> : <div className="recent-empty"><span className="recent-empty-icon">⌁</span><p>Your local engagement history will appear here.</p></div>}<button className="text-link" onClick={() => navigate("engagement")}>Open workspace <span>→</span></button></Panel></section>
    <div className="launch-footnote"><span>Risk cues support auditor judgement.</span><span>They are not findings, fraud determinations, or audit conclusions.</span></div>
  </div>;
}
