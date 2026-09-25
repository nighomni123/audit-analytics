import { useCallback, useEffect, useState, type ReactNode } from "react";

import CommandPalette from "./components/CommandPalette";
import Shell from "./components/Shell";
import { ErrorState, Loading } from "./components/ui";
import { get } from "./lib/api";
import { readRoute, type RouteState } from "./lib/navigation";
import type { StatusSummary, User } from "./lib/types";
import Activity from "./pages/Activity";
import Analysis from "./pages/Analysis";
import Engagement from "./pages/Engagement";
import Home from "./pages/Home";
import Investigation from "./pages/Investigation";
import Methodology from "./pages/Methodology";
import Overview from "./pages/Overview";
import Population from "./pages/Population";
import RiskReview from "./pages/RiskReview";
import Sample from "./pages/Sample";
import Workpapers from "./pages/Workpapers";

export default function App() {
  const [route, setRoute] = useState<RouteState>(() => readRoute());
  const [status, setStatus] = useState<StatusSummary | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [revision, setRevision] = useState(0);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState("");
  const [commandOpen, setCommandOpen] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const [nextStatus, nextUsers] = await Promise.all([get<StatusSummary>("/status"), get<User[]>("/users")]);
      setStatus(nextStatus); setUsers(nextUsers); setRevision((value) => value + 1); setError("");
    } catch (cause) { setError(cause instanceof Error ? cause.message : "The local engagement service is unavailable."); }
    finally { setInitialLoading(false); }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);
  useEffect(() => { const update = () => setRoute(readRoute()); window.addEventListener("hashchange", update); return () => window.removeEventListener("hashchange", update); }, []);
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => { if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") { event.preventDefault(); setCommandOpen(true); } };
    window.addEventListener("keydown", onKeyDown); return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  if (initialLoading) return <div className="app-loading"><div className="brand-mark">AA</div><Loading label="Opening your local audit workbench…" /></div>;
  if (!status) return <div className="app-loading"><ErrorState title="Local service unavailable" description={error || "The engagement API did not respond."} onRetry={() => void refresh()} /></div>;

  const hasEngagement = Boolean(status.engagement && Object.keys(status.engagement).length > 0);
  const screen = route.screen === "audit-trail" ? "activity" : route.screen;
  if (!hasEngagement) {
    const launchContent = screen === "engagement" ? <Engagement refresh={refresh} /> : <Home status={status} refresh={refresh} />;
    return <>{launchContent}{commandOpen && <CommandPalette status={status} onClose={() => setCommandOpen(false)} />}</>;
  }

  let content: ReactNode;
  if (screen === "engagement") content = <Overview status={status} refresh={refresh} />;
  else if (screen === "population") content = <Population status={status} users={users} refresh={refresh} revision={revision} />;
  else if (screen === "methodology") content = <Methodology status={status} users={users} refresh={refresh} revision={revision} />;
  else if (screen === "analysis") content = <Analysis status={status} users={users} refresh={refresh} revision={revision} />;
  else if (screen === "risk" || screen === "dashboard") content = <RiskReview status={status} users={users} routeParams={route.params} revision={revision} />;
  else if (screen === "investigation") content = <Investigation exceptionId={Number(route.params.get("exception")) || null} status={status} users={users} refresh={refresh} revision={revision} routeParams={route.params} />;
  else if (screen === "sample") content = <Sample status={status} users={users} refresh={refresh} revision={revision} />;
  else if (screen === "workpapers") content = <Workpapers status={status} users={users} refresh={refresh} />;
  else if (screen === "activity") content = <Activity status={status} refresh={refresh} />;
  else content = <Overview status={status} refresh={refresh} />;

  return <><Shell route={route.screen} status={status} onCommand={() => setCommandOpen(true)}>{content}</Shell>{commandOpen && <CommandPalette status={status} onClose={() => setCommandOpen(false)} />}</>;
}
