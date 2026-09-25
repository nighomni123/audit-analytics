import { useEffect, useMemo, useState } from "react";

import { get } from "../lib/api";
import type { AuditLogEntry, AuditLogPage, StatusSummary } from "../lib/types";
import { Button, Disclosure, EmptyState, ErrorState, Loading, Message, PageHeader, Panel, StatusBadge, TechnicalDetails, formatDateTime, formatNumber, titleCase } from "../components/ui";

function eventTone(action: string): "success" | "warning" | "indigo" | "slate" {
  if (action.includes("acknowledge") || action.includes("lock") || action.includes("export")) return "success";
  if (action.includes("reopen") || action.includes("follow")) return "warning";
  if (action.includes("review") || action.includes("analyze") || action.includes("sample")) return "indigo";
  return "slate";
}

function eventDescription(event: AuditLogEntry): string {
  const detail = event.detail ?? {};
  if (event.action === "import_gl") return `${formatNumber(Number(detail.accepted ?? 0))} rows accepted · ${formatNumber(Number(detail.rejected ?? 0))} rejected`;
  if (event.action === "acknowledge_population") return "Population reconciliation and reviewer acknowledgement recorded";
  if (event.action === "analyze") return `${formatNumber(Number(detail.population ?? 0))} entries analyzed · model ${String(detail.model_name ?? "deterministic")}`;
  if (event.action === "configure") return "Methodology version recorded";
  if (event.action === "assign_exception") return `Assigned to ${String(detail.assignee ?? "reviewer")}`;
  if (event.action === "review_exception") return `Disposition ${String(detail.disposition ?? "recorded").replaceAll("_", " ")}`;
  if (event.action === "create_sample") return `${formatNumber(Number(detail.selected ?? 0))} entries selected · seed ${String(detail.seed ?? "—")}`;
  if (event.action === "lock" || event.action === "reopened") return String(detail.reason ?? "Review-set governance event");
  if (event.action === "export_workpaper") return "Workpaper package and manifest written";
  return "Engagement event recorded";
}

export default function Activity({ status, refresh }: { status: StatusSummary; refresh: () => Promise<void> }) {
  const [page, setPage] = useState<AuditLogPage | null>(null);
  const [filter, setFilter] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const load = async () => { setLoading(true); setError(""); try { const query = filter.trim() ? `&action=${encodeURIComponent(filter.trim())}` : ""; setPage(await get<AuditLogPage>(`/audit-log?limit=100${query}`)); } catch (cause) { setError(cause instanceof Error ? cause.message : "The audit trail could not be loaded."); } finally { setLoading(false); } };
  useEffect(() => { void load(); }, [status.latest_run.id, status.review_set.changed_at]);
  const events = page?.rows ?? [];
  return <div className="activity-page"><PageHeader eyebrow="ENGAGEMENT TRACEABILITY" title="Audit trail" description="A human-readable record of imports, controls, analysis runs, assignments, reviews, and closeout events. Technical identifiers remain available in details." action={<Button variant="secondary" onClick={() => { void refresh(); void load(); }}>Refresh trail</Button>} />{error && <ErrorState description={error} onRetry={() => void load()} />}<div className="activity-toolbar"><div><strong>Immutable engagement history</strong><span>All events are read from the local append-only audit log.</span></div><div className="activity-filter"><input className="input" value={filter} onChange={(event) => setFilter(event.target.value)} placeholder="Filter action, e.g. review" aria-label="Filter audit action" /><Button size="sm" onClick={() => void load()}>Filter</Button></div></div>{loading ? <Loading label="Opening audit trail…" /> : !page ? <Message kind="error">Audit trail unavailable.</Message> : events.length === 0 ? <EmptyState title="No audit events yet" description="Imports, methodology changes, reviews, and exports will appear here as the engagement progresses." /> : <Panel className="audit-timeline"><div className="audit-timeline-head"><span>EVENT</span><span>ACTOR</span><span>WHEN</span><span>TECHNICAL DETAILS</span></div>{events.map((event) => <div className="audit-event" key={event.id}><div className={`audit-event-marker audit-marker-${eventTone(event.action)}`} aria-hidden="true">●</div><div className="audit-event-main"><div className="audit-event-title"><strong>{titleCase(event.action.replaceAll("_", " "))}</strong><StatusBadge tone={eventTone(event.action)}>{event.target_type}</StatusBadge></div><p>{eventDescription(event)}</p><small>Target {event.target_type} <code>#{event.target_id}</code></small></div><div className="audit-event-actor"><span className="actor-avatar">{event.actor.slice(0, 2).toUpperCase()}</span><strong>{event.actor}</strong></div><time dateTime={new Date(event.created_at * 1000).toISOString()}>{formatDateTime(event.created_at)}</time><Disclosure summary="View details"><TechnicalDetails value={{ id: event.id, action: event.action, target_type: event.target_type, target_id: event.target_id, actor: event.actor, detail: event.detail }} label="Event record" /></Disclosure></div>)}</Panel>}<div className="activity-footnote"><span className="status-dot" />Audit trail events are append-only. Review history and review-set events retain their own immutable timelines.</div></div>;
}
