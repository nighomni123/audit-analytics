import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode, SelectHTMLAttributes, TextareaHTMLAttributes } from "react";

export function Button({
  variant = "secondary",
  size = "md",
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "quiet" | "danger" | "success";
  size?: "sm" | "md" | "lg";
}) {
  return <button className={`button button-${variant} button-${size} ${className}`} {...props} />;
}

export function Panel({
  children,
  className = "",
  as: Element = "section",
}: {
  children: ReactNode;
  className?: string;
  as?: "section" | "div" | "article" | "aside";
}) {
  return <Element className={`panel ${className}`}>{children}</Element>;
}

export function PageHeader({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="page-header">
      <div className="page-heading-copy">
        {eyebrow && <div className="eyebrow">{eyebrow}</div>}
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {action && <div className="page-header-action">{action}</div>}
    </div>
  );
}

export function StatusBadge({
  children,
  tone = "neutral",
  dot = false,
}: {
  children: ReactNode;
  tone?: "neutral" | "success" | "warning" | "danger" | "indigo" | "slate";
  dot?: boolean;
}) {
  return <span className={`status-badge status-${tone}`}>{dot && <span className="status-dot" aria-hidden="true" />}{children}</span>;
}

export function SeverityBadge({ severity }: { severity: "high" | "medium" | "low" }) {
  const tone = severity === "high" ? "danger" : severity === "medium" ? "warning" : "slate";
  return <StatusBadge tone={tone} dot>{severity} priority</StatusBadge>;
}

export function ProgressBar({ value, label }: { value: number; label?: string }) {
  const safe = Math.max(0, Math.min(100, value));
  return (
    <div className="progress-wrap">
      {label && <div className="progress-label"><span>{label}</span><strong>{Math.round(safe)}%</strong></div>}
      <div className="progress-track" role="progressbar" aria-valuenow={safe} aria-valuemin={0} aria-valuemax={100} aria-label={label ?? "Progress"}>
        <span style={{ width: `${safe}%` }} />
      </div>
    </div>
  );
}

export function Metric({ label, value, detail, tone = "neutral" }: { label: string; value: ReactNode; detail?: string; tone?: "neutral" | "indigo" | "amber" | "green" }) {
  return (
    <div className={`metric metric-${tone}`}>
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      {detail && <div className="metric-detail">{detail}</div>}
    </div>
  );
}

export function Card({ label, value }: { label: string; value: ReactNode }) {
  return <Metric label={label} value={value} />;
}

export function Message({
  kind,
  children,
  action,
}: {
  kind: "error" | "success" | "info" | "warning";
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className={`message message-${kind}`} role={kind === "error" ? "alert" : "status"}>
      <div className="message-copy"><span className="message-mark" aria-hidden="true">{kind === "error" ? "!" : kind === "success" ? "✓" : kind === "warning" ? "!" : "i"}</span><span>{children}</span></div>
      {action}
    </div>
  );
}

export function Loading({ label = "Loading…" }: { label?: string }) {
  return <div className="loading-state" role="status"><span className="spinner" aria-hidden="true" />{label}</div>;
}

export function EmptyState({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return <div className="empty-state"><div className="empty-icon" aria-hidden="true">—</div><h3>{title}</h3><p>{description}</p>{action}</div>;
}

export function ErrorState({ title = "Something needs attention", description, onRetry }: { title?: string; description: string; onRetry?: () => void }) {
  return <div className="error-state"><div className="empty-icon" aria-hidden="true">!</div><h3>{title}</h3><p>{description}</p>{onRetry && <Button onClick={onRetry}>Try again</Button>}</div>;
}

export function Field({ label, hint, error, children, className = "" }: { label: string; hint?: string; error?: string; children: ReactNode; className?: string }) {
  return <label className={`field ${className}`}><span className="field-label">{label}</span>{children}{hint && <span className="field-hint">{hint}</span>}{error && <span className="field-error">{error}</span>}</label>;
}

export function TextInput(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input className={`input ${props.className ?? ""}`} {...props} />;
}

export function Select(props: SelectHTMLAttributes<HTMLSelectElement>) {
  return <select className={`input select ${props.className ?? ""}`} {...props} />;
}

export function TextArea(props: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className={`input textarea ${props.className ?? ""}`} {...props} />;
}

export function Checkbox({ label, ...props }: InputHTMLAttributes<HTMLInputElement> & { label: ReactNode }) {
  return <label className="checkbox-row"><input type="checkbox" {...props} /><span>{label}</span></label>;
}

export function Disclosure({ summary, children, defaultOpen = false }: { summary: string; children: ReactNode; defaultOpen?: boolean }) {
  return <details className="disclosure" open={defaultOpen}><summary>{summary}<span className="disclosure-chevron" aria-hidden="true">⌄</span></summary><div className="disclosure-body">{children}</div></details>;
}

export function TechnicalDetails({ value, label = "Technical details" }: { value: unknown; label?: string }) {
  return <Disclosure summary={label}><pre className="technical-json">{JSON.stringify(value, null, 2)}</pre></Disclosure>;
}

export function formatMoney(value: number, compact = false): string {
  if (compact) {
    const absolute = Math.abs(value);
    if (absolute >= 10000000) return `₹${(value / 10000000).toFixed(2)} Cr`;
    if (absolute >= 100000) return `₹${(value / 100000).toFixed(2)} L`;
  }
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 2 }).format(value);
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-IN").format(value);
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en-IN", { dateStyle: "medium" }).format(new Date(`${value}T00:00:00`));
}

export function formatDateTime(value: number | null | undefined): string {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en-IN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value * 1000));
}

export function titleCase(value: string): string {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}
