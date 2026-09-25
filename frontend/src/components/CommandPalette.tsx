import { useEffect, useMemo, useRef, useState, type FormEvent, type KeyboardEvent as ReactKeyboardEvent } from "react";

import { navigate, type Screen } from "../lib/navigation";
import type { StatusSummary } from "../lib/types";
import { Button, StatusBadge } from "./ui";

interface CommandPaletteProps {
  status: StatusSummary;
  onClose: () => void;
}

export default function CommandPalette({ status, onClose }: CommandPaletteProps) {
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  useEffect(() => inputRef.current?.focus(), []);
  useEffect(() => {
    const close = (event: KeyboardEvent) => { if (event.key === "Escape") onClose(); };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, [onClose]);

  const actions = useMemo(() => [
    { label: "Add client ledger", detail: "Population", icon: "+", screen: "population" as Screen },
    { label: "Run analysis", detail: "Analysis", icon: "▶", screen: "analysis" as Screen },
    { label: "Open risk queue", detail: `${Object.values(status.exceptions ?? {}).reduce((sum, value) => sum + value, 0)} risk cues`, icon: "≡", screen: "risk" as Screen },
    { label: "Create testing sample", detail: "Review planning", icon: "◇", screen: "sample" as Screen },
    { label: "Open workpapers", detail: "Finalize", icon: "□", screen: "workpapers" as Screen },
    { label: "Lock review set", detail: "Governance", icon: "▣", screen: "workpapers" as Screen },
  ], [status.exceptions]);
  const filtered = actions.filter((action) => `${action.label} ${action.detail}`.toLowerCase().includes(query.toLowerCase()));

  function go(screen: Screen, search?: string) {
    onClose();
    navigate(screen, search ? { search } : {});
  }

  function onSearchKeyDown(event: ReactKeyboardEvent<HTMLInputElement>) {
    if (event.key === "ArrowDown") { event.preventDefault(); setSelected((value) => filtered.length ? (value + 1) % filtered.length : 0); }
    if (event.key === "ArrowUp") { event.preventDefault(); setSelected((value) => filtered.length ? (value - 1 + filtered.length) % filtered.length : 0); }
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    if (query.trim()) go("risk", query.trim());
  }

  return <div className="modal-layer command-layer" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}><div className="command-palette" role="dialog" aria-modal="true" aria-label="Quick find"><div className="command-search"><span className="command-search-icon" aria-hidden="true">⌕</span><form onSubmit={submit}><input ref={inputRef} value={query} onChange={(event) => { setQuery(event.target.value); setSelected(0); }} onKeyDown={onSearchKeyDown} placeholder="Search entries, references, narrations, or actions" aria-label="Search entries and actions" /><kbd>Esc</kbd></form></div><div className="command-body"><div className="command-section-label">ACTIONS</div>{filtered.map((action, index) => <button className={`command-result ${index === selected ? "is-selected" : ""}`} key={`${action.screen}-${action.label}`} onMouseEnter={() => setSelected(index)} onClick={() => go(action.screen)}><span className="command-result-icon">{action.icon}</span><span><strong>{action.label}</strong><small>{action.detail}</small></span><span className="command-result-arrow">↵</span></button>)}{filtered.length === 0 && <div className="command-empty">No matching action. Press Enter to search the risk queue.</div>}<div className="command-section-label command-section-label-spaced">SEARCH SCOPE</div><div className="command-scope"><StatusBadge tone="indigo">Entry ID</StatusBadge><StatusBadge tone="neutral">Account</StatusBadge><StatusBadge tone="neutral">Narration</StatusBadge><StatusBadge tone="neutral">Reviewer</StatusBadge></div></div><div className="command-footer"><span>↑↓ to navigate</span><span>↵ to open</span><Button variant="quiet" size="sm" onClick={onClose}>Close</Button></div></div></div>;
}
