# Synthetic semantic laboratory

`ledger.csv`, `coa.csv` and `labels.csv` contain invented transactions, not client data. A1 is advisory language posted to Repairs; V1 is a repair vendor with new consulting language. Prior-month peers support the default minimum of five. G1 has missing narration and S1 a missing preparer. N1/O1 are unusual descriptions; cluster cues depend on actual model geometry, not their fixture labels.

Labels use `transaction_id` (display entry ID), optional `ledger_id` to disambiguate repeated IDs, `expected_related_group` as **semicolon-separated related entry IDs**, `expected_process`, `known_risk` and `reviewer_label`. Allowed known_risk: routine, mismatch, vendor_shift, novel, outlier, negative, sparse. Reviewer labels: positive, negative, unlabelled. Positive means reviewed for this synthetic benchmark, not an audit conclusion. Labels may cover a subset of the population. Unknown/ambiguous IDs fail closed against the run snapshot.

Precision@10 divides labelled hits by the number of retrieved candidates (up to 10), not the number of relevant entries. Recall@20 divides hits by eligible listed relevant entries. Self is excluded; ties use ledger ID. Unlabelled candidates remain searchable but are not assumed relevant. Sparse cases with no eligible relevance set do not enter the macro average. Cluster purity excludes missing clusters and ineligible entries. These measures depend on the completeness of the labels.

Tests mock vectors to verify the engine and report mathematics; they do **not** establish embedding-model quality. Real evaluation requires a separately installed, firm-authorised local Ollama model. No automatic model validation/approval occurs. Compare reports only with their model digest, population, labels, template and configuration hashes.

Example (from repository root):

```sh
python3 run.py init --db semantic-demo.db --client Synthetic --period 2025-01-01:2025-12-31
python3 run.py import-gl --db semantic-demo.db --file examples/semantic/ledger.csv
python3 run.py import-coa --db semantic-demo.db --file examples/semantic/coa.csv
# Demo-only override: deliberately no external source controls for this invented fixture.
python3 run.py acknowledge-population --db semantic-demo.db --reviewer engagement-owner --override-reconciliation --note 'Synthetic fixture only; no external control report'
python3 run.py semantic-profile --db semantic-demo.db
python3 run.py analyze --db semantic-demo.db --semantic-run 1
python3 run.py semantic-evaluate --db semantic-demo.db --run 1 --labels examples/semantic/labels.csv --actor engagement-owner
python3 run.py semantic-investigate --db semantic-demo.db --run 1 --ledger-id 10
```

Do not use a reconciliation override as a substitute for actual source control totals on real engagements.
