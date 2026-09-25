import { useEffect, useMemo, useState, type FormEvent } from "react";

import { post } from "../lib/api";
import type { Disposition, ExceptionDetail, User } from "../lib/types";
import { Button, Disclosure, Field, Message, Select, StatusBadge, TextArea } from "./ui";

const dispositions: Array<{ value: Disposition; label: string; description: string }> = [
  { value: "open", label: "Open", description: "Keep the cue in the review queue." },
  { value: "cleared", label: "Cleared", description: "Record the review conclusion and supporting work." },
  { value: "follow_up", label: "Follow up", description: "Request more evidence or clarification." },
  { value: "selected_for_testing", label: "Selected for testing", description: "Carry this entry into the proposed testing sample." },
];

export default function ReviewForm({ detail, users, locked, onSaved }: { detail: ExceptionDetail; users: User[]; locked: boolean; onSaved: () => Promise<void> }) {
  const eligible = useMemo(() => users.filter((user) => ["reviewer", "manager", "partner", "quality_reviewer"].includes(user.role)), [users]);
  const [reviewer, setReviewer] = useState("");
  const [disposition, setDisposition] = useState<Disposition>(detail.status);
  const [note, setNote] = useState("");
  const [secondReviewer, setSecondReviewer] = useState("");
  const [secondNote, setSecondNote] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => setReviewer((current) => current || eligible[0]?.username || ""), [eligible]);
  useEffect(() => { setDisposition(detail.status); }, [detail.status, detail.id]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true); setError(""); setSuccess("");
    try {
      await post("/review", { id: detail.id, reviewer, disposition, note, second_reviewer: secondReviewer || null, second_note: secondNote || null });
      setNote(""); setSecondNote("");
      setSuccess("Disposition appended to the immutable review history.");
      await onSaved();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "The review could not be saved. Check the required fields and try again.");
    } finally { setSaving(false); }
  }

  const secondRequired = detail.severity === "high" && disposition === "cleared";
  const secondReviewers = eligible.filter((user) => user.username !== reviewer);

  return <form className="review-form" onSubmit={submit}>
    <div className="review-form-heading"><div><div className="eyebrow">REVIEW</div><h2>Record disposition</h2></div><StatusBadge tone={locked ? "warning" : "success"} dot>{locked ? "Review set locked" : "Ready to record"}</StatusBadge></div>
    {locked && <Message kind="warning">The review set is locked. A manager must reopen it before review or assignment changes.</Message>}
    {error && <Message kind="error">{error}</Message>}
    {success && <Message kind="success">{success}</Message>}
    <div className="form-grid"><Field label="Current status"><div className="current-status-value"><StatusBadge tone={detail.status === "cleared" ? "success" : detail.status === "follow_up" ? "warning" : "indigo"}>{detail.status.replaceAll("_", " ")}</StatusBadge><span>Latest immutable review state</span></div></Field><Field label="Reviewer" hint="Choose the local reviewer recording this disposition."><Select value={reviewer} onChange={(event) => setReviewer(event.target.value)} disabled={locked} aria-label="Reviewer"><option value="">Choose reviewer</option>{eligible.map((user) => <option key={user.username} value={user.username}>{user.username} · {user.role}</option>)}</Select></Field></div>
    <fieldset className="disposition-fieldset" disabled={locked}><legend>Disposition</legend><div className="disposition-options">{dispositions.map((item) => <label className={`disposition-option ${disposition === item.value ? "is-selected" : ""}`} key={item.value}><input type="radio" name="disposition" value={item.value} checked={disposition === item.value} onChange={() => setDisposition(item.value)} /><span className="radio-mark" /><span><strong>{item.label}</strong><small>{item.description}</small></span></label>)}</div>    </fieldset>
    <label className="legacy-disposition-control">Disposition<select className="input" value={disposition} onChange={(event) => setDisposition(event.target.value as Disposition)} disabled={locked}>{dispositions.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select></label>
    <Field label="Review note" hint="Explain the evidence obtained, follow-up needed, or reason for the disposition."><TextArea aria-label="Audit rationale / evidence requested" rows={4} value={note} onChange={(event) => setNote(event.target.value)} disabled={locked} placeholder="e.g. Obtain approval, invoice, contract, and subsequent-payment evidence." /></Field>
    {secondRequired && <div className="second-review-box"><div className="second-review-heading"><div><strong>Independent second review required</strong><p>This high-priority cue cannot be cleared by one reviewer alone.</p></div><StatusBadge tone="warning">Two-person control</StatusBadge></div><div className="form-grid"><Field label="Second reviewer"><Select value={secondReviewer} onChange={(event) => setSecondReviewer(event.target.value)} disabled={locked}><option value="">Choose second reviewer</option>{secondReviewers.map((user) => <option key={user.username} value={user.username}>{user.username} · {user.role}</option>)}</Select></Field><Field label="Second review note"><TextArea value={secondNote} onChange={(event) => setSecondNote(event.target.value)} disabled={locked} rows={3} placeholder="Record the independent review conclusion." /></Field></div></div>}
    <div className="review-form-footer"><Button type="submit" variant="primary" size="lg" disabled={locked || saving || !reviewer || !note.trim() || (secondRequired && (!secondReviewer || !secondNote.trim()))}>{saving ? "Saving review…" : "Save review"}<span className="sr-only"> Save disposition</span></Button><span className="form-footnote">Every save creates an immutable history event.</span></div>
    <Disclosure summary="What this control preserves"><p className="muted-copy">The backend records the reviewer, disposition, note, timestamp, and any independent second review. Existing review events are never edited.</p></Disclosure>
  </form>;
}
