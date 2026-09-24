import { useEffect, useMemo, useState, type FormEvent } from "react";

import { ApiError, post, put, upload } from "../lib/api";
import { navigate } from "../lib/navigation";
import type { PreviewResult, StatusSummary, User } from "../lib/types";
import { Card, Message, PageHeader } from "../components/ui";

const mappingFields = [
  ["entry_id", "Entry identifier"],
  ["posting_date", "Posting date"],
  ["document_date", "Document date"],
  ["account_code", "Account code"],
  ["amount", "Signed amount"],
  ["debit", "Debit"],
  ["credit", "Credit"],
  ["description", "Narration / description"],
  ["preparer", "Preparer / user"],
  ["reference", "Reference"],
  ["vendor", "Vendor / supplier"],
  ["entity", "Entity / cost centre"],
  ["is_manual", "Manual / system flag"],
] as const;

function usersFor(users: User[], roles: string[]): User[] {
  return users.filter((user) => roles.includes(user.role));
}

export default function Population({
  status,
  users,
  refresh,
  revision,
}: {
  status: StatusSummary;
  users: User[];
  refresh: () => Promise<void>;
  revision: number;
}) {
  const importers = useMemo(() => usersFor(users, ["preparer", "reviewer", "manager", "partner"]), [users]);
  const reviewers = useMemo(() => usersFor(users, ["reviewer", "manager", "partner", "quality_reviewer"]), [users]);
  const managers = useMemo(() => usersFor(users, ["manager", "partner"]), [users]);
  const [actor, setActor] = useState("");
  const [reviewer, setReviewer] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<PreviewResult | null>(null);
  const [mapping, setMapping] = useState<Record<string, string>>({});
  const [expectedRows, setExpectedRows] = useState("");
  const [expectedDebits, setExpectedDebits] = useState("");
  const [expectedCredits, setExpectedCredits] = useState("");
  const [reimport, setReimport] = useState(false);
  const [note, setNote] = useState("");
  const [override, setOverride] = useState(false);
  const [overall, setOverall] = useState("");
  const [performance, setPerformance] = useState("");
  const [periodDays, setPeriodDays] = useState("3");
  const [includeIsolation, setIncludeIsolation] = useState(true);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    setActor((current) => current || importers[0]?.username || "");
    setReviewer((current) => current || reviewers[0]?.username || "");
  }, [importers, reviewers]);

  useEffect(() => {
    const policy = status.settings.analysis_policy ?? {};
    const materiality = status.settings.materiality ?? {};
    setOverall(materiality.overall?.toString() ?? "");
    setPerformance(materiality.performance?.toString() ?? "");
    setPeriodDays((policy.period_end_days ?? 3).toString());
  }, [revision, status.settings]);

  if (!status.engagement) {
    return (
      <section className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <PageHeader title="Population & Configuration" description="Create an engagement before importing evidence." />
        <button className="rounded-lg bg-slate-900 px-4 py-2 font-semibold text-white" onClick={() => navigate("engagement")}>Open engagement</button>
      </section>
    );
  }

  function reportError(cause: unknown) {
    setError(cause instanceof Error ? cause.message : String(cause));
    setSuccess("");
  }

  async function runPreview(event: FormEvent) {
    event.preventDefault();
    if (!file) return;
    setBusy("preview");
    setError("");
    setSuccess("");
    const form = new FormData();
    form.append("file", file);
    try {
      const result = await upload<PreviewResult>("/imports/preview", form);
      setPreview(result);
      setMapping(Object.fromEntries(Object.entries(result.mapping).filter((entry): entry is [string, string] => Boolean(entry[1]))));
    } catch (cause) {
      reportError(cause);
    } finally {
      setBusy("");
    }
  }

  async function runImport() {
    if (!file) return;
    setBusy("import");
    setError("");
    setSuccess("");
    const form = new FormData();
    form.append("file", file);
    form.append("actor", actor);
    form.append("reimport", String(reimport));
    if (expectedRows) form.append("expected_rows", expectedRows);
    if (expectedDebits) form.append("expected_debits", expectedDebits);
    if (expectedCredits) form.append("expected_credits", expectedCredits);
    if (Object.keys(mapping).length) form.append("mapping", JSON.stringify(mapping));
    try {
      const result = await upload<{ import_id: number; accepted: number; rejected: number }>("/imports/gl", form);
      setSuccess(`Import ${result.import_id} stored ${result.accepted} accepted and ${result.rejected} rejected rows.`);
      setFile(null);
      setPreview(null);
      setMapping({});
      setReimport(false);
      await refresh();
    } catch (cause) {
      if (cause instanceof ApiError && cause.code === "duplicate_import") {
        setError(`${cause.message}. Tick “Import as a new version” only when that duplicate is intentional.`);
      } else {
        reportError(cause);
      }
    } finally {
      setBusy("");
    }
  }

  async function acknowledge() {
    setBusy("acknowledge");
    setError("");
    setSuccess("");
    try {
      await post("/imports/acknowledge", { reviewer, note, override_reconciliation: override });
      setNote("");
      setOverride(false);
      await refresh();
      setSuccess("Population reconciliation was recorded and analysis is unlocked.");
    } catch (cause) {
      reportError(cause);
    } finally {
      setBusy("");
    }
  }

  async function saveConfiguration(event: FormEvent) {
    event.preventDefault();
    setBusy("configure");
    setError("");
    setSuccess("");
    try {
      await put("/config", {
        actor: managers[0]?.username || "",
        materiality: overall === "" ? null : Number(overall),
        performance_materiality: performance === "" ? null : Number(performance),
        period_end_days: Number(periodDays),
      });
      await refresh();
      setSuccess("Engagement parameters were saved.");
    } catch (cause) {
      reportError(cause);
    } finally {
      setBusy("");
    }
  }

  async function analyze() {
    setBusy("analyze");
    setError("");
    setSuccess("");
    try {
      const result = await post<{ run_id: number }>("/analysis-runs", { actor, include_isolation: includeIsolation });
      await refresh();
      navigate("dashboard", { run: result.run_id });
    } catch (cause) {
      reportError(cause);
    } finally {
      setBusy("");
    }
  }

  const glImports = status.imports.filter((item) => item.kind === "gl");
  const pending = glImports.some((item) => item.acknowledged_at === null);

  return (
    <section className="space-y-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
      <PageHeader
        title="Population & Configuration"
        description="Import the complete client ledger, reconcile source control totals, record the reviewer acknowledgement, persist methodology settings, and start a versioned analysis."
      />
      {error && <Message kind="error">{error}</Message>}
      {success && <Message kind="success">{success}</Message>}

      <div className="grid gap-4 md:grid-cols-4">
        <Card label="Imported entries" value={status.entries} />
        <Card label="Rejected rows" value={status.rejected_rows} />
        <Card label="GL versions" value={glImports.length} />
        <Card label="Acknowledgement" value={status.population_acknowledged ? "Ready" : "Required"} />
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <div className="rounded-xl border border-slate-200 p-5">
          <h3 className="text-lg font-bold">1. Preview and import GL</h3>
          <form className="mt-4 grid gap-3" onSubmit={runPreview}>
            <label className="grid gap-1 text-sm font-medium">
              CSV or bounded XLSX source
              <input id="gl-file" type="file" accept=".csv,.xlsx" className="rounded-lg border border-slate-300 p-2" onChange={(event) => { setFile(event.target.files?.[0] ?? null); setPreview(null); }} />
            </label>
            <label className="grid gap-1 text-sm font-medium">
              Local import user
              <select className="rounded-lg border border-slate-300 px-3 py-2" value={actor} onChange={(event) => setActor(event.target.value)}>
                {importers.map((user) => <option key={user.username} value={user.username}>{user.username} · {user.role}</option>)}
              </select>
            </label>
            <button disabled={!file || Boolean(busy)} className="w-fit rounded-lg border border-slate-300 px-4 py-2 font-semibold disabled:opacity-50">
              {busy === "preview" ? "Reading…" : "Preview source"}
            </button>
          </form>

          {preview && (
            <div className="mt-4 space-y-3">
              <Message kind={preview.missing_required.length ? "warning" : "success"}>
                {preview.missing_required.length
                  ? `Map required fields: ${preview.missing_required.join(", ")}`
                  : `All required concepts detected in ${preview.file}.`}
              </Message>
              <div className="grid gap-2 sm:grid-cols-2">
                {mappingFields.map(([field, label]) => (
                  <label key={field} className="grid gap-1 text-xs font-medium text-slate-600">
                    {label}
                    <select
                      className="rounded-lg border border-slate-300 px-2 py-1.5 text-sm"
                      value={mapping[field] ?? ""}
                      onChange={(event) => setMapping((current) => {
                        const next = { ...current };
                        if (event.target.value) next[field] = event.target.value;
                        else delete next[field];
                        return next;
                      })}
                    >
                      <option value="">Not mapped</option>
                      {preview.headers.map((header) => <option key={header} value={header}>{header}</option>)}
                    </select>
                  </label>
                ))}
              </div>
            </div>
          )}

          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <label className="grid gap-1 text-sm font-medium">Expected rows<input className="rounded-lg border border-slate-300 px-3 py-2" type="number" min="0" value={expectedRows} onChange={(event) => setExpectedRows(event.target.value)} /></label>
            <label className="grid gap-1 text-sm font-medium">Expected debits<input className="rounded-lg border border-slate-300 px-3 py-2" type="number" step="0.01" value={expectedDebits} onChange={(event) => setExpectedDebits(event.target.value)} /></label>
            <label className="grid gap-1 text-sm font-medium">Expected credits<input className="rounded-lg border border-slate-300 px-3 py-2" type="number" step="0.01" value={expectedCredits} onChange={(event) => setExpectedCredits(event.target.value)} /></label>
          </div>
          <label className="mt-3 flex items-center gap-2 text-sm">
            <input type="checkbox" checked={reimport} onChange={(event) => setReimport(event.target.checked)} />
            Import identical bytes as an explicit new version
          </label>
          <button onClick={runImport} disabled={!file || Boolean(busy)} className="mt-4 rounded-lg bg-slate-900 px-4 py-2 font-semibold text-white disabled:opacity-50">
            {busy === "import" ? "Importing…" : "Import ledger"}
          </button>
        </div>

        <div className="rounded-xl border border-slate-200 p-5">
          <h3 className="text-lg font-bold">2. Reconcile and acknowledge</h3>
          <div className="mt-4 max-h-56 space-y-2 overflow-auto">
            {glImports.length === 0 && <p className="text-sm text-slate-500">No GL import is stored.</p>}
            {glImports.map((item) => (
              <div key={item.id} className="rounded-lg bg-slate-50 p-3 text-sm">
                <div className="flex justify-between gap-3"><strong>Import {item.id}</strong><span>{item.acknowledged_at ? "Acknowledged" : "Pending"}</span></div>
                <div className="mt-1 text-slate-600">{item.original_name} · accepted {item.accepted_rows} · rejected {item.rejected_rows}</div>
                <div className="text-slate-600">Expected {item.expected_rows ?? "—"} rows · debits {item.expected_debits ?? "—"} · credits {item.expected_credits ?? "—"}</div>
                <div className={item.reconciliation?.matches ? "text-emerald-700" : "text-amber-700"}>{item.reconciliation?.matches ? "Control totals match" : "Matching totals or documented override required"}</div>
              </div>
            ))}
          </div>
          <div className="mt-4 grid gap-3">
            <label className="grid gap-1 text-sm font-medium">Reviewer<select className="rounded-lg border border-slate-300 px-3 py-2" value={reviewer} onChange={(event) => setReviewer(event.target.value)}>{reviewers.map((user) => <option key={user.username} value={user.username}>{user.username} · {user.role}</option>)}</select></label>
            <label className="grid gap-1 text-sm font-medium">Acknowledgement note<textarea className="rounded-lg border border-slate-300 px-3 py-2" rows={3} value={note} onChange={(event) => setNote(event.target.value)} /></label>
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={override} onChange={(event) => setOverride(event.target.checked)} /> Document an intentional reconciliation difference</label>
            <button onClick={acknowledge} disabled={!pending || !reviewer || !note.trim() || Boolean(busy)} className="w-fit rounded-lg bg-emerald-700 px-4 py-2 font-semibold text-white disabled:opacity-50">{busy === "acknowledge" ? "Recording…" : "Acknowledge population"}</button>
          </div>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <form onSubmit={saveConfiguration} className="rounded-xl border border-slate-200 p-5">
          <h3 className="text-lg font-bold">3. Persist engagement parameters</h3>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <label className="grid gap-1 text-sm font-medium">Overall materiality<input className="rounded-lg border border-slate-300 px-3 py-2" type="number" min="0" step="0.01" value={overall} onChange={(event) => setOverall(event.target.value)} /></label>
            <label className="grid gap-1 text-sm font-medium">Performance materiality<input className="rounded-lg border border-slate-300 px-3 py-2" type="number" min="0" step="0.01" value={performance} onChange={(event) => setPerformance(event.target.value)} /></label>
            <label className="grid gap-1 text-sm font-medium">Period-end window (days)<input className="rounded-lg border border-slate-300 px-3 py-2" type="number" min="0" max="366" value={periodDays} onChange={(event) => setPeriodDays(event.target.value)} /></label>
          </div>
          <button disabled={!managers.length || Boolean(busy)} className="mt-4 rounded-lg border border-slate-300 px-4 py-2 font-semibold disabled:opacity-50">{busy === "configure" ? "Saving…" : "Save parameters"}</button>
        </form>

        <div className="rounded-xl border border-slate-200 p-5">
          <h3 className="text-lg font-bold">4. Run governed analysis</h3>
          <p className="mt-2 text-sm text-slate-600">Analysis is blocked until every GL import is acknowledged. Each run stores its population, policy, provenance, and limitations.</p>
          <label className="mt-4 flex items-center gap-2 text-sm"><input type="checkbox" checked={includeIsolation} onChange={(event) => setIncludeIsolation(event.target.checked)} /> Enable experimental isolation-style ranking</label>
          <button onClick={analyze} disabled={!status.population_acknowledged || !actor || Boolean(busy)} className="mt-4 rounded-lg bg-amber-500 px-4 py-2 font-bold text-slate-950 disabled:opacity-50">{busy === "analyze" ? "Analyzing…" : "Run analysis"}</button>
        </div>
      </div>
    </section>
  );
}
