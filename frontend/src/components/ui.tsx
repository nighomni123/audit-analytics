import type { ReactNode } from "react";

export function Card({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
      <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 break-words text-lg font-semibold text-slate-900">{value}</div>
    </div>
  );
}

export function PageHeader({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return (
    <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <h2 className="text-2xl font-bold text-slate-950">{title}</h2>
        <p className="mt-1 max-w-3xl text-sm text-slate-600">{description}</p>
      </div>
      {action}
    </div>
  );
}

export function Message({ kind, children }: { kind: "error" | "success" | "info" | "warning"; children: ReactNode }) {
  const styles = {
    error: "border-red-300 bg-red-50 text-red-900",
    success: "border-emerald-300 bg-emerald-50 text-emerald-900",
    info: "border-sky-300 bg-sky-50 text-sky-900",
    warning: "border-amber-300 bg-amber-50 text-amber-950",
  } as const;
  return (
    <div className={`rounded-lg border px-4 py-3 text-sm ${styles[kind]}`} role={kind === "error" ? "alert" : "status"}>
      {children}
    </div>
  );
}

export function Loading({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600" role="status">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-amber-600" />
      {label}
    </div>
  );
}

export function formatMoney(value: number): string {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 2 }).format(value);
}

export function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-IN", { dateStyle: "medium" }).format(new Date(`${value}T00:00:00`));
}
