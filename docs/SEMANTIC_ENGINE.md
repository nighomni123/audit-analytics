# Semantic Risk Engine — Technical Design

Audience: developer / researcher. Permanent reference, not a build checklist.

## 1. Purpose

Add an optional, reproducible, explainable semantic layer to the local audit analytics pipeline (`audit_analytics`). It must never suppress lexical search (`max(token, cosine)`), never infer fraud, never issue an opinion, and must stay fully local (same-host Ollama only; no external embeddings, no cloud LLM, no vector database). The exact local search path uses the declared NumPy dependency; semantic-risk candidate selection remains bounded and disclosed.

Scope: narration-only embeddings (no account code, label, vendor/preparer identifier, amount, or date leakage); versioned semantic profiles; deterministic clustering; explainable cues; offline label-based evaluation; investigation UI; zero-cue evidence retention.

## 2. Architecture

```
GL import (acknowledged) → analytics.run()
                                ↓ (optional opt-in --semantic-run ID)
                        semantic_profile (run_id, model/dimensions/hash/template)
                                ↓
                        transaction embeddings (narration-only template)
                                ↓
                        profile aggregates (mean vector per kind)
                                ↓
                        deterministic spherical k-means (seed 7)
                                ↓
                        metrics → cues → semantic_results
                                ↓
                        semantic_investigate (read-only, offline evidence)
                                ↓
                        semantic_evaluate (label-based, offline, no promotion)
```

Key invariants (hard):
- **No label leakage.** Embedding template excludes `entry_id`, `account_code`, `vendor`, `preparer`, `entity`, `reference`, `amount`, `date`. Structured fields remain as searchable context but are never embedded.
- **Lexical never suppressed.** Final similarity = `max(token_score, cosine_similarity)`. Semantic only expands candidates.
- **Deterministic clustering.** Seed 7, bounded training (≤512), bounded candidates (≤64), bounded iterations (≤10), capped k (`min(12, max(2, floor(sqrt(n/5))))`).
- **Immutable runs.** Profile/run results are append-only; interruption leaves non-consumable running records and rolls back partial results.
- **Stale-population guard.** Linkage to an analysis requires matching population fingerprint; changed imports reject linkage.
- **Zero-cue retention.** `analysis_signal_results` persists evaluated components even when no cue fires, so investigation never substitutes `null` for an evaluated entry.
- **Approximation disclosure.** Every semantic run records `retrieval.method = deterministic_bounded_candidates`, `exhaustive = false`, candidate/training limits, and deterministic tie-breaking in its summary and linked analysis configuration. Consumers must not present these metrics as population-exhaustive nearest-neighbour results.
- **Exact lexical/vector search.** The ordinary `similar` route batches vectors for one model/dimension and computes exact cosine scores with NumPy; it does not silently switch to ANN. The 100k ceiling is a local performance target measured by `scripts/benchmark_similarity.py`.

## 3. Data model (additive schema only)

New tables (additive, no destructive rewrite of existing `ledger_entries`, `model_runs`, `exceptions`, `reviews`, `audit_log`):

| Table | Primary key | Purpose |
|---|---|---|
| `semantic_runs` | `id` | Run identity, actor/status, population count/hash, config/provenance/summary JSON, failure/limitation note |
| `semantic_profiles` | `(run_id, kind, profile_key)` | Mean/profile vector per kind (`transaction`/`account`/`vendor`/`preparer`/`entity`/`process`), dimensions, BLOB (float32), member count, metadata JSON |
| `semantic_results` | `(run_id, ledger_id)` | Cluster assignment, metrics/cues/evidence JSON, ineligible lines |
| `analysis_signal_results` | `(run_id, ledger_id)` | Zero-cue signal components snapshot (`analysis_snapshot` / `legacy_exception` / `unavailable`) |

Profile kinds: `transaction` = normalized line vector; aggregates = mean over eligible members with date range and representative descriptions; `process` = cluster centroid + representative descriptions + optional token hints.

Storage: float32 byte-order explicit; exact text/template/digest match required for profile-vector reuse; membership derives from transaction metadata + cluster assignments.

## 4. Embedding methodology

- **Transport:** local `Ollama` (`embeddinggemma` default; `nomic-embed-text` fast baseline; `mxbai-embed-large` pilot candidate) via restricted loopback transport. No external proxies, no redirects, no pulls.
- **Digest resolution:** resolve installed local digest before and after embedding; fail closed on unavailable/changed identity; no automatic model pulls or updates.
- **Template:** narration-only (`normalized_line_text`). Exclude account/name/vendor/preparer/reference/amount/date. Include account code / narration / optional COA account name / description / reference / entity only as structured context (not embedded).
- **Batching:** positive batch size validated; consistent-dimensional, non-empty, non-zero, finite vectors checked at shared boundaries.
- **Caching:** unchanged source-text hash → reuse embedded vector; changed text/digest invalidates; no persistent query vectors.

## 5. Metrics and clustering

- Signed cosine `[-1, 1]`; distance = `1 - cosine` in `[0, 2]`; full decision precision preserved.
- Peer rules: exclude self; minimum 5 eligible peers; missing/sparse/zero-norm => null + reason (never treated as normal).
- History: strictly earlier calendar months in this engagement only (not future, not other engagements).
- Scope: comparisons are entity-scoped (`account`/`vendor`/`preparer`/`entity`/`month`); never silently widen sparse populations.
- Metrics: own peer similarity; cross-account similarity + margin; narrative novelty (`1 - max historical cosine`); vendor semantic distance to earlier-month vendor profile; leave-one-out cluster distance.
- Clustering: deterministic spherical k-means; process labels (`Process 01`, etc.) are hints, not authoritative names.

## 6. Evidence aggregation (cues)

Experimental configurable defaults (snapshotted, not promoted):

| Cue | Condition |
|---|---|
| `semantic_account_mismatch` | own ≤ .50, alternate ≥ .75, margin ≥ .25 |
| `semantic_novel_transaction` | historical novelty ≥ .50 |
| `semantic_vendor_shift` | historical vendor distance ≥ .50 |
| `semantic_process_outlier` | eligible similarities all ≤ .50 |
| `semantic_cluster_outlier` | leave-one-out distance ≥ .50, ≥ 5 peers |

Integration with deterministic analytics (`analytics.analyze(..., semantic_run_id=...)`):
- Default deterministic output unchanged; opt-in only.
- Explicit complete population-matching run merges namespaced semantic evidence.
- Deterministic score preserved; add at most ONE 20-point contribution for any semantic cue; cap total 100.
- Correlated signals are not independent votes; components recorded separately.
- Amount/timing/frequency statuses: flagged / not flagged / not applicable; absence of flags is not correctness.

## 7. Investigation (UI + CLI)

CLI:
```
python3 run.py semantic-profile --db audit.db --model embeddinggemma --actor reviewer
python3 run.py semantic-investigate --db audit.db --run ID --ledger-id ID
python3 run.py semantic-evaluate --db ... --run ID --labels ... --actor ...
```

API (read-only GET): `/api/semantic-profile?run=ID`; `/api/semantic-investigation?run=ID&ledger_id=ID`. No computation in GET; validate positive IDs; 400 for invalid; 404 for absent; explicit stale-state notice.

UI (FastAPI + React workbench): sections for Why flagged / Normal peers / Alternative matches / Related population / Other signals / Suggested evidence. Source IDs, dates/counts, provenance, missing-data notes, approximation disclosures. Static evidence suggestions only. Keyboard-accessible labelled controls; loading/error/empty states; no automatic dispositions or graph editor.

Zero-cue entries: investigation shows `semantic_contribution: 0` with `components_source: analysis_snapshot` (not `null`); `other_signals` carries an explicit note when linked-run evidence is unavailable.

## 8. Evaluation and verification

- Synthetic fixtures (`examples/semantic/`) with unique fixture IDs, real ledger joins (`ledger_id`), transaction labels (`expected_related_group`, `expected_process`, `known_risk`, `reviewer_label`). Types: routine repair/fees/payroll; ordinary-amount advisory mismatch; historic vendor shift; novelty/outlier; negatives/missing/sparse histories.
- Offline label-based metrics: macro `precision@10`, `recall@20` (excluding self, with explicit denominator/unlabelled policy); cue false positives on negatives; applicable mismatch precision/recall; cluster purity; run/evaluation timings and Python memory (not Ollama/native memory).
- Fixed-vector tests verify mechanics separately from real-model quality.
- Real Ollama verification is explicitly out of scope for mechanics-only releases; quality/threshold validation deferred until labelled authorised audit populations are available.
- No promotion of evaluation results into audit conclusions.

## 9. Known limitations

- Experimental layer, not validated audit evidence. No statistical validation performed.
- Real-model quality (threshold calibration, false-positive control, temporal stability) requires labelled, authorised audit populations and governance sign-off — deferred.
- The historical 1,000-entry fixed-vector approximation benchmark measured bounded candidate recall of 0.0000/0.0674/0.0997 at 1/5/10. This is candidate-generation loss, not a claim about a live model.
- Ordinary similarity search is a full dense scan. The historical 100,000-entry, 64-dimension synthetic run took 17.29 seconds and approximately 398 MB peak Python memory. No ANN or paging result is implied.
- Ollama was unavailable during the historical benchmark; live model digest, dimensions, latency, cache behaviour, and quality remain unmeasured.
- Cluster labels (`Process 01`, etc.) are hints, not authoritative process names.
- Vendor is the supplied identity string, not a resolved legal entity.
- History is earlier months in the same engagement only.
- No cross-browser or full accessibility audit completed.
- Responsive layout fix (horizontal overflow from inline evidence JSON) applied in session but not fully preserved across `git checkout` restoration; should be reviewed/reapplied if needed.

## 10. Future roadmap (deferred phases)

- **Phase 2 — Investigation and optional local evidence assistant:** typed audit questions over bounded evidence; explicitly invoked small local LLM over bounded retrieval only; schema-validated observations with citations; human acceptance required; automatic conclusions prohibited.
- **Phase 3 — Calibrated multi-detector aggregation:** numerical + semantic feature models only with measured benefit; compare isolation-style detector against a few justified alternatives (not a full model zoo); calibrate correlation, drift, approval, runtime; replace clustering/sampling only when measured limitations justify it.
- **Phase 4 — Governed feedback and scale:** sufficient authorised labels may support small supervised risk-pattern models, model comparison, controlled promotion/rollback; indexed retrieval, vector deduplication, entity/process resolution only on measured demand. Local processing, ownership, immutable provenance, explainability, and human judgement remain release gates.

See `IMPLEMENTATION_PLAN.md` §8 for delivered/deferred release notes.
