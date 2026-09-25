export type Disposition = "open" | "cleared" | "follow_up" | "selected_for_testing";
export type Severity = "high" | "medium" | "low";

export interface Engagement {
  id: number;
  client: string;
  period_start: string;
  period_end: string;
  created_at: number;
}

export interface EngagementState {
  engagement: Engagement | null;
  folder: string;
}

export interface User {
  username: string;
  role: "preparer" | "reviewer" | "manager" | "partner" | "quality_reviewer" | "read_only";
}

export interface Reconciliation {
  import_id: number;
  supplied: boolean;
  matches: boolean;
  accepted_rows: number;
  expected_rows: number | null;
  control_debits: number;
  expected_debits: number | null;
  control_credits: number;
  expected_credits: number | null;
  reconciled_at: number | null;
}

export interface ImportRow {
  id: number;
  kind: string;
  original_name: string;
  evidence_path: string;
  sha256: string;
  imported_at?: number;
  accepted_rows: number;
  rejected_rows: number;
  acknowledged_at: number | null;
  acknowledged_by: string | null;
  acknowledgement_note: string | null;
  reconciled_at?: number | null;
  reconciled_by?: string | null;
  reconciliation_note?: string | null;
  expected_rows: number | null;
  expected_debits: number | null;
  expected_credits: number | null;
  reconciliation: Reconciliation | null;
  supersedes_import_id: number | null;
}

export interface ModelRun {
  id: number;
  status: string;
  population_count: number;
  started_at: number;
  completed_at: number | null;
  limitation_note: string | null;
  model_name: string | null;
  validation_status: string | null;
  configuration: Record<string, unknown> | string;
}

export interface ReviewSetState {
  locked: boolean;
  event: "locked" | "reopened" | null;
  actor: string | null;
  reason: string | null;
  changed_at: number | null;
}

export interface ReviewSetEvent extends ReviewSetState {
  id: number;
  created_at: number;
}

export interface SampleSetSummary {
  id: number;
  run_id: number;
  name: string;
  method_json?: string;
  method?: Record<string, unknown>;
  created_at: number;
  created_by: string;
}

export interface StatusSummary {
  engagement: Engagement | null;
  population_acknowledged: boolean;
  imports: ImportRow[];
  entries: number;
  rejected_rows: number;
  latest_run: Partial<ModelRun>;
  exceptions: Record<string, number>;
  review_status: Record<string, number>;
  sample_sets: SampleSetSummary[];
  review_set: ReviewSetState;
  review_set_history: ReviewSetEvent[];
  settings: {
    analysis_policy?: {
      round_amount_threshold?: number;
      period_end_days?: number;
      outlier_robust_z?: number;
    };
    materiality?: {
      overall?: number;
      performance?: number;
    };
    [key: string]: unknown;
  };
}

export interface PreviewResult {
  file: string;
  headers: string[];
  mapping: Record<string, string | null>;
  missing_required: string[];
  sample_rows: Record<string, string>[];
  row_count?: number;
}

export interface ImportResult {
  import_id: number;
  accepted: number;
  rejected: number;
  debits: number;
  credits: number;
  reconciliation?: Reconciliation;
}

export interface ExceptionRow {
  id: number;
  run_id: number;
  ledger_id: number;
  risk_score: number;
  severity: Severity;
  status: Disposition;
  materiality_band: string | null;
  assigned_to: string | null;
  due_date: string | null;
  reasons: string[];
  evidence: Record<string, unknown>;
  entry_id: string;
  posting_date: string;
  document_date?: string | null;
  account_code: string;
  account_name: string | null;
  debit: number;
  credit: number;
  signed_amount: number;
  description: string | null;
  preparer: string | null;
  reference: string | null;
  vendor?: string | null;
  entity: string | null;
  is_manual?: number | null;
  import_id: number;
  source_hash: string;
  source_row: number;
}

export interface ExceptionQueue {
  count: number;
  total: number;
  limit: number;
  offset: number;
  rows: ExceptionRow[];
}

export interface ReviewRecord {
  id: number;
  exception_id: number;
  reviewer: string;
  disposition: Disposition;
  note: string;
  created_at: number;
  second_reviewer: string | null;
  second_note: string | null;
}

export interface ExceptionDetail extends ExceptionRow {
  document_date: string | null;
  vendor: string | null;
  is_manual: number | null;
  import_id: number;
  source_record: Record<string, unknown>;
  reviews: ReviewRecord[];
}

export interface SemanticInvestigation {
  run_id: number;
  ledger_id: number;
  stale: boolean;
  entry: Record<string, unknown>;
  cluster_id: number | null;
  metrics: Record<string, number | null>;
  cues: string[];
  evidence: {
    normal_peers: EvidenceEntry[];
    alternative_matches: EvidenceEntry[];
    related_population: Record<string, { count: number; truncated: boolean; entries: EvidenceEntry[] }>;
    comparisons: Record<string, unknown>;
    suggested_evidence: string[];
    limitations: string[];
  };
  other_signals: Array<Record<string, unknown>>;
  provenance: Record<string, unknown>;
}

export interface EvidenceEntry {
  ledger_id: number;
  similarity: number;
  entry: Record<string, unknown>;
}

export interface SimilarResult {
  ledger_id: number;
  entry_id: string;
  posting_date: string;
  account_code: string;
  account_name: string | null;
  signed_amount: number;
  description: string | null;
  token_score: number;
  semantic_score: number | null;
  score: number;
  shared_tokens: string[];
  token_classes: string[];
}

export interface SampleItem {
  ledger_id: number;
  rationale: string;
  entry_id: string;
  posting_date: string;
  account_code: string;
  account_name: string | null;
  signed_amount: number;
  description: string | null;
  preparer: string | null;
  reference: string | null;
  entity: string | null;
  vendor: string | null;
  is_manual: number | null;
  import_id: number;
  source_row: number;
  source_hash: string;
  exception: {
    id: number;
    run_id: number;
    risk_score: number;
    severity: Severity;
    status: Disposition;
    materiality_band: string | null;
    assigned_to: string | null;
    due_date: string | null;
    reasons: string[];
    evidence: Record<string, unknown>;
  } | null;
}

export interface SampleSetDetail {
  id: number;
  run_id: number;
  name: string;
  method: Record<string, unknown>;
  created_at: number;
  created_by: string;
  item_count: number;
  selected_count: number;
  items: SampleItem[];
  items_truncated: boolean;
}

export interface AuditLogEntry {
  id: number;
  created_at: number;
  actor: string;
  action: string;
  target_type: string;
  target_id: string;
  detail: Record<string, unknown>;
}

export interface AuditLogPage {
  rows: AuditLogEntry[];
  limit: number;
  offset: number;
}
