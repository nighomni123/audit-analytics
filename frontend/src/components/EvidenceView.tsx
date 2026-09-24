import type { ExceptionDetail, SemanticInvestigation } from "../lib/types";

function EntrySummary({ value }: { value: Record<string, unknown> }) {
  return (
    <div className="rounded-lg bg-slate-50 p-2 text-sm">
      <strong>{String(value.entry_id ?? value.ledger_id ?? "—")}</strong>
      <div className="text-slate-600">{String(value.posting_date ?? "")} · {String(value.account_code ?? "")}</div>
      <div className="line-clamp-2 text-slate-700">{String(value.description ?? "")}</div>
    </div>
  );
}

export function SemanticEvidence({ investigation }: { investigation: SemanticInvestigation }) {
  return (
    <div className="space-y-4">
      {investigation.stale && <div className="rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm text-amber-950">Historical snapshot: the current population changed. Rebuild semantic evidence before new analysis.</div>}
      <div><h4 className="font-semibold">Why semantic analysis flagged it</h4><p className="text-sm text-slate-700">{investigation.cues.join(", ") || "No semantic cue; this is not assurance of correctness."}</p></div>
      <div className="grid gap-3 md:grid-cols-2">
        <div><h4 className="font-semibold">Normal peers</h4><div className="mt-2 grid gap-2">{investigation.evidence.normal_peers.map((item) => <EntrySummary key={item.ledger_id} value={item.entry} />)}</div></div>
        <div><h4 className="font-semibold">Alternative matches</h4><div className="mt-2 grid gap-2">{investigation.evidence.alternative_matches.map((item) => <EntrySummary key={item.ledger_id} value={item.entry} />)}</div></div>
      </div>
      <details className="rounded-lg border border-slate-200 p-3"><summary className="cursor-pointer font-semibold">Metrics, comparison basis and provenance</summary><pre className="mt-3 max-h-96 overflow-auto whitespace-pre-wrap break-words text-xs">{JSON.stringify({ metrics: investigation.metrics, comparisons: investigation.evidence.comparisons, provenance: investigation.provenance }, null, 2)}</pre></details>
      <div><h4 className="font-semibold">Suggested evidence</h4><ul className="list-disc pl-5 text-sm text-slate-700">{investigation.evidence.suggested_evidence.map((item) => <li key={item}>{item}</li>)}</ul></div>
      <p className="text-xs text-amber-900">{investigation.evidence.limitations.join(" ")}</p>
    </div>
  );
}

export function DeterministicEvidence({ detail }: { detail: ExceptionDetail }) {
  return (
    <div className="space-y-3">
      <div><h4 className="font-semibold">Recorded reasons</h4><p className="text-sm text-slate-700">{detail.reasons.join(", ") || "No deterministic cue."}</p></div>
      <details className="rounded-lg border border-slate-200 p-3" open><summary className="cursor-pointer font-semibold">Structured evidence</summary><pre className="mt-3 max-h-80 overflow-auto whitespace-pre-wrap break-words text-xs">{JSON.stringify(detail.evidence, null, 2)}</pre></details>
      <details className="rounded-lg border border-slate-200 p-3"><summary className="cursor-pointer font-semibold">Original source row</summary><pre className="mt-3 max-h-64 overflow-auto whitespace-pre-wrap break-words text-xs">{JSON.stringify(detail.source_record, null, 2)}</pre></details>
    </div>
  );
}
