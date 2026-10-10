import { useEffect, useMemo, useState, type FormEvent } from "react";

import { get, post, put } from "../lib/api";
import { navigate } from "../lib/navigation";
import type { StatusSummary, User } from "../lib/types";
import { Button, Checkbox, Disclosure, Field, Message, Panel, Select, StatusBadge, TextInput } from "../components/ui";

interface SemanticProfileResponse { available_runs?: Array<{ id: number; status: string; started_at: number }>; }
interface SemanticProviderResponse {
  configured: boolean; provider: string; enabled: boolean; base_url: string; model: string;
  referer: string; title: string; has_api_key: boolean; api_key_hint: string; key_source: string;
  acknowledged_by?: string | null; acknowledged_at?: number | null;
}
interface ProviderTestResult { ok: boolean; dimensions: number; latency_ms: number; model: string; }

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
  const [provider, setProvider] = useState<SemanticProviderResponse | null>(null);
  const [baseUrl, setBaseUrl] = useState("https://openrouter.ai/api/v1");
  const [apiKey, setApiKey] = useState("");
  const [providerModel, setProviderModel] = useState("");
  const [referer, setReferer] = useState("");
  const [title, setTitle] = useState("");
  const [remoteEnabled, setRemoteEnabled] = useState(false);
  const [acknowledge, setAcknowledge] = useState(false);
  const [providerBusy, setProviderBusy] = useState(false);
  const [providerError, setProviderError] = useState("");
  const [providerSuccess, setProviderSuccess] = useState("");
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<ProviderTestResult | null>(null);
  const [testError, setTestError] = useState("");

  useEffect(() => { setActor((current) => current || managers[0]?.username || ""); }, [managers]);
  useEffect(() => {
    const policy = status.settings.analysis_policy ?? {};
    const materiality = status.settings.materiality ?? {};
    setOverall(materiality.overall?.toString() ?? ""); setPerformance(materiality.performance?.toString() ?? "");
    setPeriodDays((policy.period_end_days ?? 3).toString()); setRoundAmount((policy.round_amount_threshold ?? 1000).toString()); setRobustZ((policy.outlier_robust_z ?? 3.5).toString());
  }, [revision, status.settings]);
  useEffect(() => { get<SemanticProfileResponse>("/semantic-profile").then((result) => setSemanticRuns(result.available_runs ?? [])).catch(() => setSemanticRuns([])); }, [revision]);
  useEffect(() => {
    get<SemanticProviderResponse>("/semantic-provider").then((result) => {
      setProvider(result); setBaseUrl(result.base_url || "https://openrouter.ai/api/v1");
      setProviderModel(result.model ?? ""); setReferer(result.referer ?? ""); setTitle(result.title ?? "");
      setRemoteEnabled(result.enabled); setApiKey("");
    }).catch(() => setProvider(null));
  }, [revision]);

  async function saveProvider(event: FormEvent) {
    event.preventDefault(); setProviderBusy(true); setProviderError(""); setProviderSuccess("");
    try {
      const saved = await put<SemanticProviderResponse>("/semantic-provider", {
        actor, enabled: remoteEnabled, base_url: baseUrl, api_key: apiKey, model: providerModel,
        referer, title, acknowledge_external_transfer: acknowledge,
      });
      setProvider(saved); setApiKey(""); setAcknowledge(false); setTestResult(null); setTestError("");
      setProviderSuccess(saved.enabled
        ? "External embedding provider enabled. Semantic runs will send ledger text to this endpoint."
        : "Provider settings saved. Semantic analysis stays on the local embedder.");
    } catch (cause) { setProviderError(cause instanceof Error ? cause.message : "The provider settings could not be saved."); }
    finally { setProviderBusy(false); }
  }

  async function testProvider() {
    setTesting(true); setTestResult(null); setTestError("");
    try {
      const result = await post<ProviderTestResult>("/semantic-provider/test", {
        actor, base_url: baseUrl, api_key: apiKey, model: providerModel, referer, title,
      });
      setTestResult(result);
    } catch (cause) { setTestError(cause instanceof Error ? cause.message : "The provider could not be reached."); }
    finally { setTesting(false); }
  }

  async function save(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError(""); setSuccess("");
    try {
      await put("/config", { actor, materiality: overall === "" ? null : Number(overall), performance_materiality: performance === "" ? null : Number(performance), period_end_days: Number(periodDays), round_amount_threshold: roundAmount === "" ? null : Number(roundAmount), outlier_robust_z: robustZ === "" ? null : Number(robustZ) });
      await refresh(); setSuccess("Engagement parameters were saved. The next analysis run will capture this methodology.");
    } catch (cause) { setError(cause instanceof Error ? cause.message : "The audit setup could not be saved."); }
    finally { setBusy(false); }
  }

  return <div className="methodology-page"><div className="page-header"><div className="page-heading-copy"><div className="eyebrow">STEP 03 · AUDIT CONTEXT</div><h1>Audit setup</h1><p>Record the planning context that helps the team decide where to focus. Keep advanced parameters available without putting them in the main path.</p></div><div className="page-header-action"><StatusBadge tone={status.population_acknowledged ? "success" : "warning"} dot>{status.population_acknowledged ? "Ready for analysis" : "Population acknowledgement required"}</StatusBadge></div></div>{error && <Message kind="error">{error}</Message>}{success && <Message kind="success">{success}</Message>}<div className="methodology-layout"><form onSubmit={save}><Panel className="setup-basics"><div className="section-heading"><div><div className="eyebrow">PLANNING CONTEXT</div><h2>Materiality and review thresholds</h2><p className="section-description">These amounts are disclosed planning context. They help label and sample the population; they do not directly modify analytical risk scores.</p></div><span className="step-chip">03</span></div><div className="form-grid"><Field label="Overall materiality" hint="Planning threshold for the engagement."><TextInput type="number" min="0" step="0.01" value={overall} onChange={(event) => setOverall(event.target.value)} placeholder="e.g. 500000" /></Field><Field label="Performance materiality" hint="Must not exceed overall materiality."><TextInput type="number" min="0" step="0.01" value={performance} onChange={(event) => setPerformance(event.target.value)} placeholder="e.g. 350000" /></Field><Field label="Period-end window (days)" hint="Highlights postings near the engagement period end."><TextInput type="number" min="0" max="366" value={periodDays} onChange={(event) => setPeriodDays(event.target.value)} /></Field><Field label="Large amount threshold" hint="Used by the round-amount review signal."><TextInput type="number" min="0" step="0.01" value={roundAmount} onChange={(event) => setRoundAmount(event.target.value)} /></Field></div><div className="helper-strip"><span>i</span><p><strong>Materiality is context, not a conclusion.</strong> The workpaper records the thresholds used so reviewers can understand the sampling and review decisions.</p></div></Panel><Panel className="advanced-panel"><Disclosure summary="Advanced methodology" defaultOpen={false}><div className="advanced-content"><div className="form-grid"><Field label="Peer outlier robust z" hint="Technical threshold for account-peer context."><TextInput type="number" min="0.1" step="0.1" value={robustZ} onChange={(event) => setRobustZ(event.target.value)} /></Field><Field label="Configuration owner"><Select value={actor} onChange={(event) => setActor(event.target.value)}><option value="">Choose manager</option>{managers.map((user) => <option key={user.username} value={user.username}>{user.username} · {user.role}</option>)}</Select></Field></div><Checkbox label="Enable experimental isolation-style ranking for the next run" checked={includeIsolation} onChange={(event) => setIncludeIsolation(event.target.checked)} /><p className="muted-copy">This is an optional ranking aid. It is recorded in the analysis configuration and can be disabled by the engagement team.</p></div></Disclosure></Panel><div className="methodology-actions"><Button type="submit" variant="primary" size="lg" disabled={busy || !actor}>{busy ? "Saving audit setup…" : "Save audit setup"}</Button><Button type="button" variant="secondary" onClick={() => navigate("analysis")}>Continue to analysis <span>→</span></Button></div></form><aside className="methodology-side"><Panel className="semantic-setup-card"><div className="section-heading"><div><div className="eyebrow">OPTIONAL SEMANTIC ANALYSIS</div><h2>Semantic context</h2></div><StatusBadge tone="warning">Experimental</StatusBadge></div><p>Use a completed local semantic profile to add narrative and peer context to the next run. The deterministic review path remains active.</p><Checkbox label="Include available semantic context" checked={semanticEnabled} onChange={(event) => setSemanticEnabled(event.target.checked)} disabled={!semanticRuns.length} /><Field label="Semantic profile run"><Select value={semanticRun} onChange={(event) => setSemanticRun(event.target.value)} disabled={!semanticEnabled || !semanticRuns.length}><option value="">{semanticRuns.length ? "Choose completed profile" : "No completed local profile"}</option>{semanticRuns.filter((run) => run.status === "complete").map((run) => <option key={run.id} value={run.id}>Run {run.id} · completed</option>)}</Select></Field>{!semanticRuns.length && <div className="semantic-unavailable"><strong>No completed semantic profile found.</strong><span>The core analysis remains available without one. Build a local profile through the approved technical workflow when needed.</span></div>}<div className="semantic-boundary"><strong>Boundary</strong><span>Semantic context augments review and never suppresses lexical or deterministic evidence.</span></div></Panel><Panel className="setup-basics"><div className="section-heading"><div><div className="eyebrow">OPTIONAL</div><h2>External embedding provider</h2><p className="section-description">By default embeddings run on this machine through local Ollama. Point this at any OpenAI-compatible <code>/embeddings</code> endpoint &mdash; OpenRouter, OpenAI, or a local vLLM server &mdash; when you need a different model.</p></div></div>{providerError && <Message kind="error">{providerError}</Message>}{providerSuccess && <Message kind="success">{providerSuccess}</Message>}<form onSubmit={saveProvider}><div className="form-grid one"><Field label="Base URL" hint="Must include the API path, e.g. https://openrouter.ai/api/v1"><TextInput value={baseUrl} onChange={(event) => setBaseUrl(event.target.value)} placeholder="https://openrouter.ai/api/v1" disabled={!actor} /></Field><Field label="Model" hint="The exact embedding model id your key can reach."><TextInput value={providerModel} onChange={(event) => setProviderModel(event.target.value)} placeholder="liquid/lfm-2.5-embedding-350m:free" disabled={!actor} /></Field><Field label="API key" hint={provider?.has_api_key ? `Stored in the engagement .env (${provider.api_key_hint}). Leave blank to keep it.` : "Saved to a .env file next to the engagement database, never into the database itself and never returned to the browser."}><TextInput type="password" autoComplete="off" value={apiKey} onChange={(event) => setApiKey(event.target.value)} placeholder={provider?.has_api_key ? "••••••••" : "sk-…"} disabled={!actor} /></Field><Field label="HTTP-Referer" hint="Optional. OpenRouter uses this for public app rankings."><TextInput value={referer} onChange={(event) => setReferer(event.target.value)} placeholder="https://your-firm.example" disabled={!actor} /></Field><Field label="X-OpenRouter-Title" hint="Optional. Application name shown in OpenRouter."><TextInput value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Audit Analytics" disabled={!actor} /></Field></div><div className="semantic-boundary"><Checkbox label="Send ledger text to this external provider" checked={remoteEnabled} onChange={(event) => setRemoteEnabled(event.target.checked)} disabled={!actor} /><span>When enabled, the transaction text needed for similarity is transmitted to the endpoint above and stored there under your provider account.</span></div>{remoteEnabled && <div className="semantic-unavailable"><strong>This moves engagement data off this machine.</strong><span>Confirm the engagement owner and your firm's confidentiality policy permit it. Remote providers publish no model digest, so a silent upstream model change cannot be detected the way a local model digest can.</span><Checkbox label="I confirm ledger text may leave this host" checked={acknowledge} onChange={(event) => setAcknowledge(event.target.checked)} disabled={!actor} /></div>}<div className="provider-actions"><Button type="submit" variant="primary" disabled={providerBusy || !actor}>{providerBusy ? "Saving…" : "Save provider settings"}</Button><Button type="button" variant="secondary" onClick={testProvider} disabled={testing || providerBusy || !actor}>{testing ? "Testing…" : "Test connection"}</Button></div></form>{testResult && <Message kind="success">Connected to {testResult.model} · {testResult.dimensions} dimensions · {testResult.latency_ms} ms</Message>}{testError && <Message kind="error">Connection failed: {testError}</Message>}</Panel><Panel className="methodology-checklist"><div className="eyebrow">BEFORE ANALYSIS</div><h2>Quick check</h2><ul><li className={status.population_acknowledged ? "is-done" : ""}><span>{status.population_acknowledged ? "✓" : "○"}</span>Population acknowledged</li><li className={Boolean(overall || performance) ? "is-done" : ""}><span>{overall || performance ? "✓" : "○"}</span>Planning context recorded</li><li className={status.latest_run.id ? "is-done" : ""}><span>{status.latest_run.id ? "✓" : "○"}</span>Analysis run versioned</li></ul><Button variant="secondary" size="sm" onClick={() => navigate(status.population_acknowledged ? "analysis" : "population")}>{status.population_acknowledged ? "Open analysis" : "Return to population"} →</Button></Panel></aside></div></div>;
}
