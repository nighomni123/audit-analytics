import type { ReactNode } from "react";

import type { ExceptionDetail, SemanticInvestigation } from "../lib/types";
import { Disclosure, Panel, StatusBadge, TechnicalDetails, formatDate, formatMoney, titleCase } from "./ui";

function entryText(value: Record<string, unknown>, key: string, fallback = "—"): string {
  const item = value[key];
  return item === null || item === undefined || item === "" ? fallback : String(item);
}

function EntrySummary({ value, score }: { value: Record<string, unknown>; score?: number }) {
  return <div className="evidence-entry"><div className="evidence-entry-top"><strong>{entryText(value, "entry_id")}</strong>{score !== undefined && <span className="similarity-score">{Math.round(score * 100)}% similar</span>}</div><div className="evidence-entry-meta">{entryText(value, "posting_date")} · {entryText(value, "account_code")}</div><div className="evidence-entry-description">{entryText(value, "description", "No narration supplied")}</div>{typeof value.signed_amount === "number" && <div className="evidence-entry-amount">{formatMoney(value.signed_amount)}</div>}</div>;
}

function EvidenceCard({ title, question, children, tone = "neutral" }: { title: string; question: string; children: ReactNode; tone?: "neutral" | "amber" | "indigo" }) {
  return <div className={`evidence-card evidence-card-${tone}`}><div className="evidence-card-heading"><div><h4>{title}</h4><p>{question}</p></div><span className="evidence-card-mark" aria-hidden="true">↗</span></div>{children}</div>;
}

function numeric(value: unknown): string {
  return typeof value === "number" ? value.toLocaleString("en-IN", { maximumFractionDigits: 2 }) : "—";
}

export function DeterministicEvidence({ detail }: { detail: ExceptionDetail }) {
  const evidence = detail.evidence ?? {};
  const hasPeer = evidence.peer_median !== undefined || evidence.robust_z !== undefined;
  const hasReversal = evidence.reversal_ledger_id !== undefined;
  const hasDuplicate = evidence.duplicate_count !== undefined;
  const hasBenford = evidence.benford_population_indicator !== undefined;
  return <div className="deterministic-evidence">
    <div className="evidence-intro"><div><div className="eyebrow">DETERMINISTIC EVIDENCE</div><h3>What is unusual?</h3></div><StatusBadge tone="indigo">Human-readable context</StatusBadge></div>
    <div className="evidence-grid">
      <EvidenceCard title="Amount" question="How does this entry compare with the account peer distribution?"><div className="evidence-stat-row"><div><span>Entry amount</span><strong>{formatMoney(detail.signed_amount)}</strong></div><div><span>Peer median</span><strong>{hasPeer ? formatMoney(Number(evidence.peer_median)) : "Not available"}</strong></div><div><span>Robust distance</span><strong>{hasPeer ? `${numeric(evidence.robust_z)} z` : "Not available"}</strong></div></div>{hasPeer ? <p className="evidence-support">The entry is compared with other entries in the same account. A signal prioritizes review; it does not establish an error.</p> : <p className="evidence-support">Peer context is not available for this account or population size.</p>}</EvidenceCard>
      <EvidenceCard title="Timing" question="Where does the posting sit relative to the engagement period-end window?"><div className="timing-line"><span className="timing-dot" /><div><strong>{formatDate(detail.posting_date)}</strong><span>{detail.reasons.some((reason) => reason.includes("period_end")) ? "Within the configured period-end window" : "Outside the highlighted period-end signal"}</span></div></div><p className="evidence-support">Configured period-end window: {detail.reasons.some((reason) => reason.includes("period_end")) ? "signal present" : "no period-end signal recorded"}.</p></EvidenceCard>
      <EvidenceCard title="Peer activity" question="What historical account activity supports the signal?"><div className="evidence-mini-list"><div><span>Account</span><strong>{detail.account_code} · {detail.account_name ?? "Unnamed account"}</strong></div><div><span>Preparer pattern</span><strong>{detail.preparer ?? "Not supplied"}</strong></div><div><span>Amount band</span><strong>{detail.materiality_band ? titleCase(detail.materiality_band) : "Not set"}</strong></div></div>{hasPeer ? <p className="evidence-support">Peer evidence is calculated from the imported population, not an external conclusion.</p> : <p className="evidence-support">Detailed peer examples appear when the relevant signal is available.</p>}</EvidenceCard>
      <EvidenceCard title="Reversal" question="Is there a linked or candidate reversal?"><div className="evidence-stat-row"><div><span>Candidate</span><strong>{hasReversal ? `Ledger #${numeric(evidence.reversal_ledger_id)}` : "None recorded"}</strong></div><div><span>Window</span><strong>30 days</strong></div></div><p className="evidence-support">A possible reversal is a prompt to inspect related entries, not a conclusion about intent.</p></EvidenceCard>
      <EvidenceCard title="Frequency" question="Does this entry repeat a known account and preparer pattern?"><div className="evidence-stat-row"><div><span>Repeat count</span><strong>{hasDuplicate ? numeric(evidence.duplicate_count) : "No repeat signal"}</strong></div><div><span>Pair</span><strong>{detail.preparer ? `${detail.account_code} / ${detail.preparer}` : "Identity incomplete"}</strong></div></div><p className="evidence-support">Frequency signals help identify where corroborating evidence may be useful.</p></EvidenceCard>
      {hasBenford && <EvidenceCard title="Population indicator" question="What population-level applicability check was recorded?" tone="amber"><p className="evidence-support">{String((evidence.benford_population_indicator as Record<string, unknown>)?.note ?? "Population-level indicator recorded.")}</p><p className="evidence-muted">This indicator does not identify a problematic entry and is not an audit conclusion.</p></EvidenceCard>}
    </div>
    <div className="evidence-footer"><span><strong>Recorded reasons</strong> · {detail.reasons.length ? detail.reasons.map((reason) => titleCase(reason)).join(" · ") : "No deterministic cue recorded"}</span><Disclosure summary="Technical evidence"><TechnicalDetails value={detail.evidence} label="Structured evidence" /></Disclosure></div>
  </div>;
}

export function SemanticEvidence({ investigation }: { investigation: SemanticInvestigation }) {
  const related = investigation.evidence.related_population ?? {};
  return <div className="semantic-evidence">
    <div className="semantic-heading"><div><div className="eyebrow">OPTIONAL LOCAL MODEL</div><h3>Semantic Context</h3><p>Experimental context that helps compare wording and related activity. It augments the deterministic review path and never suppresses it.</p></div><StatusBadge tone="warning" dot>Experimental · Local model</StatusBadge></div>
    {investigation.stale && <div className="semantic-warning"><strong>Historical snapshot.</strong> The current population changed. Rebuild semantic evidence before relying on it for a new analysis.</div>}
    <div className="semantic-grid">
      <div className="semantic-block"><div className="semantic-block-title"><span>01</span><h4>Normal peers</h4></div><p className="semantic-question">Which similar historical transactions provide context?</p><div className="evidence-entry-list">{investigation.evidence.normal_peers.length ? investigation.evidence.normal_peers.map((item) => <EntrySummary key={item.ledger_id} value={item.entry} score={item.similarity} />) : <p className="muted-copy">No normal peers returned.</p>}</div></div>
      <div className="semantic-block"><div className="semantic-block-title"><span>02</span><h4>Alternative matches</h4></div><p className="semantic-question">Which entries are similar in wording or context?</p><div className="evidence-entry-list">{investigation.evidence.alternative_matches.length ? investigation.evidence.alternative_matches.map((item) => <EntrySummary key={item.ledger_id} value={item.entry} score={item.similarity} />) : <p className="muted-copy">No alternative matches returned.</p>}</div></div>
      <div className="semantic-block"><div className="semantic-block-title"><span>03</span><h4>Historical context</h4></div><p className="semantic-question">What earlier activity or shifts are recorded?</p><div className="semantic-metrics">{Object.entries(investigation.metrics).slice(0, 6).map(([key, value]) => <div key={key}><span>{titleCase(key)}</span><strong>{value === null ? "—" : typeof value === "number" ? value.toFixed(2) : String(value)}</strong></div>)}</div></div>
      <div className="semantic-block"><div className="semantic-block-title"><span>04</span><h4>Related population</h4></div><p className="semantic-question">Which related clusters or process hints were surfaced?</p>{Object.keys(related).length ? <div className="related-list">{Object.entries(related).slice(0, 4).map(([key, group]) => <div key={key}><strong>{titleCase(key)}</strong><span>{group.count} related entries{group.truncated ? " · bounded view" : ""}</span></div>)}</div> : <p className="muted-copy">No related population clusters returned.</p>}</div>
    </div>
    <div className="semantic-bottom"><div><div className="eyebrow">SUGGESTED EVIDENCE</div><ul className="suggested-list">{investigation.evidence.suggested_evidence.length ? investigation.evidence.suggested_evidence.map((item) => <li key={item}>{item}</li>) : <li>Review the transaction narrative and obtain corroborating records.</li>}</ul></div><div><div className="eyebrow">LIMITATIONS</div><ul className="limitation-list">{investigation.evidence.limitations.map((item) => <li key={item}>{item}</li>)}</ul></div></div>
    <Disclosure summary="Provenance and comparison basis"><div className="provenance-grid"><div><span>Model</span><strong>{String(investigation.provenance.model ?? "Local semantic model")}</strong></div><div><span>Run</span><strong>{investigation.run_id}</strong></div><div><span>Population</span><strong>{String(investigation.entry.population_count ?? "Stored snapshot")}</strong></div><div><span>Retrieval</span><strong>Sampled, not exhaustive</strong></div></div><TechnicalDetails value={{ provenance: investigation.provenance, comparisons: investigation.evidence.comparisons, other_signals: investigation.other_signals }} label="Raw provenance" /></Disclosure>
  </div>;
}
