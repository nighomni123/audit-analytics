import { useEffect, useMemo, useState, type FormEvent } from "react";

import { get, post } from "../lib/api";
import { navigate } from "../lib/navigation";
import type {
  ExceptionDetail,
  InvestigationContext,
  SemanticInvestigation,
  SimilarResult,
  StatusSummary,
  User,
} from "../lib/types";
import { humanizeReason, parseRunConfiguration } from "../lib/workflow";
import { DeterministicEvidence, SemanticEvidence } from "../components/EvidenceView";
import ReviewForm from "../components/ReviewForm";
import {
  Button,
  Disclosure,
  Field,
  Loading,
  Message,
  Panel,
  SeverityBadge,
  StatusBadge,
  TechnicalDetails,
  TextArea,
  TextInput,
  formatDate,
  formatDateTime,
  formatMoney,
  titleCase,
} from "../components/ui";

function semanticRunId(detail: ExceptionDetail | null): number | null {
  const semantic = detail?.evidence?.semantic;
  if (!semantic || typeof semantic !== "object" || !("run_id" in semantic)) return null;
  return typeof semantic.run_id === "number" ? semantic.run_id : null;
}

function reasonText(reason: string): string {
  const descriptions: Record<string, string> = {
    period_end_posting: "Posted within the configured period-end window.",
    fiscal_period_end: "Posted near a configured fiscal period-end date.",
    weekend_posting: "Posted on a weekend relative to the engagement calendar.",
    round_amount: "The amount is a round value at the configured threshold.",
    robust_account_peer_outlier: "The amount is unusual compared with activity for this account.",
    rare_account_preparer_pair: "This account and preparer combination is uncommon in the population.",
    possible_reversal_within_30_days: "A possible opposite-direction entry appears within 30 days.",
    duplicate_or_repeated_entry: "A repeated account, date, amount, or description pattern was detected.",
    isolation_style_anomaly: "An experimental ranking signal placed this entry unusually far from peers.",
    semantic_account_mismatch: "Semantic context differs from the account profile.",
    semantic_vendor_shift: "Semantic context suggests a change in vendor-related activity.",
    semantic_novel_transaction: "The narrative is unlike the available local context.",
    semantic_cluster_outlier: "The entry sits apart from its semantic process cluster.",
    semantic_process_outlier: "The entry is dissimilar across multiple semantic peer dimensions.",
  };
  return descriptions[reason] ?? `${humanizeReason(reason)} was recorded by the governed analysis.`;
}

function entryFileName(detail: ExceptionDetail): string {
  const raw = detail.source_record;
  if (typeof raw === "string") {
    try {
      const obj = JSON.parse(raw);
      const keys = Object.keys(obj || {});
      const pick = keys.find((k) => /file|name/i.test(k));
      if (pick) return String(obj[pick]);
    } catch {
      // fall through to fallback
    }
  }
  return "Preserved GL evidence";
}

function SourceHash({ hash }: { hash: string }) {
  return <code className="hash-inline">{hash.slice(0, 12)}…{hash.slice(-8)}</code>;
}

function TransactionSummary({ detail }: { detail: ExceptionDetail }) {
  const fields: Array<[string, string | number | null | undefined]> = [
    ["Entry ID", detail.entry_id],
    ["Posting date", formatDate(detail.posting_date)],
    ["Document date", detail.document_date ? formatDate(detail.document_date) : "—"],
    ["Account", detail.account_code + (detail.account_name ? ` · ${detail.account_name}` : "")],
    ["Signed amount", formatMoney(detail.signed_amount)],
    ["Debit", formatMoney(detail.debit)],
    ["Credit", formatMoney(detail.credit)],
    ["Narration", detail.description || "—"],
    ["Preparer", detail.preparer || "—"],
    ["Reference", detail.reference || "—"],
    ["Vendor", detail.vendor || "—"],
    ["Entity", detail.entity || "—"],
    ["Manual / system", detail.is_manual ? "Manual" : "System / not flagged"],
  ];
  return (
    <Panel className="transaction-panel">
      <div className="section-heading">
        <div>
          <div className="eyebrow">TRANSACTION CONTEXT</div>
          <h2>Source journal entry</h2>
        </div>
        <StatusBadge tone="neutral">Persisted ledger</StatusBadge>
      </div>
      <div className="transaction-grid">
        {fields.map(([label, value]) => (
          <div className={label === "Narration" ? "transaction-field transaction-field-wide" : "transaction-field"} key={label}>
            <span>{label}</span>
            <strong className={label === "Narration" ? "wrap-value" : ""}>{value}</strong>
          </div>
        ))}
      </div>
      <Disclosure summary="Source lineage">
        <div className="lineage-grid">
          <div>
            <span>Import ID</span>
            <strong>#{detail.import_id}</strong>
          </div>
          <div>
            <span>Source row</span>
            <strong>{detail.source_row}</strong>
          </div>
          <div>
            <span>Source filename</span>
            <strong>{entryFileName(detail)}</strong>
          </div>
          <div>
            <span>SHA-256</span>
            <SourceHash hash={detail.source_hash} />
          </div>
        </div>
        <TechnicalDetails value={detail.source_record} label="Original source row" />
      </Disclosure>
    </Panel>
  );
}

function ReviewTimeline({ detail }: { detail: ExceptionDetail }) {
  return (
    <Panel className="review-timeline">
      <div className="section-heading">
        <div>
          <div className="eyebrow">IMMUTABLE HISTORY</div>
          <h2>Review timeline</h2>
        </div>
        <span className="muted-label">{detail.reviews.length} event{detail.reviews.length === 1 ? "" : "s"}</span>
      </div>
      {detail.reviews.length ? (
        <ol className="timeline-list">
          {[...detail.reviews].reverse().map((review) => (
            <li key={review.id}>
              <div className="timeline-marker" />
              <div className="timeline-time">{formatDateTime(review.created_at)}</div>
              <div className="timeline-content">
                <div>
                  <strong>{review.reviewer}</strong>
                  <StatusBadge
                    tone={
                      review.disposition === "cleared" ? "success" :
                        review.disposition === "follow_up" ? "warning" : "indigo"
                    }
                  >
                    {titleCase(review.disposition)}
                  </StatusBadge>
                </div>
                <p>{review.note}</p>
                {review.second_reviewer && (
                  <div className="second-review-note">
                    <strong>Second review · {review.second_reviewer}</strong>
                    <span>{review.second_note}</span>
                  </div>
                )}
              </div>
            </li>
          ))}
        </ol>
      ) : (
        <div className="timeline-empty">
          <span>○</span>
          <p>No review has been recorded for this cue.</p>
        </div>
      )}
    </Panel>
  );
}

function SimilarTransactions({
  query,
  setQuery,
  results,
  onSearch,
}: {
  query: string;
  setQuery: (value: string) => void;
  results: SimilarResult[];
  onSearch: (event: FormEvent) => void;
}) {
  return (
    <Panel className="similar-panel">
      <div className="section-heading">
        <div>
          <div className="eyebrow">SEARCH THE POPULATION</div>
          <h2>Find similar transactions</h2>
        </div>
        <span className="search-shortcut">⌘ K</span>
      </div>
      <form className="similar-form" onSubmit={onSearch}>
        <TextInput
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="manual year-end tax provision"
          aria-label="Find similar transactions"
        />
        <Button type="submit" size="sm">
          Search
        </Button>
      </form>
      {results.length ? (
        <div className="similar-results">
          {results.map((item) => (
            <div className="similar-result" key={item.ledger_id}>
              <div>
                <strong>{item.entry_id}</strong>
                <span>{formatDate(item.posting_date)} · {item.account_code} · {formatMoney(item.signed_amount)}</span>
                <p>{item.description || "No narration supplied"}</p>
              </div>
              <div className="similar-scores">
                <span>Overall {Math.round(item.score * 100)}%</span>
                <span>Lexical {Math.round(item.token_score * 100)}%</span>
                {item.semantic_score !== null && <span>Semantic {Math.round(item.semantic_score * 100)}%</span>}
              </div>
              {item.shared_tokens.length > 0 && (
                <div className="shared-tokens">
                  {item.shared_tokens.slice(0, 5).map((token) => (
                    <span key={token}>{token}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <p className="muted-copy">Search by wording to compare lexical and semantic context. Similarity is not proof of a relationship.</p>
      )}
    </Panel>
  );
}

function PeerCard({ stats }: { stats: InvestigationContext["population_and_peers"] }) {
  const peerStats = stats.peer_statistics;
  const hasStats = peerStats && peerStats.available;
  const reversal = stats.possible_reversal;

  return (
    <Panel className="peer-context-panel">
      <div className="section-heading">
        <div>
          <div className="eyebrow">POPULATION & PEERS</div>
          <h2>What relates to this entry</h2>
        </div>
        <StatusBadge tone={stats.available ? "neutral" : "indigo"}>
          {stats.available ? "account present" : "peer data unavailable"}
        </StatusBadge>
      </div>
      {!stats.available ? (
        <p className="muted-copy">No peers can be computed for this entry. A population must be imported and analyzed first.</p>
      ) : (
        <>
          <div className="peer-stat-row">
            <span className="peer-stat-label">Account population</span>
            <span className="peer-stat-value">{stats.population_count.toLocaleString()} entries</span>
          </div>
          {hasStats ? (
            <>
              <div className="peer-stat-row">
                <span className="peer-stat-label">Median signed amount</span>
                <span className="peer-stat-value">
                  {peerStats.median !== null ? formatMoney(peerStats.median) : "—"}
                  {!peerStats.median_available && <span className="muted"> (median not computed)</span>}
                </span>
              </div>
              <div className="peer-stat-row">
                <span className="peer-stat-label">MAD</span>
                <span className="peer-stat-value">
                  {peerStats.mad !== null ? formatMoney(peerStats.mad) : "—"}
                  {!peerStats.mad_positive && <span className="muted"> (no dispersion)</span>}
                </span>
              </div>
              {peerStats.sample_of_population ? (
                <p className="muted-note">
                  Statistics are computed on a bounded sample of {peerStats.sample_count} entries, not the full population.
                </p>
              ) : null}
              <Disclosure summary="Related entries (bounded)">
                {stats.duplicate_entries.available ? (
                  <div className="related-list">
                    {stats.duplicate_entries.count === 1 ? (
                      <p>No other entries share the same account/date/amount/narration pattern.</p>
                    ) : (
                      <>
                        <p className="muted">
                          {stats.duplicate_entries.count} related member{stats.duplicate_entries.count === 1 ? "" : "s"} found.
                          {stats.duplicate_entries.count > 10 && " Only the first 10 are shown."}
                        </p>
                        <ul className="related-items">
                          {stats.duplicate_entries.members.map((m) => (
                            <li key={m.ledger_id}>
                              <strong>{m.entry_id}</strong> · {formatDate(m.posting_date)} · {formatMoney(m.signed_amount)}
                              <span className="muted"> (row {m.source_row})</span>
                            </li>
                          ))}
                        </ul>
                      </>
                    )}
                  </div>
                ) : (
                  <p className="muted-copy">No related entries with the same account/date/amount/narration pattern.</p>
                )}
              </Disclosure>
              <Disclosure summary="Possible reversal (±30 days)">
                {reversal.status === "flagged" && reversal.counterpart ? (
                  <div className="related-list">
                    <p>
                      Reversal counterpart: <strong>{reversal.counterpart.entry_id}</strong> ·{" "}
                      {formatDate(reversal.counterpart.posting_date)} · {formatMoney(reversal.counterpart.signed_amount)} ·{" "}
                      {reversal.counterpart.narration}
                    </p>
                    <p className="muted">
                      Basis: same account, opposite signed direction, within ±30 days of posting date. First match in posting-date then ledger order (bounded to 5 candidates).
                    </p>
                    <p className="muted">Days difference: {reversal.days_difference}</p>
                  </div>
                ) : reversal.status === "not_flagged" ? (
                  <p className="muted-copy">No opposite-direction entry found within ±30 days in this account.</p>
                ) : (
                  <p className="muted-copy">Reversal check not applicable (no bank/import data for this account).</p>
                )}
              </Disclosure>
            </>
          ) : (
            <p className="muted-copy">Peer statistics are unavailable because this account has fewer than four comparable entries.</p>
          )}
          <Disclosure summary="Materiality">
            {stats.materiality.configured ? (
              <div>
                <div className="peer-stat-row">
                  <span className="peer-stat-label">Amount</span>
                  <span className="peer-stat-value">{formatMoney(stats.materiality.amount)}</span>
                </div>
                <div className="peer-stat-row">
                  <span className="peer-stat-label">Band</span>
                  <span className="peer-stat-value">{stats.materiality.band}</span>
                </div>
                {stats.materiality.overall && (
                  <p className="muted">Overall materiality: {formatMoney(stats.materiality.overall)}</p>
                )}
                {stats.materiality.performance && (
                  <p className="muted">Performance materiality: {formatMoney(stats.materiality.performance)}</p>
                )}
                <p className="muted">
                  Materiality is a planning label only; it never changes the risk score or severity.
                </p>
              </div>
            ) : (
              <p className="muted-copy">Materiality is not configured for this run.</p>
            )}
          </Disclosure>
        </>
      )}
      <Disclosure summary="Data quality">
        <div className="data-quality-grid">
          {(Object.entries(stats.data_quality) as Array<[keyof InvestigationContext["population_and_peers"]["data_quality"], boolean]>).map(
            ([field, missing]) => (
              <div key={field} className={missing ? "data-quality-item missing" : "data-quality-item"}>
                <span>{field.replace(/_/g, " ")}</span>
                <StatusBadge tone={missing ? "warning" : "success"}>{missing ? "missing" : "present"}</StatusBadge>
              </div>
            )
          )}
        </div>
        <p className="muted">
          Missing optional fields are reported as unavailable, never as suspicious.
        </p>
      </Disclosure>
    </Panel>
  );
}

function SupportingEvidence({
  bank,
  reviewHistory,
  semantic,
}: {
  bank: InvestigationContext["supporting_evidence"]["bank"];
  reviewHistory: InvestigationContext["supporting_evidence"]["review_history"];
  semantic: InvestigationContext["supporting_evidence"]["semantic"];
}) {
  return (
    <Panel className="supporting-evidence-panel">
      <div className="section-heading">
        <div>
          <div className="eyebrow">SUPPORTING EVIDENCE</div>
          <h2>What can be linked</h2>
        </div>
      </div>
      <Disclosure summary="Bank reconciliation matches">
        {bank.available ? (
          <div className="evidence-list">
            <p>Match type: <strong>{bank.match_type}</strong> · Amount difference: {formatMoney(bank.amount_diff ?? 0)}</p>
            <div className="evidence-row">
              <span>Bank date</span>
              <span>{bank.bank_entry?.bank_date ?? "—"}</span>
            </div>
            <div className="evidence-row">
              <span>Bank row</span>
              <span>{bank.bank_entry?.bank_row}</span>
            </div>
            <div className="evidence-row">
              <span>Bank narration</span>
              <span>{bank.bank_entry?.bank_narration}</span>
            </div>
            <div className="evidence-row">
              <span>Bank source hash</span>
              <SourceHash hash={bank.bank_entry?.bank_source_hash ?? ""} />
            </div>
          </div>
        ) : (
          <p className="muted-copy">{bank.note ?? "No bank-reconciliation match is linked to this entry."}</p>
        )}
      </Disclosure>
      <Disclosure summary="Review history">
        {reviewHistory.available ? (
          <ol className="evidence-list timeline-list">
            {reviewHistory.history.map((r) => (
              <li key={r.review_id}>
                <strong>{r.reviewer}</strong> · {titleCase(r.disposition)} · {formatDateTime(r.created_at)}
                <p>{r.note}</p>
                {r.second_reviewer && <p className="muted">Second review: {r.second_reviewer} — {r.second_note}</p>}
              </li>
            ))}
          </ol>
        ) : (
          <p className="muted-copy">No reviews have been recorded for this cue.</p>
        )}
        <p className="muted">
          {reviewHistory.note}
        </p>
      </Disclosure>
      <Disclosure summary="Semantic profile">
        {semantic.available ? (
          <>
            <div className="evidence-row">
              <span>Run ID</span>
              <span>#{semantic.run_id}</span>
            </div>
            <div className="evidence-row">
              <span>Model</span>
              <span>{semantic.model ?? "—"}</span>
            </div>
            <div className="evidence-row">
              <span>Dimensions</span>
              <span>{semantic.dimensions ?? "—"}</span>
            </div>
            <div className="evidence-row">
              <span>Approximate retrieval</span>
              <span>
                {semantic.approximate_retrieval_disclosed ? (
                  <StatusBadge tone="warning">disclosed</StatusBadge>
                ) : (
                  <span>—</span>
                )}
              </span>
            </div>
            <p className="muted">{semantic.approximate_retrieval_note}</p>
            <p className="muted">{semantic.limitation}</p>
          </>
        ) : (
          <p className="muted-copy">{semantic.note ?? "No semantic profile has been generated or linked for this run."}</p>
        )}
      </Disclosure>
    </Panel>
  );
}

function WhyFlagged({ cues }: { cues: InvestigationContext["cues"] }) {
  if (!cues.length) {
    return <p className="muted-copy">No cues are recorded for this entry in the selected run.</p>;
  }
  return (
    <div className="cues-list">
      {cues.map((cue) => {
        const isExperimental = cue.source === "semantic_model" || cue.source === "experimental_ranker";
        return (
          <Disclosure key={cue.cue_id} summary={`${cue.label}${isExperimental ? " (experimental)" : ""}`}>
            <div className="cue-header">
              <span className="cue-source">{cue.source}</span>
              <StatusBadge tone={cue.status === "available" ? "success" : cue.status === "not_applicable" ? "indigo" : "warning"}>
                {cue.status}
              </StatusBadge>
              {!isExperimental && (
                <span className="cue-note">Cues are evidence worth investigating, not conclusions of error, fraud, or misstatement.</span>
              )}
              {isExperimental && (
                <span className="cue-note experimental">Experimental semantic/ranking observation; requires corroboration.</span>
              )}
            </div>
            <p><strong>Why flagged:</strong> {reasonText(cue.cue_id)}</p>
            <p><strong>Suggested next step:</strong> {cue.procedure.suggested_next_step}</p>
            {cue.procedure.inspect_evidence.length > 0 && (
              <ul>
                {cue.procedure.inspect_evidence.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            )}
            <p className="muted"><strong>Audit objective:</strong> {cue.procedure.audit_objective}</p>
            {cue.limitation && <p className="muted limitation"><strong>Limitation:</strong> {cue.limitation}</p>}
          </Disclosure>
        );
      })}
    </div>
  );
}

function SuggestedProcedures({ procedures }: { procedures: InvestigationContext["suggested_procedures"] }) {
  if (!procedures.length) {
    return <p className="muted-copy">No procedure suggestions are generated for this entry.</p>;
  }
  return (
    <div className="procedures-list">
      {procedures.map((proc, idx) => (
        <Panel key={idx} className="procedure-card">
          <div className="section-heading" style={{ padding: 0 }}>
            <div>
              <h3>{proc.cue_id.replace(/_/g, " ").split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ")}</h3>
              <span className={proc.experimental ? "experimental-tag" : ""}>{proc.experimental ? "EXPERIMENTAL" : "DETERMINISTIC"}</span>
              <span className={proc.unrecognized ? "unknown-tag" : ""}>{proc.unrecognized ? "UNRECOGNIZED CUE" : ""}</span>
            </div>
          </div>
          <p>{proc.description}</p>
          <p><strong>Why:</strong> {proc.why}</p>
          <p><strong>Next step:</strong> {proc.suggested_next_step}</p>
          <p className="muted">
            <strong>Audit objective:</strong> {proc.audit_objective} ·{" "}
            <strong>Non-conclusive:</strong> {proc.non_conclusive}
          </p>
        </Panel>
      ))}
    </div>
  );
}

function InvestigationContextPanel({ context }: { context: InvestigationContext }) {
  return (
    <Panel className="investigation-context-panel">
      <div className="section-heading">
        <div>
          <div className="eyebrow">INVESTIGATION CONTEXT v{context.investigation_context_version} · READ-ONLY</div>
          <h2>Transaction, why flagged, peers, what links, what next</h2>
        </div>
        <StatusBadge tone="neutral">Read-only view</StatusBadge>
      </div>
      <div className="context-grid">
        <div className="context-card">
          <h4>1 · Transaction</h4>
          <p>{formatMoney(context.transaction_line.signed_amount)}</p>
          <p>{context.transaction_line.account_code} · {context.transaction_line.account_name}</p>
          <p className="muted">{context.transaction_line.narration}</p>
        </div>
        <div className="context-card">
          <h4>2 · Why flagged</h4>
          <p>Cues: {context.cues.length}</p>
          <p>
            {context.cues.map((c) => c.label).join(", ") || "—"}
          </p>
          <p className="muted">
            {context.why_flagged.deterministic_reasons.length} deterministic ·{" "}
            {context.why_flagged.experimental_reasons.length} experimental
          </p>
        </div>
        <div className="context-card">
          <h4>3 · Related / limits</h4>
          <p>Peers: {context.population_and_peers.population_count.toLocaleString()} entries</p>
          <p>Reversal: {context.population_and_peers.possible_reversal.status}</p>
          <p>Max related: {context.contract.max_related}</p>
          <p>Semantic approximate: {context.lineage.semantic_approximate_retrieval ? "yes" : "n/a"}</p>
        </div>
        <div className="context-card">
          <h4>4 · Suggested next step</h4>
          <p>
            {context.suggested_procedures.slice(0, 2).map((s) => s.suggested_next_step || "Inspect source evidence.").join(" | ") || "Inspect source evidence."}
          </p>
          <p className="muted">Suggestions are indicative; not audit conclusions.</p>
        </div>
      </div>
      <div className="limitations">
        <strong>Limitations disclosed:</strong> {context.limitations.join("; ") || "See context."}
      </div>
    </Panel>
  );
}

export default function Investigation({
  exceptionId,
  status,
  users,
  refresh,
  revision,
  routeParams,
}: {
  exceptionId: number | null;
  status: StatusSummary;
  users: User[];
  refresh: () => Promise<void>;
  revision: number;
  routeParams?: URLSearchParams;
}) {
  const [detail, setDetail] = useState<ExceptionDetail | null>(null);
  const [semantic, setSemantic] = useState<SemanticInvestigation | null>(null);
  const [similar, setSimilar] = useState<SimilarResult[]>([]);
  const [context, setContext] = useState<InvestigationContext | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(Boolean(exceptionId));
  const [lockReason, setLockReason] = useState("");
  const [manager, setManager] = useState("");
  const [assignee, setAssignee] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [assignmentBusy, setAssignmentBusy] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const managers = useMemo(() => users.filter((user) => ["manager", "partner"].includes(user.role)), [users]);
  const reviewers = useMemo(() => users.filter((user) => ["reviewer", "manager", "partner", "quality_reviewer"].includes(user.role)), [users]);

  useEffect(() => {
    setManager((current) => current || managers[0]?.username || "");
  }, [managers]);

  async function reloadDetail() {
    setRefreshKey((k) => k + 1);
    await refresh();
  }

  useEffect(() => {
    if (!exceptionId) {
      setDetail(null);
      setSemantic(null);
      setContext(null);
      setLoading(false);
      return;
    }
    if (!detail) {
      setLoading(true);
      setError("");
    }

    let cancelled = false;
    async function load() {
      try {
        const result = await get<ExceptionDetail>(`/exceptions/${exceptionId}`);
        if (cancelled) return;
        setDetail(result);
        setAssignee(result.assigned_to ?? "");
        setDueDate(result.due_date ?? "");

        // Semantic enrichment — optional, only when a semantic run is linked.
        const semanticId = semanticRunId(result);
        if (semanticId) {
          try {
            const s = await get<SemanticInvestigation>(`/semantic-investigation?run=${semanticId}&ledger_id=${result.ledger_id}`);
            if (!cancelled) setSemantic(s);
          } catch {
            if (!cancelled) setSemantic(null);
          }
        }

        // Deterministic investigation context — the primary read; never blocked by semantic availability.
        try {
          const ctx = await get<InvestigationContext>(
            `/investigation-context?run_id=${result.run_id}&ledger_id=${result.ledger_id}${semanticId ? `&semantic_run_id=${semanticId}` : ""}`
          );
          if (!cancelled) setContext(ctx);
        } catch (cause) {
          if (!cancelled) setError(cause instanceof Error ? cause.message : "Investigation context could not be loaded.");
        }
      } catch (cause) {
        if (!cancelled) setError(cause instanceof Error ? cause.message : "The investigation could not be opened.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [exceptionId, refreshKey, revision]);

  async function search(event: FormEvent) {
    event.preventDefault();
    if (!query.trim()) return;
    try {
      const result = await get<{ results: SimilarResult[] }>(`/similar?q=${encodeURIComponent(query.trim())}&limit=10`);
      setSimilar(result.results);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Similar transactions could not be loaded.");
    }
  }

  async function assign() {
    if (!detail) return;
    setAssignmentBusy(true);
    setError("");
    setNotice("");
    try {
      await post("/assignments", { actor: manager, exception_id: detail.id, assignee, due_date: dueDate || null });
      await reloadDetail();
      setNotice("Assignment recorded.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "The assignment could not be recorded.");
    } finally {
      setAssignmentBusy(false);
    }
  }

  async function changeLock(action: "lock" | "reopen") {
    try {
      await post(`/review-set/${action === "lock" ? "lock" : "reopen"}`, { actor: manager, reason: lockReason });
      setLockReason("");
      await refresh();
      setNotice(action === "lock" ? "Review set locked." : "Review set reopened.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "The review-set event could not be recorded.");
    }
  }

  const [query, setQuery] = useState("");

  if (!exceptionId) {
    return (
      <div className="investigation-empty">
        <div className="eyebrow">STEP 05 · INVESTIGATION</div>
        <h1>Investigation & Review</h1>
        <p>Select a risk cue from the queue to inspect its evidence, source lineage, and immutable review history.</p>
        <Button variant="primary" onClick={() => navigate("risk")}>Open risk queue</Button>
      </div>
    );
  }

  const backParams = { run: routeParams?.get("run") ?? detail?.run_id, search: routeParams?.get("search") ?? "", severity: routeParams?.get("severity") ?? "", status: routeParams?.get("status") ?? "" };

  return (
    <div className="investigation-page">
      <div className="investigation-breadcrumb">
        <button onClick={() => navigate("risk", backParams)}>← Back to risk queue</button>
        <span>/</span>
        <span>{detail?.entry_id ?? "Loading entry"}</span>
      </div>
      {error && <Message kind="error">{error}<br /><button onClick={reloadDetail} style={{ marginLeft: 8, cursor: "pointer" }}>Retry</button></Message>}
      {notice && <Message kind="success">{notice}</Message>}
      {loading || !detail ? (
        <Loading label="Opening investigation workspace…" />
      ) : (
        <>
          <header className="investigation-hero">
            <div className="investigation-hero-main">
              <div className="investigation-kicker">
                <SeverityBadge severity={detail.severity} />
                <span>{detail.run_id ? `Analysis run ${detail.run_id}` : "Risk cue"}</span>
              </div>
              <h1>Investigation & Review</h1>
              <div className="investigation-entry-line">
                <span className="entry-id-large">{detail.entry_id}</span>
                <span className="entry-separator">·</span>
                <span>{formatDate(detail.posting_date)}</span>
                <span className="entry-separator">·</span>
                <strong>{formatMoney(detail.signed_amount)}</strong>
              </div>
              <p>{detail.account_code} {detail.account_name ?? ""} <span>·</span> {detail.description || "No narration supplied"}</p>
            </div>
            <div className="investigation-hero-side">
              <StatusBadge tone={detail.status === "cleared" ? "success" : detail.status === "follow_up" ? "warning" : "indigo"} dot>
                {titleCase(detail.status)}
              </StatusBadge>
              <span className="hero-side-label">Current disposition</span>
              <span className="hero-side-value">{detail.assigned_to ? `Assigned to ${detail.assigned_to}` : "Unassigned"}</span>
            </div>
          </header>
          <div className="investigation-content">
            <div className="investigation-main-column">
              {context && <InvestigationContextPanel context={context} />}
              {context && context.why_flagged.experimental_evidence_available && !context.why_flagged.deterministic_evidence_available && (
                <Message kind="warning">
                  This entry is flagged only by experimental semantic or ranking observations. Corroborate with source evidence before drawing any conclusion.
                </Message>
              )}
              <Panel className="why-panel">
                <div className="section-heading">
                  <div>
                    <div className="eyebrow">WHY THIS ENTRY SURFACED</div>
                    <h2>Start with the reasoning</h2>
                    <p className="section-description">These are analytical cues that warrant attention. They are not conclusions about the entry.</p>
                  </div>
                  <span className="reason-count">{detail.reasons.length} cue{detail.reasons.length === 1 ? "" : "s"}</span>
                </div>
                <WhyFlagged cues={context?.cues ?? []} />
              </Panel>
              <PeerCard stats={context?.population_and_peers ?? { account: "—", available: false, status: null, population_count: 0, peer_statistics: null, duplicate_entries: { available: false, count: 0, members: [], matching_rationale: "" }, possible_reversal: { available: false, status: "not_applicable" }, materiality: { configured: false, status: "unavailable", amount: 0, band: "not_set" }, population_indicators: { benford: null }, data_quality: { missing_narration: true, missing_preparer: true, missing_reference: true, missing_entity: true, missing_vendor: true, missing_document_date: true } }} />
              <SupportingEvidence
                bank={context?.supporting_evidence.bank ?? { available: false, status: "not_applicable", note: "Bank match data not available." }}
                reviewHistory={context?.supporting_evidence.review_history ?? { available: false, review_count: 0, latest_disposition: null, history: [], governance: { locked: false, event: null, actor: null, reason: null, changed_at: null }, note: "" }}
                semantic={context?.supporting_evidence.semantic ?? { available: false, status: "unavailable", note: "No semantic profile linked to this run." }}
              />
              {context && <SuggestedProcedures procedures={context.suggested_procedures} />}
              <Panel className="why-panel">
                <div className="section-heading">
                  <div>
                    <div className="eyebrow">SOURCE RECORDS</div>
                    <h2>What the stored data shows</h2>
                  </div>
                </div>
                <DeterministicEvidence detail={detail} />
              </Panel>
              {context?.lineage.semantic_profile_run_id && (
                <Panel className="why-panel">
                  <div className="section-heading">
                    <div>
                      <div className="eyebrow">SEMANTIC ENRICHMENT</div>
                      <h2>Bounded semantic profile</h2>
                    </div>
                  </div>
                  <SemanticEvidence investigation={semantic!} />
                </Panel>
              )}
              <ReviewForm detail={detail} users={reviewers} locked={status.review_set.locked} onSaved={reloadDetail} />
              <ReviewTimeline detail={detail} />
            </div>
            <aside className="investigation-side-column">
              <SimilarTransactions query={query} setQuery={setQuery} results={similar} onSearch={search} />
              <Panel className="governance-panel">
                <div className="eyebrow">REVIEW-SET CONTROL</div>
                <h2>{status.review_set.locked ? "Review set locked" : "Governance milestone"}</h2>
                <p>{status.review_set.locked ? "Reopen with a reasoned event before changing assignments or dispositions." : "Lock the completed review set when the workpaper is ready to finalize."}</p>
                <Field label="Reason">
                  <TextInput value={lockReason} onChange={(event) => setLockReason(event.target.value)} placeholder="Reason for the governance event" />
                </Field>
                <div className="governance-actions">
                  {!status.review_set.locked && (
                    <Button size="sm" onClick={() => changeLock("lock")} disabled={!manager || !lockReason.trim()}>Lock review set</Button>
                  )}
                  {status.review_set.locked && (
                    <Button size="sm" variant="secondary" onClick={() => changeLock("reopen")} disabled={!manager || !lockReason.trim()}>Reopen review set</Button>
                  )}
                </div>
              </Panel>
            </aside>
          </div>
        </>
      )}
    </div>
  );
}
