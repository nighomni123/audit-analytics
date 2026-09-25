import { useEffect, useState, type ReactNode } from "react";

import { navigate, type Screen } from "../lib/navigation";
import { initials, nextAction, workflowStages } from "../lib/workflow";
import type { StatusSummary } from "../lib/types";
import { Button, Panel, ProgressBar, StatusBadge } from "./ui";

interface ShellProps {
  route: Screen;
  status: StatusSummary;
  children: ReactNode;
  onCommand: () => void;
}

const groups: Array<{ label: string; items: Array<{ screen: Screen; label: string; number?: string }> }> = [
  {
    label: "WORKSPACE",
    items: [
      { screen: "engagement", label: "Engagement", number: "1" },
      { screen: "population", label: "Population", number: "2" },
      { screen: "methodology", label: "Audit setup", number: "3" },
      { screen: "analysis", label: "Analysis", number: "4" },
    ],
  },
  {
    label: "REVIEW",
    items: [
      { screen: "risk", label: "Risk cues", number: "5" },
      { screen: "sample", label: "Testing sample", number: "6" },
    ],
  },
  {
    label: "FINALIZE",
    items: [{ screen: "workpapers", label: "Workpapers", number: "7" }],
  },
];

function activeScreen(route: Screen): Screen {
  if (route === "dashboard") return "risk";
  if (route === "investigation") return "risk";
  if (route === "audit-trail") return "activity";
  return route;
}

export default function Shell({ route, status, children, onCommand }: ShellProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [checklistOpen, setChecklistOpen] = useState(false);
  const [environmentOpen, setEnvironmentOpen] = useState(false);
  const current = activeScreen(route);
  const stages = workflowStages(status);
  const complete = stages.filter((stage) => stage.state === "complete").length;
  const progress = Math.round((complete / stages.length) * 100);
  const action = nextAction(status);
  const engagement = status.engagement;

  useEffect(() => {
    setMobileOpen(false);
  }, [route]);

  return (
    <div className="app-frame">
      <button className={`mobile-scrim ${mobileOpen ? "is-visible" : ""}`} aria-label="Close navigation" onClick={() => setMobileOpen(false)} />
      <aside className={`sidebar ${mobileOpen ? "is-open" : ""}`}>
        <div className="brand-lockup">
          <div className="brand-mark" aria-hidden="true">AA</div>
          <div>
            <div className="brand-name">AUDIT ANALYTICS</div>
            <div className="brand-subtitle">Audit workbench</div>
          </div>
        </div>
        {engagement && <div className="engagement-switcher"><div className="engagement-avatar">{initials(engagement.client)}</div><div className="engagement-switcher-copy"><strong>{engagement.client}</strong><span>{engagement.period_start} — {engagement.period_end}</span></div><span className="engagement-caret" aria-hidden="true">⌄</span></div>}
        <nav className="sidebar-nav" aria-label="Engagement workflow">
          {groups.map((group) => <div className="nav-group" key={group.label}><div className="nav-group-label">{group.label}</div>{group.items.map((item) => { const stage = stages.find((entry) => entry.screen === item.screen); return <button key={item.screen} className={`nav-item ${current === item.screen ? "is-active" : ""}`} onClick={() => navigate(item.screen)} aria-current={current === item.screen ? "page" : undefined}><span className="nav-number">{item.number ?? "·"}</span><span>{item.label}</span>{stage && <span className={`nav-state nav-state-${stage.state}`} aria-label={stage.state}>{stage.state === "complete" ? "✓" : stage.state === "blocked" ? "!" : stage.state === "current" ? "●" : "○"}</span>}</button>; })}</div>)}
          <div className="nav-group nav-group-secondary"><button className={`nav-item ${current === "activity" ? "is-active" : ""}`} onClick={() => navigate("activity")} aria-current={current === "activity" ? "page" : undefined}><span className="nav-number">·</span><span>Audit trail</span></button><button className="nav-item" onClick={() => setEnvironmentOpen(true)}><span className="nav-number">·</span><span>About this environment</span></button></div>
        </nav>
        <div className="sidebar-footer"><div className="local-badge"><span className="status-dot" />LOCAL ENGAGEMENT</div><p>Data stays on this computer.</p></div>
      </aside>

      <div className="main-frame">
        <header className="topbar">
          <div className="topbar-left"><Button className="mobile-menu-button" variant="quiet" size="sm" aria-label="Open navigation" onClick={() => setMobileOpen(true)}>☰</Button><div className="breadcrumb"><span>Audit Analytics</span><span className="breadcrumb-slash">/</span><strong>{engagement?.client ?? "New engagement"}</strong></div></div>
          <div className="topbar-actions"><button className="command-trigger" onClick={onCommand}><span className="command-symbol">⌘</span><span>Quick find</span><kbd>Ctrl K</kbd></button><button className="status-trigger" onClick={() => setChecklistOpen((value) => !value)}><span className={`status-trigger-dot ${status.review_set.locked ? "is-locked" : ""}`} />{status.review_set.locked ? "REVIEW SET LOCKED" : status.entries ? "REVIEW IN PROGRESS" : "SETUP IN PROGRESS"}<span aria-hidden="true">⌄</span></button></div>
          {checklistOpen && <div className="completion-popover"><div className="popover-heading"><div><div className="eyebrow">ENGAGEMENT STATUS</div><h2>{complete} of {stages.length} stages complete</h2></div><button className="icon-button" aria-label="Close completion checklist" onClick={() => setChecklistOpen(false)}>×</button></div><ProgressBar value={progress} /><div className="completion-list">{stages.map((stage) => <button key={stage.key} className="completion-row" onClick={() => { navigate(stage.screen); setChecklistOpen(false); }}><span className={`completion-icon completion-${stage.state}`}>{stage.state === "complete" ? "✓" : stage.state === "blocked" ? "!" : stage.state === "current" ? "●" : "○"}</span><span><strong>{stage.label}</strong><small>{stage.detail}</small></span><span className="completion-arrow">›</span></button>)}</div><div className="next-action-mini"><span>{action.eyebrow}</span><strong>{action.title}</strong><Button size="sm" variant="primary" onClick={() => { navigate(action.screen); setChecklistOpen(false); }}>{action.cta}</Button></div></div>}
        </header>
        <main className="content-area">{children}</main>
        <footer className="app-footer"><span><strong>LOCAL ENGAGEMENT</strong> · DATA STAYS ON THIS COMPUTER</span><span>Risk cues prioritize human review; they are not findings or audit conclusions.</span></footer>
      </div>

      {environmentOpen && <div className="modal-layer" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setEnvironmentOpen(false); }}><Panel className="environment-modal"><div className="modal-heading"><div><div className="eyebrow">ENVIRONMENT</div><h2>About this engagement</h2></div><button className="icon-button" aria-label="Close environment details" onClick={() => setEnvironmentOpen(false)}>×</button></div><div className="environment-list"><div><strong>Local engagement database</strong><p>The selected engagement database and preserved evidence stay in the local workspace opened for this session.</p></div><div><strong>Optional semantic context</strong><p>Semantic features use a local model when available. They augment review context and never replace the deterministic path.</p></div><div><strong>No cloud AI required</strong><p>Core analysis works without a network service or cloud model. This interface does not claim security beyond the controls of the local host.</p></div></div><div className="modal-footer"><StatusBadge tone="success" dot>Local-first workflow</StatusBadge><Button variant="primary" onClick={() => setEnvironmentOpen(false)}>Done</Button></div></Panel></div>}
    </div>
  );
}
