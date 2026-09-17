import { useState, useEffect } from "react";
import { get } from "./lib/api";

export default function App() {
  const [screen, setScreen] = useState<"engagement"|"population"|"dashboard"|"investigation">("engagement");
  const [meta, setMeta] = useState<any>({});
  const [exceptions, setExceptions] = useState<any[]>([]);

  useEffect(() => { get("/status").then((s:any) => setMeta(s)).catch(() => {}); }, []);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <nav className="bg-slate-800 text-white px-6 py-4 flex gap-3 items-center shadow">
        <h1 className="font-bold text-lg mr-4">Audit Analytics</h1>
        {[
          { key: "engagement" as const, label: "Engagement" },
          { key: "population" as const, label: "Population & Config" },
          { key: "dashboard" as const, label: "Risk Dashboard" },
          { key: "investigation" as const, label: "Investigation" },
        ].map(s => (
          <button key={s.key} onClick={() => setScreen(s.key)} className={`px-3 py-1 rounded text-sm ${screen===s.key?"bg-amber-500 text-black font-semibold":"hover:bg-slate-700"}`}>{s.label}</button>
        ))}
      </nav>
      <main className="p-6 max-w-6xl mx-auto">
        {screen === "engagement" && <Engagement />}
        {screen === "population" && <Population meta={meta} />}
        {screen === "dashboard" && <Dashboard exceptions={exceptions} setExceptions={setExceptions} meta={meta} />}
        {screen === "investigation" && <Investigation />}
      </main>
    </div>
  );
}

function Engagement() {
  const [meta, setMeta] = useState<any>({});
  useEffect(() => { get("/engagement").then(setMeta).catch(() => {}); }, []);
  return (
    <section className="bg-white rounded-xl shadow p-8">
      <h2 className="text-2xl font-bold mb-4">Engagement</h2>
      <div className="grid md:grid-cols-3 gap-4">
        <Card label="Client" value={meta.client||"—"} />
        <Card label="Audit period" value={meta.period||"—"} />
        <Card label="Folder" value={meta.folder||"—"} />
      </div>
      <p className="text-sm text-slate-500 mt-4">Select or create an engagement. Import GL, configure parameters, and launch analysis.</p>
    </section>
  );
}

function Card({label, value}: {label:string; value:string}) {
  return <div className="bg-slate-50 rounded-lg p-4 border border-slate-200"><div className="text-xs uppercase tracking-wide text-slate-500">{label}</div><div className="text-lg font-semibold">{value}</div></div>;
}

function Population({meta}: {meta:any}) {
  const [ack, setAck] = useState(false);
  return (
    <section className="bg-white rounded-xl shadow p-8 space-y-6">
      <h2 className="text-2xl font-bold">Population & Configuration</h2>
      <div className="bg-amber-50 border-l-4 border-amber-400 p-4 rounded">
        <strong>Reconciliation</strong> — verify source GL matches imported rows/debits/credits before analysis.
      </div>
      <div className="grid md:grid-cols-3 gap-4">
        <Card label="Source rows" value={meta.source_rows?String(meta.source_rows):"—"} />
        <Card label="Imported rows" value={meta.imported_rows?String(meta.imported_rows):"—"} />
        <Card label="Status" value={meta.population_acknowledged?"Ready":"Attention required"} />
      </div>
      <div className="flex items-center gap-3">
        <button onClick={() => setAck(!ack)} className={`px-4 py-2 rounded text-white text-sm ${ack?"bg-green-600":"bg-amber-500"}`}>{ack?"Acknowledged":"Acknowledge"}</button>
        <span className="text-xs text-slate-500">Audit control: acknowledgement required before analysis.</span>
      </div>
      <h3 className="font-bold mt-4">Audit parameters</h3>
      <div className="grid md:grid-cols-2 gap-4">
        <input className="border rounded p-2 text-sm" placeholder="Materiality (e.g. 500000)" />
        <input className="border rounded p-2 text-sm" placeholder="Performance materiality" />
        <input className="border rounded p-2 text-sm col-span-2" placeholder="Period-end window (days)" />
      </div>
    </section>
  );
}

function Dashboard({exceptions, setExceptions, meta}: {exceptions:any[]; setExceptions:(e:any[])=>void; meta:any}) {
  useEffect(() => { get("/exceptions").then((r:any) => setExceptions(r.rows||[])).catch(() => {}); }, [setExceptions]);
  return (
    <section className="bg-white rounded-xl shadow p-8 space-y-6">
      <h2 className="text-2xl font-bold">Risk Dashboard</h2>
      <div className="grid md:grid-cols-4 gap-4">
        <Card label="Population" value={String(meta.entries||"—")} />
        <Card label="Risk cues" value={String(exceptions.length)} />
        <Card label="High severity" value={String(exceptions.filter((e:any)=>e.severity==="high").length)} />
        <Card label="Selected" value={String(exceptions.filter((e:any)=>e.status==="selected_for_testing").length)} />
      </div>
      <table className="w-full text-sm border-collapse">
        <thead className="bg-slate-100"><tr><th className="text-left p-2">Entry</th><th className="text-left p-2">Severity</th><th className="text-left p-2">Reasons</th><th className="text-left p-2">Disposition</th></tr></thead>
        <tbody>
          {exceptions.slice(0,10).map((e:any) => (
            <tr key={e.id} className="border-t hover:bg-slate-50">
              <td className="p-2">{e.entry_id}</td>
              <td className="p-2"><span className={`inline-block px-2 py-0.5 rounded text-xs font-semibold ${e.severity==="high"?"bg-red-100 text-red-700":"bg-amber-100 text-amber-700"}`}>{e.severity}</span></td>
              <td className="p-2">{Array.isArray(e.reasons)?e.reasons.join(", "):String(e.reasons)}</td>
              <td className="p-2">{e.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

function Investigation() {
  return (
    <section className="bg-white rounded-xl shadow p-8 space-y-6">
      <h2 className="text-2xl font-bold">Investigation & Review</h2>
      <p className="text-sm text-slate-500">Select an exception from the Risk Dashboard to open its investigation workspace.</p>
      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
          <h3 className="font-bold mb-2">Transaction details</h3>
          <div className="text-sm text-slate-700">JE104932 · ₹8,240,000 · Repairs & Maintenance · 31-Mar-2026</div>
        </div>
        <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
          <h3 className="font-bold mb-2">Review</h3>
          <textarea className="w-full border rounded p-2 text-sm" rows={3} placeholder="Audit rationale / evidence requested" />
          <div className="flex gap-2 mt-2">
            {["open","cleared","follow_up","selected_for_testing"].map(d => (<button key={d} className="text-xs px-3 py-1 rounded bg-slate-200 hover:bg-amber-200">{d}</button>))}
          </div>
        </div>
      </div>
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm">
        <strong>Governance reminder:</strong> A risk cue is not an audit finding. Record evidence and professional judgement in the note before saving disposition.
      </div>
    </section>
  );
}
