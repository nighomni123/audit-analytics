import { useEffect, useMemo, useState, type FormEvent } from "react";

import { post } from "../lib/api";
import type { Disposition, ExceptionDetail, User } from "../lib/types";
import { Message } from "./ui";

const dispositions: Disposition[] = ["open", "cleared", "follow_up", "selected_for_testing"];

export default function ReviewForm({
  detail,
  users,
  locked,
  onSaved,
}: {
  detail: ExceptionDetail;
  users: User[];
  locked: boolean;
  onSaved: () => Promise<void>;
}) {
  const eligible = useMemo(
    () => users.filter((user) => ["reviewer", "manager", "partner", "quality_reviewer"].includes(user.role)),
    [users],
  );
  const [reviewer, setReviewer] = useState("");
  const [disposition, setDisposition] = useState<Disposition>(detail.status);
  const [note, setNote] = useState("");
  const [secondReviewer, setSecondReviewer] = useState("");
  const [secondNote, setSecondNote] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setReviewer((current) => current || eligible[0]?.username || "");
  }, [eligible]);

  useEffect(() => {
    setDisposition(detail.status);
  }, [detail.status]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");
    try {
      await post("/review", {
        id: detail.id,
        reviewer,
        disposition,
        note,
        second_reviewer: secondReviewer || null,
        second_note: secondNote || null,
      });
      setNote("");
      setSecondNote("");
      await onSaved();
      setSuccess("Disposition appended to the immutable review history.");
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setSaving(false);
    }
  }

  const secondRequired = detail.severity === "high" && disposition === "cleared";

  return (
    <form onSubmit={submit} className="space-y-3">
      <h3 className="text-lg font-bold">Record disposition</h3>
      {locked && <Message kind="warning">The review set is locked. A manager must reopen it before review or assignment changes.</Message>}
      {error && <Message kind="error">{error}</Message>}
      {success && <Message kind="success">{success}</Message>}
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="grid gap-1 text-sm font-medium">Local reviewer<select className="rounded-lg border border-slate-300 px-3 py-2" value={reviewer} onChange={(event) => setReviewer(event.target.value)} disabled={locked}>{eligible.map((user) => <option key={user.username} value={user.username}>{user.username} · {user.role}</option>)}</select></label>
        <label className="grid gap-1 text-sm font-medium">Disposition<select className="rounded-lg border border-slate-300 px-3 py-2" value={disposition} onChange={(event) => setDisposition(event.target.value as Disposition)} disabled={locked}>{dispositions.map((value) => <option key={value} value={value}>{value.replaceAll("_", " ")}</option>)}</select></label>
      </div>
      <label className="grid gap-1 text-sm font-medium">Audit rationale / evidence requested<textarea className="rounded-lg border border-slate-300 px-3 py-2" rows={3} value={note} onChange={(event) => setNote(event.target.value)} disabled={locked} /></label>
      {secondRequired && (
        <div className="grid gap-3 rounded-lg border border-amber-300 bg-amber-50 p-3 sm:grid-cols-2">
          <Message kind="warning">High-severity clear requires a distinct authorized second reviewer.</Message>
          <label className="grid gap-1 text-sm font-medium">Second reviewer<select className="rounded-lg border border-slate-300 px-3 py-2" value={secondReviewer} onChange={(event) => setSecondReviewer(event.target.value)}>{eligible.filter((user) => user.username !== reviewer).map((user) => <option key={user.username} value={user.username}>{user.username} · {user.role}</option>)}</select></label>
          <label className="grid gap-1 text-sm font-medium">Second note<textarea className="rounded-lg border border-slate-300 px-3 py-2" rows={2} value={secondNote} onChange={(event) => setSecondNote(event.target.value)} /></label>
        </div>
      )}
      <button disabled={locked || saving || !reviewer || !note.trim()} className="rounded-lg bg-slate-900 px-4 py-2 font-semibold text-white disabled:opacity-50">{saving ? "Saving…" : "Save disposition"}</button>
      <p className="text-xs text-slate-500">The selected local user is a workflow label, not authenticated identity.</p>
    </form>
  );
}
