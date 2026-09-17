# Semantic Risk Engine v1 — Build Plan

## Objective and guardrails
Extend the local audit evidence layer with reproducible semantic profiles, explainable anomaly cues, and transaction investigation. Preserve deterministic analytics, human review, engagement isolation, lexical search, and the standard-library-only deployment. Phase 1 adds no LLM, automatic audit conclusions, downloads, cloud service, vector database, or Python dependencies. Later phases below are roadmap only.

Approved implementation order: write this plan first; implement Phase 1; verify and document observed limitations. Leave unrelated untracked `data/` and `.monid-xdg/` untouched.

## Repository findings
- `semantic.py` has local Ollama transport, tokens, cosine, and mutable retrieval embeddings; account context in search vectors would leak posting labels into mismatch detection.
- `ledger_entries.id` identifies a line; `entry_id` may repeat. New joins use ledger IDs.
- Vendor has no canonical field. Entity already aliases cost centre/branch; these are not independently available dimensions.
- Reuse model_runs/exceptions/reviews/sampling/exports for opt-in analytical output. Profile runs stay separate so they cannot become default sampling runs.
- Registry validation is recorded metadata, not proof. Existing semantic/HTTP coverage is thin.
- COA header normalization removes underscores but lookup uses underscores: fix shared importer before relying on labels.

## Phase 1A — Data, representations and provenance
### Import
Add nullable vendor via additive migration. Alias vendor/vendor_name/supplier/supplier_name; support explicit mapping, preview and demo connector. Keep identifiers as strings. Existing rows retain missing vendor; never infer from narration or silently rewrite raw historic records. Group identities trim/collapse whitespace and casefold, preserving display values. Correct COA canonical header lookup.

### Representations
Retain contextual lexical/semantic search. New risk engine embeds a versioned narration-only template: exclude account/name, vendor/preparer identifiers, reference, amount and date to avoid label leakage. Keep those fields as structured context.
- Transaction: normalized line vector.
- Account/vendor/preparer/entity: normalized mean vector, member count, date range.
- Process: cluster centroid, representative descriptions and optional explicitly heuristic token-class hints.
- Empty narration is ineligible with reason; never call a zero/lexical vector semantic evidence.
Reuse LocalEmbedder/token/cosine/array helpers. Validate positive batch size, finite nonempty consistent-dimensional nonzero vectors at shared boundaries.

### Minimal schema
1. semantic_runs: ID, timestamps, actor/status, population count/hash, configuration/provenance/summary JSON, failure/limitation note.
2. semantic_profiles: primary key (run_id, kind, profile_key), optional ledger_id, dimensions/vector BLOB/member count/metadata JSON. Kinds transaction/account/vendor/preparer/entity/process. Transaction metadata includes source text hash, template, identity snapshot; aggregate metadata includes dates/representatives.
3. semantic_results: primary key (run_id, ledger_id), nullable cluster ID, metrics/cues/evidence JSON, including ineligible lines.
Use foreign keys/indexes and explicit float32 byte order. Snapshot vectors per run; reuse completed profile vectors only for exact text/template/immutable digest matches. Membership derives from transaction metadata and result cluster assignments. Storage deduplication is deferred.

### Lifecycle and provenance
Resolve installed local Ollama digest before and after embedding; fail closed on unavailable/changed immutable identity. No pulls. Restrict loopback transport, bypass external proxies, reject redirects. Record model/digest/runtime metadata/dimensions/template/engine/serialization/configuration/seed/thresholds/input hashes/population fingerprint/exact registry snapshot. Missing registration is unregistered, never automatically validated.
Commit running record, transactionally publish complete profiles/results, roll back partial results and mark failed on errors. Recheck source fingerprint before publication. Incomplete runs cannot feed analytics; interruption leaves non-consumable running records.

## Phase 1B — Metrics and process discovery
Signed cosine [-1,1]; distance = 1-cosine [0,2]. Keep full decision precision.
- Current peers exclude self; minimum 5 eligible peers.
- History means strictly earlier calendar months in this engagement only.
- Account/vendor/preparer comparisons are entity scoped; do not silently widen sparse populations.
- Missing identity, sparse/zero-norm groups/history => null plus reason, not normal.
Metrics: own account peer_similarity/account_semantic_distance; vendor/preparer/entity/month peer similarities; best eligible cross_account_similarity plus margin/support; narrative_novelty = 1-max historical account cosine; vendor_semantic_distance to earlier-month vendor profile; leave-one-out cluster_distance.
Deterministic spherical k-means seed 7, default k=min(12,max(2,floor(sqrt(n/5)))) capped by distinct vectors, max 10 iterations, hash-selected training sample <=512, assign all. Handle identical/tiny/empty/tied clusters deterministically. Label Process 01 etc., not authoritative process names.
No all-pairs matrices. Stream group sums; bounded deterministic candidate pool <=64 per comparison with pool IDs/population count/approximation disclosure. Representatives <=5; related lists <=25. Mark ceilings with ponytail comments and benchmark before claiming scale.

## Phase 1C — Evidence aggregation
Experimental configurable defaults (validated types/ranges, all snapshotted):
| Cue | Condition |
|---|---|
| semantic_account_mismatch | own <=.50, alternate >=.75, margin >=.25 |
| semantic_novel_transaction | historical novelty >=.50 |
| semantic_vendor_shift | historical vendor distance >=.50 |
| semantic_process_outlier | eligible account/vendor/preparer similarities all <=.50 |
| semantic_cluster_outlier | leave-one-out cluster distance >=.50, >=5 peers |
Persist formulas/values/thresholds/comparison basis/counts/source examples/limitations.
Extend analyze(..., semantic_run_id=None), CLI --semantic-run ID. Default deterministic output unchanged. Explicit complete population-matching run merges namespaced semantic evidence; preserve deterministic score and add only ONE 20-point contribution for any semantic cue, cap total 100 (correlated signals are not independent votes). Record score components and deterministic/semantic reasons separately. Amount/timing/frequency statuses flagged/not flagged/not applicable; absence of flags is not correctness. Snapshot semantic reference/registry metadata in model run. Reject stale population linkage. Existing reviews/materiality/sampling remain. Include semantic provenance in export manifests/report limitations.

## Phase 1D — Laboratory and investigation
CLI:
```
python3 run.py semantic-profile --db audit.db --model embeddinggemma --actor reviewer
python3 run.py semantic-investigate --db audit.db --run ID --ledger-id ID
python3 run.py analyze --db audit.db --actor reviewer --semantic-run ID
```
Profile supports --batch-size and --config JSON file. Require existing analysis-role set, nonempty acknowledged population. Output JSON: identity, model/dimensions, eligibility/coverage/missing fields, clusters, ranked cues, novelty, time/limitations. Investigation reads immutable evidence offline.
API read-only GET /api/semantic-profile?run=ID (latest completed default), /api/semantic-investigation?run=ID&ledger_id=ID. Validate positive IDs, invalid 400/absent 404; no computation in GET; explicit stale state. Add optional analysis-run filter to /api/exceptions preserving omitted-filter behavior.
Extend existing server.py inline review page (not DSH GUI): semantic summary/run selection, Investigate button, Why flagged / Normal peers / Alternative matches / Related population / Other signals / Suggested evidence sections. Display source IDs, dates/counts, provenance/missing-data/approximation notes. Static evidence suggestions only. Escape ledger text, keyboard-accessible labelled controls, loading/error/empty states. No automatic dispositions or graph editor.

## Phase 1E — Evaluation and verification
Synthetic ledger/COA/labels under examples/semantic with transaction_id, expected_related_group, expected_process, known_risk, reviewer_label. Unique fixture IDs; real joins ledger_id. Routine repair/fees/payroll, ordinary-amount advisory mismatch, historic vendor shift, novelty/outlier, negatives/missing/sparse histories.
semantic-evaluate --db ... --run ID --labels ... --actor ... emits report with label hash/audit log, never promotes validation. Macro precision@10/recall@20 excluding self with explicit denominator/unlabelled policy; cue false positives on negatives; applicable mismatch precision/recall; cluster purity; run/evaluation timings and peak Python allocations (not Ollama/native memory). Comparable digest/config-keyed reports for optional installed models, no auto installs. Fixed vectors test mechanics separately from real-model quality.
Acceptance checks:
1. Repeatable old/new DB migration preserves data/reviews/cache.
2. Vendor mapping/connector and COA canonical/alias labels.
3. Reject malformed/mixed/nonfinite/zero vectors; failures cannot publish partial runs.
4. Exact cache reuse; changed text/digest invalidates; population/COA changes reject linkage; old evidence stable.
5. No self/future leakage; missing/sparse => inapplicable.
6. Fixed-vector metrics/cues/clusters/rankings deterministic and traceable.
7. Default analyze unchanged; opt-in capped semantic contribution, preserved evidence/materiality.
8. Evaluation formulas/negatives/planted cases; no audit validation claim.
9. CLI and actual HTTP responses (not only route strings), invalid/missing/stale/offline/escaping.
10. Full unittest regression plus temp-DB import→acknowledge→profile→analyze→investigate→export. Measure actual runtime/memory; explicitly disclose absent real Ollama verification.
11. Rendered page inspection if browser tooling available; otherwise visual verification explicitly outstanding. No persistent replacement server.

## Phase 2 — Investigation and optional local evidence assistant (deferred)
Typed audit questions combine retrieval and deterministic filters. Expand seed investigations by vendor/preparer/account/entity/cluster/history. Only then an explicitly invoked small local LLM over bounded evidence returning schema-validated observations/possible explanations/evidence requests/follow-ups with citations. Treat ledger text as untrusted, require human acceptance, prohibit automatic conclusions/dispositions. Gate on hallucination/citation/injection/offline tests.

## Phase 3 — Calibrated multi-detector aggregation (deferred)
Authorised labels and temporal holdouts evaluate semantic/statistical disagreement. Add numerical+semantic feature models only with demonstrated benefit; compare existing isolation-style detector against few justified alternatives, not an entire model zoo. Calibrate correlated signals/drift/approval/workstation runtime. Replace sampling/clustering only when measured limitations justify it.

## Phase 4 — Governed feedback and scale (deferred)
Sufficient authorised labels may support small supervised risk-pattern models, model comparison, controlled promotion/rollback. Indexed retrieval, vector deduplication, entity/process resolution only on measured demand. Local processing, ownership, immutable provenance, explainability and human judgement remain release gates.

## Assumptions
Experimental laboratory, not production validation. Transaction = ledger line; journal aggregation deferred. History = earlier months in same engagement. Vendor is supplied identity, not resolved legal entity. Cluster labels are hints. Thresholds/sampling require evaluation, not benchmark faith. Existing search stays available; no new model required.

## Implementation checklist
- [x] Inspect schema, analytics, semantic infrastructure, registry, server, imports and tests; approve plan.
- [x] Save complete build roadmap before coding.
- [x] Phase 1A import/schema.
- [x] Phase 1A representations/provenance/lifecycle.
- [x] Phase 1B metrics/clustering.
- [x] Phase 1C integration.
- [x] Phase 1D CLI/API/UI.
- [x] Phase 1E fixtures/evaluation/tests.
- [x] Regression/E2E/docs and limitations.

## Verification record (2026-09-16)
- Suite: `PYTHONPATH=src python3 -m pytest tests/ -q` → 25 passed (15 pre-existing regression, 10 new semantic tests).
- E2E: fixture import → acknowledge → semantic-profile → semantic-investigate → analyze (baseline + opt-in) → semantic-evaluate → export → live HTTP checks (profile/investigation/queue filter/400/404/stale) in `tests/test_semantic_integration.py`.
- JavaScript syntax checked with `node --check`; rendered-browser inspection NOT performed (no browser tooling available) — visual verification outstanding.
- Real Ollama verification NOT performed; mechanics use fixed mock vectors only. Thresholds/quality unvalidated.
- 600-entry benchmark: homogeneous 0.06 s; diverse ~23.5 s (~6.5 MB Python peak), dominated by tracemalloc accounting. Approximate ceilings (≤64 candidate neighbours, ≤512 training vectors, ≤10 k-means iterations) remain per design.
