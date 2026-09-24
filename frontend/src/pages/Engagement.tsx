import { useEffect, useState, type FormEvent } from "react";

import { get, post } from "../lib/api";
import { navigate } from "../lib/navigation";
import type { EngagementState } from "../lib/types";
import { Card, Loading, Message, PageHeader, formatDate } from "../components/ui";

export default function Engagement({
  refresh,
  revision,
}: {
  refresh: () => Promise<void>;
  revision: number;
}) {
  const [state, setState] = useState<EngagementState | null>(null);
  const [client, setClient] = useState("");
  const [period, setPeriod] = useState("2025-04-01:2026-03-31");
  const [owner, setOwner] = useState("manager");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setState(null);
    setError("");
    get<EngagementState>("/engagement").then(setState).catch((cause: Error) => setError(cause.message));
  }, [revision]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      await post("/engagement", { client, period, owner });
      await refresh();
      navigate("population");
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setSaving(false);
    }
  }

  if (!state && !error) return <Loading label="Loading engagement…" />;
  const engagement = state?.engagement;

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
      <PageHeader
        title="Engagement"
        description="The server is bound to one engagement database selected with serve --db. This screen creates or displays that engagement; it never changes databases from the browser."
      />
      {error && <div className="mb-5"><Message kind="error">{error}</Message></div>}
      {engagement ? (
        <>
          <div className="grid gap-4 md:grid-cols-3">
            <Card label="Client" value={engagement.client} />
            <Card label="Audit period" value={`${formatDate(engagement.period_start)} – ${formatDate(engagement.period_end)}`} />
            <Card label="Local folder" value={state?.folder ?? "—"} />
          </div>
          <div className="mt-6 flex flex-wrap gap-3">
            <button className="rounded-lg bg-amber-500 px-4 py-2 font-semibold text-slate-950 hover:bg-amber-400" onClick={() => navigate("population")}>
              Continue to population
            </button>
            <span className="self-center text-sm text-slate-500">Restart with another database using the CLI serve command.</span>
          </div>
        </>
      ) : (
        <form className="grid max-w-2xl gap-4" onSubmit={submit}>
          <Message kind="info">Create the engagement before importing a client ledger.</Message>
          <label className="grid gap-1 text-sm font-medium text-slate-700">
            Client name
            <input className="rounded-lg border border-slate-300 px-3 py-2" value={client} onChange={(event) => setClient(event.target.value)} required maxLength={200} />
          </label>
          <label className="grid gap-1 text-sm font-medium text-slate-700">
            Audit period
            <input className="rounded-lg border border-slate-300 px-3 py-2" value={period} onChange={(event) => setPeriod(event.target.value)} required pattern="\d{4}-\d{2}-\d{2}:\d{4}-\d{2}-\d{2}" />
          </label>
          <label className="grid gap-1 text-sm font-medium text-slate-700">
            Local owner
            <input className="rounded-lg border border-slate-300 px-3 py-2" value={owner} onChange={(event) => setOwner(event.target.value)} required maxLength={100} />
          </label>
          <button disabled={saving} className="w-fit rounded-lg bg-slate-900 px-5 py-2 font-semibold text-white disabled:opacity-50">
            {saving ? "Creating…" : "Create engagement"}
          </button>
        </form>
      )}
    </section>
  );
}
