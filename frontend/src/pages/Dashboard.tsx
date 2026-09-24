import { useEffect, useMemo, useState, type FormEvent } from "react";

import { download, get } from "../lib/api";
import { navigate } from "../lib/navigation";
import type { Disposition, ExceptionQueue, ModelRun, Severity, StatusSummary, User } from "../lib/types";
import { Card, Loading, Message, PageHeader, formatDate, formatMoney } from "../components/ui";

export default function Dashboard({
  status,
  users,
  routeParams,
  revision,
}: {
  status: StatusSummary;
  users: User[];
  routeParams: URLSearchParams;
  revision: number;
}) {
  const latestRun = status.latest_run.id ?? null;
  const [runs, setRuns] = useState<ModelRun[]>([]);
  const [run, setRun] = useState(routeParams.get("run") ?? (latestRun ? String(latestRun) : ""));
  const [severity, setSeverity] = useState(routeParams.get("severity") ?? "");
  const [statusFilter, setStatusFilter] = useState(routeParams.get("status") ?? "");
  const [search, setSearch] = useState(routeParams.get("search") ?? "");
  const [page, setPage] = useState(Number(routeParams.get("page") ?? "0"));
  const [queue, setQueue] = useState<ExceptionQueue | null>(null);
  const [error, setError] = useState("");
  const [exporting, setExporting] = useState(false);
  const [notice, setNotice] = useState("");
  const limit = 25;
  const exportUsers = useMemo(() => users.filter((user) => ["preparer", "reviewer", "manager", "partner", "quality_reviewer"].includes(user.role)), [users]);
  const [exportActor, setExportActor] = useState("");

  useEffect(() => {
    get<{ rows: ModelRun[] }>("/analysis-runs?limit=100").then((result) => {
      setRuns(result.rows);
      if (!run && result.rows[0]) setRun(String(result.rows[0].id));
    }).catch((cause: Error) => setError(cause.message));
  }, [revision]);

  useEffect(() => {
    setExportActor((current) => current || exportUsers[0]?.username || "");
  }, [exportUsers]);

  useEffect(() => {
    setQueue(null);
    setError("");
    const query = new URLSearchParams({ limit: String(limit), offset: String(page * limit) });
    if (run) query.set("run", run);
    if (severity) query.set("severity", severity);
    if (statusFilter) query.set("status", statusFilter);
    if (search.trim()) query.set("search", search.trim());
    get<ExceptionQueue>(`/exceptions?${query}`)
      .then((result) => {
        setQueue(result);
        navigate("dashboard", { run, severity, status: statusFilter, search, page });
      })
      .catch((cause: Error) => setError(cause.message));
  }, [run, severity, statusFilter, search, page, revision]);

  function applyFilters(event: FormEvent) {
    event.preventDefault();
    setPage(0);
  }

  async function exportWorkpaper() {
    setExporting(true);
    setError("");
    setNotice("");
    try {
      await download("exports/package", { actor: exportActor }, "audit-analytics-workpaper.zip");
      setNotice("Workpaper package downloaded.");
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setExporting(false);
    }
  }

  const totalPages = queue ? Math.max(1, Math.ceil(queue.total / limit)) : 1;

  return (
    <section className="space-y-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
      <PageHeader
        title="Risk Dashboard"
        description="Review ranked, explainable risk cues. A score prioritizes work; it is not a fraud, audit finding, or audit conclusion."
        action={
          <div className="flex flex-wrap items-end gap-2">
            <label className="grid gap-1 text-xs font-medium">Export user<select className="rounded-lg border border-slate-300 px-2 py-1.5 text-sm" value={exportActor} onChange={(event) => setExportActor(event.target.value)}>{exportUsers.map((user) => <option key={user.username} value={user.username}>{user.username}</option>)}</select></label>
            <button onClick={exportWorkpaper} disabled={!exportActor || exporting} className="rounded-lg bg-slate-900 px-3 py-2 text-sm font-semibold text-white disabled:opacity-50">{exporting ? "Packaging…" : "Export package"}</button>
          </div>
        }
      />
      {error && <Message kind="error">{error}</Message>}
      {notice && <Message kind="success">{notice}</Message>}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card label="Accepted population" value={status.entries} />
        <Card label="Risk cues" value={queue?.total ?? "—"} />
        <Card label="High severity" value={queue?.rows.filter((row) => row.severity === "high").length ?? "—"} />
        <Card label="Review set" value={status.review_set.locked ? "Locked" : "Open"} />
      </div>

      <form onSubmit={applyFilters} className="grid gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 md:grid-cols-5">
        <label className="grid gap-1 text-xs font-medium">Analysis run<select className="rounded-lg border border-slate-300 px-2 py-2 text-sm" value={run} onChange={(event) => { setRun(event.target.value); setPage(0); }}><option value="">All runs</option>{runs.map((item) => <option key={item.id} value={item.id}>Run {item.id} · {item.status} · {item.population_count} rows</option>)}</select></label>
        <label className="grid gap-1 text-xs font-medium">Severity<select className="rounded-lg border border-slate-300 px-2 py-2 text-sm" value={severity} onChange={(event) => { setSeverity(event.target.value); setPage(0); }}><option value="">All</option><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option></select></label>
        <label className="grid gap-1 text-xs font-medium">Disposition<select className="rounded-lg border border-slate-300 px-2 py-2 text-sm" value={statusFilter} onChange={(event) => { setStatusFilter(event.target.value); setPage(0); }}><option value="">All</option><option value="open">Open</option><option value="cleared">Cleared</option><option value="follow_up">Follow up</option><option value="selected_for_testing">Selected for testing</option></select></label>
        <label className="grid gap-1 text-xs font-medium">Search<input className="rounded-lg border border-slate-300 px-2 py-2 text-sm" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Entry, narration, reference" /></label>
        <button className="self-end rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-semibold">Apply filters</button>
      </form>

      {!queue ? <Loading label="Loading risk cues…" /> : queue.rows.length === 0 ? (
        <Message kind="info">No risk cues match these filters.</Message>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="bg-slate-100 text-xs uppercase tracking-wide text-slate-600">
              <tr><th className="px-3 py-3">Entry / date</th><th className="px-3 py-3">Amount</th><th className="px-3 py-3">Risk</th><th className="px-3 py-3">Reasons</th><th className="px-3 py-3">Disposition</th><th className="px-3 py-3">Action</th></tr>
            </thead>
            <tbody>
              {queue.rows.map((row) => (
                <tr key={row.id} className="border-t border-slate-200 hover:bg-amber-50/50">
                  <td className="px-3 py-3"><strong>{row.entry_id}</strong><div className="text-xs text-slate-500">{formatDate(row.posting_date)} · {row.account_code}</div></td>
                  <td className="px-3 py-3 font-medium">{formatMoney(row.signed_amount)}</td>
                  <td className="px-3 py-3"><span className={`rounded-full px-2 py-1 text-xs font-bold ${row.severity === "high" ? "bg-red-100 text-red-800" : row.severity === "medium" ? "bg-amber-100 text-amber-900" : "bg-slate-100 text-slate-700"}`}>{row.severity} · {row.risk_score}</span></td>
                  <td className="max-w-sm px-3 py-3 text-slate-700">{row.reasons.join(", ") || "No deterministic cue"}</td>
                  <td className="px-3 py-3">{row.status.replaceAll("_", " ")}</td>
                  <td className="px-3 py-3"><button className="rounded-lg border border-slate-300 px-3 py-1.5 font-semibold hover:bg-slate-100" onClick={() => navigate("investigation", { exception: row.id, run: row.run_id })}>Investigate {row.entry_id}</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="flex items-center justify-between text-sm">
        <span>Page {page + 1} of {totalPages}</span>
        <div className="flex gap-2"><button disabled={page === 0} onClick={() => setPage((value) => Math.max(0, value - 1))} className="rounded-lg border border-slate-300 px-3 py-1.5 disabled:opacity-40">Previous</button><button disabled={!queue || page + 1 >= totalPages} onClick={() => setPage((value) => value + 1)} className="rounded-lg border border-slate-300 px-3 py-1.5 disabled:opacity-40">Next</button></div>
      </div>
    </section>
  );
}
