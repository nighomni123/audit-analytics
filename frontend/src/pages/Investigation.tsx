import { useEffect, useMemo, useState, type FormEvent } from "react";

import { get, post } from "../lib/api";
import { navigate } from "../lib/navigation";
import type { ExceptionDetail, SemanticInvestigation, SimilarResult, StatusSummary, User } from "../lib/types";
import { DeterministicEvidence, SemanticEvidence } from "../components/EvidenceView";
import ReviewForm from "../components/ReviewForm";
import { Card, Loading, Message, PageHeader, formatDate, formatMoney } from "../components/ui";

function semanticRunId(detail: ExceptionDetail | null): number | null {
  const semantic = detail?.evidence.semantic;
  if (!semantic || typeof semantic !== "object" || !("run_id" in semantic)) return null;
  const value = semantic.run_id;
  return typeof value === "number" ? value : null;
}

export default function Investigation({
  exceptionId,
  status,
  users,
  refresh,
  revision,
}: {
  exceptionId: number | null;
  status: StatusSummary;
  users: User[];
  refresh: () => Promise<void>;
  revision: number;
}) {
  const [detail, setDetail] = useState<ExceptionDetail | null>(null);
  const [semantic, setSemantic] = useState<SemanticInvestigation | null>(null);
  const [query, setQuery] = useState("");
  const [similar, setSimilar] = useState<SimilarResult[]>([]);
  const [loading, setLoading] = useState(Boolean(exceptionId));
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [reload, setReload] = useState(0);
  const [lockReason, setLockReason] = useState("");
  const managers = useMemo(() => users.filter((user) => ["manager", "partner"].includes(user.role)), [users]);
  const [manager, setManager] = useState("");

  useEffect(() => {
    setManager((current) => current || managers[0]?.username || "");
  }, [managers]);

  useEffect(() => {
    if (!exceptionId) {
      setDetail(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError("");
    get<ExceptionDetail>(`/exceptions/${exceptionId}`)
      .then((result) => {
        setDetail(result);
        const run = semanticRunId(result);
        if (run) return get<SemanticInvestigation>(`/semantic-investigation?run=${run}&ledger_id=${result.ledger_id}`).then(setSemantic);
        setSemantic(null);
        return undefined;
      })
      .catch((cause: Error) => setError(cause.message))
      .finally(() => setLoading(false));
  }, [exceptionId, reload, revision]);

  async function reloadDetail() {
    setReload((value) => value + 1);
    await refresh();
  }

  async function search(event: FormEvent) {
    event.preventDefault();
    if (!query.trim()) return;
    setError("");
    try {
      const result = await get<{ results: SimilarResult[] }>(`/similar?q=${encodeURIComponent(query.trim())}&limit=10`);
      setSimilar(result.results);
    } catch (cause) {
      setError((cause as Error).message);
    }
  }

  async function changeLock(event: "locked" | "reopened") {
    setError("");
    setNotice("");
    try {
      await post(`/review-set/${event === "locked" ? "lock" : "reopen"}`, { actor: manager, reason: lockReason });
      setLockReason("");
      await refresh();
      setNotice(event === "locked" ? "Review set locked." : "Review set reopened.");
    } catch (cause) {
      setError((cause as Error).message);
    }
  }

  if (!exceptionId) {
    return (
      <section className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <PageHeader title="Investigation & Review" description="Select a risk cue from the dashboard to inspect its persisted ledger, evidence, semantic context, and review history." />
        <button className="rounded-lg bg-slate-900 px-4 py-2 font-semibold text-white" onClick={() => navigate("dashboard")}>Open dashboard</button>
      </section>
    );
  }

  return (
    <section className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <PageHeader
          title="Investigation & Review"
          description="The workspace is bound to the selected exception. All transaction identity, evidence, and review state comes from the engagement database."
          action={<button className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-semibold" onClick={() => navigate("dashboard", { run: detail?.run_id })}>Back to dashboard</button>}
        />
        {error && <div className="mb-5"><Message kind="error">{error}</Message></div>}
        {notice && <div className="mb-5"><Message kind="success">{notice}</Message></div>}
        {loading || !detail ? <Loading label="Loading selected exception…" /> : (
          <>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <Card label="Entry" value={detail.entry_id} />
              <Card label="Posting date" value={formatDate(detail.posting_date)} />
              <Card label="Signed amount" value={formatMoney(detail.signed_amount)} />
              <Card label="Current status" value={detail.status.replaceAll("_", " ")} />
            </div>
            <div className="mt-5 grid gap-5 xl:grid-cols-2">
              <div className="rounded-xl border border-slate-200 p-5">
                <h3 className="text-lg font-bold">Transaction context</h3>
                <dl className="mt-3 grid grid-cols-[9rem_1fr] gap-y-2 text-sm">
                  <dt className="font-medium text-slate-500">Account</dt><dd>{detail.account_code} {detail.account_name ?? ""}</dd>
                  <dt className="font-medium text-slate-500">Narration</dt><dd>{detail.description || "—"}</dd>
                  <dt className="font-medium text-slate-500">Preparer</dt><dd>{detail.preparer || "—"}</dd>
                  <dt className="font-medium text-slate-500">Reference</dt><dd>{detail.reference || "—"}</dd>
                  <dt className="font-medium text-slate-500">Source lineage</dt><dd>Import {detail.import_id} · row {detail.source_row} · SHA-256 {detail.source_hash.slice(0, 16)}…</dd>
                </dl>
              </div>
              <div className="rounded-xl border border-slate-200 p-5">
                <DeterministicEvidence detail={detail} />
              </div>
            </div>
          </>
        )}
      </div>

      {semantic && <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"><h3 className="mb-4 text-lg font-bold">Experimental semantic evidence</h3><SemanticEvidence investigation={semantic} /></div>}

      <div className="grid gap-6 xl:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          {detail ? <ReviewForm detail={detail} users={users} locked={status.review_set.locked} onSaved={reloadDetail} /> : <Loading />}
        </div>
        <div className="space-y-6">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-lg font-bold">Review-set governance</h3>
            <p className="mt-2 text-sm text-slate-600">Current state: <strong>{status.review_set.locked ? "locked" : "open"}</strong>{status.review_set.reason ? ` · ${status.review_set.reason}` : ""}</p>
            <div className="mt-3 grid gap-3 sm:grid-cols-2">
              <label className="grid gap-1 text-sm font-medium">Manager<select className="rounded-lg border border-slate-300 px-3 py-2" value={manager} onChange={(event) => setManager(event.target.value)}>{managers.map((user) => <option key={user.username} value={user.username}>{user.username}</option>)}</select></label>
              <label className="grid gap-1 text-sm font-medium">Reason<input className="rounded-lg border border-slate-300 px-3 py-2" value={lockReason} onChange={(event) => setLockReason(event.target.value)} /></label>
            </div>
            <div className="mt-3 flex gap-2">
              <button disabled={status.review_set.locked || !manager || !lockReason.trim()} onClick={() => changeLock("locked")} className="rounded-lg bg-slate-900 px-3 py-2 text-sm font-semibold text-white disabled:opacity-40">Lock review set</button>
              <button disabled={!status.review_set.locked || !manager || !lockReason.trim()} onClick={() => changeLock("reopened")} className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-semibold disabled:opacity-40">Reopen review set</button>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-lg font-bold">Similar transaction search</h3>
            <form onSubmit={search} className="mt-3 flex gap-2"><input className="min-w-0 flex-1 rounded-lg border border-slate-300 px-3 py-2" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="manual year-end tax provision" /><button className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-semibold">Search</button></form>
            <div className="mt-3 grid gap-2">{similar.map((item) => <div key={item.ledger_id} className="rounded-lg bg-slate-50 p-3 text-left text-sm"><strong>{item.entry_id}</strong> · {formatMoney(item.signed_amount)} · score {item.score}<div className="text-slate-600">{item.description || "—"}</div></div>)}</div>
          </div>
        </div>
      </div>

      {detail && <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"><h3 className="mb-3 text-lg font-bold">Immutable review history</h3>{detail.reviews.length === 0 ? <p className="text-sm text-slate-500">No review has been recorded.</p> : <ol className="space-y-3">{detail.reviews.map((review) => <li key={review.id} className="rounded-lg border border-slate-200 p-3 text-sm"><strong>{review.disposition.replaceAll("_", " ")}</strong> by {review.reviewer}<div>{review.note}</div>{review.second_reviewer && <div className="mt-1 text-indigo-800">Second review: {review.second_reviewer} · {review.second_note}</div>}</li>)}</ol>}</div>}
    </section>
  );
}
