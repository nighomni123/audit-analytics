import { useEffect, useState, type FormEvent } from "react";

import { get, post } from "../lib/api";
import { navigate } from "../lib/navigation";
import type { EngagementState } from "../lib/types";
import { Button, Field, Message, Panel, TextInput, formatDate } from "../components/ui";

const setupSteps = ["Local workspace", "Client ledger", "Population", "Analysis", "Review", "Final package"];

export default function Engagement({ refresh, onRemember }: { refresh: () => Promise<void>; onRemember?: (client: string, period: string) => void }) {
  const [state, setState] = useState<EngagementState | null>(null);
  const [client, setClient] = useState("");
  const [period, setPeriod] = useState("2025-04-01:2026-03-31");
  const [owner, setOwner] = useState("manager");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setState(null); setError("");
    get<EngagementState>("/engagement").then(setState).catch((cause: Error) => setError(cause.message));
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault(); setSaving(true); setError("");
    try {
      await post("/engagement", { client, period, owner });
      onRemember?.(client, period);
      await refresh();
      navigate("population");
    } catch (cause) { setError(cause instanceof Error ? cause.message : "The engagement could not be created."); }
    finally { setSaving(false); }
  }

  if (!state && !error) return <div className="loading-page"><div className="spinner" />Opening engagement setup…</div>;
  const engagement = state?.engagement;
  return <div className="setup-page"><div className="setup-header"><div><div className="eyebrow">ENGAGEMENT SETUP</div><h1>Start a local audit workspace</h1><p>Give the engagement a clear home. The ledger and evidence will be preserved beside this local database.</p></div><div className="setup-local-note"><span className="status-dot" />Local workspace</div></div><div className="setup-layout"><aside className="setup-progress"><div className="eyebrow">YOUR PATH</div><h2>Engagement setup</h2><ol>{setupSteps.map((step, index) => <li className={index === 0 ? "is-current" : ""} key={step}><span>{index === 0 ? "●" : "○"}</span>{step}</li>)}</ol><div className="setup-progress-note">You can return to any stage. Governance controls remain active throughout.</div></aside><Panel className="setup-form-card">{error && <Message kind="error">{error}</Message>}{engagement ? <div className="existing-engagement"><div className="eyebrow">CURRENT ENGAGEMENT</div><h2>{engagement.client}</h2><p>{formatDate(engagement.period_start)} — {formatDate(engagement.period_end)}</p><div className="existing-engagement-meta"><span>Local folder</span><strong>{state?.folder ?? "Local workspace"}</strong></div><Button variant="primary" onClick={() => navigate("population")}>Continue to population</Button></div> : <form className="setup-form" onSubmit={submit}><div className="form-intro"><span className="step-number">01</span><div><h2>Tell us about the engagement</h2><p>Use plain audit language. You can change the local workflow users later.</p></div></div><Field label="Client name" hint="The client or entity whose ledger you are reviewing."><TextInput value={client} onChange={(event) => setClient(event.target.value)} placeholder="e.g. Northstar Industries Ltd" required maxLength={200} autoFocus /></Field><Field label="Audit period" hint="Format: YYYY-MM-DD:YYYY-MM-DD"><TextInput value={period} onChange={(event) => setPeriod(event.target.value)} placeholder="2025-04-01:2026-03-31" required pattern="\d{4}-\d{2}-\d{2}:\d{4}-\d{2}-\d{2}" /></Field><Field label="Engagement owner" hint="This creates a local manager workflow user."><TextInput value={owner} onChange={(event) => setOwner(event.target.value)} placeholder="manager" required maxLength={100} /></Field><div className="setup-form-footer"><Button type="submit" variant="primary" size="lg" disabled={saving}>{saving ? "Creating workspace…" : "Create engagement"}</Button><span>Your data stays on this computer.</span></div></form>}</Panel></div></div>;
}
