import { useCallback, useEffect, useState } from "react";

import { get } from "./lib/api";
import { navigate, readRoute, type RouteState, type Screen } from "./lib/navigation";
import type { StatusSummary, User } from "./lib/types";
import { Loading, Message } from "./components/ui";
import Engagement from "./pages/Engagement";
import Population from "./pages/Population";
import Dashboard from "./pages/Dashboard";
import Investigation from "./pages/Investigation";

const screens: Array<{ key: Screen; label: string }> = [
  { key: "engagement", label: "Engagement" },
  { key: "population", label: "Population & Config" },
  { key: "dashboard", label: "Risk Dashboard" },
  { key: "investigation", label: "Investigation" },
];

export default function App() {
  const [route, setRoute] = useState<RouteState>(() => readRoute());
  const [status, setStatus] = useState<StatusSummary | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [revision, setRevision] = useState(0);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    try {
      const [nextStatus, nextUsers] = await Promise.all([
        get<StatusSummary>("/status"),
        get<User[]>("/users"),
      ]);
      setStatus(nextStatus);
      setUsers(nextUsers);
      setRevision((value) => value + 1);
      setError("");
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setInitialLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    const update = () => setRoute(readRoute());
    window.addEventListener("hashchange", update);
    return () => window.removeEventListener("hashchange", update);
  }, []);

  if (initialLoading) {
    return <div className="min-h-screen bg-slate-50 p-8"><Loading label="Opening local engagement…" /></div>;
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-700 bg-slate-900 text-white shadow">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-4 px-4 py-4 sm:px-6">
          <div className="mr-auto">
            <h1 className="text-lg font-bold">Audit Analytics</h1>
            <p className="text-xs text-slate-300">Local-first explainable journal-entry workbench</p>
          </div>
          <span className="rounded-full border border-slate-600 px-3 py-1 text-xs text-slate-300">Loopback lab · no authentication</span>
          {status?.review_set.locked && <span className="rounded-full bg-amber-500 px-3 py-1 text-xs font-bold text-slate-950">Review set locked</span>}
        </div>
        <nav className="mx-auto flex max-w-7xl gap-1 overflow-x-auto px-4 pb-3 sm:px-6" aria-label="Workbench sections">
          {screens.map((item) => (
            <button
              key={item.key}
              onClick={() => navigate(item.key)}
              aria-current={route.screen === item.key ? "page" : undefined}
              className={`whitespace-nowrap rounded-t-lg px-4 py-2 text-sm font-semibold ${route.screen === item.key ? "bg-amber-500 text-slate-950" : "text-slate-200 hover:bg-slate-800"}`}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </header>

      <main className="mx-auto max-w-7xl p-4 sm:p-6">
        {error && <div className="mb-5"><Message kind="error">{error}</Message></div>}
        {!status ? <Message kind="error">The engagement API is unavailable.</Message> : (
          <>
            {route.screen === "engagement" && <Engagement refresh={refresh} revision={revision} />}
            {route.screen === "population" && <Population status={status} users={users} refresh={refresh} revision={revision} />}
            {route.screen === "dashboard" && <Dashboard status={status} users={users} routeParams={route.params} revision={revision} />}
            {route.screen === "investigation" && (
              <Investigation
                exceptionId={Number(route.params.get("exception")) || null}
                status={status}
                users={users}
                refresh={refresh}
                revision={revision}
              />
            )}
          </>
        )}
      </main>

      <footer className="mx-auto max-w-7xl px-6 py-8 text-xs leading-5 text-slate-500">
        Risk scores prioritize human review. They are not findings, fraud determinations, audit conclusions, or opinions. Engagement data remains in the selected local database and optional local Ollama service.
      </footer>
    </div>
  );
}
