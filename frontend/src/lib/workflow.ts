import type { ModelRun, StatusSummary } from "./types";

export type StageState = "complete" | "current" | "not_started" | "blocked";

export interface WorkflowStage {
  key: string;
  label: string;
  detail: string;
  state: StageState;
  screen: "engagement" | "population" | "methodology" | "analysis" | "risk" | "sample" | "workpapers";
}

export interface NextAction {
  eyebrow: string;
  title: string;
  description: string;
  cta: string;
  screen: WorkflowStage["screen"];
  tone: "indigo" | "amber" | "green";
}

export function parseRunConfiguration(run: Partial<ModelRun> | undefined): Record<string, unknown> {
  const value = run?.configuration;
  if (!value) return {};
  if (typeof value === "object") return value;
  try {
    const parsed: unknown = JSON.parse(value);
    return parsed && typeof parsed === "object" ? (parsed as Record<string, unknown>) : {};
  } catch {
    return {};
  }
}

export function humanize(value: string): string {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function humanizeReason(value: string): string {
  const labels: Record<string, string> = {
    round_amount: "Round amount",
    robust_account_peer_outlier: "Account peer outlier",
    rare_account_preparer_pair: "Rare account / preparer pair",
    period_end: "Period-end posting",
    weekend_posting: "Weekend posting",
    reversal_candidate: "Possible reversal",
    repeated_pattern: "Repeated pattern",
    frequency: "Repeated activity",
    semantic_account_mismatch: "Semantic account context mismatch",
    semantic_vendor_shift: "Semantic vendor shift",
    semantic_novel_transaction: "Narrative novelty",
  };
  return labels[value] ?? humanize(value);
}

export function workflowStages(status: StatusSummary): WorkflowStage[] {
  const hasLedger = status.entries > 0 || status.imports.some((item) => item.kind === "gl");
  const pendingPopulation = status.imports.some((item) => item.kind === "gl" && item.acknowledged_at === null);
  const hasMethodology = Boolean(status.settings.materiality?.overall || status.settings.materiality?.performance);
  const hasRun = Boolean(status.latest_run.id && status.latest_run.status === "complete");
  const openReviews = status.exceptions && Object.keys(status.exceptions).length > 0
    ? Object.entries(status.exceptions).reduce((total, [, count]) => total + count, 0)
    : 0;
  const hasSample = (status.sample_sets?.length ?? 0) > 0;
  const locked = status.review_set.locked;

  const state = (complete: boolean, current: boolean, blocked = false): StageState =>
    complete ? "complete" : blocked ? "blocked" : current ? "current" : "not_started";

  return [
    {
      key: "engagement",
      label: "Engagement",
      detail: status.engagement?.client ?? "Create the engagement workspace",
      state: state(Boolean(status.engagement), !status.engagement),
      screen: "engagement",
    },
    {
      key: "population",
      label: "Population",
      detail: hasLedger ? `${status.entries.toLocaleString("en-IN")} ledger entries` : "Add and reconcile the client ledger",
      state: state(status.population_acknowledged, hasLedger && pendingPopulation, hasLedger && pendingPopulation),
      screen: "population",
    },
    {
      key: "methodology",
      label: "Methodology",
      detail: hasMethodology ? "Planning context recorded" : "Record materiality and review context",
      state: state(hasMethodology, status.population_acknowledged && !hasMethodology),
      screen: "methodology",
    },
    {
      key: "analysis",
      label: "Analysis",
      detail: hasRun ? `Run ${status.latest_run.id} complete` : status.population_acknowledged ? "Ready to run governed analysis" : "Locked until population acknowledgement",
      state: state(hasRun, status.population_acknowledged && !hasRun, !status.population_acknowledged),
      screen: "analysis",
    },
    {
      key: "review",
      label: "Risk cues",
      detail: hasRun ? `${openReviews} cues to review` : "Analysis produces review cues",
      state: state(locked || openReviews === 0, hasRun && !locked && openReviews > 0),
      screen: "risk",
    },
    {
      key: "sample",
      label: "Testing sample",
      detail: hasSample ? "Reproducible selection recorded" : "Build a proposed testing sample",
      state: state(hasSample, locked && !hasSample),
      screen: "sample",
    },
    {
      key: "workpapers",
      label: "Workpapers",
      detail: locked ? "Review set locked · package ready" : "Lock the review set before closeout",
      state: state(locked, hasSample && !locked),
      screen: "workpapers",
    },
  ];
}

export function nextAction(status: StatusSummary): NextAction {
  const glImports = status.imports.filter((item) => item.kind === "gl");
  if (!status.engagement) {
    return {
      eyebrow: "START HERE",
      title: "Create an engagement workspace",
      description: "Name the client and period, then bring the ledger into a local audit file.",
      cta: "Create engagement",
      screen: "engagement",
      tone: "indigo",
    };
  }
  if (!glImports.length) {
    return {
      eyebrow: "NEXT ACTION",
      title: "Add the client's ledger",
      description: "Start with the complete GL export. We will preserve the original file and show the field mapping before import.",
      cta: "Add client ledger",
      screen: "population",
      tone: "indigo",
    };
  }
  if (status.imports.some((item) => item.kind === "gl" && item.acknowledged_at === null)) {
    return {
      eyebrow: "ATTENTION REQUIRED",
      title: "Population reconciliation requires review",
      description: "Compare the imported rows and control totals with the client source before analysis can begin.",
      cta: "Review population",
      screen: "population",
      tone: "amber",
    };
  }
  if (!status.latest_run.id) {
    return {
      eyebrow: "NEXT ACTION",
      title: "Set the audit context and run analysis",
      description: "Record planning materiality, then create a versioned analysis run for this population.",
      cta: "Open audit setup",
      screen: "methodology",
      tone: "indigo",
    };
  }
  const openCues = Object.values(status.exceptions ?? {}).reduce((total, count) => total + count, 0);
  if (openCues > 0 && !status.review_set.locked) {
    return {
      eyebrow: "NEXT ACTION",
      title: `${openCues.toLocaleString("en-IN")} risk cues remain to review`,
      description: "Start with the highest-ranked entries. Evidence and immutable review history stay attached to each investigation.",
      cta: "Review risk cues",
      screen: "risk",
      tone: "indigo",
    };
  }
  if (!(status.sample_sets?.length ?? 0)) {
    return {
      eyebrow: "NEXT ACTION",
      title: "Create your testing sample",
      description: "Combine risk-directed entries with seeded random coverage. The engagement team approves the final sample.",
      cta: "Build testing sample",
      screen: "sample",
      tone: "indigo",
    };
  }
  return {
    eyebrow: "READY TO CLOSE",
    title: "Final workpaper package is ready",
    description: "The review set is locked and the selected testing sample is recorded. Generate the reproducible package for filing.",
    cta: "Open workpapers",
    screen: "workpapers",
    tone: "green",
  };
}

export function formatCompactMoney(value: number): string {
  const absolute = Math.abs(value);
  if (absolute >= 10000000) return `₹${(value / 10000000).toFixed(2)} Cr`;
  if (absolute >= 100000) return `₹${(value / 100000).toFixed(2)} L`;
  if (absolute >= 1000) return `₹${(value / 1000).toFixed(1)}K`;
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value);
}

export function formatTimestamp(value: number | null | undefined): string {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en-IN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value * 1000));
}

export function initials(value: string): string {
  return value
    .split(/[\s._-]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");
}
