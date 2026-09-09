## User

I want to replicate the pipeline from [@qcom-scraping](file:///Users/Mitesh%20Gada/Documents/Projects/qcom-scraping/) and transfer its usecase and pipeline to be used for audit and accounting firms being able to use these statistical models in financial and forensic audits

## User

.

## Assistant

<thinking>


**Planning code exploration and inspection**
</thinking>

I’ll first map the existing `qcom-scraping` pipeline—its inputs, processing stages, models, and outputs—then translate that into an audit-focused design rather than assuming the use case.

**Tool Call: pwd && rg --files qcom-scraping | sed -n '1,240p'**
Status: Completed

Terminal:
```
/Users/Mitesh Gada/Documents/Projects
qcom-scraping/run.py
qcom-scraping/ARCHITECTURE.md
qcom-scraping/DEMAND_RADAR.md
qcom-scraping/tools/dashboard.html
qcom-scraping/IMPLEMENTATION_LOG.md
qcom-scraping/tools/pw_catalog.js
qcom-scraping/exports/opp_snapshot.json
qcom-scraping/exports/dpi_20260822.csv
qcom-scraping/exports/embedding_map_gemma.html
qcom-scraping/exports/locality_corridor_borivali_andheri.json
qcom-scraping/exports/product_fields_sample.csv
qcom-scraping/exports/locality_current_blinkit.json
qcom-scraping/exports/embedding_map.html
qcom-scraping/exports/locality_current_zepto.json
qcom-scraping/exports/locality_andheri_west.json
qcom-scraping/exports/embedding_map_opp.html
qcom-scraping/exports/product_space_understanding.md
qcom-scraping/exports/product_space_engine.html
qcom-scraping/exports/parser_eval_report.csv
qcom-scraping/exports/locality_corridor_goregaon.json
qcom-scraping/exports/embedding_map_opp_nemotron_current.html
qcom-scraping/exports/locality_current_instamart.json
qcom-scraping/README.md
qcom-scraping/src/inventory.py
qcom-scraping/src/alert.py
qcom-scraping/src/prober.py
qcom-scraping/src/incremental.py
qcom-scraping/src/ai_assist.py
qcom-scraping/src/miniyaml.py
qcom-scraping/src/detect.py
qcom-scraping/src/product_vectors.py
qcom-scraping/src/gaps.py
qcom-scraping/src/search.py
qcom-scraping/src/pricing.py
qcom-scraping/src/assortment_gaps.py
qcom-scraping/src/orchestrator.py
qcom-scraping/src/density.py
qcom-scraping/src/product_fields.py
qcom-scraping/src/honey.py
qcom-scraping/src/opportunities.py
qcom-scraping/src/watchlist.py
qcom-scraping/docs/swiggy-apk-instamart-findings.md
qcom-scraping/docs/qcapi_sweep_Swiggy.search.json
qcom-scraping/docs/qcapi_sweep_BlinkIt.search.json
qcom-scraping/docs/qcapi_paan_sweep.json
qcom-scraping/docs/qcapi_sweep_Swiggy.eta.json
qcom-scraping/docs/qcapi_sample_swiggy_mumbai.search.json
qcom-scraping/docs/paan_comparison.txt
qcom-scraping/docs/catalog-sku-counting.md
qcom-scraping/docs/blinkit-apk-reverse-findings.md
qcom-scraping/docs/tracking_expansion_vouchers.md
qcom-scraping/docs/qcapi_sweep_Zepto.eta.json
qcom-scraping/docs/paan_comparison_run2.txt
qcom-scraping/docs/embed-openrouter-migration.md
qcom-scraping/docs/demand-radar-34292-36517-findings.md
qcom-scraping/docs/qcapi_sweep_Zepto.search.json
qcom-scraping/docs/zepto-apk-reverse-findings.md
qcom-scraping/docs/qcapi_sweep_BlinkIt.eta.json
qcom-scraping/docs/qcapi_sample_swiggy_mumbai.eta.json
qcom-scraping/docs/quickcommerce-api-vetting.md
qcom-scraping/docs/demand-catchment-plan.md
qcom-scraping/config.yaml
qcom-scraping/src/adapters/amazon.py
qcom-scraping/src/adapters/base.py
qcom-scraping/src/adapters/demo.py
qcom-scraping/src/adapters/bigbasket.py
qcom-scraping/src/adapters/blinkit.py
qcom-scraping/src/adapters/trackers.py
qcom-scraping/src/adapters/jiomart.py
qcom-scraping/src/adapters/flipkart.py
qcom-scraping/src/adapters/instamart.py
qcom-scraping/src/adapters/zepto.py
qcom-scraping/src/dashboard.py
qcom-scraping/src/human_review.py
qcom-scraping/src/__init__.py
qcom-scraping/src/tgbot.py
qcom-scraping/src/locality.py
qcom-scraping/src/categories.py
qcom-scraping/src/events.py
qcom-scraping/src/embed.py
qcom-scraping/src/product_space.py
qcom-scraping/src/temporal.py
qcom-scraping/src/store.py
qcom-scraping/src/geo.py
qcom-scraping/src/demand.py
qcom-scraping/AGENTS.md
qcom-scraping/scripts/test_embeddinggemma.py
qcom-scraping/scripts/embed_gemini_resume.py
qcom-scraping/scripts/bench_ollama_batch.py
qcom-scraping/scripts/qcapi_probe.sh
qcom-scraping/scripts/compare_embeddings.py
qcom-scraping/scripts/live_sweep.py
qcom-scraping/scripts/compare_paan.py
qcom-scraping/scripts/eval_parser.py
qcom-scraping/scripts/export_opp_json.py
qcom-scraping/scripts/embed_3d_map.py
qcom-scraping/codes.yaml
qcom-scraping/GUIDE.md
qcom-scraping/PRODUCT_SPACE_PLAN.md
qcom-scraping/tests/test_temporal.py
qcom-scraping/tests/test_product_fields.py
qcom-scraping/tests/test_inventory_capture.py
qcom-scraping/tests/test_product_space.py
qcom-scraping/tests/test_validation.py
qcom-scraping/tests/test_assortment_gaps.py
qcom-scraping/inventory_milestones.md
qcom-scraping/tests/test_gaps.py
qcom-scraping/tests/test_density.py
qcom-scraping/tests/test_incremental.py
qcom-scraping/tests/test_human_review.py
qcom-scraping/tests/test_opportunities.py
qcom-scraping/tests/test_product_vectors.py
qcom-scraping/tests/__init__.py

```


## Assistant

<thinking>


**Inspecting architecture and config from README**
</thinking>

**Tool Call: "sed -n '1,260p' qcom-scraping/AGENTS.md && sed -n '1,260p' qcom-scraping/README.md && sed -n '1,300p' qcom-scraping/ARCHITECTURE.md && sed -n '1,220p' qcom-scraping/config.yaml"**
Status: Completed

Terminal:
```
# Agent Instructions (User Preferences)

## Web searches
- ALWAYS use `monid` (the Monid CLI) for web searches and web research.
- NEVER use the built-in `web_search` tool/plugin (or any DeepSeek/Exa-backed built-in search).
- Workflow: `monid discover --query "<what you need>"` to find a suitable data endpoint, then `monid inspect` and `monid run` to execute it.
- monid is installed at `/Users/Mitesh Gada/.npm-global/bin/monid`.
- monid writes its config/state via XDG paths, which the sandbox denies under `~/.config`. Always run it with `XDG_CONFIG_HOME="/Users/Mitesh Gada/Documents/Projects/.monid/xdg"` (workspace-writable; contains `monid/config.yaml` + `credentials.yaml`).
- Proven working call: `XDG_CONFIG_HOME=".../.monid/xdg" monid run --provider tinyfish --endpoint /search --query '{"query":"...","domain_type":"web"}' --wait 90 -j` (free endpoint; pass params via `--query`, not `-i`). Use `tinyfish /fetch` (free) with a JSON body `{"urls":[...]}` when full page text is needed.

## Ponytail — lazy senior dev mode (installed, applies to every project here)

You are a lazy senior developer. Lazy means efficient, not careless. The best code is the code never written.

Before writing any code, stop at the first rung that holds:

1. Does this need to be built at all? (YAGNI)
2. Does it already exist in this codebase? Reuse the helper, util, or pattern that's already here, don't re-write it.
3. Does the standard library already do this? Use it.
4. Does a native platform feature cover it? Use it.
5. Does an already-installed dependency solve it? Use it.
6. Can this be one line? Make it one line.
7. Only then: write the minimum code that works.

The ladder runs after you understand the problem, not instead of it: read the task and the code it touches, trace the real flow end to end, then climb.

Bug fix = root cause, not symptom: a report names a symptom. Grep every caller of the function you touch and fix the shared function once — one guard there is a smaller diff than one per caller, and patching only the path the ticket names leaves a sibling caller still broken.

Rules:

- No abstractions that weren't explicitly requested.
- No new dependency if it can be avoided.
- No boilerplate nobody asked for.
- Deletion over addition. Boring over clever. Fewest files possible.
- Shortest working diff wins, but only once you understand the problem. The smallest change in the wrong place isn't lazy, it's a second bug.
- Question complex requests: "Do you actually need X, or does Y cover it?"
- Pick the edge-case-correct option when two stdlib approaches are the same size, lazy means less code, not the flimsier algorithm.
- Mark deliberate simplifications that cut a real corner with a known ceiling (global lock, O(n²) scan, naive heuristic) with a `ponytail:` comment naming the ceiling and upgrade path.

Not lazy about: understanding the problem (read it fully and trace the real flow before picking a rung, a small diff you don't understand is just laziness dressed up as efficiency), input validation at trust boundaries, error handling that prevents data loss, security, accessibility, the calibration real hardware needs (the platform is never the spec ideal, a clock drifts, a sensor reads off), anything explicitly requested. Lazy code without its check is unfinished: non-trivial logic leaves ONE runnable check behind, the smallest thing that fails if the logic breaks (an assert-based demo/self-check or one small test file; no frameworks, no fixtures). Trivial one-liners need no test.

Canonical install: `.tools/ponytail` (update with `git pull`; source of the six `/ponytail*` skills — review, audit, debt, gain, help — and of this ruleset). When asked to review a diff or repo for over-engineering, follow `skills/ponytail-review/SKILL.md` and `skills/ponytail-audit/SKILL.md` there.

# AGENTS.md — qcom-scraping

Notes for humans and agents working on this repo. Read this before changing
anything; it covers the non-obvious environment quirks and the invariants that
keep the data honest.

## What this repo is

One tool, three features (all sharing the same browser-intercept crawler):

1. **Glitch monitor** — price anomalies across Blinkit/Zepto/Instamart on the
   Mumbai corridor (Virar→Andheri). Design: `ARCHITECTURE.md`.
2. **Price-search Telegram bot** — cheapest offer per product across 5
   platforms (`src/search.py`, `src/tgbot.py`, `src/pricing.py`), with
   search-history persistence + keyword category analytics
   (`src/categories.py`; dashboard endpoints `/searches`, `/categories`),
   plus proactive keyword watches: `/watch <product>` stores a chat-level
   watch and WatchPusher (`src/tgbot.py`) pushes Telegram pings whenever a
   search result or crawl batch matches (rate-capped); `/digest` replies with
   today's cheapest find per category + Demand Radar DPI top-5. Matching is
   token-overlap with an OPTIONAL semantic lift (`src/embed.py`: NVIDIA-hosted
   embeddings via ai.embedding_base_url, or the OPT-IN local Ollama
   embeddinggemma provider — ai.embedding_provider: "ollama"; cached in an
   additive `embeddings` table;
   blend = max(token, semantic) so it can only add candidates, never demote;
   endpoint down/disabled ⇒ exact historical token behaviour; backfill =
   `--embed-catalog`, archive query = `--similar`). A semantic catalog
   re-key guard was evaluated and REJECTED 09-05 — brand-sibling names
   cosine above genuine relabels, see src/watchlist.py.
3. **Demand Radar** — per-darkstore stock-out intelligence for a locality
   (Andheri West first). Design + status: `DEMAND_RADAR.md`. Pipeline:
   `--map-locality` → `--build-watchlist` → `--demand` → (phase 4: analysis).

## Concurrent agents — coordination rules

This repo is edited by MORE THAN ONE agent at a time (as of 08-22: one on the
Demand Radar phases, one on search-history/category analytics). Rules:

- **Use the subagent tool generously** to complete tasks: fan out independent,
  file-disjoint work (test runs, eval/report commands, read-only research,
  new-module drafts) to background subagents instead of doing everything
  in-thread — parallel verification is the norm here, not a special case.
  Each delegation must name the exact files it may touch (or "no files —
  read-only") and the verification commands it ran. File-disjoint means
  disjoint WRITES: two agents may read anything, but never edit the same
  file. If a subagent stalls or dies mid-task, kill it, keep whatever it
  already wrote to disk, and finish that slice in-thread — don't re-delegate
  a stuck task.
- **Verify before AND after you edit**: run the full check suite (below) on
  entry — if it fails, someone else is mid-edit; wait and re-read the file.
- **Targeted edits only.** Never rewrite whole files from memory; re-read the
  current content first (another agent may have just changed it). Use small
  anchored `old_string` replacements, never full-file overwrites.
- **Schema changes are additive**: `CREATE TABLE IF NOT EXISTS` / new columns
  via backfill (see `Store._backfill_categories` for the pattern). Never
  drop/rename tables or columns — other features read them live.
- **config.yaml must stay miniyaml-compatible** (stdlib fallback parser when
  PyYAML is absent). Add new sections at the END of an existing section with
  comments; don't reorder keys.
- **Document as you go**: new CLI flags → README + the Commands list here;
  new modules/tables → Repo map; new behavioral invariants → the invariants
  section. Undocumented behavior will get broken by the next agent.
- **Single implementation log**: all milestone/phase logs (M1, M2, …) live in
  ONE file — `IMPLEMENTATION_LOG.md` at repo root — NEVER per-phase files
  (`M1_*.md`, `M2_*.md`, etc.). Update it **proactively** as each step
  completes (do NOT wait to be reminded); append the next phase's status table
  + steps when its work begins. Keep the "Comments & deviations" as **one-line
  entries that state the reason for every deviation** from
  `PRODUCT_SPACE_PLAN.md`.
- **The repo is git-managed** (branch `main`, baseline `b7f3502` = verified
  merged state of all workstreams). `git status` must be clean when you start;
  commit after every verified milestone with a descriptive message. Never
  force-push or amend published history — the other agent builds on HEAD.
  If the tree contains modifications you did NOT make, stop: run the verify
  suite, `git diff` them, and read AGENTS.md/README changes before proceeding.
- Don't run two long crawls (`--demand`, `--map-locality`, `--build-watchlist`,
  `--store-inventory`, `live_sweep.py`) simultaneously against the same app —
  rate-limit bans hurt both workstreams. Coordinate timing instead. Observed
  08-24: an inventory sweep started while `--demand` was running got its
  fresh sessions throttled into empty probes (stores resolved, products=0),
  while the same sweep run alone captured 200+ products per probe.

## Repo map

```
run.py                  entrypoint; ALL CLI flags live here (--check --demo
                        --search --bot --ui [--bot] [--monitor] [--no-monitor]
                        --once --map-locality --build-watchlist --demand
                        --store-inventory; --ui alone is dashboard-ONLY (no
                        loops); add --bot and/or --monitor to also run them
                        alongside; bare --bot keeps bot+monitor; flag
                        args parsed by _flag_* helpers)
config.yaml             every tunable; secrets go in .env only
codes.yaml              delivery fees + offer codes (user-editable)
GUIDE.md                combined first-run guide + plain-English glossary:
                        what to run in what order + how to interpret each
                        output, with every jargon term defined where it
                        first appears — link new contributors here before
                        the other docs
tools/pw_catalog.js     THE crawler: real app in headless Chromium, intercepts
                        signed API calls; deep-sweep visit queue (categories +
                        search terms; --skip filters category labels — the
                        demand.skip_categories milk de-biasing knob); --deep-cats
                        discovers sub-category links ON category pages (one-hop
                        BFS; catalog-inventory mode); --pre
                        pre-visits gated verticals before the target page
                        (Blinkit tobacco shelf, "URL::LABEL|..." pairs);
                        location seeding + request rewrite;
                        DSH_BODY_DIR raw-body dump hook
src/
  orchestrator.py       glitch-monitor loop (jitter, off-peak speedup)
  locality.py           phase 1: anchor grid + darkstore discovery/clustering
  watchlist.py          phase 2: per-store SKU probe set builder (+ catalog-
                        inventory mode: --catalog full snapshots + 'new'/
                        'delisted' churn diffs into catalog_snapshots/events)
  prober.py             phase 3: stock_obs loop + debounced oos_events machine
  demand.py             phase 4: DPI rollups, hour×SKU onset heatmap, ETA
                        curves, CSV export (pure functions over sqlite)
  categories.py         keyword product-category classifier (ordered rules)
  inventory.py          SINGLE-STORE full-category inventory capture
                        (--store-inventory): requires --app + --store, resolves
                        lat/lon from --lat/--lon (override — target ANY store,
                        even outside the machine's real location) or deals.db
                        .darkstores. Calls WatchlistBuilder.build_one_store()
                        (every-category deep sweep) and writes a RICH, COMPLETE
                        per-product record to inventory/inventory_<app>.db
                        (table inventory_catalog: name/price/mrp/in_stock/url/
                        collections [APP taxonomy]/category [internal taxonomy]/
                        raw_json [opaque app payload] + raw_json_truncated/
                        raw_json_bytes). The operational catalog_snapshots are
                        ALSO written to deals.db. Vouchers are captured here
                        and filtered downstream in the union layer.
  product_fields.py     grocery product-name FIELD PARSER (parse_name): brand,
                        pack_value/pack_unit, is_multipack, variant, unit_base,
                        unit_price, parse_status. Pure stdlib; self-test
                        python3 -m src.product_fields (20 curated cases).
  product_space.py      M1 UNION LAYER: load_product_space() reads inventory_
                        <app>.db.inventory_catalog UNION deals.db.catalog_
                        snapshots (latest per sku fallback), excludes vouchers,
                        attaches parsed fields, runs ENTITY-RESOLUTION product
                        groups (exact canonical key → within-brand match_score
                        candidate gen → pack/variant VETO → semantic confirm
                        fallback; semantics never override a pack/variant veto).
                        Provenance: every row carries app/store_id/sku_key/
                        inventory_db. Self-test python3 -m src.product_space.
  store.py              sqlite schema + all persistence helpers
  embed.py              OPTIONAL semantic matching (NVIDIA-hosted embeddings,
                        ai.embedding_base_url + NVIDIA_Build_API_KEY (asymmetric:
                        corpus=passage, query=query; nvidia/llama-nemotron-embed-vl-1b-v2 @2048
                        dims; a whole 1000-name batch counts as ONE request,
                        50 req/day free tier): batched stdlib-urllib client
                        + sqlite cache in an additive `embeddings` table
                        (one vector per distinct name, keyed model+dims so
                        a provider switch re-keys cleanly); search ranking +
                        WatchPusher blend max(token, semantic) so semantics
                        only LIFT candidates; endpoint down or
                        ai.semantic_matching: false => exact historical
                        token behaviour. Self-test: python3 -m src.embed
                        (offline, fake transport; fake vectors mirror live
                        cosines of the current model). Backfill attempts are
                        journaled to logs/embed_backfill.log (run start,
                        per-batch counts, stop reason + resume hint; the
                        embeddings table itself stays the source of truth
                        for which names are done). OPT-IN local provider
                        (ai.embedding_provider: "ollama"): embeddinggemma-300m
                        via the workspace-local Ollama server (.tools/ollama/),
                        no API key; its 768-dim rows sit BESIDE the NVIDIA
                        @2048 rows. Batch 256 is the measured optimum on this
                        2-core/8GB box (flat ~8 items/s for B=64→256; B≥512
                        exhausts free RAM and kills the Ollama runner — see
                        Environment quirks)
  ai_assist.py          OPTIONAL LLM advisor behind the dashboard AI panel
                        (/ai/*): result explanations, whitelisted demand-probe
                        tuning, product-focus staple_queries; OpenAI-compatible
  geo.py                corridor anchors + store resolver (glitch monitor)
  adapters/             blinkit / zepto / instamart / bigbasket /
                         jiomart / amazon / flipkart / trackers / demo;
                        base.py holds the browser machinery
  detect.py alert.py honey.py events.py dashboard.py search.py pricing.py
                        tgbot.py miniyaml.py (stdlib YAML fallback)
exports/                locality mapping JSON (rotation pools per store)
docs/                   research reports: QuickCommerce API vetting + Zepto/Swiggy
                        APK reverse-engineering findings (source .apkm files live in
                        apks/, gitignored — too large to commit)
scripts/live_sweep.py   one-shot real-glitch hunt
scripts/test_embeddinggemma.py  local-Ollama embeddinggemma backfill + demo
                        queries (self-managing: starts serve, pulls model)
scripts/compare_embeddings.py   embeddinggemma-vs-NVIDIA neighbour-agreement
                        comparison (numpy in .venv/ — run with .venv/bin/python)
scripts/embed_gemini_resume.py  additive GEMINI corpus backfill
                        (gemini-embedding-001 @768 via the AI_API_KEY pool,
                        config override in-process — repo default stays
                        NVIDIA; embedding_send_extras: false because Gemini
                        400s on the NVIDIA-only body fields; batch 100 +
                        16s pause ~= 94 RPM/key under the 100 RPM wall,
                        ~4k names/day across 4 keys, resets midnight PT;
                        re-run daily until pending hits 0)
scripts/bench_ollama_batch.py   Ollama batch-size throughput/RAM benchmark
scripts/embed_3d_map.py  Inventory Atlas: dark-themed semantic explorer over
                        the `embeddings` table -> exports/embedding_map.html
                        (self-contained; run with .venv/bin/python — needs
                        sklearn/plotly/scipy; --model nemotron|gemma renders
                        from either provider's vectors: nemotron (default,
                        2048d) -> embedding_map.html, gemma (768d) ->
                        embedding_map_gemma.html). Pipeline: cosine-normalize
                        -> PCA-50 -> k-means (--k, default 24) -> PCA-3 + PCA-2
                        (--projection umap upgrades both, needs umap-learn)
                        -> cheapest-latest price/store/category/stock join per
                        name -> one HTML (3D map + 2D hull-territory overview +
                        cluster explorer + click-to-select product inspector
                        with similar-products list; Semantic/Price/Store/
                        Category/Density modes restyle the same geometry).
                        --sample N renders N random names for fast UI testing;
                        --seed N fixes PCA/k-means/sampling; --neighbors N
                        sizes the inspector list (default 20)
.tools/ollama/          workspace-local Ollama binary (gitignored; models in
                        .ollama/, server HOME in .ollama_home/ — ~800MB total,
# qcom-scraping v2 — Glitch & Deal Monitor

Two features in one tool:

1. **Glitch monitor** — watches Blinkit/Instamart/Zepto across the Mumbai
   corridor (Virar → Andheri) for pricing glitches, upstream of Telegram groups.
2. **Price-search bot** — message a Telegram bot any product name and get the
   cheapest offer across Blinkit, Zepto, Instamart, Amazon & Flipkart,
   including delivery fees and applicable codes/offers. Both run simultaneously.
3. **Demand Radar** (new) — maps the darkstores serving a locality (e.g. Andheri
   West), then tracks per-store in/out-of-stock + delivery ETA over time to
   build a chronological demand-pressure heatmap. See `DEMAND_RADAR.md`.

See `ARCHITECTURE.md` for the design and the anti-block strategy.
First time here? `GUIDE.md` walks you through what to run, in what order,
and how to interpret every result — with every jargon term (OOS, DPI,
darkstore, honey pot, WAF…) defined in plain English where it first appears.


## Demand Radar (phases 0–3 live)

    python3 run.py --map-locality                    # discover Andheri West darkstores
    python3 run.py --map-locality --apps blinkit     # one app only
    python3 run.py --map-locality --max-points 5     # quick partial sweep
    python3 run.py --store-inventory --app blinkit --store 34292            # one store, full-category capture
    python3 run.py --store-inventory --app zepto --store Z9 --lat 19.07 --lon 72.88  # any store, anywhere
    python3 run.py --product-fields                                       # grocery name parser self-test
    python3 run.py --product-fields --report --sample 200                 # accuracy CSV (exports/product_fields_sample.csv)
    python3 run.py --product-space --apps blinkit,zepto,instamart --csv   # normalized union -> exports/product_space.csv
    python3 run.py --product-vectors --csv              # M2 per-group attribute+commercial vectors
    python3 run.py --detect-assortment-gaps --csv       # M3 cross-app assortment gaps
    python3 run.py --product-density --csv              # M4 per-category density + coverage guards
    python3 run.py --detect-gaps --csv                  # M5 internal/attribute gaps
    python3 run.py --score-opportunities --persist      # M6 scoring + M7 persist to deals.db
    python3 run.py --opportunity-report --limit 10      # latest persisted opportunity snapshot
    python3 run.py --temporal-analysis --min-n 25        # temporal signals + category stability report
    python3 run.py --validate-opportunities --limit 20   # top persisted opportunities for human review
    python3 run.py --opportunity-pipeline --force        # incremental refresh (full refresh with --force)
    # --min-n honored by: product-density, detect-gaps, score-opportunities, temporal-analysis (stability)
    python3 run.py --build-watchlist                 # per-store SKU probe set
    python3 run.py --build-watchlist --apps blinkit --store 47578 \
                    --max-per-store 100 --max-queries 10
    python3 run.py --build-watchlist --catalog --apps blinkit --store 34292
                                                    # catalog-inventory snapshot:
                                                    # every category, no search
                                                    # terms (~20-60 min, run ALONE)
    python3 run.py --catalog-report [--store 34292]  # snapshot history + new/delisted churn
    python3 run.py --embed-catalog [--limit N]      # one-time semantic backfill:
                                    # vectorize every distinct product name
                                    # (NVIDIA-hosted nvidia/llama-nemotron-
                                    # embed-vl-1b-v2 @2048 dims via
                                    # ai.embedding_base_url +
                                    # NVIDIA_Build_API_KEY; RESUMABLE — re-run
                                    # to continue, cached names are skipped).
                                    # LOCAL OPT-IN ALTERNATIVE (zero quota):
                                    # set ai.embedding_provider: "ollama" ->
                                    # workspace-local Ollama +
                                    # embeddinggemma-300m @768 dims. Harness:
                                    # scripts/test_embeddinggemma.py (starts
                                    # the server + pulls the model itself);
                                    # quality comparison vs NVIDIA:
                                    # scripts/compare_embeddings.py (numpy in
                                    # .venv/ — run with .venv/bin/python);
                                    # batch-size benchmark:
                                    # scripts/bench_ollama_batch.py (batch 256
                                    # is the measured optimum on this box)
    python3 run.py --similar <phrase> [--limit 10]  # semantic archive query:
                                    # most similar archived names (needs
                                    # --embed-catalog first)
    .venv/bin/python scripts/embed_3d_map.py [--model nemotron|gemma] [--k 24]
                                    # Inventory Atlas: self-contained dark-themed
                                    # HTML explorer of the embedding archive ->
                                    # exports/embedding_map[_<model>].html
                                    # (3D semantic map + 2D overview + cluster
                                    # explorer + product inspector; Semantic /
                                    # Price / Store / Category / Density modes;
                                    # needs sklearn/plotly/scipy in .venv/;
                                    # --projection umap needs umap-learn;
                                    # --sample N renders N random names for
                                    # fast UI testing)
    python3 run.py --demand                          # continuous stock probing loop
    python3 run.py --demand --once --apps blinkit --store 47578   # single round
    python3 run.py --demand-report --csv             # DPI ranking + heatmap summary
    python3 run.py --purge-vouchers [--dry-run]      # wipe voucher/gift-card rows from Demand Radar tables
    python3 run.py --qc-status                       # per-app QC health board

**Silent-hour scheduling (09-02):** the `--demand` loop only *starts* rounds in
the hours listed in `demand.sweep_windows` (local time, `"0-23"` = all hours =
no change). The Aug 24–Sep 1 `stock_obs` history had **zero observations in
hours 02–10 and 15–16**, so OOS onsets that began in those windows were only
recorded at the next sweep (the onset heatmap's `started_at` is the first read,
not the true onset) and the heatmap is biased to sweep hours. Leave the Demand
prober feature running 24/7 to cover every hour, or set e.g.
`demand.sweep_windows: ["2-10", "15-16"]` to spend the crawl budget *only* on
the historically-silent windows. The loop idles (no crawls, no rate-limit burn)
outside the windows and resumes at the next in-window hour; a round already in
flight always finishes.

**Live progress:** every browser sweep (`--build-watchlist`, `--map-locality`,
`--store-inventory`, `--demand`) streams its progress as it works — which store
it's on as `(i/N) <app> @ store <id> — <label>`, how many visits are queued
(categories + searches), then one `[sweep] …` line per visit with the
cumulative SKU count, plus onboarding/localization steps. Watch it in the
terminal, or start the feature from the dashboard's **Features** panel and
open its **log** (auto-refreshes ~1.2 s). Mute with
`anti_block.stream_progress: false` in `config.yaml`.

**Store inventory — single-store full-category capture (`--store-inventory`):**
targets ONE store and runs a complete every-category sweep (the same
catalog-inventory engine `--build-watchlist --catalog` uses), writing a RICH,
COMPLETE record per product into a per-app database in the `inventory/` folder:
`inventory/inventory_blinkit.db`, `inventory/inventory_instamart.db`,
`inventory/inventory_zepto.db`. The table is `inventory_catalog` (columns: `name,
price, mrp, in_stock, url, collections` [the APP's own shelf taxonomy], `category`
[our normalized internal taxonomy from `categorize`], `raw_json` [the full
app-specific payload, opaque — never force-fit into a shared column], plus
`raw_json_truncated`/`raw_json_bytes` for provenance). The operational snapshot
(catalog_snapshots / watchlist / churn) is ALSO written to `deals.db` so Demand
Radar, `--embed-catalog` and the union layer keep working. The capture is
complete (vouchers included); business filtering like voucher exclusion happens
downstream in the union layer, never here.

Requires `--app <app>` + `--store <store_id>`. Location resolves from `--lat/--lon`
(override — lets you target ANY store, even outside this machine's real location),
else from `deals.db.darkstores` for that store (run `--map-locality` first if
unknown). **Run it alone:** starting it while `--demand` / `--map-locality` /
`--build-watchlist` is also crawling the same apps gets the fresh sessions
rate-limited into empty probes
(stores resolve, products = 0). Stop other crawls first (Features panel),
then start the inventory.

**Demand analysis (phase 4):** the dashboard's Demand Radar panels show a
Demand Pressure Index per SKU (Σ OOS-minutes × recency ÷ observation-days),
a hour×SKU stock-out onset heatmap (local time — when demand spikes), and
per-hour delivery-ETA curves. `--demand-report` prints the same in the
terminal; `--csv` exports `exports/dpi_<date>.csv`.

**What DPI actually measures (09-04):** the prober's light sweep samples home
+ 30 category shelves + the store's watchlist search terms — a few hundred
SKUs per cycle — while the watchlist itself is now a full catalog census
(~8-24k rows/store from `--build-watchlist --catalog`). DPI is therefore
shelf-sampler demand pressure, not whole-inventory: stock-outs shorter than
the probe interval are invisible by construction. Delisting truth is
snapshot-driven (`catalog_events` diffs), and the prober only opens `vanished`
events for SKUs it has itself sighted before — a never-sighted row's absence
is a coverage gap, not churn.

**QC-first defaults** (since 08-22): amazon/flipkart tracking is disabled and
the search bot compares quick-commerce platforms only — re-enable via
`adapters.trackers` / `search.platforms` in `config.yaml`.

`--map-locality` resolves each app's distinct darkstores by probing a
landmark+grid anchor set (config → `demand.locality`), enforcing our GPS on
every intercepted API call (cached-location seeding + request rewrite). For
Instamart, each probe also types the anchor's own locality name into the app's
"Add your location" modal (landmark name, rotated landmark names for grid
anchors) so the session binds that anchor's darkstore instead of one shared
city-wide store.
`--build-watchlist` deep-sweeps each store in ONE browser session — home feed,
category click-throughs, staple searches — scoring every SKU (search hits >
home presence) into the `watchlist` table. `--demand` then loops: each cycle
re-sweeps a store's watchlist collections and writes `stock_obs`; debounced
stock-outs become `oos_events` (restart-proof; vanished SKUs get their own
event kind; canary/mass-flip guards freeze the machine on suspected
soft-blocks instead of faking demand). Query it:

    sqlite3 deals.db "SELECT sku_key, COUNT(*) FROM oos_events
                      WHERE kind='oos' GROUP BY sku_key ORDER BY 2 DESC;"

## Price-search bot

    python3 run.py --bot            # telegram bot + monitor, simultaneously
    python3 run.py --bot --no-monitor   # bot only
    python3 run.py --ui             # dashboard ONLY (no loops); add --bot
                                    # and/or --monitor to also run them alongside
    python3 run.py --search "amul milk" # CLI, no telegram needed

Setup the bot once:
1. Talk to [@BotFather](https://t.me/BotFather) → `/newbot` → copy the token.
2. Put it in `.env` as `TG_BOT_TOKEN=...`.
3. Start `python3 run.py --bot`, open your bot in Telegram, send it a product name.

Reply looks like:

```
🔎 “amul milk” — cheapest across platforms

🥇 BLINKIT — Amul Taaza Toned Milk 500ml
     ₹17 (MRP ₹17)
     → ₹42 effective  (+₹25 delivery)
🥈 FLIPKART — Amul A2 Buffalo Milk, 1 L
     ₹70
     → ₹103 effective  (code AXISFK 10% −₹7, +₹40 delivery)
...
```

Offers/delivery fees live in `codes.yaml` — **edit it** to match the cards and
codes you actually hold; every applied offer shows its note so you can verify
at checkout before paying.

### Proactive alerts: /watch & /digest

    👀 /watch amul milk     # ping this chat when crawls/searches surface a match
    👀 /watch               # list your watches
    🗑 /unwatch amul milk   # stop watching
    📋 /digest              # today's cheapest find per category + DPI top-5

Watches persist in `deals.db` (the `keyword_watches` table, up to 10 per chat).
Every `--search` run, every bot search, and every monitor/demo crawl batch is
matched against them — same token-overlap scoring as search ranking — and any
match is pushed straight to your Telegram chat with platform, price and link.
Pushes are rate-limited by `alert.rate_cap` per hour plus a 6-hour per-watch
cooldown (`last_alerted_ts`), so restarts and hot keywords can't spam you.
`/digest` reads today's archived search results + the Demand Radar DPI ranking
straight from the DB — no crawling.

## How it beats polling limits

- **Browser-intercept, not web scraping.** Runs the *real* mobile web app in
  headless Chromium. JS challenges that block `curl` are solved by the browser.
- **The app is the API docs.** We intercept the app's own signed catalog calls
  and replay them on a tight loop. When the app rotates paths/headers, the next
  page load re-discovers them.
- **Geo-anchored store walking.** Each Mumbai station coordinate resolves a
  *different* dark store; glitches are local, so we watch the corridor and treat
  each store as its own baseline.
- **Rotated identity.** Fresh mobile UA + install-id + (optional) residential
  proxy per cycle.
- **Honey-pot canaries.** Hardcoded TRUE prices for a few high-velocity SKUs;
  any large deviation is an instant glitch flag — no ML needed for the first pass.
- **Off-peak speedup.** Crawls *faster* at night when server rate limits are
  looser — inverts the usual bot-burst signature.

## Setup

    cd ~/Documents/Projects/qcom-scraping
    pip install pyyaml            # optional; a stdlib fallback parser is built in

    # Browser layer uses the PRE-INSTALLED Playwright + Chromium (no install needed):
    #   ../Do not delete folder/node_modules  +  ../Do not delete folder/.pw-browsers
    #   (paths configured in config.yaml → anti_block.node_path / pw_browsers_path)

    cp .env.example .env            # fill TG_BOT_TOKEN / TG_CHAT_ID for phone push
    python3 run.py --check          # validate config + adapters
    python3 run.py --demo           # end-to-end pipeline with an injected glitch
                                    # (writes scratch deals.demo.db — never touches deals.db)
    python3 scripts/live_sweep.py   # hunt REAL glitches across the corridor now
    python3 run.py                  # continuous loop

Without Node/Chromium available the QC adapters degrade gracefully (return no
data) and the trackers + detection engine still run. Demo mode needs nothing
external.

## Config (`config.yaml`)

- `geo.corridor` — Mumbai stations Virar→Andheri with lat/lon. Edit to widen.
- `schedule.crawl_terms` — one rotating search per app per monitor cycle;
  de-biases deal-finder coverage away from the dairy-first home carousel
  ([] = off).
- `anti_block.honey_pot` — canary SKUs with `true_price`. Tune to your basket.
# qcom-scraping v2 — Architecture

Updated 2025-09-08 to reflect current repo state (evidence from `AGENTS.md`, `src/`, `run.py`, `config.yaml`, `deals.db` schema, and `tools/pw_catalog.js`).

> **Interactive architecture diagram (archify skill):** authored spec saved to `/tmp/qcom_arch.json` (showcase profile, 13 components covering adapters / browser intercept / geo-store / database / demand pipeline / search / product-space / embeddings / dashboard). The HTML render requires geometry adjustments (label overlap); the spec is the authoritative topology reference.

---

## 1. What this repo is

One browser-intercept crawler (`tools/pw_catalog.js`) shared by three live features:

1. **Glitch monitor** — per-darkstore price anomalies across the Mumbai corridor (Virar → Andheri).
2. **Price-search Telegram bot** (`--bot`) — cheapest effective price across 7 tracked apps with `/watch` keyword pushes (`WatchPusher`) and `/digest` daily summary.
3. **Demand Radar** (`--map-locality` → `--build-watchlist` → `--demand`) — per-store stock-out intelligence; phase 4 (DPI / heatmap / ETA) is **BUILT** (verified 08-22); phase 5 (proxy plumbing) is **WIRED end-to-end** but live validation with a Mumbai residential pool is still **PENDING**.

Plus the M1–M7 **Product-Space Intelligence** pipeline (`--product-space`, `--product-vectors`, `--detect-assortment-gaps`, `--detect-gaps`, `--score-opportunities --persist`, `--opportunity-report`, `--temporal-analysis`, `--validate-opportunities`, `--opportunity-pipeline`) and the optional **semantic-embedding** layer (`--embed-catalog`, `--similar` — NVIDIA `nvidia/llama-nemotron-embed-vl-1b-v2` @2048 dims + opt-in local Ollama `embeddinggemma-300m` @768 dims).

---

## 2. Core design invariants

- **The app is the API documentation.** We never guess endpoints. `pw_catalog.js` runs the real mobile web app in headless Chromium, intercepts its signed XHR/fetch calls, and replays them exactly (`request-signature`, `x-csrf-secret`, `x-api-key`, `device_id`, `session_id`). When paths rotate, the next page load rediscovers them.
- **Location is enforced, not assumed.** Each adapter seeds `localStorage.location`, rewrites `lat`/`lon` in cookies/requests, and drops cached `merchant` IDs. Apps that cache serving store server-side from the request IP (e.g. Jiomart) must match exit-IP to anchor geo; this is the acceptance test for Phase 5 proxies.
- **Vouchers are excluded from every demand surface.** `is_voucher_name()` (token match `voucher` / `gift card`) is used by watchlist builder, prober, DPI rollups, and purge (`--purge-vouchers`). Their "stock-outs" are code-pool replenishments, not demand.
- **Schema changes are additive only.** `CREATE TABLE IF NOT EXISTS` + `ALTER TABLE ADD COLUMN` with backfills (`_backfill_categories`, `_backfill_first_seen`). No drops/renames — other features read `deals.db` live.
- **One browser session per store per sweep.** The continuous loop (`--demand`) never spawns per-SKU processes. Catalog mode (`--catalog`) is the exception: it runs ONE full sweep per store and writes `catalog_snapshots` + `catalog_events` (`new`/`delisted`) via pair reconciliation (`name,price`). A snapshot whose pair count collapses to <70% of previous is recorded but its diff is **skipped** (mass-absence = crawl flake, not churn).
- **NULL ≠ OOS.** A failed parse/crawl writes `in_stock=NULL`; it must never become `0`. Scraper errors must not fabricate demand.
- **Delisting is snapshot-driven only (`catalog_events`).** A partial sweep or light prob round never produces `delisted`. The watchlist's `active=0` rows are kept (the discontinued archive); `oos_events` for `kind='oos'` are reconciled with `catalog_events`, not the reverse.
- **Restart-proof streaks.** `Store.trailing_oos_streak()` rebuilds from `stock_obs` history; `started_at` is the first zero read, never the threshold-crossing time.
- **Vanished ≠ OOS.** A SKU missing from successful sweeps but with prior `stock_obs` sightings opens `kind='vanished'` (not `oos`). A never-sighted SKU (catalog-built but never probed) is a coverage gap, not churn.
- **Suspect cycles freeze the machine.** Canary queries returning only-OOS or mass in-stock→OOS flip record observations but open/close nothing.
- **Silent-hour coverage matters.** `demand.sweep_windows` (local hours) gates loop starts; the Aug 24–Sep 1 history had zero observations in hours 02–10 and 15–16, so onset windows in those hours are biased. Keep `--demand` running 24/7 or set windows to fill them.

---

## 3. Adapter layer (`src/adapters/`)

All 7 adapters subclass `base.Adapter`. Each defines `APP_URL`, `HEALTH_URL` (override for apps whose home serves zero products — Zepto), `PROBE_URL`, `PROBE_TERMS`, and `name`. The adapter interface:

- `crawl(station, lat, lon)` → list of `{sku_key, name, price, mrp, url, in_stock}`.
- `search(query, lat, lon)` → search results (token overlap ≥ 0.5; optional semantic blend from `embeddings` table).
- `probe_point(station, lat, lon, im_term)` → single product-bearing probe; `PROBE_TERMS` fired in-session for catalog breadth beyond home carousel.
- `deep_sweep(station, lat, lon, categories, terms, deep_cats, skip, mirror_page_ms, tabs, on_batch)` → full watchlist sweep.

**Enabled apps and live state:**

| App | Adapter | Key behavior / fix date |
|-----|---------|------------------------|
| **Blinkit** (`blinkit.py`) | `blinkit` | `APP_URL` = category shelf routes (`/dc/`); text search (`/s/?q=`) serves **no tobacco** (server-side curated) — tobacco SKUs come from `--pre` shelf visit (`URL::LABEL`) merged into search results (`BlinkitAdapter.search`). Category regex fixed 09-02 (`(cn|category|categories|c|dc|sc)(/|$)`) — `dc/` routes yield ~300 products per shelf in warm sessions; old regex collapsed to home feed (~104 SKUs, all `collections=home`). Age gate is UI-only; crawler goes straight to shelf URLs. |
| **Zepto** (`zepto.py`) | `zepto` | `HEALTH_URL` overrides to search route (home serves no products for fresh sessions). Signing (`request-signature`, `x-csrf-secret`, `x-xsrf-token`, `x-api-key`, `device_id`, `session_id`) lives in web bundle chunks (`89411-*.js`, `88682-*.js`); crawler harvests already-signed responses — no forging needed. Hard gate is IP-reputation (403 WAF), not signature validation. Fixed 08-22. |
| **Instamart** (`instamart.py`) | `instamart` | Target is `instamart.in` (NOT `www.swiggy.com/instamart` — login-walled for our IP). Inner-scrollable container pagination (`POST /api/instamart/category-listing/filter/v2`) with advancing `items_offset` (stride 20); URL `pageNo`/`offset` are decoys. Mirror pagination (`--mirror-stride 20 --mirror-max-pages 80 --mirror-page-ms 900`) is default; `--scroll-rounds` is opt-in. `--im-term` passes locality term to modal binding. Subcategory routes (`/sc/<l0>/<l1>-<id>/t10`) matched by regex (`sc` added 09-02). |
| **Amazon** (`amazon.py`) | `amazon` | `amazon.in` search (DOM extraction). |
| **Flipkart** (`flipkart.py`) | `flipkart` | Search + price-track (`trackers.py`). |
| **Jiomart** (`jiomart.py`) | `jiomart` | **Enabled**, but block: store is resolved **server-side from request IP** (delivery promise identical at 820.3851 m across different `app_geolocation` cookie values). Client-side location seeding does nothing. Rate-limits hard (~4 rapid probes → empty; ~2.5 min recovery). Not anchor-steerable; at best a machine-location `--store-inventory` source. |
| **Bigbasket** (`bigbasket.py`) | `bigbasket` | `enabled: false`. Akamai Bot Manager 403 (`errors.edgesuite.net`) on every route + UA; curl passes, browsers don't. No `bbnow` domain resolves. Revisit requires residential proxy or real-Chrome fingerprint. |

**Adapter expansion notes (dropped/rejected):**
- `dmart` — dropped 08-31: web is login-gated; no fake accounts.
- `amazon_now` — dropped 08-31: Amazon Now IS live in Mumbai (expanded Sept–Nov 2025) but only in SELECT neighbourhoods; no standalone app; web routes serve generic search or empty Fresh shell. Would pollute `price_obs`.
- `demo` adapter (`demo.py`) — simulated source with injected glitch (`--demo`); runs against scratch `deals.demo.db` (NEVER touches real `deals.db`).

---

## 4. Browser-intercept layer (`tools/pw_catalog.js`)

- **Engine:** Playwright (pre-installed at `../Do not delete folder/node_modules` + `.pw-browsers`; wired via `config.yaml` `anti_block.node_path` / `anti_block.pw_browsers_path`).
- **Anti-block machinery (`base.py`):**
  - `MOBILE_UAS` — 4 mobile UAs (iPhone / Android / Pixel); `rotate_user_agent` toggle.
  - `fresh_install_id()` — 16-char plausible device ID.
  - `load_proxies()` / `pick_proxy()` — reads `PROXY_URL` env + `config.yaml` `anti_block.proxies`.
  - `_rotate()` returns `(ua, iid, proxy)`.
- **Geo seed (`pw_catalog.js` init):** seeds `localStorage.location`, rewrites `lat`/`lon` in cookies/request paths/query/body, drops cached `merchant`.
- **Deep-cats discovery (`--deep-cats`):** one-hop BFS (`sc` / `category` links) for sub-category shelf links. Catalog inventory mode (`--catalog`) uses this; `skip_categories` overrides to `[]` (no skips — a skipped shelf would fabricate delistings).
- **Mirror pagination (`--mirror-page-ms`, `--mirror-stride`, `--mirror-max-pages`, `--tabs`):** mirrors the visit's own captured listing POST (`apiHits` mirror pattern — session's own auth, no forging). `items_offset` advances (20 stride). `--tabs N` opens N concurrent tabs inside the SAME browser context (same `device_id`, one session/store).
- **Progress streaming (`anti_block.stream_progress`):** `stderr` lines (`[app_label] ...`) stream live; stdout carries batch JSON (`{"type":"batch","products":...}`) + terminal summary JSON (`{"products":...,"store_hint":...,"api_endpoints_seen":...}`). `on_batch` writes incrementally to sqlite.
- **Timeout / reap:** process group (`start_new_session`); timer kills group on timeout; reap watchdog kills grandchildren if process exits but browsers hold pipes.
- **Multi-tab (`--tabs N`):** intra-session concurrency (same `device_id`, same visit queue, each tab keeps own intercepted-api list + collection label). Cross-tab throttling possible; `--tabs 3 --mirror-page-ms 600` tested on Instamart.

---

## 5. Demand Radar pipeline (phases 1–4 built; phase 5 wired)

Evidence: `DEMAND_RADAR.md`, `AGENTS.md`, `src/locality.py`, `src/watchlist.py`, `src/prober.py`, `src/demand.py`, `run.py` flags (`--map-locality`, `--build-watchlist`, `--demand`, `--demand-report`, `--catalog-report`, `--store-inventory`, `--catalog`, `--catalog`, `--purge-vouchers`, `--qc-status`).

### Phase 1: Locality (`locality.py`)
- `anchor` grid + `landmark` seeds → resolve + cluster darkstores.
- `geo.corridor` regenerated by location editor (`/location` POST); validated with BOTH `miniyaml` loaders before atomic write; previous file backed to `/tmp`.
- `exports/locality_<name>.json` rotation pools per store.

### Phase 2: Watchlist (`watchlist.py`)
- Per-store SKU probe set: `home` harvest → DOM category click-through (`categories=...`) + staple searches (`terms=...`).
- Scored by search hits > home; `score DESC` orders active set.
- `catalog` mode (`--catalog`): ALL category links (`--deep-cats`), NO search terms, NO `skip_categories` (skipped shelf = false delisting). Writes `catalog_snapshots` + diff events (`new`/`delisted`) vs previous snapshot (pair reconciliation on exact `(name,price)`).
- `deactivate_watchlist_except()` keeps inactive rows (discontinued archive); never deletes.

### Phase 3: Prober (`prober.py`)
- Continuous loop (`--demand`): re-sweep active watchlist collections; writes `stock_obs` snapshots; runs debounced `oos_events` machine.
- `open_oos_event()` opens only when `snapshots` consecutive zero reads met; any `1` closes it immediately. Nulls (`in_stock=NULL`) pause, not reset.
- `vanished` (`kind='vanished'`) opens only for SKUs with prior `stock_obs` sightings. Catalog-covered never-sighted rows are coverage gaps, not churn.
- `close_oos_event()` reconciles stale `oos` events for SKUs outside active set at last observed reading (durations never fabricate unseen time).
- Suspect-cycle freeze: only-OOS canary results or mass in-stock→OOS flip freeze machine (record observations, no events).
- Voucher purge (`store.purge_vouchers()`): defensive removal from `watchlist`, `stock_obs`, `oos_events`; idempotent.

### Phase 4: Analysis (`demand.py` — BUILT 08-22)
- `dpi_table()` — ranked `[{sku_key, name, dpi, n_events, total_min, mean_restock_min, last_price, last_seen, active}]`; excludes `is_voucher_name()`.
- `heatmap()` — hour-of-day (local) × top-DPI SKU matrix of `oos` onset counts.
- `eta_curve()` — per-hour ETA stats from `stock_obs.eta_min`.
- `demand_summary()` — per-darkstore overview + totals.
- `export_csv()` → `exports/dpi_<date>.csv`.
- `run.py --demand-report [--store ID] [--csv]` — DPI table + heatmap summary.
- `run.py --catalog-report [--store ID]` — catalog snapshots + new/delisted churn log.

### Phase 5: Hardening (WIRED; PENDING live validation)
- `anti_block.proxies` (config) + `PROXY_URL` env → `load_proxies()` + `pick_proxy()` → `--proxy` → `pw_catalog.js` `browser.newContext({proxy})`.
- One proxy per invocation = one fresh browser+context = fresh WAF identity (session-bound token constraint; never rotate under live context).
- Empty pool = exact old behavior (verified: blinkit probe unchanged).
- Acceptance test: jiomart store MUST change per exit IP (IP-locked resolution).
- Global launcher `.tools/ollama/ollama-global` wraps binary, pins `HOME`/`OLLAMA_HOME`/`OLLAMA_MODELS` into workspace; symlinked `/usr/local/bin/ollama`.

---

## 6. Search, bot, and pricing (`search.py`, `tgbot.py`, `pricing.py`, `categories.py`)

- **Cross-platform fan-out:** `search.py` launches all 5 tracked apps in parallel (`ThreadPool`); results ranked by `effective` price (`pricing.py`: listed price − best `codes.yaml` offer − delivery fee).
- **Matching:** `token overlap ≥ 0.5` (`fuzzy`); optional semantic lift via `embeddings` table (`blend = max(token, semantic)` — adds candidates, never demotes; endpoint down / `semantic_matching: false` → exact historical token behavior).
- **Telegram bot (`tgbot.py`):**
  - `/watch <product>` → `keyword_watches` (chat-level); `/unwatch <product>` deactivates (history preserved).
  - `/digest` → today's cheapest per category (`store.today_cheapest_by_category`) + Demand Radar DPI top-5 (`demand.dpi_table`).
  - `WatchPusher` pushes when crawl/search results match active watches; rate-capped (`alert.rate_cap` pushes/hour + 6h per-watch cooldown via `last_alerted_ts`); restart-proof.
- **Categories (`categories.py`):** keyword classifier; ordered rules; feeds `category` column and `categories` stats.

---

## 7. Product-Space Intelligence pipeline (`src/product_space.py`, `src/product_vectors.py`, etc.)

Evidence: `PRODUCT_SPACE_PLAN.md`, `IMPLEMENTATION_LOG.md`, M1–M7 references.

- **M1 (`product_space.py`):** `load_product_space()` — reads `inventory/inventory_<app>.db.inventory_catalog` UNION `deals.db.catalog_snapshots` (latest per SKU fallback); excludes vouchers; attaches parsed fields (`product_fields.parse_name`); runs entity-resolution (exact canonical key → within-brand `match_score` → pack/variant veto → semantic confirm fallback; semantics never override veto). Provenance: every row carries `app/store_id/sku_key/inventory_db`.
- **M2 (`product_vectors.py`):** attribute + commercial vectors per product group (price/density normalized; `demand.dpi_table` mean; store/app coverage; churn flags). `--csv` → `exports/product_vectors.csv`.
- **M3 (`detect_assortment_gaps` / `assortment_gaps.py`):** cross-app gaps (present on some apps, not all).
- **M4 (`density.py` / `product_density`):** per-category density + insufficient / stale coverage guards.
- **M5 (`detect_gaps` / `gaps.py`):** internal/attribute gap scoring on top of density guards.
- **M6 (`opportunities.py` / `score_opportunities`):** `gap_strength × DPI × coverage × churn` scoring with provenance + validation codes; `--persist` writes to `deals.db.opportunities`.
- **M7 (`opportunity_report` / `opportunities.py`):** `run.py --opportunity-report [--limit N]` — latest persisted snapshot.

---

## 8. Semantic embeddings (`src/embed.py`, `.tools/ollama/`)

- **NVIDIA (default):** `nvidia/llama-nemotron-embed-vl-1b-v2` @2048 dims; `ai.embedding_base_url` + `NVIDIA_Build_API_KEY`; asymmetric (`corpus=passage`, `query=query`); batch 1000; 50 req/day free tier (`X-RateLimit-Limit`). Cache: additive `embeddings` table (keyed `model+dims`); backfill journaled `logs/embed_backfill.log`.
- **Local Ollama (opt-in):** `ai.embedding_provider: "ollama"`; `.tools/ollama/ollama-global` binary; `embeddinggemma-300m` @768 dims; server HOME `.ollama_home/`; `embedding_batch: 256` is optimum (throughput flat ~8 items/s; B≥512 kills runner). `.ollama/` models ~621MB total.
- **Backfill commands:** `--embed-catalog [--limit N]` (NVIDIA); `--similar <phrase> [--limit N]` (offline lexical + stored-vector expansion); `scripts/test_embeddinggemma.py` (self-managing local backfill + demo queries); `scripts/compare_embeddings.py` (gemma vs NVIDIA agreement); `scripts/embed_3d_map.py` (semantic explorer → `exports/embedding_map.html` / `embedding_map_gemma.html`).
- **Catalog re-key guard (rejected 09-05):** brand-sibling names (`Coke Zero` / `Coke`) cosine above genuine relabels; semantic catalog re-key rejected per `AGENTS.md`. Watchlist key-rotation handled via exact `(name,price)` pair reconciliation, not embeddings.

---

## 9. Dashboard (`run.py --ui` → `http://127.0.0.1:8787`)

Evidence: `README.md`, `AGENTS.md` endpoints list.

- **Features panel (`/features`):** spawn/terminate any repo feature (`monitor`, `bot`, `--demand`, `demo`, `inventory sweeps`) as managed child processes. Editable `args` spec per feature; server whitelists flags against spec (unknown flags rejected 400, never forwarded). `localStorage` persists last-used values. `STOP ALL /shutdown` reaps all children.
- **Endpoints:**
  - `/status` — live event bus (`fkind="gate" | "skip" | "boost"` for WAF failover).
  - `/categories`, `/searches`, `/search/<id>` — bot/search analytics.
  - `/demand`, `/heatmap?store=`, `/eta`, `/qc` — DB-backed Demand Radar.
  - `/db`, `/db/<db>/<table>` — read-only browser over all sqlite files (`deals.db`, `inventory/*.db`).
  - `/semsearch?q=` — lexical search; `/semsearch?seed=` — stored-vector expansion (`gemma` / `google` / `nematron` silos).
  - `/location`, `/location/presets`, `/location/locality`, `/location/corridor` — interactive working-area editor (regenerates `geo.corridor`, `demand.locality`, `search.station` in `config.yaml` with both loaders validated before atomic write).
  - `/ai/status`, `/ai/explain`, `/ai/explain/followup`, `/ai/methodology`, `/ai/focus` — optional LLM assistant (`src/ai_assist.py`); provider = any OpenAI-compatible endpoint (`ai:` in `config.yaml`) or local Ollama (keyless); `/ai/explain` persists full analysis as markdown to `exports/ai_explain_<stamp>.md`; `/ai/explain/followup` appends Q&A to saved file; `/ai/methodology[/apply]` and `/ai/focus[/apply]` enforce suggestions against `INT_PARAMS` whitelist (only `demand:` knobs writable). No arbitrary CLI execution.

---

## 10. Data model (`deals.db` + `inventory/*.db`)

Evidence: `src/store.py` schema (`_SCHEMA`), `AGENTS.md` repo map.

### `deals.db` (main sqlite; WAL mode)

| Table | Purpose | Key invariants |
|-------|---------|----------------|
| `price_obs` | Price history per `(app, store_id, sku_key)` | Rolling window (`usual_price()` excludes newest row; used for alert reference price). `category` backfilled. |
| `alerts` | Glitch events | `mrp` column (additive, backfilled); `reason` + `score`. |
| `darkstores` | Resolved stores per app | `lat/lon/label/eta_min`; `ON CONFLICT` upsert. |
| `watchlist` | Active + inactive SKU probe sets | `collections` (CSV labels: `home`, category names, `q:<term>`); `score DESC` orders; `first_seen_ts` backfilled; `is_digital_voucher` flag; `active` set by sweep (overflow = 0). Never deletes. |
| `stock_obs` | Per-cycle stock observations | `in_stock` (1/0/`NULL` — `NULL` = unknown/parse failure); `price`/`mrp`/`eta_min`; `source` (`home`/`collection`/`search`); `catalog_version` migration. |
| `oos_events` | Debounced out-of-stock events | `kind` (`oos` / `vanished`); `started_at` (first zero read); `ended_at`; `snapshots` (consecutive zero reads when open/closed); `restock_trigger`. Restart-proof rebuilt from `trailing_oos_streak`. |
| `searches` | Search query archive | `query`, `source` (`telegram`/`dashboard`/`cli`), `elapsed`, `n_results`, `top_*`. |
| `search_results` | Per-search result rows | `rank`, `platform`, `name`, `category`, `match`, `mrp`, `listed`, `discount`, `code`, `net`, `delivery`, `effective`, `url`, `note`. |
| `keyword_watches` | Telegram watch phrases | `chat_id`, `keyword` (lowercase); `created_ts`; `active`; `last_alerted_ts` (6h cooldown + rate cap). Deactivation only; rows kept. |
| `catalog_snapshots` | Full-catalog sweep snapshots | `(ts, app, store_id, sku_key)`; `name`, `price`, `in_stock`, `collections`. Idempotent per `(ts, sku)`. |
| `catalog_events` | Snapshot diff results | `kind` (`new`/`delisted`); pair reconciliation (`name,price`) excludes re-keys; mass-absence (<70% pair count) skips diff. |
| `embeddings` | Semantic vector cache | Keyed `(model, dims, name)`; `vector` (BLOB/text). Additive — provider switch re-keys cleanly. |
| `opportunities` | M7 persisted opportunity snapshots | Scored opportunity records (`gap_strength`, `DPI`, `coverage`, `churn`, `provenance`). |

### `inventory/inventory_<app>.db` (per-app; lazy-created by `Store`)

- `inventory_catalog` table: `id`, `ts`, `app`, `store_id`, `sku_key`, `name`, `price`, `mrp`, `in_stock`, `url`, `collections`, `category`, `raw_json`, `raw_json_truncated` (0/1), `raw_json_bytes`. `raw_json` capped at 16 KB (`_RAW_JSON_CAP`); truncated flag distinguishes capped from genuinely complete. `derive_product_url()` builds Blinkit `/prn/<slug>/prid/<id>` from `raw` payload when `url` absent.
- `catalog_snapshots` also written to `deals.db` (operational); inventory DB is the complete per-product record.

---

## 11. File map (current)

Evidence from `ls` and `AGENTS.md` repo map:

```
qcom-scraping/
  ARCHITECTURE.md          this file (updated 2025-09-08)
  README.md                 run guide + glossary (linked before contributing)
  GUIDE.md                  first-run + interpretation guide
  AGENTS.md                 multi-agent rules; invariant list; adapter state table
  DEMAND_RADAR.md            phase design + live status + proxy plan
  IMPLEMENTATION_LOG.md     single milestone log (M1-M7); never per-phase files
  PRODUCT_SPACE_PLAN.md     M1-M7 design + accepted/rejected decisions
  config.yaml               all tunables; miniyaml-compatible; secrets in .env only
  codes.yaml                user-editable delivery fees + offer codes
  run.py                    entrypoint; ALL CLI flags; feature catalog with editable args spec
  .env / .env.example       secrets (NVIDIA_Build_API_KEY, AI_API_KEY, etc.)
  deals.db                  main sqlite (WAL); all persistent data
  deals.demo.db             scratch DB for --demo (NEVER touches real DB)
  exports/                  locality JSON, embedding maps, DPI CSV, AI explain reports
  inventory/                per-app DBs + inventory_catalog snapshots
  inventory_milestones.md   inventory pipeline milestones
  docs/                    APK reverse findings (zepto, swiggy, blinkit); quick-commerce API vetting
  apks/                    APK files (gitignored; too large)
  .tools/ollama/            workspace-local Ollama binary; .ollama/ models; .ollama_home/ server
  .venv/                    Python environment (numpy / sklearn / plotly / plotly for embed_3d_map)
  src/                     core modules (see below)
  src/adapters/             7 adapters + base + demo
  scripts/                  self-managing scripts: live_sweep, test_embeddinggemma, compare_embeddings, embed_3d_map, bench_ollama_batch, embed_gemini_resume, embed_3d_map
  tests/                    test files
  backups/                  DB backups (deals.db.bak-*)
```

### Key `src/` modules

| File | Role | Key functions / notes |
|------|------|-----------------------|
| `run.py` | Entrypoint; CLI parsing (`_flag_*` helpers); `run()` dispatches all paths. | `--check` (config + adapter sanity); `--demo` (scratch DB); `--search`, `--bot`, `--ui` (with `--bot`/`--monitor`), `--once`; `--map-locality`, `--build-watchlist`, `--demand`, `--store-inventory`, `--catalog` (catalog inventory mode); `--embed-catalog`, `--similar`; `--product-fields`, `--product-space`, `--product-vectors`, `--detect-assortment-gaps`, `--product-density`, `--detect-gaps`, `--score-opportunities`, `--opportunity-report`, `--temporal-analysis`, `--validate-opportunities`, `--opportunity-pipeline`; `--demand-report`, `--catalog-report`; `--qc-status`; `--purge-vouchers`; feature catalog with `args` whitelist. |
| `src/store.py` | SQLite persistence (main class `Store`). | Schema (`_SCHEMA`), migrations (additive only), `record()`, `record_alert()`, `usual_price()` (excludes newest), `upsert_darkstore()`, `watchlist_for_store()`, `record_stock_obs()`, `open/close_oos_event()`, `trailing_oos_streak()`, `catalog_snapshot_list()`, `catalog_event_list()`, `record_catalog_snapshot()`, `catalog_prev_snapshot()` (pair reconciliation), `record_catalog_events()`, `deactivate_watchlist_except()` / `deactivate_watchlist_skus()`, `inventory_catalog` upsert (`_derive_product_url()`, `raw_json_truncated`), `purge_vouchers()`, `add/remove_watch()`, `today_cheapest_by_category()`. |
| `src/adapters/base.py` | Adapter interface + anti-block helpers. | `Adapter` class (`PROBE_URL`, `PROBE_TERMS`, `_rotate()`, `_browser_catalog_full()`); `load_proxies()`; `fresh_user_agent()`; `norm_price()`; `_stock_state()`; `_parse_catalog()`; process-group timeout + reap; stderr/stdout drain threads; `on_batch` incremental persistence. |
| `src/adapters/blinkit.py` | Blinkit adapter. | Overrides `APP_URL` / `HEALTH_URL`; `search()` merges `--pre` shelf results (`Cigarettes` shelf: 15119 → l1_cat 1948; `Cigar` 62439 → 3466; `Lighters` 383144 → 7778; `Rolling Needs` 11644 → 1982; `Paan Masala` 127957 → 2517). Text search yields accessories only; shelf provides real tobacco. |
| `src/adapters/zepto.py` | Zepto adapter. | `HEALTH_URL` = search route; `search()` uses signed responses. |
| `src/adapters/instamart.py` | Instamart adapter. | `APP_URL` = `instamart.in`; inner-container pagination (`POST /api/instamart/category-listing/filter/v2`); `--im-term` locality binding; `--mirror-page-ms` / `--mirror-stride`. |
| `src/adapters/amazon.py` | Amazon adapter. | Search + price-track. |
| `src/adapters/flipkart.py` | Flipkart adapter. | Search + price-track. |
| `src/adapters/jiomart.py` | Jiomart adapter. | IP-locked store resolution; `search()` works; rate-limited. |
| `src/adapters/bigbasket.py` | Bigbasket adapter. | `enabled: false`; Akamai 403. |
| `src/adapters/demo.py` | Demo adapter. | Injected glitch; scratch DB only. |
| `src/adapters/trackers.py` | Amazon / Flipkart price trackers. | `Tracker` class; `crawl()` for price tracking. |
| `src/locality.py` | Demand phase 1. | `anchor` grid + `landmark` seeds; `discover_darkstores()`; `resolve_store()`; `cluster_darkstores()`; `build_corridor()`; `rotate_anchor_term()` (process-local rotation was broken 09-02; fixed by passing config landmark names directly — `im_term` for landmark anchors = config name; grid anchors rotate through config names). `src/locality.py` self-test (`python3 -m src.locality`). |
| `src/watchlist.py` | Demand phase 2. | `WatchlistBuilder`; `build_for_store()` (one session/store); `build_all_stores()`; `catalog_inventory_mode()`; `catalog_inventory_mode()` deep-cats (`--catalog`); `pair_reconcile()` for snapshot diff. Self-test (`python3 -m src.watchlist`). |
| `src/prober.py` | Demand phase 3. | `Prober` class; `run_round()`; `observe_store()`; `record_obs()`; `reconcile_stale_events()`; `update_canary_state()`; `freeze_suspect()`; `update_watchlist()`; `build_report()`. Self-test (`python3 -m src.prober`). |
| `src/demand.py` | Demand phase 4. | Pure sqlite functions: `dpi_table()`, `heatmap()`, `eta_curve()`, `demand_summary()`, `export_csv()`. |
| `src/search.py` | Search engine. | `SearchEngine` class; `search()`; `execute_parallel()`; `load_product_space()` call for entity resolution; `match_score()`; `blend_score()` (max of token + semantic). |
| `src/pricing.py` | Effective price calculation. | `PricingEngine`; `calculate()`; reads `codes.yaml`. |
| `src/categories.py` | Keyword classifier. | `categorize()`; ordered rules. |
| `src/dashboard.py` | Dashboard server. | Flask-like endpoints; `start_feature()` / `stop_feature()` / `get_feature_status()` / `get_feature_log()`; `FEATURE_CATALOG` with editable `args` whitelist. |
| `src/tgbot.py` | Telegram bot. | `Bot` class; `/watch`, `/unwatch`, `/digest`, `list_watches()`; `WatchPusher` (matches search results / crawl batches against `keyword_watches`; rate-capped + cooldown); `start()` / `poll()` loop. |
| `src/orchestrator.py` | Monitor loop scheduler. | `Orchestrator` class; `schedule` config (`stagger`/`jitter`/`waf_failover`); `run_cycle()`; `WafFailover` strike ledger (`N` consecutive empty/errored → gate for `gate_cooldown_cycles`; other app gated → `blinkit_priority_extra` extra passes); event emission (`/status` shows `gate`/`skip`/`boost`). `protected_apps` = `blinkit`. Self-test (`python3 -m src.orchestrator`). |
| `src/events.py` | Thread-safe event bus. | `EventBus`; `publish()` / `subscribe()`; feeds `/status`. |
| `src/alert.py` | Alert fan-out. | `AlertPusher`; desktop + telegram + log (`deals.log`); carries reference price (`mrp` / `usual_price`). |
| `src/detect.py` | Glitch detector. | `GlitchDetector`; `score()`; `z-score` against local per-store baseline. |
| `src/honey.py` | Honey-pot SKU basket. | `HoneyBasket`; `load()`; `check()`. |
| `src/miniyaml.py` | YAML subset parser. | Stdlib fallback when `PyYAML` absent; parses `config.yaml`. |
| `src/ai_assist.py` | AI assistant. | `AIExplain`; `explain_demand()`; `suggest_focus()`; `suggest_methodology()`; `INT_PARAMS` whitelist enforcement; output saved to `exports/ai_explain_<stamp>.md`. |
| `src/embed.py` | Embedding client. | `EmbedClient`; NVIDIA (`urllib`) + local Ollama (`requests`); batch 256 (Ollama) / 1000 (NVIDIA); `embeddings` table read/write; `search_vectors()`; `backfill_catalog()`. Self-test (`python3 -m src.embed` — fake transport). |
| `src/inventory.py` | Catalog inventory module. | `InventoryCapture`; `run_sweep()`; `build_catalog()`; `resolve_location()` (uses `lat`/`lon` override from `--lat`/`--lon` or `deals.db.darkstores`); `store_inventory()` writes both `inventory_catalog` (inventory DB) and `catalog_snapshots` (deals.db); captures `raw_json` with cap/truncated flag. |
| `src/product_fields.py` | Grocery product parser. | `parse_name()` — brand, pack_value/pack_unit, `is_multipack`, variant, `unit_base`, `unit_price`, `parse_status`. Self-test (`python3 -m src.product_fields`). |
| `src/geo.py` | Geo layer. | `GeoResolver`; `resolve_darkstore()`; `build_grid()`; `anchor` + `landmark` definitions. |
| `scripts/live_sweep.py` | One-shot real-glitch hunt. | Runs full crawl across stations; outputs to terminal + file. |
| `scripts/test_embeddinggemma.py` | Local Ollama demo. | Starts `ollama serve`, pulls `embeddinggemma`, runs demo queries. |
| `scripts/compare_embeddings.py` | Quality comparison. | Compares `embeddinggemma` vs NVIDIA neighbors (numpy); needs `.venv/bin/python`. |
| `scripts/embed_3d_map.py` | Inventory atlas. | `PCA-50` → `k-means` → `PCA-3` / `PCA-2` (`UMAP` optional); renders interactive `exports/embedding_map.html` / `embedding_map_gemma.html`. Self-test with `--sample N`. |
| `scripts/bench_ollama_batch.py` | Batch-size benchmark. | Confirms B=256 optimum; B≥512 kills runner (connection reset by peer). |
| `scripts/embed_gemini_resume.py` | Gemini backfill. | `gemini-embedding-001` @768; `embedding_send_extras: false`; batch 100 + 16s pause ≈ 94 RPM/key; 4 keys ≈ 4k names/day; resets midnight PT. |

---

## 12. Current status (evidence-based)

Evidence: `IMPLEMENTATION_LOG.md`, `AGENTS.md` phase table, `README.md`, `DEMAND_RADAR.md`, `run.py --check` output (verified clean), `git status` (clean at `main` `b7f3502`), `node --check tools/pw_catalog.js`, `python3 -m py_compile` on touched files.

- **P1 locality:** BUILT (`locality.py` + `geo.py` + `exports/locality_*.json`).
- **P2 watchlist:** BUILT (`watchlist.py`; `--catalog` deep-cats; pair reconciliation; voucher purge; `catalog_events` new/delisted; `inventory.py` full sweep).
- **P3 prober:** BUILT (`prober.py` + `store.py` `oos_events`; debounce; streak reconstruction; vanished guard; suspect-cycle freeze; stale event reconciliation; `catalog_inventory` snapshot + event pipeline).
- **P4 analysis:** BUILT 08-22 (`demand.py`; DPI rollups; heatmap; ETA curve; `demand_summary`; CSV export; `/demand`, `/heatmap`, `/eta` endpoints; `--demand-report` / `--catalog-report`).
- **P5 hardening:** WIRED (`proxy` plumbing: config + env + adapter `pick_proxy()` + `pw_catalog.js` `--proxy` + process-group isolation). **PENDING:** procure Mumbai-exit residential proxy pool; validate IP↔anchor coherence live (jiomart store change per IP); stagger/jitter + global req/hr cap + backoff per `DEMAND_RADAR.md` Phase 5.
- **Product Space M1–M7:** M1 (union layer) BUILT; M2 (vectors) BUILT; M3 (assortment gaps) BUILT; M4 (density) BUILT; M5 (detect-gaps) BUILT; M6 (`score-opportunities` + `--persist`) BUILT; M7 (`opportunity-report` + temporal analysis + validation) BUILT.
- **Embeddings:** NVIDIA provider verified (batch 1000, 39 requests / 14.5 min for 44,487 names). Ollama (`embeddinggemma`) verified locally (`scripts/test_embeddinggemma.py`; `scripts/compare_embeddings.py`). `embeddings` table additive.
- **Dashboard:** All listed endpoints verified; feature panel editable args spec enforced; location editor validates both YAML loaders + backups to `/tmp`; AI panel whitelist enforced (`INT_PARAMS`); `/shutdown` reaps children.
- **Adapters:** All 7 present (`amazon`, `flipkart`, `blinkit`, `zepto`, `instamart`, `jiomart`, `bigbasket`). `bigbasket` `enabled: false`. `jiomart` enabled but with documented block. `amazon`/`flipkart` search + price-track working.
- **Schema:** Additive migrations verified (`category` column on `price_obs`; `mrp` on `alerts`; `catalog_version` columns; `restock_trigger` / `voucher_type` / `promotional_context` on `stock_obs`; `is_digital_voucher` / `first_seen_ts` on `watchlist`; `first_seen_ts` backfill; `first_seen_ts` / `catalog_version` / category backfills present).

---

## 13. How to read the updated architecture

This file is the evidence-based source of truth. The `ARCHITECTURE.md` update (2025-09-08) was produced by inspecting:
# qcom-scraping v2 config — tunables only. Secrets live in .env (never commit it).

schedule:
  # Base seconds between full cycles. Jittered +/- 30% at runtime.
  cycle_seconds: 300
  # Invert the bot pattern: crawl more in off-peak. Multiplier applied to
  # cycle_seconds during quiet_hours (smaller = faster crawling).
  offpeak_speedup: 0.4
  quiet_hours:
    start: "23:30"
    end: "07:30"
  # WAF failover (Blinkit-as-fallback): when Zepto/Instamart get WAF-gated
  # (consecutive empty/errored crawls), back them off and lean on Blinkit by
  # giving it extra per-station passes so coverage doesn't crater. Blinkit is
  # the resilient source — its APK has no AWS WAF and no request signature.
  waf_failover:
    enabled: true
    empty_strikes_to_gate: 3        # consecutive empty/err crawls => app gated
    gate_cooldown_cycles: 4         # cycles to back off a gated app
    blinkit_priority_extra: 1       # extra blinkit passes/cycle while any other app gated
    protected_apps: [blinkit]       # never auto-gate these (the fallback)
  # Rotating coverage queries for the glitch monitor (deal finder): one is
  # searched per app per cycle (round-robin), diversifying price_obs beyond
  # the dairy-first home carousel + honey canaries. [] = off.
  crawl_terms: ["cigarettes", "chips", "shampoo", "usb drive", "cold drinks", "detergent"]

geo:
  # Mumbai corridor we watch. Each point resolves to the nearest dark store.
  corridor:
    - { station: "Borivali",  lat: 19.23, lon: 72.856 }
    - { station: "Kandivali", lat: 19.207, lon: 72.851 }
    - { station: "Malad",     lat: 19.186, lon: 72.848 }
    - { station: "Goregaon",  lat: 19.166, lon: 72.852 }
    - { station: "Andheri",   lat: 19.119, lon: 72.846 }
adapters:
  # Browser-intercept adapters need Playwright + a chromium build.
  # Set enabled:false if you only want the trackers + engine to run.
  blinkit:   { enabled: true,  app: "blinkit" }
  instamart: { enabled: true,  app: "instamart" }
  zepto:     { enabled: true,  app: "zepto" }
  # QC-first focus (08-22): amazon/flipkart tracking off by default.
  # Flip back to true to resume e-commerce price tracking.
  trackers:  { enabled: false }
  # Expansion (08-31): wired + routes verified, then traced live. Both stay
  # OFF — the blockers are ENVIRONMENTAL (not fixable in code from here):
  #  - bigbasket: Akamai Bot Manager 403s our headless browser on EVERY route
  #    and UA (curl passes, real browsers don't). No bbnow/alt domain exists.
  #    Needs a residential proxy or a real-Chrome fingerprint to revisit.
  #  - jiomart: extraction WORKS (12+ products, stock, mrp, store ids — see
  #    pw_catalog.js), but the QC darkstore is resolved SERVER-SIDE from the
  #    request IP (delivery-promise returned the same store at an identical
  #    820.3851 m across runs whose app_geolocation cookie held 3 different
  #    values, and even pre-cookie). So it CANNOT be steered to Demand-Radar
  #    anchors (violates "location is enforced, not assumed"); and its search
  #    endpoint rate-limits hard (~4 rapid probes -> empty, ~2.5 min recovery).
  #    Usable ONLY for machine-location --store-inventory if ever enabled.
  # DROPPED 08-31 (evidence, do not re-add blindly): dmart (web login-gates;
  # no fake accounts) and amazon_now (Amazon Now is app-only — web routes
  # serve generic search or the empty legacy Fresh shell; would pollute
  # price_obs with non-grocery results).
  bigbasket: { enabled: false, app: "bigbasket" }
  jiomart:   { enabled: false, app: "jiomart" }

anti_block:
  # Rotate these per cycle to defeat simple rate fingerprints.
  rotate_user_agent: true
  rotate_install_id: true
  # Pre-installed Playwright (Node) + Chromium used by the browser-intercept layer.
  node_path: "/Users/Mitesh Gada/Documents/Projects/Do not delete folder/node_modules"
  pw_browsers_path: "/Users/Mitesh Gada/Documents/Projects/Do not delete folder/.pw-browsers"
  # Optional residential proxy pool (env: PROXY_URL or list here).
  proxies: []
  # Honey-pot basket: SKUs whose TRUE price we hardcode. Any deviation = glitch.
  honey_pot:
    - { app: "blinkit",   query: "amul milk 1l",    true_price: 66 }
    - { app: "blinkit",   query: "lays 90g",        true_price: 20 }
    - { app: "instamart", query: "maggi 12 pack",   true_price: 168 }
    - { app: "zepto",     query: "amul gold 1l",    true_price: 72 }
  # Stream the crawler's per-visit progress (home / category / search term ->
  # cumulative SKUs, onboarding steps) live to the log while a sweep runs,
  # instead of staying silent until the multi-minute store sweep finishes.
  # Surface it via the dashboard Features > Build watchlist > log (or terminal).
  stream_progress: true

detect:
  # Glitch scoring thresholds.
  honey_deviation_pct: 25      # >25% off true price on a honey SKU => instant
  stat_zscore: 2.5             # statistical outlier vs store baseline
  min_margin_off_mrp: 40       # % off MRP to even consider
  max_price: 5000              # ignore silly high prices

alert:
  desktop: true                # macOS notification
  telegram:
    enabled: false             # set true + fill .env to push to phone
  log_file: "deals.log"
  max_alerts_per_hour: 30
  # Keyword-watch pushes (/watch in the Telegram bot): max proactive watch
  # alerts per hour across all chats. 0 turns proactive watch pushes off.
  rate_cap: 10

db: "deals.db"

# Cross-platform price search (Telegram bot / --search CLI)
search:
  station: "Andheri"          # dark-store anchor for qcomm searches
  # QC-first focus (08-22): quick-commerce platforms only. To include
  # e-commerce in price comparisons, use:
  #   platforms: [blinkit, zepto, instamart, amazon, flipkart]
  platforms: [blinkit, zepto, instamart]
  per_platform_limit: 3       # top matches kept per platform
  min_match_score: 0.5        # fuzzy token-overlap threshold

codes_file: "codes.yaml"      # delivery fees + offers knowledge base

# Demand Radar (see DEMAND_RADAR.md): per-darkstore stock-out intelligence.
demand:
  enabled: true
  locality:
    # widened 09-01 to span full Borivali→Andheri corridor so the locator
    # fans out across distinct Instamart darkstores instead of one Goregaon pocket
    name: "Corridor · Borivali-Andheri"
    bbox:
      min_lat: 19.119
      max_lat: 19.230
      min_lon: 72.820
      max_lon: 72.880
    grid_step_m: 900
    landmarks:
      # explicit form — resolves exactly, no preset matching:
      - { name: "Andheri", lat: 19.119, lon: 72.846 }
      - { name: "Goregaon", lat: 19.166, lon: 72.852 }
      - { name: "Borivali", lat: 19.230, lon: 72.856 }
  # discovery sweep tuning
  min_points_before_early_stop: 6   # probes before saturation-stop may trigger
  saturation_stop: 4                # stop app sweep after N probes w/o new store
  # watchlist builder (phase 2)
  categories_per_store: 30          # DOM category pages visited per store (broad)
  # Empty staple_queries => the built-in UNBIASED broad-coverage default list
  # in src/watchlist.py (grocery + paan/tobacco + wellness + adult + electronics
  # + household + pharma). Set a list here to override with your own terms.
  staple_queries: ["maggi noodles", "cup noodles", "yippee noodles", "poha", "ready to eat"]
  # Unbiased harvesting: when true, the builder keeps EVERY discovered SKU
  # (no truncation to the active cap) and never auto-deactivates the overflow.
  # The active cap below only limits what the prober re-probes by search;
  # passive category/home observations still capture the full catalog.
  unbiased_harvest: true
  watchlist_max_per_store: 4000
  # stock prober (phase 3)
  probe_interval_sec: 60           # per-store cycle target; jittered, off-peak faster
  probe_terms_max: 40               # watchlist search terms re-probed per store/cycle
  oos_debounce_snapshots: 6         # consecutive OOS reads before an event opens
  vanished_cycles: 6                # missed successful sweeps before 'vanished'
  stock_canary_queries: ["amul milk", "eggs"]   # must return in-stock items
  suspect_flip_min: 10              # mass-flip soft-block guard: >= N flips...
  suspect_flip_pct: 50              # ...>= % of previously-in-stock seen SKUs
  # Category-rail de-biasing (watchlist builder + demand prober): QC apps
  # order their category rail dairy/bread/eggs-first, so a plain "first N
  # categories" sweep over-samples milk. These case-insensitive substrings
  # skip matching category labels; freed queue slots go to the NEXT
  # categories (snacks, personal care, electronics, ...). Empty list = off.
  skip_categories: []
  # Voucher de-biasing (09-02): digital vouchers / gift cards (Steam, Roblox,
  # Xbox, Blinkit Gift Card, retail vouchers…) are NOT commodities — their
  # "stock-outs" are code-pool replenishments that skew Demand Radar DPI.
  # true = the watchlist builder drops them at build time, the prober skips
  # them in every sweep, and DPI rollups ignore them. Run
  # `python3 run.py --purge-vouchers` to remove already-recorded voucher rows.
  exclude_vouchers: true
  # Catalog-inventory mode (--build-watchlist --catalog): upper bound on
  # category visits per full sweep — the queue drains naturally at "all
  # discovered links" (incl. one-hop sub-categories via --deep-cats); this cap
  # just keeps a pathological app from never terminating. Full sweeps take
  # ~20-60 min/store: run ONE store at a time, never beside other crawls.
  catalog_max_categories: 300
  # Silent-hour scheduling (09-02): the prober loop may only START rounds in
  # the local hours listed here, so the rate-limit budget is spent where the
  # history is thin. The Aug 24–Sep 1 stock_obs history has ZERO observations
  # in hours 02–10 and 15–16 — the demand curve's OOS-onset windows land in
  # exactly those gaps, so onsets get recorded late (started_at = first read
  # after the gap) and the onset heatmap is biased to sweep hours. Default
  # "0-23" = all hours (no behaviour change): leave the Demand prober feature
  # running 24/7 and every hour is covered. To concentrate on the missing
  # windows, set e.g. ["2-10", "15-16"] — the loop then idles outside them
  # and sweeps only inside, so silent hours finally get probes. Ranges are
  # inclusive ("H-H"); single hours as "H"; wrap-around ranges not supported.
  sweep_windows: "0-23"
  # future phases (analysis/heatmap) will read these:

ui:
  port: 8787                  # live dashboard: http://127.0.0.1:8787

# Optional AI assistant (dashboard panel). Any OpenAI-compatible chat API;
# the key goes in .env as AI_API_KEY — never here. Point base_url at a local
# keyless server instead, e.g. Ollama: http://127.0.0.1:11434/v1
ai:
  enabled: true
  base_url: "https://generativelanguage.googleapis.com/v1beta/openai/"                  # empty = https://api.openai.com/v1
  model: "gemini-3.5-flash-lite"
  # Reasoning models burn tokens thinking before answering — give them room.
  # If a response still truncates (finish_reason=length), chat() auto-retries
  # once with 4x this budget.
  max_tokens: 65000
  # Semantic product matching (embeddings, src/embed.py): lifts search/watch
  # matches whose meaning fits but whose words don't ("diet coke" ->
  # "Coca-Cola Zero Sugar 750ml"). Set semantic_matching: false to fall back
  # to token-only matching.
  # 09-05 PROVIDER SWITCH: embeddings moved Gemini -> OpenRouter (free tier),
  # then to NVIDIA-hosted nvidia/llama-nemotron-embed-vl-1b-v2 (integrate.api.
  # nvidia.com). Gemini free quota counted EACH INPUT ITEM as its own request
  # (100-name batch = 100 RPM + 100 RPD; 1,000 RPD/key -> ~9 days for 44k
  # names). OpenRouter counted a WHOLE BATCH as ONE request (1000 names/
  # request, 44,487 names in 39 requests / 14.5 min) but its free tier is
  # 50 requests/day shared across accounts. NVIDIA's trial NIM is RPM-capped
  # (~40 RPM, no hard daily request wall) and accepts batches of 2000. The
  # model is ASYMMETRIC: corpus names embed as "passage", live queries as
  # "query" (transient, never persisted). Gemini rows already banked
  # (gemini-embedding-001 @768) stay untouched; Nemotron rows @2048 are
  # additive (composite PK model,dims,name). embedding_input_type / sem_lo /
  # sem_hi are per-model overrides; defaults live in src/embed.py.

```


## Assistant

<thinking>


**Planning core architecture review**
</thinking>

**Tool Call: "sed -n '1,300p' qcom-scraping/ARCHITECTURE.md; sed -n '1,260p' qcom-scraping/run.py; rg -n \"CREATE TABLE|def (dpi_table|heatmap|eta_curve|demand_summary|score|detect|load_product_space|cluster|opportunity)\" qcom-scraping/src qcom-scraping/scripts"**
Status: Completed

Terminal:
```
# qcom-scraping v2 — Architecture

Updated 2025-09-08 to reflect current repo state (evidence from `AGENTS.md`, `src/`, `run.py`, `config.yaml`, `deals.db` schema, and `tools/pw_catalog.js`).

> **Interactive architecture diagram (archify skill):** authored spec saved to `/tmp/qcom_arch.json` (showcase profile, 13 components covering adapters / browser intercept / geo-store / database / demand pipeline / search / product-space / embeddings / dashboard). The HTML render requires geometry adjustments (label overlap); the spec is the authoritative topology reference.

---

## 1. What this repo is

One browser-intercept crawler (`tools/pw_catalog.js`) shared by three live features:

1. **Glitch monitor** — per-darkstore price anomalies across the Mumbai corridor (Virar → Andheri).
2. **Price-search Telegram bot** (`--bot`) — cheapest effective price across 7 tracked apps with `/watch` keyword pushes (`WatchPusher`) and `/digest` daily summary.
3. **Demand Radar** (`--map-locality` → `--build-watchlist` → `--demand`) — per-store stock-out intelligence; phase 4 (DPI / heatmap / ETA) is **BUILT** (verified 08-22); phase 5 (proxy plumbing) is **WIRED end-to-end** but live validation with a Mumbai residential pool is still **PENDING**.

Plus the M1–M7 **Product-Space Intelligence** pipeline (`--product-space`, `--product-vectors`, `--detect-assortment-gaps`, `--detect-gaps`, `--score-opportunities --persist`, `--opportunity-report`, `--temporal-analysis`, `--validate-opportunities`, `--opportunity-pipeline`) and the optional **semantic-embedding** layer (`--embed-catalog`, `--similar` — NVIDIA `nvidia/llama-nemotron-embed-vl-1b-v2` @2048 dims + opt-in local Ollama `embeddinggemma-300m` @768 dims).

---

## 2. Core design invariants

- **The app is the API documentation.** We never guess endpoints. `pw_catalog.js` runs the real mobile web app in headless Chromium, intercepts its signed XHR/fetch calls, and replays them exactly (`request-signature`, `x-csrf-secret`, `x-api-key`, `device_id`, `session_id`). When paths rotate, the next page load rediscovers them.
- **Location is enforced, not assumed.** Each adapter seeds `localStorage.location`, rewrites `lat`/`lon` in cookies/requests, and drops cached `merchant` IDs. Apps that cache serving store server-side from the request IP (e.g. Jiomart) must match exit-IP to anchor geo; this is the acceptance test for Phase 5 proxies.
- **Vouchers are excluded from every demand surface.** `is_voucher_name()` (token match `voucher` / `gift card`) is used by watchlist builder, prober, DPI rollups, and purge (`--purge-vouchers`). Their "stock-outs" are code-pool replenishments, not demand.
- **Schema changes are additive only.** `CREATE TABLE IF NOT EXISTS` + `ALTER TABLE ADD COLUMN` with backfills (`_backfill_categories`, `_backfill_first_seen`). No drops/renames — other features read `deals.db` live.
- **One browser session per store per sweep.** The continuous loop (`--demand`) never spawns per-SKU processes. Catalog mode (`--catalog`) is the exception: it runs ONE full sweep per store and writes `catalog_snapshots` + `catalog_events` (`new`/`delisted`) via pair reconciliation (`name,price`). A snapshot whose pair count collapses to <70% of previous is recorded but its diff is **skipped** (mass-absence = crawl flake, not churn).
- **NULL ≠ OOS.** A failed parse/crawl writes `in_stock=NULL`; it must never become `0`. Scraper errors must not fabricate demand.
- **Delisting is snapshot-driven only (`catalog_events`).** A partial sweep or light prob round never produces `delisted`. The watchlist's `active=0` rows are kept (the discontinued archive); `oos_events` for `kind='oos'` are reconciled with `catalog_events`, not the reverse.
- **Restart-proof streaks.** `Store.trailing_oos_streak()` rebuilds from `stock_obs` history; `started_at` is the first zero read, never the threshold-crossing time.
- **Vanished ≠ OOS.** A SKU missing from successful sweeps but with prior `stock_obs` sightings opens `kind='vanished'` (not `oos`). A never-sighted SKU (catalog-built but never probed) is a coverage gap, not churn.
- **Suspect cycles freeze the machine.** Canary queries returning only-OOS or mass in-stock→OOS flip record observations but open/close nothing.
- **Silent-hour coverage matters.** `demand.sweep_windows` (local hours) gates loop starts; the Aug 24–Sep 1 history had zero observations in hours 02–10 and 15–16, so onset windows in those hours are biased. Keep `--demand` running 24/7 or set windows to fill them.

---

## 3. Adapter layer (`src/adapters/`)

All 7 adapters subclass `base.Adapter`. Each defines `APP_URL`, `HEALTH_URL` (override for apps whose home serves zero products — Zepto), `PROBE_URL`, `PROBE_TERMS`, and `name`. The adapter interface:

- `crawl(station, lat, lon)` → list of `{sku_key, name, price, mrp, url, in_stock}`.
- `search(query, lat, lon)` → search results (token overlap ≥ 0.5; optional semantic blend from `embeddings` table).
- `probe_point(station, lat, lon, im_term)` → single product-bearing probe; `PROBE_TERMS` fired in-session for catalog breadth beyond home carousel.
- `deep_sweep(station, lat, lon, categories, terms, deep_cats, skip, mirror_page_ms, tabs, on_batch)` → full watchlist sweep.

**Enabled apps and live state:**

| App | Adapter | Key behavior / fix date |
|-----|---------|------------------------|
| **Blinkit** (`blinkit.py`) | `blinkit` | `APP_URL` = category shelf routes (`/dc/`); text search (`/s/?q=`) serves **no tobacco** (server-side curated) — tobacco SKUs come from `--pre` shelf visit (`URL::LABEL`) merged into search results (`BlinkitAdapter.search`). Category regex fixed 09-02 (`(cn|category|categories|c|dc|sc)(/|$)`) — `dc/` routes yield ~300 products per shelf in warm sessions; old regex collapsed to home feed (~104 SKUs, all `collections=home`). Age gate is UI-only; crawler goes straight to shelf URLs. |
| **Zepto** (`zepto.py`) | `zepto` | `HEALTH_URL` overrides to search route (home serves no products for fresh sessions). Signing (`request-signature`, `x-csrf-secret`, `x-xsrf-token`, `x-api-key`, `device_id`, `session_id`) lives in web bundle chunks (`89411-*.js`, `88682-*.js`); crawler harvests already-signed responses — no forging needed. Hard gate is IP-reputation (403 WAF), not signature validation. Fixed 08-22. |
| **Instamart** (`instamart.py`) | `instamart` | Target is `instamart.in` (NOT `www.swiggy.com/instamart` — login-walled for our IP). Inner-scrollable container pagination (`POST /api/instamart/category-listing/filter/v2`) with advancing `items_offset` (stride 20); URL `pageNo`/`offset` are decoys. Mirror pagination (`--mirror-stride 20 --mirror-max-pages 80 --mirror-page-ms 900`) is default; `--scroll-rounds` is opt-in. `--im-term` passes locality term to modal binding. Subcategory routes (`/sc/<l0>/<l1>-<id>/t10`) matched by regex (`sc` added 09-02). |
| **Amazon** (`amazon.py`) | `amazon` | `amazon.in` search (DOM extraction). |
| **Flipkart** (`flipkart.py`) | `flipkart` | Search + price-track (`trackers.py`). |
| **Jiomart** (`jiomart.py`) | `jiomart` | **Enabled**, but block: store is resolved **server-side from request IP** (delivery promise identical at 820.3851 m across different `app_geolocation` cookie values). Client-side location seeding does nothing. Rate-limits hard (~4 rapid probes → empty; ~2.5 min recovery). Not anchor-steerable; at best a machine-location `--store-inventory` source. |
| **Bigbasket** (`bigbasket.py`) | `bigbasket` | `enabled: false`. Akamai Bot Manager 403 (`errors.edgesuite.net`) on every route + UA; curl passes, browsers don't. No `bbnow` domain resolves. Revisit requires residential proxy or real-Chrome fingerprint. |

**Adapter expansion notes (dropped/rejected):**
- `dmart` — dropped 08-31: web is login-gated; no fake accounts.
- `amazon_now` — dropped 08-31: Amazon Now IS live in Mumbai (expanded Sept–Nov 2025) but only in SELECT neighbourhoods; no standalone app; web routes serve generic search or empty Fresh shell. Would pollute `price_obs`.
- `demo` adapter (`demo.py`) — simulated source with injected glitch (`--demo`); runs against scratch `deals.demo.db` (NEVER touches real `deals.db`).

---

## 4. Browser-intercept layer (`tools/pw_catalog.js`)

- **Engine:** Playwright (pre-installed at `../Do not delete folder/node_modules` + `.pw-browsers`; wired via `config.yaml` `anti_block.node_path` / `anti_block.pw_browsers_path`).
- **Anti-block machinery (`base.py`):**
  - `MOBILE_UAS` — 4 mobile UAs (iPhone / Android / Pixel); `rotate_user_agent` toggle.
  - `fresh_install_id()` — 16-char plausible device ID.
  - `load_proxies()` / `pick_proxy()` — reads `PROXY_URL` env + `config.yaml` `anti_block.proxies`.
  - `_rotate()` returns `(ua, iid, proxy)`.
- **Geo seed (`pw_catalog.js` init):** seeds `localStorage.location`, rewrites `lat`/`lon` in cookies/request paths/query/body, drops cached `merchant`.
- **Deep-cats discovery (`--deep-cats`):** one-hop BFS (`sc` / `category` links) for sub-category shelf links. Catalog inventory mode (`--catalog`) uses this; `skip_categories` overrides to `[]` (no skips — a skipped shelf would fabricate delistings).
- **Mirror pagination (`--mirror-page-ms`, `--mirror-stride`, `--mirror-max-pages`, `--tabs`):** mirrors the visit's own captured listing POST (`apiHits` mirror pattern — session's own auth, no forging). `items_offset` advances (20 stride). `--tabs N` opens N concurrent tabs inside the SAME browser context (same `device_id`, one session/store).
- **Progress streaming (`anti_block.stream_progress`):** `stderr` lines (`[app_label] ...`) stream live; stdout carries batch JSON (`{"type":"batch","products":...}`) + terminal summary JSON (`{"products":...,"store_hint":...,"api_endpoints_seen":...}`). `on_batch` writes incrementally to sqlite.
- **Timeout / reap:** process group (`start_new_session`); timer kills group on timeout; reap watchdog kills grandchildren if process exits but browsers hold pipes.
- **Multi-tab (`--tabs N`):** intra-session concurrency (same `device_id`, same visit queue, each tab keeps own intercepted-api list + collection label). Cross-tab throttling possible; `--tabs 3 --mirror-page-ms 600` tested on Instamart.

---

## 5. Demand Radar pipeline (phases 1–4 built; phase 5 wired)

Evidence: `DEMAND_RADAR.md`, `AGENTS.md`, `src/locality.py`, `src/watchlist.py`, `src/prober.py`, `src/demand.py`, `run.py` flags (`--map-locality`, `--build-watchlist`, `--demand`, `--demand-report`, `--catalog-report`, `--store-inventory`, `--catalog`, `--catalog`, `--purge-vouchers`, `--qc-status`).

### Phase 1: Locality (`locality.py`)
- `anchor` grid + `landmark` seeds → resolve + cluster darkstores.
- `geo.corridor` regenerated by location editor (`/location` POST); validated with BOTH `miniyaml` loaders before atomic write; previous file backed to `/tmp`.
- `exports/locality_<name>.json` rotation pools per store.

### Phase 2: Watchlist (`watchlist.py`)
- Per-store SKU probe set: `home` harvest → DOM category click-through (`categories=...`) + staple searches (`terms=...`).
- Scored by search hits > home; `score DESC` orders active set.
- `catalog` mode (`--catalog`): ALL category links (`--deep-cats`), NO search terms, NO `skip_categories` (skipped shelf = false delisting). Writes `catalog_snapshots` + diff events (`new`/`delisted`) vs previous snapshot (pair reconciliation on exact `(name,price)`).
- `deactivate_watchlist_except()` keeps inactive rows (discontinued archive); never deletes.

### Phase 3: Prober (`prober.py`)
- Continuous loop (`--demand`): re-sweep active watchlist collections; writes `stock_obs` snapshots; runs debounced `oos_events` machine.
- `open_oos_event()` opens only when `snapshots` consecutive zero reads met; any `1` closes it immediately. Nulls (`in_stock=NULL`) pause, not reset.
- `vanished` (`kind='vanished'`) opens only for SKUs with prior `stock_obs` sightings. Catalog-covered never-sighted rows are coverage gaps, not churn.
- `close_oos_event()` reconciles stale `oos` events for SKUs outside active set at last observed reading (durations never fabricate unseen time).
- Suspect-cycle freeze: only-OOS canary results or mass in-stock→OOS flip freeze machine (record observations, no events).
- Voucher purge (`store.purge_vouchers()`): defensive removal from `watchlist`, `stock_obs`, `oos_events`; idempotent.

### Phase 4: Analysis (`demand.py` — BUILT 08-22)
- `dpi_table()` — ranked `[{sku_key, name, dpi, n_events, total_min, mean_restock_min, last_price, last_seen, active}]`; excludes `is_voucher_name()`.
- `heatmap()` — hour-of-day (local) × top-DPI SKU matrix of `oos` onset counts.
- `eta_curve()` — per-hour ETA stats from `stock_obs.eta_min`.
- `demand_summary()` — per-darkstore overview + totals.
- `export_csv()` → `exports/dpi_<date>.csv`.
- `run.py --demand-report [--store ID] [--csv]` — DPI table + heatmap summary.
- `run.py --catalog-report [--store ID]` — catalog snapshots + new/delisted churn log.

### Phase 5: Hardening (WIRED; PENDING live validation)
- `anti_block.proxies` (config) + `PROXY_URL` env → `load_proxies()` + `pick_proxy()` → `--proxy` → `pw_catalog.js` `browser.newContext({proxy})`.
- One proxy per invocation = one fresh browser+context = fresh WAF identity (session-bound token constraint; never rotate under live context).
- Empty pool = exact old behavior (verified: blinkit probe unchanged).
- Acceptance test: jiomart store MUST change per exit IP (IP-locked resolution).
- Global launcher `.tools/ollama/ollama-global` wraps binary, pins `HOME`/`OLLAMA_HOME`/`OLLAMA_MODELS` into workspace; symlinked `/usr/local/bin/ollama`.

---

## 6. Search, bot, and pricing (`search.py`, `tgbot.py`, `pricing.py`, `categories.py`)

- **Cross-platform fan-out:** `search.py` launches all 5 tracked apps in parallel (`ThreadPool`); results ranked by `effective` price (`pricing.py`: listed price − best `codes.yaml` offer − delivery fee).
- **Matching:** `token overlap ≥ 0.5` (`fuzzy`); optional semantic lift via `embeddings` table (`blend = max(token, semantic)` — adds candidates, never demotes; endpoint down / `semantic_matching: false` → exact historical token behavior).
- **Telegram bot (`tgbot.py`):**
  - `/watch <product>` → `keyword_watches` (chat-level); `/unwatch <product>` deactivates (history preserved).
  - `/digest` → today's cheapest per category (`store.today_cheapest_by_category`) + Demand Radar DPI top-5 (`demand.dpi_table`).
  - `WatchPusher` pushes when crawl/search results match active watches; rate-capped (`alert.rate_cap` pushes/hour + 6h per-watch cooldown via `last_alerted_ts`); restart-proof.
- **Categories (`categories.py`):** keyword classifier; ordered rules; feeds `category` column and `categories` stats.

---

## 7. Product-Space Intelligence pipeline (`src/product_space.py`, `src/product_vectors.py`, etc.)

Evidence: `PRODUCT_SPACE_PLAN.md`, `IMPLEMENTATION_LOG.md`, M1–M7 references.

- **M1 (`product_space.py`):** `load_product_space()` — reads `inventory/inventory_<app>.db.inventory_catalog` UNION `deals.db.catalog_snapshots` (latest per SKU fallback); excludes vouchers; attaches parsed fields (`product_fields.parse_name`); runs entity-resolution (exact canonical key → within-brand `match_score` → pack/variant veto → semantic confirm fallback; semantics never override veto). Provenance: every row carries `app/store_id/sku_key/inventory_db`.
- **M2 (`product_vectors.py`):** attribute + commercial vectors per product group (price/density normalized; `demand.dpi_table` mean; store/app coverage; churn flags). `--csv` → `exports/product_vectors.csv`.
- **M3 (`detect_assortment_gaps` / `assortment_gaps.py`):** cross-app gaps (present on some apps, not all).
- **M4 (`density.py` / `product_density`):** per-category density + insufficient / stale coverage guards.
- **M5 (`detect_gaps` / `gaps.py`):** internal/attribute gap scoring on top of density guards.
- **M6 (`opportunities.py` / `score_opportunities`):** `gap_strength × DPI × coverage × churn` scoring with provenance + validation codes; `--persist` writes to `deals.db.opportunities`.
- **M7 (`opportunity_report` / `opportunities.py`):** `run.py --opportunity-report [--limit N]` — latest persisted snapshot.

---

## 8. Semantic embeddings (`src/embed.py`, `.tools/ollama/`)

- **NVIDIA (default):** `nvidia/llama-nemotron-embed-vl-1b-v2` @2048 dims; `ai.embedding_base_url` + `NVIDIA_Build_API_KEY`; asymmetric (`corpus=passage`, `query=query`); batch 1000; 50 req/day free tier (`X-RateLimit-Limit`). Cache: additive `embeddings` table (keyed `model+dims`); backfill journaled `logs/embed_backfill.log`.
- **Local Ollama (opt-in):** `ai.embedding_provider: "ollama"`; `.tools/ollama/ollama-global` binary; `embeddinggemma-300m` @768 dims; server HOME `.ollama_home/`; `embedding_batch: 256` is optimum (throughput flat ~8 items/s; B≥512 kills runner). `.ollama/` models ~621MB total.
- **Backfill commands:** `--embed-catalog [--limit N]` (NVIDIA); `--similar <phrase> [--limit N]` (offline lexical + stored-vector expansion); `scripts/test_embeddinggemma.py` (self-managing local backfill + demo queries); `scripts/compare_embeddings.py` (gemma vs NVIDIA agreement); `scripts/embed_3d_map.py` (semantic explorer → `exports/embedding_map.html` / `embedding_map_gemma.html`).
- **Catalog re-key guard (rejected 09-05):** brand-sibling names (`Coke Zero` / `Coke`) cosine above genuine relabels; semantic catalog re-key rejected per `AGENTS.md`. Watchlist key-rotation handled via exact `(name,price)` pair reconciliation, not embeddings.

---

## 9. Dashboard (`run.py --ui` → `http://127.0.0.1:8787`)

Evidence: `README.md`, `AGENTS.md` endpoints list.

- **Features panel (`/features`):** spawn/terminate any repo feature (`monitor`, `bot`, `--demand`, `demo`, `inventory sweeps`) as managed child processes. Editable `args` spec per feature; server whitelists flags against spec (unknown flags rejected 400, never forwarded). `localStorage` persists last-used values. `STOP ALL /shutdown` reaps all children.
- **Endpoints:**
  - `/status` — live event bus (`fkind="gate" | "skip" | "boost"` for WAF failover).
  - `/categories`, `/searches`, `/search/<id>` — bot/search analytics.
  - `/demand`, `/heatmap?store=`, `/eta`, `/qc` — DB-backed Demand Radar.
  - `/db`, `/db/<db>/<table>` — read-only browser over all sqlite files (`deals.db`, `inventory/*.db`).
  - `/semsearch?q=` — lexical search; `/semsearch?seed=` — stored-vector expansion (`gemma` / `google` / `nematron` silos).
  - `/location`, `/location/presets`, `/location/locality`, `/location/corridor` — interactive working-area editor (regenerates `geo.corridor`, `demand.locality`, `search.station` in `config.yaml` with both loaders validated before atomic write).
  - `/ai/status`, `/ai/explain`, `/ai/explain/followup`, `/ai/methodology`, `/ai/focus` — optional LLM assistant (`src/ai_assist.py`); provider = any OpenAI-compatible endpoint (`ai:` in `config.yaml`) or local Ollama (keyless); `/ai/explain` persists full analysis as markdown to `exports/ai_explain_<stamp>.md`; `/ai/explain/followup` appends Q&A to saved file; `/ai/methodology[/apply]` and `/ai/focus[/apply]` enforce suggestions against `INT_PARAMS` whitelist (only `demand:` knobs writable). No arbitrary CLI execution.

---

## 10. Data model (`deals.db` + `inventory/*.db`)

Evidence: `src/store.py` schema (`_SCHEMA`), `AGENTS.md` repo map.

### `deals.db` (main sqlite; WAL mode)

| Table | Purpose | Key invariants |
|-------|---------|----------------|
| `price_obs` | Price history per `(app, store_id, sku_key)` | Rolling window (`usual_price()` excludes newest row; used for alert reference price). `category` backfilled. |
| `alerts` | Glitch events | `mrp` column (additive, backfilled); `reason` + `score`. |
| `darkstores` | Resolved stores per app | `lat/lon/label/eta_min`; `ON CONFLICT` upsert. |
| `watchlist` | Active + inactive SKU probe sets | `collections` (CSV labels: `home`, category names, `q:<term>`); `score DESC` orders; `first_seen_ts` backfilled; `is_digital_voucher` flag; `active` set by sweep (overflow = 0). Never deletes. |
| `stock_obs` | Per-cycle stock observations | `in_stock` (1/0/`NULL` — `NULL` = unknown/parse failure); `price`/`mrp`/`eta_min`; `source` (`home`/`collection`/`search`); `catalog_version` migration. |
| `oos_events` | Debounced out-of-stock events | `kind` (`oos` / `vanished`); `started_at` (first zero read); `ended_at`; `snapshots` (consecutive zero reads when open/closed); `restock_trigger`. Restart-proof rebuilt from `trailing_oos_streak`. |
| `searches` | Search query archive | `query`, `source` (`telegram`/`dashboard`/`cli`), `elapsed`, `n_results`, `top_*`. |
| `search_results` | Per-search result rows | `rank`, `platform`, `name`, `category`, `match`, `mrp`, `listed`, `discount`, `code`, `net`, `delivery`, `effective`, `url`, `note`. |
| `keyword_watches` | Telegram watch phrases | `chat_id`, `keyword` (lowercase); `created_ts`; `active`; `last_alerted_ts` (6h cooldown + rate cap). Deactivation only; rows kept. |
| `catalog_snapshots` | Full-catalog sweep snapshots | `(ts, app, store_id, sku_key)`; `name`, `price`, `in_stock`, `collections`. Idempotent per `(ts, sku)`. |
| `catalog_events` | Snapshot diff results | `kind` (`new`/`delisted`); pair reconciliation (`name,price`) excludes re-keys; mass-absence (<70% pair count) skips diff. |
| `embeddings` | Semantic vector cache | Keyed `(model, dims, name)`; `vector` (BLOB/text). Additive — provider switch re-keys cleanly. |
| `opportunities` | M7 persisted opportunity snapshots | Scored opportunity records (`gap_strength`, `DPI`, `coverage`, `churn`, `provenance`). |

### `inventory/inventory_<app>.db` (per-app; lazy-created by `Store`)

- `inventory_catalog` table: `id`, `ts`, `app`, `store_id`, `sku_key`, `name`, `price`, `mrp`, `in_stock`, `url`, `collections`, `category`, `raw_json`, `raw_json_truncated` (0/1), `raw_json_bytes`. `raw_json` capped at 16 KB (`_RAW_JSON_CAP`); truncated flag distinguishes capped from genuinely complete. `derive_product_url()` builds Blinkit `/prn/<slug>/prid/<id>` from `raw` payload when `url` absent.
- `catalog_snapshots` also written to `deals.db` (operational); inventory DB is the complete per-product record.

---

## 11. File map (current)

Evidence from `ls` and `AGENTS.md` repo map:

```
qcom-scraping/
  ARCHITECTURE.md          this file (updated 2025-09-08)
  README.md                 run guide + glossary (linked before contributing)
  GUIDE.md                  first-run + interpretation guide
  AGENTS.md                 multi-agent rules; invariant list; adapter state table
  DEMAND_RADAR.md            phase design + live status + proxy plan
  IMPLEMENTATION_LOG.md     single milestone log (M1-M7); never per-phase files
  PRODUCT_SPACE_PLAN.md     M1-M7 design + accepted/rejected decisions
  config.yaml               all tunables; miniyaml-compatible; secrets in .env only
  codes.yaml                user-editable delivery fees + offer codes
  run.py                    entrypoint; ALL CLI flags; feature catalog with editable args spec
  .env / .env.example       secrets (NVIDIA_Build_API_KEY, AI_API_KEY, etc.)
  deals.db                  main sqlite (WAL); all persistent data
  deals.demo.db             scratch DB for --demo (NEVER touches real DB)
  exports/                  locality JSON, embedding maps, DPI CSV, AI explain reports
  inventory/                per-app DBs + inventory_catalog snapshots
  inventory_milestones.md   inventory pipeline milestones
  docs/                    APK reverse findings (zepto, swiggy, blinkit); quick-commerce API vetting
  apks/                    APK files (gitignored; too large)
  .tools/ollama/            workspace-local Ollama binary; .ollama/ models; .ollama_home/ server
  .venv/                    Python environment (numpy / sklearn / plotly / plotly for embed_3d_map)
  src/                     core modules (see below)
  src/adapters/             7 adapters + base + demo
  scripts/                  self-managing scripts: live_sweep, test_embeddinggemma, compare_embeddings, embed_3d_map, bench_ollama_batch, embed_gemini_resume, embed_3d_map
  tests/                    test files
  backups/                  DB backups (deals.db.bak-*)
```

### Key `src/` modules

| File | Role | Key functions / notes |
|------|------|-----------------------|
| `run.py` | Entrypoint; CLI parsing (`_flag_*` helpers); `run()` dispatches all paths. | `--check` (config + adapter sanity); `--demo` (scratch DB); `--search`, `--bot`, `--ui` (with `--bot`/`--monitor`), `--once`; `--map-locality`, `--build-watchlist`, `--demand`, `--store-inventory`, `--catalog` (catalog inventory mode); `--embed-catalog`, `--similar`; `--product-fields`, `--product-space`, `--product-vectors`, `--detect-assortment-gaps`, `--product-density`, `--detect-gaps`, `--score-opportunities`, `--opportunity-report`, `--temporal-analysis`, `--validate-opportunities`, `--opportunity-pipeline`; `--demand-report`, `--catalog-report`; `--qc-status`; `--purge-vouchers`; feature catalog with `args` whitelist. |
| `src/store.py` | SQLite persistence (main class `Store`). | Schema (`_SCHEMA`), migrations (additive only), `record()`, `record_alert()`, `usual_price()` (excludes newest), `upsert_darkstore()`, `watchlist_for_store()`, `record_stock_obs()`, `open/close_oos_event()`, `trailing_oos_streak()`, `catalog_snapshot_list()`, `catalog_event_list()`, `record_catalog_snapshot()`, `catalog_prev_snapshot()` (pair reconciliation), `record_catalog_events()`, `deactivate_watchlist_except()` / `deactivate_watchlist_skus()`, `inventory_catalog` upsert (`_derive_product_url()`, `raw_json_truncated`), `purge_vouchers()`, `add/remove_watch()`, `today_cheapest_by_category()`. |
| `src/adapters/base.py` | Adapter interface + anti-block helpers. | `Adapter` class (`PROBE_URL`, `PROBE_TERMS`, `_rotate()`, `_browser_catalog_full()`); `load_proxies()`; `fresh_user_agent()`; `norm_price()`; `_stock_state()`; `_parse_catalog()`; process-group timeout + reap; stderr/stdout drain threads; `on_batch` incremental persistence. |
| `src/adapters/blinkit.py` | Blinkit adapter. | Overrides `APP_URL` / `HEALTH_URL`; `search()` merges `--pre` shelf results (`Cigarettes` shelf: 15119 → l1_cat 1948; `Cigar` 62439 → 3466; `Lighters` 383144 → 7778; `Rolling Needs` 11644 → 1982; `Paan Masala` 127957 → 2517). Text search yields accessories only; shelf provides real tobacco. |
| `src/adapters/zepto.py` | Zepto adapter. | `HEALTH_URL` = search route; `search()` uses signed responses. |
| `src/adapters/instamart.py` | Instamart adapter. | `APP_URL` = `instamart.in`; inner-container pagination (`POST /api/instamart/category-listing/filter/v2`); `--im-term` locality binding; `--mirror-page-ms` / `--mirror-stride`. |
| `src/adapters/amazon.py` | Amazon adapter. | Search + price-track. |
| `src/adapters/flipkart.py` | Flipkart adapter. | Search + price-track. |
| `src/adapters/jiomart.py` | Jiomart adapter. | IP-locked store resolution; `search()` works; rate-limited. |
| `src/adapters/bigbasket.py` | Bigbasket adapter. | `enabled: false`; Akamai 403. |
| `src/adapters/demo.py` | Demo adapter. | Injected glitch; scratch DB only. |
| `src/adapters/trackers.py` | Amazon / Flipkart price trackers. | `Tracker` class; `crawl()` for price tracking. |
| `src/locality.py` | Demand phase 1. | `anchor` grid + `landmark` seeds; `discover_darkstores()`; `resolve_store()`; `cluster_darkstores()`; `build_corridor()`; `rotate_anchor_term()` (process-local rotation was broken 09-02; fixed by passing config landmark names directly — `im_term` for landmark anchors = config name; grid anchors rotate through config names). `src/locality.py` self-test (`python3 -m src.locality`). |
| `src/watchlist.py` | Demand phase 2. | `WatchlistBuilder`; `build_for_store()` (one session/store); `build_all_stores()`; `catalog_inventory_mode()`; `catalog_inventory_mode()` deep-cats (`--catalog`); `pair_reconcile()` for snapshot diff. Self-test (`python3 -m src.watchlist`). |
| `src/prober.py` | Demand phase 3. | `Prober` class; `run_round()`; `observe_store()`; `record_obs()`; `reconcile_stale_events()`; `update_canary_state()`; `freeze_suspect()`; `update_watchlist()`; `build_report()`. Self-test (`python3 -m src.prober`). |
| `src/demand.py` | Demand phase 4. | Pure sqlite functions: `dpi_table()`, `heatmap()`, `eta_curve()`, `demand_summary()`, `export_csv()`. |
| `src/search.py` | Search engine. | `SearchEngine` class; `search()`; `execute_parallel()`; `load_product_space()` call for entity resolution; `match_score()`; `blend_score()` (max of token + semantic). |
| `src/pricing.py` | Effective price calculation. | `PricingEngine`; `calculate()`; reads `codes.yaml`. |
| `src/categories.py` | Keyword classifier. | `categorize()`; ordered rules. |
| `src/dashboard.py` | Dashboard server. | Flask-like endpoints; `start_feature()` / `stop_feature()` / `get_feature_status()` / `get_feature_log()`; `FEATURE_CATALOG` with editable `args` whitelist. |
| `src/tgbot.py` | Telegram bot. | `Bot` class; `/watch`, `/unwatch`, `/digest`, `list_watches()`; `WatchPusher` (matches search results / crawl batches against `keyword_watches`; rate-capped + cooldown); `start()` / `poll()` loop. |
| `src/orchestrator.py` | Monitor loop scheduler. | `Orchestrator` class; `schedule` config (`stagger`/`jitter`/`waf_failover`); `run_cycle()`; `WafFailover` strike ledger (`N` consecutive empty/errored → gate for `gate_cooldown_cycles`; other app gated → `blinkit_priority_extra` extra passes); event emission (`/status` shows `gate`/`skip`/`boost`). `protected_apps` = `blinkit`. Self-test (`python3 -m src.orchestrator`). |
| `src/events.py` | Thread-safe event bus. | `EventBus`; `publish()` / `subscribe()`; feeds `/status`. |
| `src/alert.py` | Alert fan-out. | `AlertPusher`; desktop + telegram + log (`deals.log`); carries reference price (`mrp` / `usual_price`). |
| `src/detect.py` | Glitch detector. | `GlitchDetector`; `score()`; `z-score` against local per-store baseline. |
| `src/honey.py` | Honey-pot SKU basket. | `HoneyBasket`; `load()`; `check()`. |
| `src/miniyaml.py` | YAML subset parser. | Stdlib fallback when `PyYAML` absent; parses `config.yaml`. |
| `src/ai_assist.py` | AI assistant. | `AIExplain`; `explain_demand()`; `suggest_focus()`; `suggest_methodology()`; `INT_PARAMS` whitelist enforcement; output saved to `exports/ai_explain_<stamp>.md`. |
| `src/embed.py` | Embedding client. | `EmbedClient`; NVIDIA (`urllib`) + local Ollama (`requests`); batch 256 (Ollama) / 1000 (NVIDIA); `embeddings` table read/write; `search_vectors()`; `backfill_catalog()`. Self-test (`python3 -m src.embed` — fake transport). |
| `src/inventory.py` | Catalog inventory module. | `InventoryCapture`; `run_sweep()`; `build_catalog()`; `resolve_location()` (uses `lat`/`lon` override from `--lat`/`--lon` or `deals.db.darkstores`); `store_inventory()` writes both `inventory_catalog` (inventory DB) and `catalog_snapshots` (deals.db); captures `raw_json` with cap/truncated flag. |
| `src/product_fields.py` | Grocery product parser. | `parse_name()` — brand, pack_value/pack_unit, `is_multipack`, variant, `unit_base`, `unit_price`, `parse_status`. Self-test (`python3 -m src.product_fields`). |
| `src/geo.py` | Geo layer. | `GeoResolver`; `resolve_darkstore()`; `build_grid()`; `anchor` + `landmark` definitions. |
| `scripts/live_sweep.py` | One-shot real-glitch hunt. | Runs full crawl across stations; outputs to terminal + file. |
| `scripts/test_embeddinggemma.py` | Local Ollama demo. | Starts `ollama serve`, pulls `embeddinggemma`, runs demo queries. |
| `scripts/compare_embeddings.py` | Quality comparison. | Compares `embeddinggemma` vs NVIDIA neighbors (numpy); needs `.venv/bin/python`. |
| `scripts/embed_3d_map.py` | Inventory atlas. | `PCA-50` → `k-means` → `PCA-3` / `PCA-2` (`UMAP` optional); renders interactive `exports/embedding_map.html` / `embedding_map_gemma.html`. Self-test with `--sample N`. |
| `scripts/bench_ollama_batch.py` | Batch-size benchmark. | Confirms B=256 optimum; B≥512 kills runner (connection reset by peer). |
| `scripts/embed_gemini_resume.py` | Gemini backfill. | `gemini-embedding-001` @768; `embedding_send_extras: false`; batch 100 + 16s pause ≈ 94 RPM/key; 4 keys ≈ 4k names/day; resets midnight PT. |

---

## 12. Current status (evidence-based)

Evidence: `IMPLEMENTATION_LOG.md`, `AGENTS.md` phase table, `README.md`, `DEMAND_RADAR.md`, `run.py --check` output (verified clean), `git status` (clean at `main` `b7f3502`), `node --check tools/pw_catalog.js`, `python3 -m py_compile` on touched files.

- **P1 locality:** BUILT (`locality.py` + `geo.py` + `exports/locality_*.json`).
- **P2 watchlist:** BUILT (`watchlist.py`; `--catalog` deep-cats; pair reconciliation; voucher purge; `catalog_events` new/delisted; `inventory.py` full sweep).
- **P3 prober:** BUILT (`prober.py` + `store.py` `oos_events`; debounce; streak reconstruction; vanished guard; suspect-cycle freeze; stale event reconciliation; `catalog_inventory` snapshot + event pipeline).
- **P4 analysis:** BUILT 08-22 (`demand.py`; DPI rollups; heatmap; ETA curve; `demand_summary`; CSV export; `/demand`, `/heatmap`, `/eta` endpoints; `--demand-report` / `--catalog-report`).
- **P5 hardening:** WIRED (`proxy` plumbing: config + env + adapter `pick_proxy()` + `pw_catalog.js` `--proxy` + process-group isolation). **PENDING:** procure Mumbai-exit residential proxy pool; validate IP↔anchor coherence live (jiomart store change per IP); stagger/jitter + global req/hr cap + backoff per `DEMAND_RADAR.md` Phase 5.
- **Product Space M1–M7:** M1 (union layer) BUILT; M2 (vectors) BUILT; M3 (assortment gaps) BUILT; M4 (density) BUILT; M5 (detect-gaps) BUILT; M6 (`score-opportunities` + `--persist`) BUILT; M7 (`opportunity-report` + temporal analysis + validation) BUILT.
- **Embeddings:** NVIDIA provider verified (batch 1000, 39 requests / 14.5 min for 44,487 names). Ollama (`embeddinggemma`) verified locally (`scripts/test_embeddinggemma.py`; `scripts/compare_embeddings.py`). `embeddings` table additive.
- **Dashboard:** All listed endpoints verified; feature panel editable args spec enforced; location editor validates both YAML loaders + backups to `/tmp`; AI panel whitelist enforced (`INT_PARAMS`); `/shutdown` reaps children.
- **Adapters:** All 7 present (`amazon`, `flipkart`, `blinkit`, `zepto`, `instamart`, `jiomart`, `bigbasket`). `bigbasket` `enabled: false`. `jiomart` enabled but with documented block. `amazon`/`flipkart` search + price-track working.
- **Schema:** Additive migrations verified (`category` column on `price_obs`; `mrp` on `alerts`; `catalog_version` columns; `restock_trigger` / `voucher_type` / `promotional_context` on `stock_obs`; `is_digital_voucher` / `first_seen_ts` on `watchlist`; `first_seen_ts` backfill; `first_seen_ts` / `catalog_version` / category backfills present).

---

## 13. How to read the updated architecture

This file is the evidence-based source of truth. The `ARCHITECTURE.md` update (2025-09-08) was produced by inspecting:
#!/usr/bin/env python3
"""
run.py — qcom-scraping v2 entrypoint.

Usage:
  python3 run.py            # continuous monitor loop
  python3 run.py --monitor  # same monitor loop (explicit; pairs with --ui/--bot)
  python3 run.py --once    # single cycle (good for testing)
  python3 run.py --check   # validate config + adapter availability
  python3 run.py --ui      # dashboard ONLY — starts no loops; add --bot
                           # and/or --monitor to also run them alongside
  python3 run.py --bot     # telegram bot + monitor together (--no-monitor
                           # for bot only)

Requires (for the browser-intercept QC adapters):  pip install playwright && playwright install chromium
Without it, the orchestrator still runs the e-commerce trackers + detection engine.
"""
from __future__ import annotations

import sys
import os

# allow `python3 run.py` from repo root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import yaml
    def load_cfg():
        with open("config.yaml") as f:
            return yaml.safe_load(f)
except ModuleNotFoundError:
    # stdlib-only fallback so the tool runs with zero external deps
    from src import miniyaml
    def load_cfg():
        return miniyaml.load("config.yaml")


from src.orchestrator import loop, build_adapters, run_cycle
from src.store import Store
from src.alert import Alert
from src.geo import Corridor
from src.honey import load_honey



def _flag_value(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


def _flag_list(name):
    v = _flag_value(name)
    return [a.strip() for a in v.split(",") if a.strip()] if v else None


def _flag_int(name):
    v = _flag_value(name)
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _flag_float(name):
    v = _flag_value(name)
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main():
    cfg = load_cfg()
    # --demo runs the pipeline against a SCRATCH database — never the
    # production one. (09-04: --demo used to wipe whatever cfg["db"] pointed
    # at — including the live deals.db from the dashboard's one-click Demo
    # card — with a backup that nobody watched for. The demo runs on a clean
    # slate by design, so it only ever needs its own throwaway file.)
    if "--demo" in sys.argv:
        cfg = {**cfg, "db": "deals.demo.db"}
    corridor = Corridor(cfg.get("geo", {}).get("corridor", []))
    honey = load_honey(cfg)
    store = Store(cfg.get("db", "deals.db"))
    alert = Alert(cfg)
    demo = "--demo" in sys.argv
    adapters = build_adapters(cfg, corridor, honey, demo=demo)

    if "--check" in sys.argv:
        print("config ok; stations:", len(corridor.anchors()))
        for a in adapters:
            label = "browser-intercept" if getattr(a, "APP_URL", None) else (
                "demo (simulated)" if a.name == "demo" else "http trackers")
            print(f"  adapter {a.name}: enabled ({label})")
        return

    if "--demo" in sys.argv:
        print("[demo] running the REAL pipeline (geo->adapter->detector->store->alert)")
        print("[demo] with a deliberately injected glitch: Blinkit / Andheri / Amul Milk 1L")
        print("[demo] normal ₹66 -> glitched ₹29\n")
        run_cycle(cfg, store, alert, adapters, corridor, honey)
        print_demo_report(store)
        return

    if "--map-locality" in sys.argv:
        from src.locality import LocalityMapper
        LocalityMapper(cfg, store).map_locality(apps=_flag_list("--apps"),
                                                max_points=(_flag_int("--max-points") or 10))
        return

    if "--build-watchlist" in sys.argv:
        from src.watchlist import WatchlistBuilder
        WatchlistBuilder(cfg, store).build(apps=_flag_list("--apps"),
                                           store_filter=_flag_value("--store"),
                                           max_per_store=_flag_int("--max-per-store"),
                                           max_queries=_flag_int("--max-queries"),
                                           catalog="--catalog" in sys.argv,
                                           categories_override=_flag_int("--categories"),
                                           mirror_page_ms=_flag_int("--mirror-page-ms"),
                                           tabs=_flag_int("--tabs"))
        return

    if "--store-inventory" in sys.argv:
        # Single-store, every-category capture (Product-Space Intelligence M1):
        # --app + --store REQUIRED; --lat/--lon override the store's resolved
        # location. Writes the rich inventory_catalog (url + raw_json + collections)
        # to the per-app inventory DB and the operational snapshot to deals.db.
        from src.inventory import run_inventory
        app = _flag_value("--app")
        store_id = _flag_value("--store")
        if not app or not store_id:
            print("usage: python3 run.py --store-inventory --app <app> --store <store_id> "
                  "[--lat L --lon L] [--mirror-page-ms N] [--tabs N]")
            return
        run_inventory(cfg, app, store_id,
                      lat=_flag_float("--lat"), lon=_flag_float("--lon"),
                      mirror_page_ms=_flag_int("--mirror-page-ms"),
                      tabs=_flag_int("--tabs"))
        return

    if "--product-fields" in sys.argv:
        # M1 Phase 1: grocery name parser self-test / accuracy report.
        from src.product_fields import _run_selftest, sample_report
        if "--report" in sys.argv:
            i = sys.argv.index("--report")
            rest = sys.argv[i + 1:]
            sample_n, db = 200, cfg.get("db", "deals.db")
            for j, a in enumerate(rest):
                if a == "--sample" and j + 1 < len(rest):
                    try:
                        sample_n = int(rest[j + 1])
                    except ValueError:
                        pass
                elif a == "--db" and j + 1 < len(rest):
                    db = rest[j + 1]
            sample_report(db, sample_n)
        else:
            if not _run_selftest():
                import sys as _s
                _s.exit(1)
        return

    if "--product-space" in sys.argv:
        # M1 Phase 2: normalized product-space union (read-only). Joins the per-app
        # inventory DBs (rich capture) with deals.db catalog_snapshots; excludes
        # vouchers; resolves cross-app product groups via entity resolution.
        from src.product_space import load_product_space
        rows = load_product_space(apps=_flag_list("--apps"),
                                  attach_embeddings=("--embeddings" in sys.argv))
        if "--csv" in sys.argv:
            import csv, os
            out = "exports/product_space.csv"
            os.makedirs("exports", exist_ok=True)
            with open(out, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["product_group_id", "group_method", "group_confidence",
                            "app", "store_id", "sku_key", "name", "brand",
                            "pack_value", "pack_unit", "is_multipack", "variant",
                            "unit_base", "unit_price", "price", "mrp", "in_stock",
                            "category", "collections", "url", "source"])
                for r in rows:
                    w.writerow([r["product_group_id"], r["group_method"], r["group_confidence"],
                                r["app"], r["store_id"], r["sku_key"], r["name"], r["brand"],
                                r["pack_value"], r["pack_unit"], r["is_multipack"], r["variant"],
                                r["unit_base"], r["unit_price"], r["price"], r["mrp"],
                                r["in_stock"], r["category"], r["collections"], r["url"], r["source"]])
            print(f"[product-space] wrote {len(rows)} rows -> {out}")
        else:
            from collections import Counter
            print(f"[product-space] {len(rows)} normalized records · "
                  f"{len({r['product_group_id'] for r in rows})} product groups "
                  f"(vouchers excluded)")
            print("  apps:", dict(Counter(r["app"] for r in rows)))
            print("  top categories:", Counter(r["category"] for r in rows).most_common(6))
        return

    if "--product-vectors" in sys.argv:
        # M2 Phase 3B/3C: grocery-shaped attribute + commercial vectors per
        # product_group_id. Read-only over the union layer + Demand Radar rollup.
        from src.product_vectors import build_product_vectors
        from src.product_space import load_product_space
        import json
        rows = load_product_space(apps=_flag_list("--apps"))
        vecs = build_product_vectors(rows, db=store)
        if "--csv" in sys.argv:
            import csv, os
            out = "exports/product_vectors.csv"
            os.makedirs("exports", exist_ok=True)
            with open(out, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["product_group_id", "rep_name", "category", "member_count",
                            "present_apps", "unit_price", "pack_value",
                            "attr_unitprice_z", "attr_pack_z", "attr_multipack",
                            "attr_catdepth", "dpi", "store_count", "app_count",
                            "days_since_first_seen", "is_currently_active",
                            "recent_churn_flag", "flags"])
                for gid, v in vecs.items():
                    a = v["attribute_vector"]; c = v["commercial_features"]
                    w.writerow([gid, v["rep_name"], v["category"], v["member_count"],
                                ",".join(v["present_apps"]), v.get("unit_price"),
                                v.get("pack_value"), a[0], a[1], a[2], a[3],
                                c["dpi"], c["store_count"], c["app_count"],
                                c["days_since_first_seen"], c["is_currently_active"],
                                c["recent_churn_flag"], json.dumps(v["flags"])])
            print(f"[product-vectors] wrote {len(vecs)} groups -> {out}")
        else:
            multi = sum(1 for v in vecs.values()
                        if v["commercial_features"]["app_count"] > 1)
            print(f"[product-vectors] {len(vecs)} product groups vectorized "
                  f"({multi} cross-app)")
        return

    if "--detect-assortment-gaps" in sys.argv:
        # M3 Phase 6: cross-app assortment gaps from the union layer (coverage
        # signal only -- never a demand claim).
        from src.assortment_gaps import detect_assortment_gaps
        from src.product_space import load_product_space
        rows = load_product_space(apps=_flag_list("--apps"))
        gaps = detect_assortment_gaps(rows)
        if "--csv" in sys.argv:
            import csv, os
            out = "exports/assortment_gaps.csv"
            os.makedirs("exports", exist_ok=True)
            with open(out, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["product_group_id", "rep_name", "present_apps",
                            "missing_apps", "member_count", "store_count",
                            "category", "confidence"])
                for g in gaps:
                    w.writerow([g["product_group_id"], g["rep_name"],
                                ",".join(g["present_apps"]),
                                ",".join(g["missing_apps"]), g["member_count"],
                                g["store_count"], g["category"], g["confidence"]])
            print(f"[assortment-gaps] wrote {len(gaps)} candidates -> {out}")
        else:
            print(f"[assortment-gaps] {len(gaps)} cross-app assortment gaps")
            for g in gaps[:20]:
                print(f"  {g['rep_name'][:44]:<46} present="
qcom-scraping/scripts/eval_parser.py:107:def score(rows, use_ref=True):
qcom-scraping/scripts/embed_3d_map.py:738:def cluster_embeddings(low, k, seed):
qcom-scraping/scripts/embed_3d_map.py:860:def cluster_hulls(xy2, labels, k, cap=1500, seed=0):
qcom-scraping/src/assortment_gaps.py:47:def detect_assortment_gaps(rows, tracked_apps=("blinkit", "zepto", "instamart")):
qcom-scraping/src/opportunities.py:50:def score_opportunities(rows, db=None, min_n=25):
qcom-scraping/src/opportunities.py:200:CREATE TABLE IF NOT EXISTS opportunities (
qcom-scraping/src/gaps.py:45:def score_internal_gaps(rows, min_n=25, db=None, knn_weight=0.5, attr_weight=0.5):
qcom-scraping/src/human_review.py:12:    "CREATE TABLE IF NOT EXISTS opportunity_reviews ("
qcom-scraping/src/temporal.py:168:    conn.execute("CREATE TABLE catalog_snapshots (ts REAL, sku_key TEXT, collections TEXT)")
qcom-scraping/src/embed.py:88:CREATE TABLE IF NOT EXISTS embeddings (
qcom-scraping/src/embed.py:935:    c.execute("CREATE TABLE embeddings(name TEXT PRIMARY KEY, vec BLOB, "
qcom-scraping/src/store.py:40:CREATE TABLE IF NOT EXISTS price_obs (
qcom-scraping/src/store.py:54:CREATE TABLE IF NOT EXISTS alerts (
qcom-scraping/src/store.py:65:CREATE TABLE IF NOT EXISTS darkstores (
qcom-scraping/src/store.py:76:CREATE TABLE IF NOT EXISTS watchlist (
qcom-scraping/src/store.py:91:CREATE TABLE IF NOT EXISTS stock_obs (
qcom-scraping/src/store.py:108:CREATE TABLE IF NOT EXISTS oos_events (
qcom-scraping/src/store.py:120:CREATE TABLE IF NOT EXISTS searches (
qcom-scraping/src/store.py:131:CREATE TABLE IF NOT EXISTS search_results (
qcom-scraping/src/store.py:151:CREATE TABLE IF NOT EXISTS keyword_watches (
qcom-scraping/src/store.py:161:CREATE TABLE IF NOT EXISTS catalog_snapshots (
qcom-scraping/src/store.py:174:CREATE TABLE IF NOT EXISTS catalog_events (
qcom-scraping/src/store.py:391:            "CREATE TABLE IF NOT EXISTS inventory_catalog ("
qcom-scraping/src/product_space.py:147:def load_product_space(apps=None, since=None, attach_embeddings=False, root=None):
qcom-scraping/src/demand.py:83:def dpi_table(db, store_id=None, since_days=7, limit=50):
qcom-scraping/src/demand.py:141:def heatmap(db, store_id=None, top=20):
qcom-scraping/src/demand.py:166:def eta_curve(db, store_id=None):
qcom-scraping/src/demand.py:184:def demand_summary(db):

```


## Assistant

<thinking>


**Clarifying pipeline use case and scope**
</thinking>

**Tool Call: find . -maxdepth 2 -type f \( -iname 'README.md' -o -iname 'AGENTS.md' -o -iname 'pyproject.toml' -o -iname 'package.json' \) -print | sed -n '1,260p'; sed -n '1,240p' qcom-scraping/src/store.py; sed -n '1,260p' qcom-scraping/src/demand.py; sed -n '1,260p' qcom-scraping/src/detect.py**
Status: Completed

Terminal:
```
./Clock-app-productivity-v3/package.json
./Clock-app-productivity-v3/AGENTS.md
./qcom-scraping/README.md
./qcom-scraping/AGENTS.md
./qr-transfer/README.md
./High-Angle_Robust_Fast_FaceAlignment/pyproject.toml
./High-Angle_Robust_Fast_FaceAlignment/README.md
./StudyMonitor/README.md
./Financial-model-v2/README.md
./Vibe-Trading/pyproject.toml
./Vibe-Trading/README.md
./deepseek-harness-token/README.md
./deepseek-harness-token/package.json
./Generic Apps/README.md
./Generic Apps/package.json
./imessage-bridge/README.md
./imessage-bridge/package.json
./AGENTS.md
./reverse-skill/README.md
./reverse-skill/AGENTS.md
./Financial-model-v1/README.md
"""
store.py — persistence: price history + per-(store,sku) baseline.

We keep a rolling window of observed prices per (app, store_id, sku_key) so the
detector can compute a z-score against the *local* norm. Quick-commerce promos
are local, so a global baseline would cry wolf constantly.
"""
from __future__ import annotations

import json
import logging
import re
import sqlite3
import statistics
import threading
import time
import os

from .categories import categorize

log = logging.getLogger("store")

# Digital vouchers / gift cards are NOT commodities: their "stock-outs" are
# code-pool replenishment cycles, not shelf demand, so they poison the Demand
# Radar (they once held 15 of the top-20 DPI slots). One shared matcher so the
# watchlist builder, prober and DPI rollups all draw the same line. Kept to
# name tokens only — verified 09-02: every voucher SKU name on Blinkit carries
# "voucher" or "gift card"; NO real grocery/retail SKU does (0 false
# positives over the whole price_obs corpus), so no brand keywords needed.
VOUCHER_TOKENS = ("voucher", "gift card")


def is_voucher_name(name):
    """True when a product name is a digital voucher / gift-card SKU."""
    n = (name or "").lower()
    return any(t in n for t in VOUCHER_TOKENS)


_SCHEMA = """
CREATE TABLE IF NOT EXISTS price_obs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL,
    app TEXT,
    store_id TEXT,
    sku_key TEXT,
    name TEXT,
    price REAL,
    mrp REAL,
    url TEXT,
    category TEXT,
    catalog_version TEXT DEFAULT NULL
);
CREATE INDEX IF NOT EXISTS idx_obs ON price_obs(app, store_id, sku_key, ts);
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL,
    app TEXT,
    store_id TEXT,
    sku_key TEXT,
    reason TEXT,
    price REAL,
    score REAL,
    mrp REAL                  -- 09-02: reference price shown on alerts (NULL = unknown)
);
CREATE TABLE IF NOT EXISTS darkstores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL,
    app TEXT,
    store_id TEXT,
    label TEXT,
    lat REAL,
    lon REAL,
    eta_min REAL
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_darkstore ON darkstores(app, store_id);
CREATE TABLE IF NOT EXISTS watchlist (
    app TEXT,
    store_id TEXT,
    sku_key TEXT,
    name TEXT,
    collections TEXT,          -- 'home', category names, 'q:<term>' (csv)
    last_price REAL,
    last_in_stock INTEGER,     -- 1/0/null at build time
    last_seen_ts REAL,
    score REAL DEFAULT 0,      -- curation rank (higher = keep)
    active INTEGER DEFAULT 1,  -- probe-set membership (phase-3 prober reads this)
    is_digital_voucher INTEGER DEFAULT 0,
    PRIMARY KEY (app, store_id, sku_key)
);
CREATE INDEX IF NOT EXISTS idx_wl_active ON watchlist(app, store_id, active);
CREATE TABLE IF NOT EXISTS stock_obs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL,
    app TEXT,
    store_id TEXT,
    sku_key TEXT,
    in_stock INTEGER,          -- 1/0/null (null = unknown: failed parse etc.)
    price REAL,
    mrp REAL,
    eta_min REAL,
    source TEXT,               -- 'home' | 'collection' | 'search'
    restock_trigger TEXT DEFAULT NULL,
    voucher_type TEXT DEFAULT NULL,
    promotional_context TEXT DEFAULT NULL,
    catalog_version TEXT DEFAULT NULL
);
CREATE INDEX IF NOT EXISTS idx_so ON stock_obs(store_id, sku_key, ts);
CREATE TABLE IF NOT EXISTS oos_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app TEXT,
    store_id TEXT,
    sku_key TEXT,
    kind TEXT DEFAULT 'oos',   -- 'oos' | 'vanished'
    started_at REAL,
    ended_at REAL,             -- NULL = ongoing
    snapshots INTEGER,          -- consecutive OOS obs when open/closed
    restock_trigger TEXT DEFAULT NULL
);
CREATE INDEX IF NOT EXISTS idx_oos ON oos_events(store_id, sku_key, started_at);
CREATE TABLE IF NOT EXISTS searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL,
    query TEXT,
    source TEXT,               -- 'telegram' | 'dashboard' | 'cli'
    elapsed REAL,
    n_results INTEGER,
    top_platform TEXT,
    top_name TEXT,
    top_effective REAL
);
CREATE TABLE IF NOT EXISTS search_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_id INTEGER REFERENCES searches(id),
    rank INTEGER,
    platform TEXT,
    name TEXT,
    category TEXT,
    match REAL,
    mrp REAL,
    listed REAL,
    discount REAL,
    code TEXT,
    net REAL,
    delivery REAL,
    effective REAL,
    url TEXT,
    note TEXT
);
CREATE INDEX IF NOT EXISTS idx_sr ON search_results(search_id);
CREATE INDEX IF NOT EXISTS idx_sr_cat ON search_results(category);
CREATE TABLE IF NOT EXISTS keyword_watches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id TEXT,              -- telegram chat to push matches to
    keyword TEXT,              -- lowercase watch phrase (token-overlap match)
    created_ts REAL,
    active INTEGER DEFAULT 1,  -- 0 after /unwatch; rows are never deleted
    last_alerted_ts REAL,      -- last successful push (per-watch cooldown basis)
    UNIQUE(chat_id, keyword)
);
CREATE INDEX IF NOT EXISTS idx_kww_active ON keyword_watches(active);
CREATE TABLE IF NOT EXISTS catalog_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL,                   -- sweep timestamp (one sweep = one snapshot)
    app TEXT,
    store_id TEXT,
    sku_key TEXT,
    name TEXT,
    price REAL,
    in_stock INTEGER,          -- 1/0/null at sweep time
    collections TEXT,          -- category labels seen this sweep (csv)
    UNIQUE(app, store_id, ts, sku_key)
);
CREATE INDEX IF NOT EXISTS idx_cs ON catalog_snapshots(app, store_id, ts);
CREATE TABLE IF NOT EXISTS catalog_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL,
    app TEXT,
    store_id TEXT,
    sku_key TEXT,
    kind TEXT,                 -- 'new' | 'delisted'
    name TEXT,
    price REAL,
    snapshot_ts REAL,          -- sweep that produced the event
    prev_snapshot_ts REAL,     -- sweep it was diffed against (NULL if first)
    detail TEXT                -- e.g. category where first seen
);
CREATE INDEX IF NOT EXISTS idx_ce ON catalog_events(app, store_id, kind, ts);
"""


class Store:
    def __init__(self, path="deals.db"):
        self.path = path
        self.lock = threading.Lock()   # search persistence can come from any thread
        self.conn = sqlite3.connect(path, check_same_thread=False)
        try:
            self.conn.execute("PRAGMA journal_mode=WAL")
        except Exception:
            pass
        self.conn.executescript(_SCHEMA)
        # migration: category column on price_obs
        try:
            self.conn.execute("ALTER TABLE price_obs ADD COLUMN category TEXT")
        except Exception:
            pass  # already exists
        # migration: expanded tracking parameters for digital vouchers / restock triggers
        migrations = [
            ("stock_obs", "restock_trigger", "TEXT DEFAULT NULL"),
            ("stock_obs", "voucher_type", "TEXT DEFAULT NULL"),
            ("stock_obs", "promotional_context", "TEXT DEFAULT NULL"),
            ("stock_obs", "catalog_version", "TEXT DEFAULT NULL"),
            ("watchlist", "is_digital_voucher", "INTEGER DEFAULT 0"),
            ("oos_events", "restock_trigger", "TEXT DEFAULT NULL"),
            ("price_obs", "catalog_version", "TEXT DEFAULT NULL"),
            ("alerts", "mrp", "REAL"),          # 09-02: MRP/usual shown on alerts
            ("watchlist", "first_seen_ts", "REAL"),  # 09-02: catalog churn tracking
        ]
        for table, col, col_type in migrations:
            try:
                self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
            except Exception:
                pass  # already exists
        self.conn.commit()
        self._backfill_categories()
        self._backfill_first_seen()

    def _backfill_first_seen(self):
        """Catalog churn tracking (09-02): existing watchlist rows predate
        first-seen tracking. Backfill with last_seen_ts (conservative: the
        earliest time we can honestly claim the SKU was present), so nothing
        historic ever shows up as a false 'new' arrival."""
        try:
            nul = self.conn.execute(
                "SELECT COUNT(*) FROM watchlist WHERE first_seen_ts IS NULL").fetchone()[0]
            if not nul:
                return
            self.conn.execute(
                "UPDATE watchlist SET first_seen_ts=last_seen_ts "
                "WHERE first_seen_ts IS NULL AND last_seen_ts IS NOT NULL")
            self.conn.commit()
"""
demand.py — Demand Radar phase 4: analysis rollups over stock_obs + oos_events.

All numbers are PROXIES for demand built from stock-out behaviour:

  DPI (Demand Pressure Index) per SKU
      = Σ over 'oos' events of duration_min × exp(-age_days / HALF_LIFE_DAYS)
        / observation_days

  where observation_days = days since that store's first stock_obs snapshot
  (floor 0.5 so a fresh store doesn't divide by ~0). Higher DPI = more
  frequent / recent / longer stock-outs. 'vanished' events are delistings,
  NOT demand — excluded here, surfaced separately.

  Resolution honesty (09-04): DPI measures demand pressure on PROBED
  shelves, not the whole inventory — the light sweep (home +
  categories_per_store shelves + watchlist search terms) sights a few
  hundred SKUs/cycle vs the watchlist's full catalog census (~8-24k
  rows/store). A never-sighted SKU's absence is a coverage gap, never a
  stock signal; whole-inventory delisting truth comes from catalog_events
  snapshot diffs.

  Restock velocity = mean minutes of CLOSED oos events (a SKU that comes back
  fast is being bought out fast).

Hours are LOCAL time (the operator's wall clock) — consistent across views.
Pure functions over sqlite; no network. Used by the dashboard (/demand,
/heatmap, /eta, /qc), `run.py --demand-report`, and CSV exports.

Vouchers / gift cards are NOT commodities (their stock-outs are code-pool
replenishments, not demand) — they are excluded at the source (watchlist
builder + prober) and again here defensively, so pre-purge or stray rows can
never re-enter the DPI table.
"""
from __future__ import annotations

import csv
import math
import os
import time

from .store import is_voucher_name

HALF_LIFE_DAYS = 3.0


def _now():
    return time.time()


def _recency_weight(ts, now):
    age_days = max(0.0, (now - ts)) / 86400.0
    return math.exp(-age_days * math.log(2) / HALF_LIFE_DAYS)


def _name_map(db, store_id=None):
    """sku_key -> best known product name. Watchlist first; price_obs
    (glitch-monitor crawls + inventory captures, newest wins) as fallback —
    the prober records stock for SKUs it merely passes by in search results,
    which never land in the watchlist and would otherwise show anonymous
    in the DPI table / AI digests."""
    q = "SELECT sku_key, name FROM watchlist" + (" WHERE store_id=?" if store_id else "")
    rows = db.conn.execute(q, (store_id,) if store_id else ()).fetchall()
    names = {r[0]: r[1] for r in rows if r[1]}
    fallback = {}
    for sku, name in db.conn.execute(
            "SELECT sku_key, name FROM price_obs WHERE name IS NOT NULL ORDER BY ts"):
        fallback[sku] = name              # ascending ts -> newest wins
    for sku, name in fallback.items():
        names.setdefault(sku, name)
    return names


def observation_span_days(db, store_id=None):
    """Days of collected observations (floor 0.5)."""
    q = "SELECT MIN(ts) FROM stock_obs" + (" WHERE store_id=?" if store_id else "")
    row = db.conn.execute(q, (store_id,) if store_id else ()).fetchone()
    if not row or not row[0]:
        return 0.5
    return max(0.5, (_now() - row[0]) / 86400.0)


def dpi_table(db, store_id=None, since_days=7, limit=50):
    """
    Ranked [{sku_key,name,dpi,n_events,total_min,mean_restock_min,last_price,
             last_seen,active}] — highest pressure first.
    """
    now = _now()
    since = now - since_days * 86400
    names = _name_map(db, store_id)
    obs_days = observation_span_days(db, store_id)

    ev_q = ("SELECT sku_key, started_at, ended_at, snapshots FROM oos_events "
            "WHERE kind='oos' AND started_at>=?" + (" AND store_id=?" if store_id else ""))
    args = [since] + ([store_id] if store_id else [])
    agg = {}
    for sku, started, ended, snaps in db.conn.execute(ev_q, args):
        a = agg.setdefault(sku, {"n": 0, "total_min": 0.0, "weighted": 0.0,
                                 "closed_min": []})
        dur_min = ((ended or now) - started) / 60.0
        a["n"] += 1
        a["total_min"] += dur_min
        a["weighted"] += dur_min * _recency_weight(started, now)
        if ended:
            a["closed_min"].append(dur_min)

    last_q = ("SELECT sku_key, price, MAX(ts) FROM stock_obs "
              + ("WHERE store_id=?" if store_id else "") +
              " GROUP BY sku_key")
    largs = [store_id] if store_id else []
    last_price, last_seen = {}, {}
    active = {r[0] for r in db.conn.execute(
        "SELECT sku_key FROM watchlist WHERE active=1"
        + (" AND store_id=?" if store_id else ""), largs)}
    for sku, price, ts in db.conn.execute(last_q, largs):
        last_price[sku] = price
        last_seen[sku] = ts

    rows = []
    for sku, a in agg.items():
        name = names.get(sku)
        if name and is_voucher_name(name):
            continue          # vouchers are not commodities — never in the radar
        closed = sorted(a["closed_min"])
        mean_restock = round(sum(closed) / len(closed), 1) if closed else None
        rows.append({
            "sku_key": sku,
            "name": name or sku,
            "dpi": round(a["weighted"] / obs_days, 2),
            "n_events": a["n"],
            "total_min": round(a["total_min"], 1),
            "mean_restock_min": mean_restock,
            "last_price": last_price.get(sku),
            "last_seen": last_seen.get(sku),
            "active": sku in active,
        })
    rows.sort(key=lambda r: (-r["dpi"], -r["n_events"]))
    return rows[:limit]


def heatmap(db, store_id=None, top=20):
    """
    Hour-of-day (local) × top-DPI SKU matrix of OOS ONSET counts.
    Returns {hours:[0..23], skus:[{name,total,by_hour:[24]}], peak_hour}.
    """
    names = _name_map(db, store_id)
    ranked = dpi_table(db, store_id=store_id, limit=top)
    want = {r["sku_key"]: {"name": r["name"], "total": 0, "by_hour": [0] * 24}
            for r in ranked}
    ev_q = ("SELECT sku_key, started_at FROM oos_events WHERE kind='oos'"
            + (" AND store_id=?" if store_id else ""))
    args = [store_id] if store_id else []
    for sku, started in db.conn.execute(ev_q, args):
        cell = want.get(sku)
        if cell:
            hr = time.localtime(started).tm_hour
            cell["by_hour"][hr] += 1
            cell["total"] += 1
    skus = [v | {"sku_key": k} for k, v in want.items()]
    skus.sort(key=lambda s: (-s["total"], s["name"]))
    hourly_tot = [sum(s["by_hour"][h] for s in skus) for h in range(24)]
    peak = hourly_tot.index(max(hourly_tot)) if any(hourly_tot) else None
    return {"hours": list(range(24)), "skus": skus, "peak_hour": peak}


def eta_curve(db, store_id=None):
    """Per-local-hour delivery ETA stats from stock_obs.eta_min."""
    q = ("SELECT ts, eta_min FROM stock_obs WHERE eta_min IS NOT NULL"
         + (" AND store_id=?" if store_id else ""))
    args = [store_id] if store_id else []
    buckets = {h: [] for h in range(24)}
    for ts, eta in db.conn.execute(q, args):
        buckets[time.localtime(ts).tm_hour].append(eta)
    out = []
    for h in range(24):
        vals = buckets[h]
        out.append({"hour": h, "n": len(vals),
                    "avg": round(sum(vals) / len(vals), 1) if vals else None,
                    "min": min(vals) if vals else None,
                    "max": max(vals) if vals else None})
    return out


def demand_summary(db):
    """Per-darkstore overview + totals — feeds the dashboard's radar panel."""
    stores = []
    for app, sid, label, lat, lon, eta in db.darkstores():
        one = lambda q, a: db.conn.execute(q, a).fetchone()[0]
        stores.append({
            "app": app, "store_id": sid, "label": label,
            "obs": one("SELECT COUNT(*) FROM stock_obs WHERE store_id=?", (sid,)),
            "skus_seen": one("SELECT COUNT(DISTINCT sku_key) FROM stock_obs WHERE store_id=?", (sid,)),
            "active_skus": one("SELECT COUNT(*) FROM watchlist WHERE store_id=? AND active=1", (sid,)),
            "open_oos": one("SELECT COUNT(*) FROM oos_events WHERE store_id=? AND ended_at IS NULL AND kind='oos'", (sid,)),
            "vanished": one("SELECT COUNT(*) FROM oos_events WHERE store_id=? AND ended_at IS NULL AND kind='vanished'", (sid,)),
            "eta_min": eta,
        })
    totals = {
        "obs": sum(s["obs"] for s in stores),
        "open_oos": sum(s["open_oos"] for s in stores),
        "vanished": sum(s["vanished"] for s in stores),
        "obs_days": round(observation_span_days(db), 1),
    }
    return {"stores": stores, "totals": totals}


def export_csv(db, path=None):
    """Nightly-style DPI export → exports/dpi_<date>.csv. Returns path."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outdir = os.path.join(root, "exports")
    os.makedirs(outdir, exist_ok=True)
    path = path or os.path.join(outdir, f"dpi_{time.strftime('%Y%m%d')}.csv")
    rows = dpi_table(db, limit=10000)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rank", "app", "store_id", "sku_key", "name", "dpi",
                    "oos_events", "total_oos_min", "mean_restock_min",
                    "last_price", "active"])
        store_meta = {s["store_id"]: s["app"] for s in demand_summary(db)["stores"]}
        for i, r in enumerate(rows, 1):
            sku = r["sku_key"]
            # watchlist PK is (app, store_id, sku_key) — resolve app+store per row
            m = db.conn.execute(
                "SELECT app, store_id FROM watchlist WHERE sku_key=? ORDER BY last_seen_ts DESC LIMIT 1",
                (sku,)).fetchone()
            app, sid = (m[0], m[1]) if m else ("", "")
            w.writerow([i, app or store_meta.get(sid, ""), sid, sku, r["name"],
                        r["dpi"], r["n_events"], r["total_min"],
                        r["mean_restock_min"], r["last_price"], int(r["active"])])
    return path
"""
detect.py — glitch / anomaly scoring.

Two layers:
  1. Honey-pot: deviation vs hardcoded TRUE price (instant, high confidence).
  2. Statistical: z-score of current price vs the per-store rolling baseline.
     Because QC prices are local, we baseline per (store, sku), not globally.

Returns (is_glitch: bool, score: float, reason: str).
"""
from __future__ import annotations

import statistics


def _zscore(value, values):
    if len(values) < 3:
        return 0.0
    m = statistics.mean(values)
    sd = statistics.pstdev(values)
    if sd == 0:
        return 0.0
    return (m - value) / sd  # positive => cheaper than norm


def _honey_match(honey, app, sku_key, name):
    """Return (true_price) if this product matches a canary, else None.
    Matches on token overlap so live catalog names ('Amul Gold Milk 1L')
    still hit the 'amul milk' canary."""
    n = f"{sku_key} {name or ''}".lower()
    for h in honey:
        if h.get("app") != app:
            continue
        q = (h.get("query") or "").lower().split()
        if q and all(tok in n for tok in q):
            return h.get("true_price")
    return None


def evaluate(app, store_id, sku_key, price, mrp, cfg, store, honey=None, name=None):
    dcfg = cfg.get("detect", {})
    honey_dev = dcfg.get("honey_deviation_pct", 25)
    z_thr = dcfg.get("stat_zscore", 2.5)
    min_off = dcfg.get("min_margin_off_mrp", 40)
    max_price = dcfg.get("max_price", 5000)

    if price is None or price <= 0:
        return False, 0.0, ""
    if price > max_price:
        return False, 0.0, "price over cap"

    # Layer 1: honey-pot deviation (token-overlap match on name/sku)
    if honey:
        true_p = _honey_match(honey, app, sku_key, name)
        if true_p:
            dev = (true_p - price) / true_p * 100
            if dev >= honey_dev:
                return True, round(dev, 1), f"honey -{dev:.0f}% vs true ₹{true_p}"
            # canary priced ABOVE its known-good price is also interesting
            if dev <= -30:
                return True, round(-dev, 1), f"honey +{-dev:.0f}% above true ₹{true_p}"

    # MRP margin gate
    if mrp and mrp > 0:
        off = (mrp - price) / mrp * 100
        if off < min_off:
            # cheap but not a real deal vs MRP; still allow stat outliers
            pass

    # Layer 2: statistical outlier vs store baseline
    hist = store.window(app, store_id, sku_key)
    if hist:
        z = _zscore(price, hist)
        if z >= z_thr:
            return True, round(z, 2), f"z={z:.1f} below store norm"

    # First-seen honey / MRP deal w/ big margin
    if mrp and mrp > 0:
        off = (mrp - price) / mrp * 100
        if off >= min_off and len(hist) >= 1:
            # only flag if it's clearly below its own recent price too
            if not hist or price <= min(hist) * 0.8:
                return True, round(off, 1), f"-{off:.0f}% off MRP"

    return False, 0.0, ""

```


## Assistant

<thinking>


**Formulating initial audit questions**
</thinking>

The source is a mature evidence pipeline, not simply a scraper: it preserves time-stamped observations, distinguishes unknown/partial data from true events, scores anomalies against entity-specific baselines, keeps provenance, and serves reviewable reports. For audit work, the crawler should be replaced by controlled client-data ingestion and the “demand” signal by audit-risk evidence.

## Input Requested

Input requested

## Assistant

<thinking>


**Clarifying intent and data specifics**
</thinking>

## Input Requested

Input requested

## Assistant

<thinking>


**Clarifying blueprint requirements**
</thinking>

## Input Requested

Input requested

## Assistant

<thinking>


**Planning blueprint requirements and standards research**
</thinking>

I’m grounding the controls in the current Indian audit standards so the blueprint treats analytics as audit evidence and auditor judgment—not an autonomous conclusion engine.

**Tool Call: XDG_CONFIG_HOME="/Users/Mitesh Gada/Documents/Projects/.monid/xdg" /Users/Mitesh\ Gada/.npm-global/bin/monid discover --query "ICAI Standards on Auditing SA 240 journal entries audit documentation SA 230 official"**
Status: Completed

Terminal:
```
- Searching for "ICAI Standards on Auditing SA 240 journal entries audit documentation SA 230 official"...
✔ Found 5 result(s)

Update available: 0.1.6 → 0.1.7.
  Run `npm update -g @monid-ai/cli` to update monid-cli.
  Download the latest version of skill at https://monid.ai/SKILL.md.
Provider       Endpoint                     Price        Description                                        Verified
api.strale.io  /x402/seo-audit              $0.3564/call Comprehensive SEO audit of a URL. Checks title,...
api.strale.io  /x402/v2/accessibility-audit $0.3564/call WCAG 2.1 accessibility audit of a URL. Checks c...
api.kadec0.xyz /v1/website-audit            $0.088/call  Instant website SEO audit. On-page SEO, perform...
surf           /onchain/sql                 $0.024/call  Run a read-only ClickHouse SQL query against on...    ✓
api.strale.io  /x402/v2/dependency-audit    $0.0594/call Audit npm or Python dependencies. Checks each p...

```


## Assistant

<thinking>


**Preparing to run inspect phase**
</thinking>

**Tool Call: XDG_CONFIG_HOME="/Users/Mitesh Gada/Documents/Projects/.monid/xdg" /Users/Mitesh\ Gada/.npm-global/bin/monid inspect --provider tinyfish --endpoint /search**
Status: Completed

Terminal:
```
- Inspecting tinyfish//search...

Provider
  TinyFish (tinyfish)

Endpoint
  /search

Description
  Search the live web, news, or research papers and get ranked results.

✓ Verified

Summary
  Browser-rendered search over the live web — results are never cached, so pricing pages, earnings releases, and breaking news are current at query time. Set 'domain_type' to 'web' (default), 'news' (adds publisher and date), or 'research_paper' (adds authors, venue, year, cited_by_count, and pdf_url). Filters cover geo ('location') and 'language', domain allow/block lists ('include_domains' / 'exclude_domains'), a freshness window ('recency_minutes') or calendar bounds ('after_date' / 'before_date'), publication-year bounds for papers, and paging ('page', 0-10). Pass 'purpose' — a short statement of the task the results are for — to sharpen ranking. Returns position, title, url, site_name, and snippet per result. Snippets only: this endpoint does not return page content — pipe the result URLs into TinyFish /fetch, which is also free, when you need the full text.

Pricing
  Type:   PER_CALL
  Amount: $0/call

Input
  Query Params
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "minLength": 1,
      "description": "Search query. Accepts natural language and still honours site:/-site: operators, though include_domains / exclude_domains are preferred because they do not collide with other query syntax. Example: 'NVIDIA Q4 FY2025 revenue'."
    },
    "purpose": {
      "type": "string",
      "minLength": 1,
      "maxLength": 2000,
      "description": "Optional short statement of the task these results are for — the goal behind the request, not the request itself. TinyFish uses it as an extra ranking signal. Example: 'Compare pricing tiers across vendors for a procurement report'. Max 2000 characters."
    },
    "location": {
      "description": "Country code for geo-targeted results. Example: US, GB, FR, DE. Auto-resolves from `language` when omitted; defaults to US if neither is set.",
      "type": "string",
      "minLength": 1
    },
    "language": {
      "description": "Language code for result language. Example: en, fr, de. Auto-resolves from `location` when omitted; defaults to en if neither is set.",
      "type": "string",
      "minLength": 1
    },
    "include_domains": {
      "description": "Comma-separated domains to restrict results to. Example: github.com,arxiv.org.",
      "type": "string",
      "minLength": 1
    },
    "exclude_domains": {
      "description": "Comma-separated domains to exclude from results. Example: pinterest.com,quora.com.",
      "type": "string",
      "minLength": 1
    },
    "recency_minutes": {
      "description": "Freshness window in minutes, relative to now. Example: 60 for the last hour. Cannot be combined with after_date or before_date, and is not supported for domain_type=research_paper.",
      "type": "integer",
      "minimum": 1,
      "maximum": 5256000
    },
    "after_date": {
      "description": "Lower calendar bound, YYYY-MM-DD. Example: 2026-06-01. Cannot be combined with recency_minutes, and is not supported for domain_type=research_paper.",
      "type": "string",
      "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
    },
    "before_date": {
      "description": "Upper calendar bound, YYYY-MM-DD. Example: 2026-06-18. Cannot be combined with recency_minutes, and is not supported for domain_type=research_paper.",
      "type": "string",
      "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
    },
    "domain_type": {
      "description": "Corpus to search. 'web' (default) returns general results; 'news' adds publisher and date; 'research_paper' searches academic work and adds authors, venue, year, cited_by_count, and pdf_url.",
      "type": "string",
      "enum": [
        "web",
        "news",
        "research_paper"
      ]
    },
    "pub_year_min": {
      "description": "Inclusive lower publication-year bound. Only supported for domain_type=research_paper. Example: 2017.",
      "type": "integer",
      "minimum": 0,
      "maximum": 9999
    },
    "pub_year_max": {
      "description": "Inclusive upper publication-year bound. Only supported for domain_type=research_paper. Example: 2024.",
      "type": "integer",
      "minimum": 0,
      "maximum": 9999
    },
    "page": {
      "description": "Zero-indexed result page. Example: 2 returns the third page. Maximum 10.",
      "type": "integer",
      "minimum": 0,
      "maximum": 10
    }
  },
  "required": [
    "query"
  ],
  "additionalProperties": false,
  "~standard": {
    "vendor": "zod",
    "version": 1,
    "jsonSchema": {}
  }
}

Documentation
  https://docs.tinyfish.ai/search-api/reference

Hints
  find other endpoints: monid discover -q '<QUERY>'
  run this endpoint: monid run -p tinyfish -e /search -i '<BODY>' --query '<QUERY_PARAMS>' --path '<PATH_PARAMS>'
  get the full page text for these results: monid inspect -p tinyfish -e /fetch  # also free, up to 10 URLs per call
  search and get page content in one call: monid discover -q 'web search with inline page content'  # several providers return content in one round-trip
  semantic search rather than keyword matching: monid inspect -p exa -e /search  # neural search with highlights

✔ Fetched details about /search from tinyfish

Update available: 0.1.6 → 0.1.7.
  Run `npm update -g @monid-ai/cli` to update monid-cli.
  Download the latest version of skill at https://monid.ai/SKILL.md.

```


**Tool Call: XDG_CONFIG_HOME="/Users/Mitesh Gada/Documents/Projects/.monid/xdg" /Users/Mitesh\ Gada/.npm-global/bin/monid run --provider tinyfish --endpoint /search --query '{"query":"ICAI SA 240 journal entries testing SA 230 documentation official","purpose":"Ground an architecture blueprint for an India-focused journal-entry audit analytics platform","include_domains":"icai.org"}' --wait 90 -j**
Status: Completed

Terminal:
```
{
  "runId": "01M22594W27V1YZXQSCVDJRA63",
  "provider": "tinyfish",
  "endpoint": "/search",
  "status": "COMPLETED",
  "output": {
    "query": "ICAI SA 240 journal entries testing SA 230 documentation official",
    "results": [
      {
        "date": "May 13, 2026",
        "position": 1,
        "site_name": "www.icai.org",
        "snippet": "SA 230, Audit Documentation SA 240, The Auditor's Responsibilities Relating to Fraud in an Audit of Financial Statements",
        "title": "Engagement and Quality Control Standards - Complete Text - ICAI",
        "url": "https://www.icai.org/post/auditing-review-and-other-standards-formerly-known-as-aas-complete-text"
      },
      {
        "position": 2,
        "site_name": "live.icai.org",
        "snippet": "SA 230 Scope: To prepare audit documentation for an audit of financial statements. Objective of SA SA 240 Identify. Test Journal Entries at period end, unusual ...",
        "title": "[PDF] SA 200 - ICAI",
        "url": "https://live.icai.org/bos/vcc-3rd-batch/pdf/SA_Chart_200_330.pdf"
      },
      {
        "date": "Oct 1, 2022",
        "position": 3,
        "site_name": "internalaudit.icai.org",
        "snippet": "The testing is executed and approved and signed off with prior acceptance. Documentation of test cases and approvals for each system solution ...",
        "title": "[PDF] Compendium of Standards on Internal Audit",
        "url": "https://internalaudit.icai.org/wp-content/uploads/2026/03/Compendium-of-Standards-on-Internal-Audit-October-2022.pdf"
      },
      {
        "position": 4,
        "site_name": "internalaudit.icai.org",
        "snippet": "SA 240 (The Auditor's Responsibilities Relating to Fraud in an Audit of Financial Statement)",
        "title": "[PDF] Compendium of Standards on Internal Audit",
        "url": "https://internalaudit.icai.org/wp-content/uploads/2026/03/Comp-of-Stnd-on-Internal-Audit-26.pdf?mkt_tok=NTIwLVJYUC0wMDMAAAGgnfhOC1xcJMlEYsQyn04Xx_ZK5RArX7NmyAY9dD0XdiWObMu2JiPBlcOVK9LRLiUp_8nXHyqpup2cfJwbin40Mf9s_JVRPvOVOX1VynRrPGdHH1QK-gUX"
      },
      {
        "date": "Dec 20, 2025",
        "position": 5,
        "site_name": "udin.icai.org",
        "snippet": "Standard on Auditing (SA)- 230 on Audit Documentation. in alignment with SQC-1 and SA 230, the same can be generated within 60 days … including ...",
        "title": "[PDF] FAQs on Unique Document Identification Number (UDIN) - ICAI",
        "url": "https://udin.icai.org/assets/images/FAQs%20on%20UDIN.pdf"
      },
      {
        "position": 6,
        "site_name": "www.icai.org",
        "snippet": "240. Constitution of Groups to study students related issues and ... 230. Release of Advertisement for Special B.Com Course with major in Accountancy ...",
        "title": "The Institute of Chartered Accountants of India - ICAI",
        "url": "https://www.icai.org/post/834"
      },
      {
        "position": 7,
        "site_name": "sustainability.icai.org",
        "snippet": "This document should provide detailed information about the NPO, the terms of the offering, risks involved, and the social impact of the organization's ...",
        "title": "[PDF] Business Responsibility & Sustainability Reporting(BRSR)",
        "url": "https://sustainability.icai.org/wp-content/uploads/2025/06/Background-Material-on-Sustainability-Business-Responsibility-Sustainability-Reporting-BRSR-Revised-Edition-2024.pdf"
      },
      {
        "date": "Jan 20, 2022",
        "position": 8,
        "site_name": "ic.icai.org",
        "snippet": "SAICA Initial Professional Development (IPD) committee, Accounting entries are distorted as a result of this kind of deception.",
        "title": "[PDF] ICAI-2022-Souvenir-Rev1.2.pdf",
        "url": "https://ic.icai.org/Doc/ICAI-2022-Souvenir-Rev1.2.pdf"
      }
    ],
    "total_results": 8,
    "page": 0
  },
  "providerResponse": {
    "httpStatus": 200
  },
  "price": {
    "type": "PER_CALL",
    "amount": {
      "value": 0,
      "currency": "USD"
    }
  },
  "billing": {
    "reportedCost": {
      "currency": "USD",
      "value": 0,
      "unit": "MICRO_DOLLAR"
    }
  },
  "resultCount": 0,
  "billedUnits": 0,
  "createdAt": "2026-09-09T04:02:10.842Z",
  "completedAt": "2026-09-09T04:02:12.631Z",
  "hints": {
    "retrieve the response later": "monid runs get -r 01M22594W27V1YZXQSCVDJRA63",
    "get the full page text for these results": "monid inspect -p tinyfish -e /fetch  # also free, up to 10 URLs per call",
    "semantic search rather than keyword matching": "monid inspect -p exa -e /search  # neural search with highlights",
    "search and get page content in one call": "monid discover -q 'web search with inline page content'  # several providers return content in one round-trip"
  },
  "notes": [
    "Update available: 0.1.6 → 0.1.7. Run `npm update -g @monid-ai/cli` to update monid-cli. Download the latest version of skill at https://monid.ai/SKILL.md."
  ]
}

```


## Assistant

<thinking>


**Clarifying blueprint scope and target users**

**Verifying firm segments and deployment needs**
</thinking>

## Input Requested

Input requested

## Assistant

<thinking>


**Designing modular pipeline blueprint**

**Finalizing detailed proposed plan**
</thinking>

# Audit Analytics Pipeline Blueprint

## Summary

Create a standalone, firm-controlled audit analytics application for India-focused external statutory audits. It will ingest general-ledger and chart-of-accounts extracts, identify explainable journal-entry risk cues, and produce reviewer-controlled workpapers. It will not issue audit opinions, determine fraud, or require complete supporting-document collections.

Transfer the reliable pipeline patterns from `qcom-scraping`—incremental observation storage, entity-specific baselines, event/state handling, provenance, anomaly ranking, human review, exports, and dashboarding—while replacing web crawling and demand signals with controlled financial-data ingestion and audit-risk evidence.

## Pipeline and interfaces

- **Engagement setup:** Create an isolated engagement workspace with client, period, materiality/planning settings, currency, fiscal calendar, and approved reviewers. Store data locally or in the firm’s private VPC; do not send client ledger data to external AI or model APIs.

- **Ingestion contract:** Start with CSV/XLSX GL and COA extracts. The GL contract requires a unique entry ID, posting date, document date where available, account code, debit/credit or signed amount, description/narration, user/preparer, document/reference number, and source-file row identity. Preserve raw source files, validation results, import mappings, and immutable row hashes.

- **Normalization and population controls:** Validate required fields, date/amount parsing, debit-credit balancing, duplicate entry IDs, COA joins, fiscal-period assignment, and rejected-row reasons. Reconcile the accepted GL population to supplied control totals; block scoring until the reviewer accepts or documents population differences.

- **Feature layer:** Build entry, account, preparer, period, and peer-group features: account-normalized amount, posting-time/date patterns, manual-versus-system indicator where supplied, weekend/holiday and period-end proximity, rare account combinations, unusual users, narration/reference repetition, round-number behavior, reversals, duplicate/split entries, and debit-credit pair patterns.

- **Risk analytics:** Run the agreed hybrid suite:
  - Deterministic tests for duplicate entries, duplicate amounts/references, round amounts, period-end/manual postings, unusual account pairs, reversals, and threshold breaches.
  - Robust peer-group outlier detection using median/MAD and percentile measures, grouped by account, entity, preparer, and comparable period.
  - Benford analysis only on populations meeting applicability and minimum-size checks; label it as a population-level indicator, never an entry-level fraud conclusion.
  - Optional Isolation Forest only when the engagement has sufficient clean, comparable population volume; retain feature contributions/proxy explanations and never allow the model alone to create an exception.

- **Risk scoring and sampling:** Combine triggered tests into an explainable score with component-level reasons, population context, severity, and confidence/coverage flags. Produce ranked review queues plus documented, risk-based population strata and sample selections. No score becomes an audit finding without auditor disposition.

- **Workpaper review:** Provide an in-app queue showing original GL fields, source-file reference, triggered tests, peer baseline, visual trend/context, reviewer notes, status, owner, and final disposition. Preserve every disposition/change in an append-only audit trail. Export Excel/PDF workpapers with population reconciliation, methodology, selected samples, results, exceptions, and reviewer sign-off fields.

- **Reporting:** Provide engagement-level planning and completion views: data quality, population coverage, high-risk accounts/users/periods, test results, unresolved items, and limitations. Clearly label outputs as audit decision support under auditor judgment, aligned to SA 230 documentation and SA 240 journal-entry fraud-risk procedures.

## Product architecture

- Reuse the source project’s SQLite/WAL-style incremental data model, dashboard pattern, pure analysis functions, additive schema migrations, CSV export approach, and human-review workflow.
- Replace its crawler/adapters with file import adapters; future ERP connectors and broader audit packages plug into the same normalized ingestion boundary.
- Use separate raw-import, normalized-ledger, derived-feature, model-run, exception, reviewer-disposition, and immutable-audit-log records. Every result must link back to an import version and original row identity.
- Keep models versioned and parameters captured per run so a workpaper can be reproduced after configuration changes.
- Treat missing, malformed, or incomplete data as coverage limitations—not suspicious transactions—and surface them separately from risk exceptions.

## Test plan

- Import valid and malformed GL/COA files; verify mapping, rejection reporting, hashes, and accepted-population reconciliation.
- Verify debit-credit/control-total reconciliation and that scoring is blocked until population differences are acknowledged.
- Use synthetic ledgers to test every deterministic risk cue, peer-group outlier ranking, Benford applicability guardrails, and optional model minimum-data guardrails.
- Confirm no external network/model call is made with engagement data.
- Confirm source-row traceability, immutable review history, reproducible reruns, role restrictions, and complete Excel/PDF workpaper exports.
- Validate that exports describe limitations and never present risk scores as audit conclusions.

## Assumptions

- V1 is a standalone application blueprint, not a fork of `qcom-scraping`.
- Initial users are Indian audit firms performing external statutory audits.
- V1 is GL-first with COA support; ERP connectors, invoices/vouchers, OCR, bank data, related-party graphs, and continuous internal-audit monitoring remain future extensions.
- Review happens in-app with exportable workpapers; human auditors retain responsibility for procedures, evidence evaluation, and conclusions.


**Tool Call: Implement this plan?**
Status: Completed

User approved the plan.

## Assistant

<thinking>


**Planning audit-analytics minimal implementation**

**Checking dependencies and git status**
</thinking>

I’ll build this as a new standalone `audit-analytics` project, keeping the first release local-only and CSV-first with XLSX support when `openpyxl` is available. I’ll preserve raw-source traceability and make statistical outputs review cues rather than conclusions.

**Tool Call: git status --short && git -C qcom-scraping status --short && python3 - <<'PY'
try:
 import openpyxl
 print('openpyxl: available')
except ImportError:
 print('openpyxl: unavailable')
PY
rg --files | rg '(^|/)(audit|ledger|journal)' | sed -n '1,160p'**
Status: Completed

Terminal:
```
Vibe-Trading/agent/src/governance/ledger.py
Vibe-Trading/agent/src/live/audit.py

```


## Assistant

<thinking>


**Verifying git rerun and dependencies**
</thinking>

**Tool Call: git -C qcom-scraping status --short; python3 - <<'PY'
try:
 import openpyxl
 print('openpyxl: available')
except ImportError:
 print('openpyxl: unavailable')
PY
find . -maxdepth 1 -type d -print**
Status: Completed

Terminal:
```
openpyxl: unavailable
.
./Clock-app-productivity-v3
./qcom-scraping
./qr-transfer
./Profile Audits
./BlueBubbles
./High-Angle_Robust_Fast_FaceAlignment
./StudyMonitor
./Financial-model-v2
./Vibe-Trading
./deepseek-harness-token
./Generic Apps
./imessage-bridge
./Qwen Webapp
./.archify
./.tools
./Do not delete folder
./Games
./.monid-config
./reverse-skill
./.monid
./Financial-model-v1

```


## Assistant

<thinking>


**Planning minimal standalone project structure**

**Defining CLI commands and import data model**

**Planning analytics and ack-population command**
</thinking>

<thinking>


**Planning lightweight isolation forest implementation**

**Designing simple isolation forest dashboard and API**
</thinking>

**Tool Call: mkdir -p audit-analytics/src/audit_analytics audit-analytics/tests**
Status: Completed

Terminal:
```






```


## Assistant

<thinking>


**Planning patch-based changes**
</thinking>

**Tool Call: Editing files**
Status: Completed

Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/README.md
```
# Audit Analytics

Local-first journal-entry analytics for Indian statutory-audit teams. It ranks
explainable risk cues for auditor review; it does not make audit conclusions or
issue an opinion.

## Quick start

```sh
cd audit-analytics
python3 run.py init --db demo/audit.db --client "Example Ltd" --period 2025-04-01:2026-03-31
python3 run.py import-gl --db demo/audit.db --file journal_entries.csv
python3 run.py acknowledge-population --db demo/audit.db --reviewer "A. Auditor" --note "Agreed to client GL control totals"
python3 run.py analyze --db demo/audit.db
python3 run.py serve --db demo/audit.db
```

Open `http://127.0.0.1:8788` to review and disposition flagged entries. Export
an evidence-linked CSV workpaper with `python3 run.py export --db demo/audit.db
--out demo/workpaper.csv`.

## Supported GL fields

Headers are matched case-insensitively with common aliases. Required: entry ID,
posting date, account code, and either signed amount or debit and credit.
Optional fields include document date, description/narration, preparer/user,
reference/document number, entity, and manual/system indicator. COA imports
are supported through `import-coa` and enrich account labels only.

CSV is supported with the standard library. `.xlsx` is deliberately rejected
unless `openpyxl` is installed in the firm-controlled environment; no client
data is uploaded to enable it.

## Controls and limitations

- Every imported source file is copied into `evidence/` beside the engagement
  database and is SHA-256 hashed; each entry retains source row identity.
- Import validation separates rejected/missing data from risk cues.
- Analysis is blocked until a reviewer acknowledges the accepted population and
  control totals.
- The statistical suite includes deterministic tests, account-peer robust
  outliers, Benford population checks, reversal matching, and an optional local
  isolation-style model for populations of at least 256 entries.
- Risk scores are prioritisation cues. Reviewer dispositions and audit-log
  records are append-only; no result is labelled fraud or an audit conclusion.

The controls are designed to support documentation under SA 230 and journal
entry procedures under SA 240; the engagement team remains responsible for
audit design, evidence evaluation, and conclusions.

```


Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/run.py
```
#!/usr/bin/env python3
"""Local journal-entry analytics entry point."""
from audit_analytics.cli import main

if __name__ == "__main__":
    main()

```


Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/src/audit_analytics/__init__.py
```
"""Audit analytics: explainable journal-entry risk cues for human review."""

```


Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/src/audit_analytics/importer.py
```
from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

from .store import Store

ALIASES = {
    "entry_id": ("entry_id", "journal_entry_id", "voucher_no", "voucher_number", "transaction_id", "document_id"),
    "posting_date": ("posting_date", "date", "entry_date", "postingdate"),
    "document_date": ("document_date", "doc_date", "voucher_date"),
    "account_code": ("account_code", "account", "gl_code", "ledger_code", "account_number"),
    "debit": ("debit", "dr", "debit_amount"), "credit": ("credit", "cr", "credit_amount"),
    "amount": ("amount", "signed_amount", "net_amount", "value"),
    "description": ("description", "narration", "memo", "particulars"),
    "preparer": ("preparer", "user", "created_by", "posted_by"),
    "reference": ("reference", "reference_no", "document_no", "invoice_no", "voucher_no"),
    "entity": ("entity", "company", "cost_center", "branch"),
    "is_manual": ("is_manual", "manual", "source_type"),
}


def _key(s): return "".join(c.lower() for c in (s or "") if c.isalnum() or c == "_")

def _number(value):
    if value in (None, ""): return 0.0
    return float(str(value).replace(",", "").replace("₹", "").strip().strip("()") or 0)

def _date(value):
    raw = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try: return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError: pass
    raise ValueError("invalid posting date")

def _rows(path: Path):
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as f:
            yield from csv.DictReader(f)
        return
    if path.suffix.lower() == ".xlsx":
        try: import openpyxl
        except ImportError as e: raise ValueError("XLSX requires local openpyxl; CSV is available without dependencies") from e
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb.active; headers = [str(x or "") for x in next(ws.iter_rows(values_only=True))]
        for cells in ws.iter_rows(values_only=True): yield dict(zip(headers, cells))
        return
    raise ValueError("only .csv and .xlsx files are supported")

def _canonical(row):
    indexed = {_key(k): v for k, v in row.items()}
    out = {}
    for field, aliases in ALIASES.items():
        out[field] = next((indexed[_key(a)] for a in aliases if _key(a) in indexed), None)
    return out

def import_gl(store: Store, filename: str, actor="system"):
    source = Path(filename)
    if not source.is_file(): raise ValueError(f"source file not found: {source}")
    evidence = store.path.parent / "evidence"; evidence.mkdir(exist_ok=True)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    target = evidence / f"{digest[:12]}_{source.name}"
    if not target.exists(): shutil.copy2(source, target)
    cur = store.conn.execute("INSERT INTO imports(kind,original_name,evidence_path,sha256,imported_at,accepted_rows,rejected_rows) VALUES('gl',?,?,?,?,?,?)",
                             (source.name, str(target), digest, __import__('time').time(), 0, 0))
    import_id = cur.lastrowid; accepted = rejected = 0; debits = credits = 0.0
    for line, raw in enumerate(_rows(source), 2):
        try:
            r = _canonical(raw); entry_id = str(r["entry_id"] or "").strip(); account = str(r["account_code"] or "").strip()
            if not entry_id or not account: raise ValueError("missing entry ID or account code")
            posting = _date(r["posting_date"])
            debit, credit = _number(r["debit"]), _number(r["credit"])
            if not debit and not credit:
                amount = _number(r["amount"])
                debit, credit = (amount, 0.0) if amount >= 0 else (0.0, -amount)
            if debit < 0 or credit < 0 or (debit and credit): raise ValueError("invalid debit/credit values")
            manual = str(r["is_manual"] or "").lower() in ("1", "true", "yes", "manual")
            raw_json = json.dumps(raw, default=str, sort_keys=True); row_hash = hashlib.sha256(raw_json.encode()).hexdigest()
            store.conn.execute("""INSERT INTO ledger_entries(import_id,entry_id,posting_date,document_date,account_code,debit,credit,signed_amount,description,preparer,reference,entity,is_manual,source_row,source_hash,raw_json)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (import_id, entry_id, posting, _date(r["document_date"]) if r["document_date"] else None, account, debit, credit, debit-credit, r["description"], r["preparer"], r["reference"], r["entity"], int(manual), line, row_hash, raw_json))
            accepted += 1; debits += debit; credits += credit
        except (ValueError, TypeError) as e:
            rejected += 1; store.conn.execute("INSERT INTO rejected_rows(import_id,source_row,reason,raw_json) VALUES(?,?,?,?)", (import_id, line, str(e), json.dumps(raw, default=str)))
    store.conn.execute("UPDATE imports SET accepted_rows=?,rejected_rows=?,control_debits=?,control_credits=? WHERE id=?", (accepted, rejected, debits, credits, import_id))
    store.log(actor, "import_gl", "import", import_id, {"accepted": accepted, "rejected": rejected, "sha256": digest})
    store.conn.commit(); return import_id, accepted, rejected, debits, credits

def import_coa(store: Store, filename: str, actor="system"):
    source = Path(filename); rows = list(_rows(source)); cur = store.conn.execute("INSERT INTO imports(kind,original_name,evidence_path,sha256,imported_at,accepted_rows,rejected_rows) VALUES('coa',?,?,?,?,?,?)", (source.name, str(source), hashlib.sha256(source.read_bytes()).hexdigest(), __import__('time').time(), 0, 0)); iid = cur.lastrowid
    for raw in rows:
        r = {_key(k): v for k, v in raw.items()}; code = r.get("account_code") or r.get("account") or r.get("gl_code")
        if code: store.conn.execute("INSERT OR REPLACE INTO coa VALUES(?,?,?,?)", (str(code), r.get("account_name") or r.get("name"), r.get("account_type") or r.get("type"), iid))
    store.conn.execute("UPDATE imports SET accepted_rows=? WHERE id=?", (len(rows), iid)); store.log(actor, "import_coa", "import", iid, {"rows": len(rows)}); store.conn.commit(); return iid

```


Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/src/audit_analytics/store.py
```
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path


SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS engagement (
  id INTEGER PRIMARY KEY CHECK(id=1), client TEXT NOT NULL, period_start TEXT NOT NULL,
  period_end TEXT NOT NULL, created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS imports (
  id INTEGER PRIMARY KEY, kind TEXT NOT NULL, original_name TEXT NOT NULL,
  evidence_path TEXT NOT NULL, sha256 TEXT NOT NULL, imported_at REAL NOT NULL,
  accepted_rows INTEGER NOT NULL, rejected_rows INTEGER NOT NULL, control_debits REAL,
  control_credits REAL, acknowledged_at REAL, acknowledged_by TEXT, acknowledgement_note TEXT
);
CREATE TABLE IF NOT EXISTS coa (
  account_code TEXT PRIMARY KEY, account_name TEXT, account_type TEXT, import_id INTEGER REFERENCES imports(id)
);
CREATE TABLE IF NOT EXISTS ledger_entries (
  id INTEGER PRIMARY KEY, import_id INTEGER NOT NULL REFERENCES imports(id), entry_id TEXT NOT NULL,
  posting_date TEXT NOT NULL, document_date TEXT, account_code TEXT NOT NULL, debit REAL NOT NULL,
  credit REAL NOT NULL, signed_amount REAL NOT NULL, description TEXT, preparer TEXT,
  reference TEXT, entity TEXT, is_manual INTEGER, source_row INTEGER NOT NULL,
  source_hash TEXT NOT NULL, raw_json TEXT NOT NULL, UNIQUE(import_id, source_row)
);
CREATE INDEX IF NOT EXISTS ledger_account_date ON ledger_entries(account_code, posting_date);
CREATE INDEX IF NOT EXISTS ledger_entry_id ON ledger_entries(entry_id);
CREATE TABLE IF NOT EXISTS rejected_rows (
  id INTEGER PRIMARY KEY, import_id INTEGER NOT NULL REFERENCES imports(id), source_row INTEGER NOT NULL,
  reason TEXT NOT NULL, raw_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS model_runs (
  id INTEGER PRIMARY KEY, started_at REAL NOT NULL, completed_at REAL, configuration TEXT NOT NULL,
  population_count INTEGER NOT NULL, status TEXT NOT NULL, limitation_note TEXT
);
CREATE TABLE IF NOT EXISTS exceptions (
  id INTEGER PRIMARY KEY, run_id INTEGER NOT NULL REFERENCES model_runs(id), ledger_id INTEGER NOT NULL REFERENCES ledger_entries(id),
  risk_score REAL NOT NULL, severity TEXT NOT NULL, reasons_json TEXT NOT NULL,
  evidence_json TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'open', UNIQUE(run_id, ledger_id)
);
CREATE TABLE IF NOT EXISTS reviews (
  id INTEGER PRIMARY KEY, exception_id INTEGER NOT NULL REFERENCES exceptions(id), reviewer TEXT NOT NULL,
  disposition TEXT NOT NULL, note TEXT NOT NULL, created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY, created_at REAL NOT NULL, actor TEXT NOT NULL, action TEXT NOT NULL,
  target_type TEXT NOT NULL, target_id TEXT NOT NULL, detail_json TEXT NOT NULL
);
"""


class Store:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def log(self, actor: str, action: str, target_type: str, target_id: str | int, detail: dict):
        self.conn.execute("INSERT INTO audit_log VALUES(NULL,?,?,?,?,?,?)",
                          (time.time(), actor, action, target_type, str(target_id), json.dumps(detail, sort_keys=True)))

    def engagement(self):
        return self.conn.execute("SELECT * FROM engagement WHERE id=1").fetchone()

    def population_acknowledged(self):
        row = self.conn.execute("SELECT COUNT(*) FROM imports WHERE kind='gl' AND acknowledged_at IS NULL").fetchone()
        return row[0] == 0 and self.conn.execute("SELECT COUNT(*) FROM imports WHERE kind='gl'").fetchone()[0] > 0

    def close(self):
        self.conn.close()

```


## Assistant

<thinking>


**Applying patch for dashboard CLI test**
</thinking>

**Tool Call: Editing files**
Status: Completed

Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/src/audit_analytics/analytics.py
```
from __future__ import annotations

import json
import math
import random
import statistics
import time
from collections import Counter, defaultdict
from datetime import date, timedelta

from .store import Store


def _median_mad(values):
    median = statistics.median(values)
    mad = statistics.median([abs(x - median) for x in values])
    return median, mad

def _benford(entries):
    numbers = [abs(e["signed_amount"]) for e in entries if abs(e["signed_amount"]) >= 1]
    if len(numbers) < 100: return {"applicable": False, "n": len(numbers), "reason": "requires at least 100 non-zero amounts"}
    observed = Counter(str(int(x)).lstrip("0")[0] for x in numbers if str(int(x)).lstrip("0"))
    expected = {str(i): math.log10(1 + 1 / i) for i in range(1, 10)}
    mad = sum(abs(observed[str(i)] / len(numbers) - expected[str(i)]) for i in range(1, 10)) / 9
    return {"applicable": True, "n": len(numbers), "mad": round(mad, 4), "flag": mad > 0.015,
            "note": "Population-level indicator only; it does not identify fraudulent entries."}

def _isolation_scores(entries, trees=40, seed=7):
    """Small deterministic isolation-style scorer; retains all data locally.

    ponytail: this is a compact random-cut forest, not a replacement for a
    governed ML platform; upgrade to a validated model registry when needed.
    """
    if len(entries) < 256: return {}
    amounts = [math.log1p(abs(e["signed_amount"])) for e in entries]
    account_counts, user_counts = Counter(e["account_code"] for e in entries), Counter(e["preparer"] or "" for e in entries)
    points = [(amounts[i], -math.log(account_counts[e["account_code"]] / len(entries)), -math.log(user_counts[e["preparer"] or ""] / len(entries))) for i, e in enumerate(entries)]
    rng = random.Random(seed); depths = [0.0] * len(entries)
    for _ in range(trees):
        active = list(range(len(entries))); depth = [0] * len(entries)
        while len(active) > 1:
            dim = rng.randrange(3); vals = [points[i][dim] for i in active]; lo, hi = min(vals), max(vals)
            if lo == hi: break
            cut = rng.uniform(lo, hi); left = [i for i in active if points[i][dim] < cut]; right = [i for i in active if points[i][dim] >= cut]
            if not left or not right: break
            for i in active: depth[i] += 1
            # Recursively isolate the smaller partition first; one cut per tree level keeps runtime bounded.
            active = left if len(left) <= len(right) else right
        for i in range(len(entries)): depths[i] += depth[i]
    max_depth = max(depths) or 1
    return {entries[i]["id"]: round(1 - depths[i] / max_depth, 3) for i in range(len(entries))}

def analyze(store: Store, actor="system", include_isolation=True):
    if not store.population_acknowledged(): raise ValueError("analysis blocked: acknowledge every GL import's accepted population and control totals first")
    entries = [dict(r) for r in store.conn.execute("SELECT * FROM ledger_entries ORDER BY id")]
    if not entries: raise ValueError("no GL entries imported")
    cfg = {"tests": ["duplicate", "round_amount", "period_end", "weekend", "rare_account_user", "reversal", "robust_peer_outlier", "benford"], "isolation": include_isolation and len(entries) >= 256}
    run = store.conn.execute("INSERT INTO model_runs(started_at,configuration,population_count,status) VALUES(?,?,?,?)", (time.time(), json.dumps(cfg), len(entries), "running")).lastrowid
    reasons, evidence = defaultdict(list), defaultdict(dict)
    by_key = defaultdict(list); by_account = defaultdict(list); by_user_pair = Counter(); ref_key = defaultdict(list)
    for e in entries:
        amount = round(abs(e["signed_amount"]), 2); by_account[e["account_code"]].append(e)
        by_user_pair[(e["account_code"], e["preparer"] or "")]+=1
        if e["reference"]: by_key[(e["account_code"], e["reference"], amount)].append(e)
        by_key[(e["account_code"], e["posting_date"], amount, e["description"] or "")].append(e)
        ref_key[(e["account_code"], amount)].append(e)
    for group in by_key.values():
        if len(group) > 1:
            for e in group: reasons[e["id"]].append("duplicate_or_repeated_entry"); evidence[e["id"]]["duplicate_count"] = len(group)
    end = date.fromisoformat(store.engagement()["period_end"])
    for e in entries:
        eid, amount = e["id"], abs(e["signed_amount"]); posted = date.fromisoformat(e["posting_date"])
        if amount and amount >= 1000 and amount % 1000 == 0: reasons[eid].append("round_amount")
        if posted >= end - timedelta(days=3): reasons[eid].append("period_end_posting")
        if posted.weekday() >= 5: reasons[eid].append("weekend_posting")
        if by_user_pair[(e["account_code"], e["preparer"] or "")] <= 2: reasons[eid].append("rare_account_preparer_pair")
        peer = [abs(x["signed_amount"]) for x in by_account[e["account_code"]]]
        if len(peer) >= 8:
            med, mad = _median_mad(peer)
            if mad and abs(amount-med)/(1.4826*mad) >= 3.5:
                reasons[eid].append("robust_account_peer_outlier"); evidence[eid]["peer_median"] = round(med, 2); evidence[eid]["robust_z"] = round(abs(amount-med)/(1.4826*mad), 2)
        for other in ref_key[(e["account_code"], round(amount, 2))]:
            if other["id"] != eid and other["signed_amount"] * e["signed_amount"] < 0 and abs((date.fromisoformat(other["posting_date"])-posted).days) <= 30:
                reasons[eid].append("possible_reversal_within_30_days"); evidence[eid]["reversal_ledger_id"] = other["id"]; break
    benford = _benford(entries)
    if benford["applicable"] and benford["flag"]:
        for e in entries: evidence[e["id"]]["benford_population_indicator"] = benford
    isolation = _isolation_scores(entries) if cfg["isolation"] else {}
    for e in entries:
        iso = isolation.get(e["id"], 0)
        if iso >= 0.72: reasons[e["id"]].append("isolation_style_anomaly"); evidence[e["id"]]["isolation_score"] = iso
        if not reasons[e["id"]]: continue
        score = min(100, 20 * len(set(reasons[e["id"]])) + (15 if evidence[e["id"]].get("robust_z", 0) >= 5 else 0) + (15 if iso >= .85 else 0))
        severity = "high" if score >= 70 else "medium" if score >= 40 else "low"
        store.conn.execute("INSERT INTO exceptions(run_id,ledger_id,risk_score,severity,reasons_json,evidence_json) VALUES(?,?,?,?,?,?)", (run, e["id"], score, severity, json.dumps(sorted(set(reasons[e["id"]]))), json.dumps(evidence[e["id"]], sort_keys=True)))
    limitation = "Benford: " + (benford.get("note") or benford.get("reason", "not applicable"))
    store.conn.execute("UPDATE model_runs SET completed_at=?,status='complete',limitation_note=? WHERE id=?", (time.time(), limitation, run))
    store.log(actor, "analyze", "model_run", run, {"population": len(entries), "benford": benford, "isolation_enabled": bool(isolation)})
    store.conn.commit(); return run

```


Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/src/audit_analytics/cli.py
```
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .analytics import analyze
from .importer import import_coa, import_gl
from .server import serve
from .store import Store

def _store(path): return Store(path)

def main():
    p = argparse.ArgumentParser(description="Local journal-entry audit analytics")
    sub = p.add_subparsers(dest="cmd", required=True)
    init = sub.add_parser("init"); init.add_argument("--db", required=True); init.add_argument("--client", required=True); init.add_argument("--period", required=True, help="YYYY-MM-DD:YYYY-MM-DD")
    for name in ("import-gl", "import-coa"):
        x=sub.add_parser(name); x.add_argument("--db", required=True); x.add_argument("--file", required=True); x.add_argument("--actor", default="system")
    ack=sub.add_parser("acknowledge-population"); ack.add_argument("--db", required=True); ack.add_argument("--reviewer", required=True); ack.add_argument("--note", required=True)
    a=sub.add_parser("analyze"); a.add_argument("--db", required=True); a.add_argument("--actor", default="system"); a.add_argument("--no-isolation", action="store_true")
    e=sub.add_parser("export"); e.add_argument("--db", required=True); e.add_argument("--out", required=True)
    s=sub.add_parser("serve"); s.add_argument("--db", required=True); s.add_argument("--port", type=int, default=8788)
    args=p.parse_args(); store=_store(args.db)
    try:
        if args.cmd == "init":
            start, end=args.period.split(":", 1); store.conn.execute("INSERT INTO engagement VALUES(1,?,?,?,strftime('%s','now'))", (args.client,start,end)); store.log("system","init","engagement",1,{"client":args.client}); store.conn.commit(); print(f"created engagement for {args.client}")
        elif args.cmd == "import-gl":
            iid,n,b,d,c=import_gl(store,args.file,args.actor); print(f"GL import {iid}: accepted={n}, rejected={b}, debit={d:.2f}, credit={c:.2f}")
        elif args.cmd == "import-coa": print(f"COA import {import_coa(store,args.file,args.actor)} complete")
        elif args.cmd == "acknowledge-population":
            pending=store.conn.execute("SELECT id,accepted_rows,rejected_rows,control_debits,control_credits FROM imports WHERE kind='gl' AND acknowledged_at IS NULL").fetchall()
            if not pending: raise ValueError("no unacknowledged GL imports")
            for r in pending: store.conn.execute("UPDATE imports SET acknowledged_at=strftime('%s','now'),acknowledged_by=?,acknowledgement_note=? WHERE id=?",(args.reviewer,args.note,r["id"])); store.log(args.reviewer,"acknowledge_population","import",r["id"],dict(r))
            store.conn.commit(); print(f"acknowledged {len(pending)} GL import(s)")
        elif args.cmd == "analyze": print(f"analysis run {analyze(store,args.actor,not args.no_isolation)} complete")
        elif args.cmd == "export":
            rows=store.conn.execute("""SELECT e.*,l.entry_id,l.posting_date,l.account_code,l.signed_amount,l.description,l.preparer,l.reference,e.reasons_json,e.evidence_json
              FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id ORDER BY e.risk_score DESC""").fetchall(); out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
            with out.open("w",newline="",encoding="utf-8") as f:
                w=csv.writer(f); w.writerow(["exception_id","risk_score","severity","status","entry_id","posting_date","account_code","signed_amount","description","preparer","reference","reasons","evidence"]); w.writerows([[r[k] for k in ("id","risk_score","severity","status","entry_id","posting_date","account_code","signed_amount","description","preparer","reference","reasons_json","evidence_json")] for r in rows])
            print(f"wrote {len(rows)} review cues to {out}")
        else: serve(args.db,args.port)
    finally: store.close()

```


## Assistant

<thinking>


**Planning server implementation and test fixes**
</thinking>

The core implementation is in place: immutable import evidence, population acknowledgement gating, local hybrid scoring, and traceable exceptions. I’m adding the review UI/export path now, then I’ll exercise it with a synthetic ledger.

**Tool Call: Editing files**
Status: Completed

Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/src/audit_analytics/server.py
```
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from .store import Store

PAGE = """<!doctype html><title>Audit Analytics Review</title><style>body{font:14px system-ui;margin:2rem;max-width:1200px}table{border-collapse:collapse;width:100%}th,td{border:1px solid #ddd;padding:.5rem;text-align:left}th{background:#f5f5f5}.high{color:#a00;font-weight:bold}.medium{color:#a60;font-weight:bold}textarea{width:100%;height:3rem}</style><h1>Journal-entry review</h1><p id=summary></p><table><thead><tr><th>Risk</th><th>Entry</th><th>Context</th><th>Reasons / evidence</th><th>Disposition</th></tr></thead><tbody id=rows></tbody></table><script>
async function load(){let x=await (await fetch('/api/exceptions')).json();document.querySelector('#summary').textContent=`${x.count} review cues · outputs support auditor judgement and are not conclusions.`;let body=document.querySelector('#rows');body.innerHTML=x.rows.map(r=>`<tr><td class="${r.severity}">${r.risk_score} (${r.severity})<br>${r.status}</td><td>${r.entry_id}<br>${r.posting_date}<br>${r.account_code}: ${r.signed_amount}</td><td>${r.description||''}<br>Preparer: ${r.preparer||'—'}<br>Ref: ${r.reference||'—'}</td><td>${r.reasons.join('<br>')}<hr><small>${JSON.stringify(r.evidence)}</small></td><td><select id=s${r.id}><option>open</option><option>cleared</option><option>follow_up</option><option>selected_for_testing</option></select><textarea id=n${r.id} placeholder="Audit rationale / evidence requested"></textarea><button onclick="review(${r.id})">Save</button></td></tr>`).join('')}
async function review(id){let reviewer=prompt('Reviewer name');if(!reviewer)return;let disposition=document.querySelector('#s'+id).value,note=document.querySelector('#n'+id).value;if(!note){alert('A review note is required');return}let r=await fetch('/api/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id,reviewer,disposition,note})});if(!r.ok)alert(await r.text());else load()}load();</script>"""

def serve(db_path: str, port=8788):
    class Handler(BaseHTTPRequestHandler):
        def _json(self, value, status=200):
            payload=json.dumps(value, default=str).encode(); self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(payload))); self.end_headers(); self.wfile.write(payload)
        def do_GET(self):
            if urlparse(self.path).path == "/":
                payload=PAGE.encode(); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(payload))); self.end_headers(); self.wfile.write(payload); return
            if urlparse(self.path).path == "/api/exceptions":
                s=Store(db_path)
                try:
                    rows=s.conn.execute("""SELECT e.*,l.entry_id,l.posting_date,l.account_code,l.signed_amount,l.description,l.preparer,l.reference
                    FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id ORDER BY e.risk_score DESC""").fetchall()
                    out=[]
                    for r in rows:
                        x=dict(r); x["reasons"]=json.loads(x.pop("reasons_json")); x["evidence"]=json.loads(x.pop("evidence_json")); out.append(x)
                    self._json({"count":len(out),"rows":out})
                finally: s.close()
                return
            self._json({"error":"not found"},404)
        def do_POST(self):
            if urlparse(self.path).path != "/api/review": self._json({"error":"not found"},404); return
            try:
                data=json.loads(self.rfile.read(int(self.headers.get("Content-Length","0"))))
                if not all(isinstance(data.get(k),str) and data[k].strip() for k in ("reviewer","disposition","note")): raise ValueError("reviewer, disposition, and note are required")
                if data["disposition"] not in {"open","cleared","follow_up","selected_for_testing"}: raise ValueError("invalid disposition")
                s=Store(db_path)
                try:
                    exists=s.conn.execute("SELECT 1 FROM exceptions WHERE id=?",(data.get("id"),)).fetchone()
                    if not exists: raise ValueError("exception not found")
                    cur=s.conn.execute("INSERT INTO reviews(exception_id,reviewer,disposition,note,created_at) VALUES(?,?,?,?,strftime('%s','now'))",(data["id"],data["reviewer"].strip(),data["disposition"],data["note"].strip()))
                    s.conn.execute("UPDATE exceptions SET status=? WHERE id=?",(data["disposition"],data["id"])); s.log(data["reviewer"],"review_exception","exception",data["id"],{"review_id":cur.lastrowid,"disposition":data["disposition"]}); s.conn.commit()
                finally: s.close()
                self._json({"ok":True})
            except (ValueError, json.JSONDecodeError) as e: self._json({"error":str(e)},400)
        def log_message(self,*args): pass
    print(f"Audit review UI: http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1",port),Handler).serve_forever()

```


Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/tests/test_pipeline.py
```
import csv
import tempfile
import unittest
from pathlib import Path

from audit_analytics.analytics import analyze
from audit_analytics.importer import import_gl
from audit_analytics.store import Store

class PipelineTest(unittest.TestCase):
    def test_import_requires_acknowledgement_then_creates_traceable_exception(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); gl=root/'gl.csv'
            with gl.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['entry_id','posting_date','account_code','amount','description','preparer','reference']); w.writeheader()
                for i in range(12): w.writerow({'entry_id':f'J{i}','posting_date':'2026-03-31' if i==11 else '2026-02-01','account_code':'6000','amount':1000 if i==11 else 100+i,'description':'accrual','preparer':'admin','reference':f'R{i}'})
            store=Store(str(root/'audit.db')); store.conn.execute("INSERT INTO engagement VALUES(1,'Client','2025-04-01','2026-03-31',0)"); store.conn.commit()
            iid,accepted,rejected,_,_=import_gl(store,str(gl)); self.assertEqual((accepted,rejected),(12,0))
            with self.assertRaisesRegex(ValueError,'acknowledge'): analyze(store)
            store.conn.execute("UPDATE imports SET acknowledged_at=1,acknowledged_by='Auditor',acknowledgement_note='agreed' WHERE id=?",(iid,)); store.conn.commit()
            analyze(store); row=store.conn.execute("SELECT e.*,l.source_row,l.source_hash FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id WHERE l.entry_id='J11'").fetchone()
            self.assertIsNotNone(row); self.assertEqual(row['source_row'],13); self.assertTrue(row['source_hash'])
            self.assertTrue((root/'evidence').exists())

if __name__ == '__main__': unittest.main()

```


## Assistant

<thinking>


**Configuring PYTHONPATH for tests**
</thinking>

**Tool Call: PYTHONPATH=src python3 -m unittest discover -s tests -v && python3 -m py_compile run.py src/audit_analytics/*.py**
Status: Completed

Terminal:
```
test_import_requires_acknowledgement_then_creates_traceable_exception (test_pipeline.PipelineTest.test_import_requires_acknowledgement_then_creates_traceable_exception) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.091s

OK

```


## Assistant

<thinking>


**Planning Python path patch for CLI imports**

**Fixing COA raw evidence copying in import**
</thinking>

**Tool Call: Editing files**
Status: Completed

Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/run.py
```
#!/usr/bin/env python3
"""Local journal-entry analytics entry point."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from audit_analytics.cli import main

if __name__ == "__main__":
    main()

```


Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/src/audit_analytics/importer.py
```
from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

from .store import Store

ALIASES = {
    "entry_id": ("entry_id", "journal_entry_id", "voucher_no", "voucher_number", "transaction_id", "document_id"),
    "posting_date": ("posting_date", "date", "entry_date", "postingdate"),
    "document_date": ("document_date", "doc_date", "voucher_date"),
    "account_code": ("account_code", "account", "gl_code", "ledger_code", "account_number"),
    "debit": ("debit", "dr", "debit_amount"), "credit": ("credit", "cr", "credit_amount"),
    "amount": ("amount", "signed_amount", "net_amount", "value"),
    "description": ("description", "narration", "memo", "particulars"),
    "preparer": ("preparer", "user", "created_by", "posted_by"),
    "reference": ("reference", "reference_no", "document_no", "invoice_no", "voucher_no"),
    "entity": ("entity", "company", "cost_center", "branch"),
    "is_manual": ("is_manual", "manual", "source_type"),
}


def _key(s): return "".join(c.lower() for c in (s or "") if c.isalnum() or c == "_")

def _number(value):
    if value in (None, ""): return 0.0
    return float(str(value).replace(",", "").replace("₹", "").strip().strip("()") or 0)

def _date(value):
    raw = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try: return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError: pass
    raise ValueError("invalid posting date")

def _rows(path: Path):
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as f:
            yield from csv.DictReader(f)
        return
    if path.suffix.lower() == ".xlsx":
        try: import openpyxl
        except ImportError as e: raise ValueError("XLSX requires local openpyxl; CSV is available without dependencies") from e
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb.active; headers = [str(x or "") for x in next(ws.iter_rows(values_only=True))]
        for cells in ws.iter_rows(values_only=True): yield dict(zip(headers, cells))
        return
    raise ValueError("only .csv and .xlsx files are supported")

def _canonical(row):
    indexed = {_key(k): v for k, v in row.items()}
    out = {}
    for field, aliases in ALIASES.items():
        out[field] = next((indexed[_key(a)] for a in aliases if _key(a) in indexed), None)
    return out

def import_gl(store: Store, filename: str, actor="system"):
    source = Path(filename)
    if not source.is_file(): raise ValueError(f"source file not found: {source}")
    evidence = store.path.parent / "evidence"; evidence.mkdir(exist_ok=True)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    target = evidence / f"{digest[:12]}_{source.name}"
    if not target.exists(): shutil.copy2(source, target)
    cur = store.conn.execute("INSERT INTO imports(kind,original_name,evidence_path,sha256,imported_at,accepted_rows,rejected_rows) VALUES('gl',?,?,?,?,?,?)",
                             (source.name, str(target), digest, __import__('time').time(), 0, 0))
    import_id = cur.lastrowid; accepted = rejected = 0; debits = credits = 0.0
    for line, raw in enumerate(_rows(source), 2):
        try:
            r = _canonical(raw); entry_id = str(r["entry_id"] or "").strip(); account = str(r["account_code"] or "").strip()
            if not entry_id or not account: raise ValueError("missing entry ID or account code")
            posting = _date(r["posting_date"])
            debit, credit = _number(r["debit"]), _number(r["credit"])
            if not debit and not credit:
                amount = _number(r["amount"])
                debit, credit = (amount, 0.0) if amount >= 0 else (0.0, -amount)
            if debit < 0 or credit < 0 or (debit and credit): raise ValueError("invalid debit/credit values")
            manual = str(r["is_manual"] or "").lower() in ("1", "true", "yes", "manual")
            raw_json = json.dumps(raw, default=str, sort_keys=True); row_hash = hashlib.sha256(raw_json.encode()).hexdigest()
            store.conn.execute("""INSERT INTO ledger_entries(import_id,entry_id,posting_date,document_date,account_code,debit,credit,signed_amount,description,preparer,reference,entity,is_manual,source_row,source_hash,raw_json)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (import_id, entry_id, posting, _date(r["document_date"]) if r["document_date"] else None, account, debit, credit, debit-credit, r["description"], r["preparer"], r["reference"], r["entity"], int(manual), line, row_hash, raw_json))
            accepted += 1; debits += debit; credits += credit
        except (ValueError, TypeError) as e:
            rejected += 1; store.conn.execute("INSERT INTO rejected_rows(import_id,source_row,reason,raw_json) VALUES(?,?,?,?)", (import_id, line, str(e), json.dumps(raw, default=str)))
    store.conn.execute("UPDATE imports SET accepted_rows=?,rejected_rows=?,control_debits=?,control_credits=? WHERE id=?", (accepted, rejected, debits, credits, import_id))
    store.log(actor, "import_gl", "import", import_id, {"accepted": accepted, "rejected": rejected, "sha256": digest})
    store.conn.commit(); return import_id, accepted, rejected, debits, credits

def import_coa(store: Store, filename: str, actor="system"):
    source = Path(filename); rows = list(_rows(source)); digest = hashlib.sha256(source.read_bytes()).hexdigest()
    evidence = store.path.parent / "evidence"; evidence.mkdir(exist_ok=True); target = evidence / f"{digest[:12]}_{source.name}"
    if not target.exists(): shutil.copy2(source, target)
    cur = store.conn.execute("INSERT INTO imports(kind,original_name,evidence_path,sha256,imported_at,accepted_rows,rejected_rows) VALUES('coa',?,?,?,?,?,?)", (source.name, str(target), digest, __import__('time').time(), 0, 0)); iid = cur.lastrowid
    for raw in rows:
        r = {_key(k): v for k, v in raw.items()}; code = r.get("account_code") or r.get("account") or r.get("gl_code")
        if code: store.conn.execute("INSERT OR REPLACE INTO coa VALUES(?,?,?,?)", (str(code), r.get("account_name") or r.get("name"), r.get("account_type") or r.get("type"), iid))
    store.conn.execute("UPDATE imports SET accepted_rows=? WHERE id=?", (len(rows), iid)); store.log(actor, "import_coa", "import", iid, {"rows": len(rows)}); store.conn.commit(); return iid

```


## Assistant

<thinking>


**Planning CLI temp file testing**

**Preparing to run compile and tests**
</thinking>

**Tool Call: python3 run.py --help >/dev/null && PYTHONPATH=src python3 -m unittest discover -s tests -v && python3 -m py_compile run.py src/audit_analytics/*.py && find . -maxdepth 3 -type f | sort**
Status: Completed

Terminal:
```
test_import_requires_acknowledgement_then_creates_traceable_exception (test_pipeline.PipelineTest.test_import_requires_acknowledgement_then_creates_traceable_exception) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.088s

OK
./README.md
./__pycache__/run.cpython-312.pyc
./run.py
./src/audit_analytics/__init__.py
./src/audit_analytics/analytics.py
./src/audit_analytics/cli.py
./src/audit_analytics/importer.py
./src/audit_analytics/server.py
./src/audit_analytics/store.py
./tests/__pycache__/test_pipeline.cpython-312.pyc
./tests/test_pipeline.py

```


## Assistant

<thinking>


**Evaluating pycache removal impact**

**Reviewing potential code inconsistencies and testing needs**

**Assessing XLSX support and README update**
</thinking>

<thinking>


**Implementing XLSX row parsing with date conversion**
</thinking>

**Tool Call: Editing files**
Status: Completed

Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/README.md
```
# Audit Analytics

Local-first journal-entry analytics for Indian statutory-audit teams. It ranks
explainable risk cues for auditor review; it does not make audit conclusions or
issue an opinion.

## Quick start

```sh
cd audit-analytics
python3 run.py init --db demo/audit.db --client "Example Ltd" --period 2025-04-01:2026-03-31
python3 run.py import-gl --db demo/audit.db --file journal_entries.csv
python3 run.py acknowledge-population --db demo/audit.db --reviewer "A. Auditor" --note "Agreed to client GL control totals"
python3 run.py analyze --db demo/audit.db
python3 run.py serve --db demo/audit.db
```

Open `http://127.0.0.1:8788` to review and disposition flagged entries. Export
an evidence-linked CSV workpaper with `python3 run.py export --db demo/audit.db
--out demo/workpaper.csv`.

## Supported GL fields

Headers are matched case-insensitively with common aliases. Required: entry ID,
posting date, account code, and either signed amount or debit and credit.
Optional fields include document date, description/narration, preparer/user,
reference/document number, entity, and manual/system indicator. COA imports
are supported through `import-coa` and enrich account labels only.

CSV and ordinary first-sheet `.xlsx` exports are supported with the standard
library; no client data is uploaded or sent to a conversion service.

## Controls and limitations

- Every imported source file is copied into `evidence/` beside the engagement
  database and is SHA-256 hashed; each entry retains source row identity.
- Import validation separates rejected/missing data from risk cues.
- Analysis is blocked until a reviewer acknowledges the accepted population and
  control totals.
- The statistical suite includes deterministic tests, account-peer robust
  outliers, Benford population checks, reversal matching, and an optional local
  isolation-style model for populations of at least 256 entries.
- Risk scores are prioritisation cues. Reviewer dispositions and audit-log
  records are append-only; no result is labelled fraud or an audit conclusion.

The controls are designed to support documentation under SA 230 and journal
entry procedures under SA 240; the engagement team remains responsible for
audit design, evidence evaluation, and conclusions.

```


Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/src/audit_analytics/importer.py
```
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

from .store import Store

ALIASES = {
    "entry_id": ("entry_id", "journal_entry_id", "voucher_no", "voucher_number", "transaction_id", "document_id"),
    "posting_date": ("posting_date", "date", "entry_date", "postingdate"),
    "document_date": ("document_date", "doc_date", "voucher_date"),
    "account_code": ("account_code", "account", "gl_code", "ledger_code", "account_number"),
    "debit": ("debit", "dr", "debit_amount"), "credit": ("credit", "cr", "credit_amount"),
    "amount": ("amount", "signed_amount", "net_amount", "value"),
    "description": ("description", "narration", "memo", "particulars"),
    "preparer": ("preparer", "user", "created_by", "posted_by"),
    "reference": ("reference", "reference_no", "document_no", "invoice_no", "voucher_no"),
    "entity": ("entity", "company", "cost_center", "branch"),
    "is_manual": ("is_manual", "manual", "source_type"),
}


def _key(s): return "".join(c.lower() for c in (s or "") if c.isalnum() or c == "_")

def _number(value):
    if value in (None, ""): return 0.0
    return float(str(value).replace(",", "").replace("₹", "").strip().strip("()") or 0)

def _date(value):
    if isinstance(value, (int, float)) or (str(value).replace(".", "", 1).isdigit() and float(value) > 20000):
        return (datetime(1899, 12, 30) + __import__('datetime').timedelta(days=float(value))).date().isoformat()
    raw = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try: return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError: pass
    raise ValueError("invalid posting date")

def _rows(path: Path):
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as f:
            yield from csv.DictReader(f)
        return
    if path.suffix.lower() == ".xlsx":
        ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
        with zipfile.ZipFile(path) as book:
            shared = []
            if "xl/sharedStrings.xml" in book.namelist():
                root = ET.fromstring(book.read("xl/sharedStrings.xml"))
                shared = ["".join(node.itertext()) for node in root.findall(f"{ns}si")]
            sheets = sorted(n for n in book.namelist() if n.startswith("xl/worksheets/sheet") and n.endswith(".xml"))
            if not sheets: raise ValueError("XLSX contains no worksheet")
            parsed = []
            for row in ET.fromstring(book.read(sheets[0])).iter(f"{ns}row"):
                values = []
                for cell in row.findall(f"{ns}c"):
                    val = cell.find(f"{ns}v"); text = "" if val is None else val.text or ""
                    if cell.get("t") == "s" and text: text = shared[int(text)]
                    elif cell.get("t") == "inlineStr": text = "".join(cell.itertext())
                    values.append(text)
                parsed.append(values)
        if not parsed: return
        headers = [str(x or "") for x in parsed[0]]
        for values in parsed[1:]: yield dict(zip(headers, values))
        return
    raise ValueError("only .csv and .xlsx files are supported")

def _canonical(row):
    indexed = {_key(k): v for k, v in row.items()}
    out = {}
    for field, aliases in ALIASES.items():
        out[field] = next((indexed[_key(a)] for a in aliases if _key(a) in indexed), None)
    return out

def import_gl(store: Store, filename: str, actor="system"):
    source = Path(filename)
    if not source.is_file(): raise ValueError(f"source file not found: {source}")
    evidence = store.path.parent / "evidence"; evidence.mkdir(exist_ok=True)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    target = evidence / f"{digest[:12]}_{source.name}"
    if not target.exists(): shutil.copy2(source, target)
    cur = store.conn.execute("INSERT INTO imports(kind,original_name,evidence_path,sha256,imported_at,accepted_rows,rejected_rows) VALUES('gl',?,?,?,?,?,?)",
                             (source.name, str(target), digest, __import__('time').time(), 0, 0))
    import_id = cur.lastrowid; accepted = rejected = 0; debits = credits = 0.0
    for line, raw in enumerate(_rows(source), 2):
        try:
            r = _canonical(raw); entry_id = str(r["entry_id"] or "").strip(); account = str(r["account_code"] or "").strip()
            if not entry_id or not account: raise ValueError("missing entry ID or account code")
            posting = _date(r["posting_date"])
            debit, credit = _number(r["debit"]), _number(r["credit"])
            if not debit and not credit:
                amount = _number(r["amount"])
                debit, credit = (amount, 0.0) if amount >= 0 else (0.0, -amount)
            if debit < 0 or credit < 0 or (debit and credit): raise ValueError("invalid debit/credit values")
            manual = str(r["is_manual"] or "").lower() in ("1", "true", "yes", "manual")
            raw_json = json.dumps(raw, default=str, sort_keys=True); row_hash = hashlib.sha256(raw_json.encode()).hexdigest()
            store.conn.execute("""INSERT INTO ledger_entries(import_id,entry_id,posting_date,document_date,account_code,debit,credit,signed_amount,description,preparer,reference,entity,is_manual,source_row,source_hash,raw_json)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (import_id, entry_id, posting, _date(r["document_date"]) if r["document_date"] else None, account, debit, credit, debit-credit, r["description"], r["preparer"], r["reference"], r["entity"], int(manual), line, row_hash, raw_json))
            accepted += 1; debits += debit; credits += credit
        except (ValueError, TypeError) as e:
            rejected += 1; store.conn.execute("INSERT INTO rejected_rows(import_id,source_row,reason,raw_json) VALUES(?,?,?,?)", (import_id, line, str(e), json.dumps(raw, default=str)))
    store.conn.execute("UPDATE imports SET accepted_rows=?,rejected_rows=?,control_debits=?,control_credits=? WHERE id=?", (accepted, rejected, debits, credits, import_id))
    store.log(actor, "import_gl", "import", import_id, {"accepted": accepted, "rejected": rejected, "sha256": digest})
    store.conn.commit(); return import_id, accepted, rejected, debits, credits

def import_coa(store: Store, filename: str, actor="system"):
    source = Path(filename); rows = list(_rows(source)); digest = hashlib.sha256(source.read_bytes()).hexdigest()
    evidence = store.path.parent / "evidence"; evidence.mkdir(exist_ok=True); target = evidence / f"{digest[:12]}_{source.name}"
    if not target.exists(): shutil.copy2(source, target)
    cur = store.conn.execute("INSERT INTO imports(kind,original_name,evidence_path,sha256,imported_at,accepted_rows,rejected_rows) VALUES('coa',?,?,?,?,?,?)", (source.name, str(target), digest, __import__('time').time(), 0, 0)); iid = cur.lastrowid
    for raw in rows:
        r = {_key(k): v for k, v in raw.items()}; code = r.get("account_code") or r.get("account") or r.get("gl_code")
        if code: store.conn.execute("INSERT OR REPLACE INTO coa VALUES(?,?,?,?)", (str(code), r.get("account_name") or r.get("name"), r.get("account_type") or r.get("type"), iid))
    store.conn.execute("UPDATE imports SET accepted_rows=? WHERE id=?", (len(rows), iid)); store.log(actor, "import_coa", "import", iid, {"rows": len(rows)}); store.conn.commit(); return iid

```


## Assistant

<thinking>


**Fixing column index calculation for blank cells**
</thinking>

**Tool Call: Editing files**
Status: Completed

Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/src/audit_analytics/importer.py
```
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

from .store import Store

ALIASES = {
    "entry_id": ("entry_id", "journal_entry_id", "voucher_no", "voucher_number", "transaction_id", "document_id"),
    "posting_date": ("posting_date", "date", "entry_date", "postingdate"),
    "document_date": ("document_date", "doc_date", "voucher_date"),
    "account_code": ("account_code", "account", "gl_code", "ledger_code", "account_number"),
    "debit": ("debit", "dr", "debit_amount"), "credit": ("credit", "cr", "credit_amount"),
    "amount": ("amount", "signed_amount", "net_amount", "value"),
    "description": ("description", "narration", "memo", "particulars"),
    "preparer": ("preparer", "user", "created_by", "posted_by"),
    "reference": ("reference", "reference_no", "document_no", "invoice_no", "voucher_no"),
    "entity": ("entity", "company", "cost_center", "branch"),
    "is_manual": ("is_manual", "manual", "source_type"),
}


def _key(s): return "".join(c.lower() for c in (s or "") if c.isalnum() or c == "_")

def _number(value):
    if value in (None, ""): return 0.0
    return float(str(value).replace(",", "").replace("₹", "").strip().strip("()") or 0)

def _date(value):
    if isinstance(value, (int, float)) or (str(value).replace(".", "", 1).isdigit() and float(value) > 20000):
        return (datetime(1899, 12, 30) + __import__('datetime').timedelta(days=float(value))).date().isoformat()
    raw = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try: return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError: pass
    raise ValueError("invalid posting date")

def _rows(path: Path):
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as f:
            yield from csv.DictReader(f)
        return
    if path.suffix.lower() == ".xlsx":
        ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
        with zipfile.ZipFile(path) as book:
            shared = []
            if "xl/sharedStrings.xml" in book.namelist():
                root = ET.fromstring(book.read("xl/sharedStrings.xml"))
                shared = ["".join(node.itertext()) for node in root.findall(f"{ns}si")]
            sheets = sorted(n for n in book.namelist() if n.startswith("xl/worksheets/sheet") and n.endswith(".xml"))
            if not sheets: raise ValueError("XLSX contains no worksheet")
            parsed = []
            for row in ET.fromstring(book.read(sheets[0])).iter(f"{ns}row"):
                values = []
                for cell in row.findall(f"{ns}c"):
                    letters = "".join(c for c in cell.get("r", "") if c.isalpha())
                    col = 0
                    for letter in letters: col = col * 26 + ord(letter.upper()) - 64
                    while len(values) < max(0, col - 1): values.append("")
                    val = cell.find(f"{ns}v"); text = "" if val is None else val.text or ""
                    if cell.get("t") == "s" and text: text = shared[int(text)]
                    elif cell.get("t") == "inlineStr": text = "".join(cell.itertext())
                    values.append(text)
                parsed.append(values)
        if not parsed: return
        headers = [str(x or "") for x in parsed[0]]
        for values in parsed[1:]: yield dict(zip(headers, values))
        return
    raise ValueError("only .csv and .xlsx files are supported")

def _canonical(row):
    indexed = {_key(k): v for k, v in row.items()}
    out = {}
    for field, aliases in ALIASES.items():
        out[field] = next((indexed[_key(a)] for a in aliases if _key(a) in indexed), None)
    return out

def import_gl(store: Store, filename: str, actor="system"):
    source = Path(filename)
    if not source.is_file(): raise ValueError(f"source file not found: {source}")
    evidence = store.path.parent / "evidence"; evidence.mkdir(exist_ok=True)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    target = evidence / f"{digest[:12]}_{source.name}"
    if not target.exists(): shutil.copy2(source, target)
    cur = store.conn.execute("INSERT INTO imports(kind,original_name,evidence_path,sha256,imported_at,accepted_rows,rejected_rows) VALUES('gl',?,?,?,?,?,?)",
                             (source.name, str(target), digest, __import__('time').time(), 0, 0))
    import_id = cur.lastrowid; accepted = rejected = 0; debits = credits = 0.0
    for line, raw in enumerate(_rows(source), 2):
        try:
            r = _canonical(raw); entry_id = str(r["entry_id"] or "").strip(); account = str(r["account_code"] or "").strip()
            if not entry_id or not account: raise ValueError("missing entry ID or account code")
            posting = _date(r["posting_date"])
            debit, credit = _number(r["debit"]), _number(r["credit"])
            if not debit and not credit:
                amount = _number(r["amount"])
                debit, credit = (amount, 0.0) if amount >= 0 else (0.0, -amount)
            if debit < 0 or credit < 0 or (debit and credit): raise ValueError("invalid debit/credit values")
            manual = str(r["is_manual"] or "").lower() in ("1", "true", "yes", "manual")
            raw_json = json.dumps(raw, default=str, sort_keys=True); row_hash = hashlib.sha256(raw_json.encode()).hexdigest()
            store.conn.execute("""INSERT INTO ledger_entries(import_id,entry_id,posting_date,document_date,account_code,debit,credit,signed_amount,description,preparer,reference,entity,is_manual,source_row,source_hash,raw_json)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (import_id, entry_id, posting, _date(r["document_date"]) if r["document_date"] else None, account, debit, credit, debit-credit, r["description"], r["preparer"], r["reference"], r["entity"], int(manual), line, row_hash, raw_json))
            accepted += 1; debits += debit; credits += credit
        except (ValueError, TypeError) as e:
            rejected += 1; store.conn.execute("INSERT INTO rejected_rows(import_id,source_row,reason,raw_json) VALUES(?,?,?,?)", (import_id, line, str(e), json.dumps(raw, default=str)))
    store.conn.execute("UPDATE imports SET accepted_rows=?,rejected_rows=?,control_debits=?,control_credits=? WHERE id=?", (accepted, rejected, debits, credits, import_id))
    store.log(actor, "import_gl", "import", import_id, {"accepted": accepted, "rejected": rejected, "sha256": digest})
    store.conn.commit(); return import_id, accepted, rejected, debits, credits

def import_coa(store: Store, filename: str, actor="system"):
    source = Path(filename); rows = list(_rows(source)); digest = hashlib.sha256(source.read_bytes()).hexdigest()
    evidence = store.path.parent / "evidence"; evidence.mkdir(exist_ok=True); target = evidence / f"{digest[:12]}_{source.name}"
    if not target.exists(): shutil.copy2(source, target)
    cur = store.conn.execute("INSERT INTO imports(kind,original_name,evidence_path,sha256,imported_at,accepted_rows,rejected_rows) VALUES('coa',?,?,?,?,?,?)", (source.name, str(target), digest, __import__('time').time(), 0, 0)); iid = cur.lastrowid
    for raw in rows:
        r = {_key(k): v for k, v in raw.items()}; code = r.get("account_code") or r.get("account") or r.get("gl_code")
        if code: store.conn.execute("INSERT OR REPLACE INTO coa VALUES(?,?,?,?)", (str(code), r.get("account_name") or r.get("name"), r.get("account_type") or r.get("type"), iid))
    store.conn.execute("UPDATE imports SET accepted_rows=? WHERE id=?", (len(rows), iid)); store.log(actor, "import_coa", "import", iid, {"rows": len(rows)}); store.conn.commit(); return iid

```


## Assistant

<thinking>


**Planning test for `_date` imports**
</thinking>

**Tool Call: python3 run.py --help >/dev/null && PYTHONPATH=src python3 -m unittest discover -s tests -v && python3 -m py_compile run.py src/audit_analytics/*.py && git -C /Users/Mitesh/Gada/Documents/Projects/audit-analytics status --short 2>/dev/null || true**
Status: Completed

Terminal:
```
test_import_requires_acknowledgement_then_creates_traceable_exception (test_pipeline.PipelineTest.test_import_requires_acknowledgement_then_creates_traceable_exception) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.056s

OK

```


## Assistant

<thinking>


**Planning final documentation touches**
</thinking>

Implemented the standalone audit analytics MVP in [audit-analytics](/Users/Mitesh%20Gada/Documents/Projects/audit-analytics).

It includes:

- Local CSV/XLSX GL and COA ingestion with evidence-file copies, hashes, source-row traceability, validation, and rejected-row reporting.
- Population acknowledgement gate before analytics run.
- Hybrid risk cues: duplicates, round amounts, period-end/weekend postings, rare account-preparer pairs, reversals, robust account-peer outliers, Benford applicability checks, and local optional isolation-style scoring.
- SQLite engagement store, immutable audit log, exception queue, reviewer dispositions, and CSV workpaper export.
- Local review UI via `python3 run.py serve --db <path>`.
- A runnable end-to-end test covering import, acknowledgement blocking, analysis, and source traceability.

Start from [README.md](/Users/Mitesh%20Gada/Documents/Projects/audit-analytics/README.md). Verified with `unittest` and Python compilation.

## User

also note down the extensive and elaborate plan in a file in the project folder

## Assistant

<thinking>


**Planning implementation documentation and patching**
</thinking>

I’ll add a detailed implementation and evolution plan alongside the application, covering the delivered foundation, architecture, controls, future connectors, and acceptance criteria.

**Tool Call: Editing files**
Status: Completed

Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/IMPLEMENTATION_PLAN.md
```
# Audit Analytics — Implementation and Evolution Plan

## 1. Purpose and operating boundary

Audit Analytics is a local-first journal-entry analytics system for audit and
accounting firms conducting Indian external statutory audits. Its purpose is to
help engagement teams profile a ledger population, identify explainable risk
cues, select and document responsive procedures, and retain an evidence-linked
review trail.

It is deliberately **not** an automated audit engine. It must never express an
audit opinion, determine that fraud occurred, treat a risk score as a finding,
or replace the auditor's professional judgement. A flagged entry is a review
cue. A reviewer must assess the entry, obtain appropriate evidence, and record
their disposition.

The initial product boundary is general-ledger (GL) and chart-of-accounts (COA)
data. Supporting documents, OCR, bank data, vendor/customer masters,
related-party graphs, continuous controls monitoring, and ERP integrations are
future additions behind the same normalized-data boundary.

The documentation and review controls are intended to support engagement teams
working under SA 230 and SA 240. The firm remains responsible for applying the
current standards, its audit methodology, quality-management policies, and any
jurisdiction-specific legal requirements.

## 2. Design translated from qcom-scraping

The source project supplied reusable pipeline principles rather than an audit
domain model:

| Source-pipeline pattern | Audit Analytics equivalent |
| --- | --- |
| Captured observation with time, source, and location | Imported GL record with import version, source row, hash, and evidence-file path |
| Entity-specific statistical baseline | Account, preparer, entity, and period peer groups |
| Unknown is not an out-of-stock event | Missing or invalid financial data is a coverage limitation, never a suspicious transaction |
| Debounced state/event handling | Versioned model runs, reviewed exceptions, and append-only dispositions |
| Ranked demand-pressure signal | Ranked, explainable journal-entry risk cue |
| Dashboard, export, and human review | Engagement review queue, reviewer note/disposition, and workpaper export |
| Additive migrations and reproducibility | Versioned imports/runs, immutable logs, and no destructive data rewrite |

The web crawler, consumer-product semantics, pricing logic, and demand claims
are intentionally not reused. Financial data enters only through trusted,
controlled imports and future read-only connector adapters.

## 3. Delivered foundation

The current implementation is a functional local MVP.

### 3.1 Engagement and data controls

- `init` creates one engagement database with client and audit-period metadata.
- `import-gl` accepts CSV and ordinary first-sheet XLSX exports without sending
  data to an external conversion service.
- Common header aliases are mapped to a canonical GL contract. Required fields
  are entry ID, posting date, account code, and signed amount or debit/credit.
- Accepted rows retain their complete original row JSON, SHA-256 row hash,
  source row number, import identifier, and evidence-file reference.
- Each source file is copied to an engagement-local `evidence/` directory and
  hash recorded before processing.
- Invalid rows are preserved with a rejection reason rather than silently
  discarded.
- The import records accepted/rejected counts and calculated debit/credit
  control totals. Analytics is blocked until the reviewer explicitly
  acknowledges every GL import and records a note.

### 3.2 Statistical and deterministic analytics

The analysis run is versioned and stores configuration, population size,
limitations, and every exception's component evidence.

- Repeated-entry tests identify repeated account/date/amount/description and
  repeated account/reference/amount patterns.
- Amount tests identify material round-number entries.
- Timing tests identify period-end and weekend postings.
- Relationship tests identify rare account/preparer combinations and potential
  opposite-sign reversals in the same account within 30 days.
- Robust peer outliers use the account-level median and median absolute
  deviation (MAD), avoiding fragile mean/standard-deviation assumptions.
- Benford analysis runs only when at least 100 non-zero amounts exist and is
  kept as a population-level indicator, not an entry-level accusation.
- An optional local isolation-style random-cut model operates only for
  populations of at least 256 entries. It is explicitly an additional ranking
  feature, not the sole basis for an exception or audit response.

Scores are bounded and severity-labelled for prioritisation. Reasons and peer
context remain visible so the reviewer can understand why an entry appeared.

### 3.3 Review and workpapers

- The local HTTP review UI shows entry context, score, reasons, model evidence,
  current status, and a required reviewer note.
- Supported dispositions are `open`, `cleared`, `follow_up`, and
  `selected_for_testing`.
- Each disposition creates an append-only `reviews` record and an `audit_log`
  event with actor, time, target, and structured details.
- `export` creates a CSV workpaper containing risk information, original GL
  context, reasons, and evidence. Firms can load this into their prescribed
  workpaper template.

## 4. Canonical data contract

### Required GL fields

| Canonical field | Purpose | Typical aliases |
| --- | --- | --- |
| `entry_id` | Stable journal/voucher-line identifier | journal_entry_id, voucher_no, transaction_id |
| `posting_date` | Accounting posting date | date, entry_date |
| `account_code` | GL account identifier | account, gl_code, ledger_code |
| `signed_amount` or `debit`/`credit` | Transaction value | amount, net_amount, debit_amount, credit_amount |

### Recommended optional fields

`document_date`, `description`, `preparer`, `reference`, `entity`, and
`is_manual` improve population profiling and analytical precision. Their
absence is recorded as a coverage limitation; it does not become a risk cue.

### COA contract

COA imports are optional enrichment and accept account code plus account name
and type where present. Future account-risk taxonomy mappings should be stored
separately from the raw client COA so firm methodology does not overwrite
client evidence.

## 5. Data model and lineage

The SQLite database is the engagement's system of record. Its logical flow is:

```text
evidence file -> imports -> ledger_entries / rejected_rows
                               |
                               v
                         model_runs -> exceptions -> reviews
                               \             \-> audit_log
                                \-> workpaper export
```

- `imports` stores file lineage, hash, counts, control totals, and reviewer
  acknowledgement.
- `ledger_entries` holds normalized data and immutable source identity.
- `rejected_rows` makes quality issues inspectable and countable.
- `model_runs` captures run configuration and limitations for reproducibility.
- `exceptions` links a particular run to a particular original ledger record.
- `reviews` is append-only; status changes do not erase earlier reviewer work.
- `audit_log` records administrative, import, analysis, and review actions.

Schema evolution must be additive: new tables or nullable columns plus
backfills where appropriate. Never overwrite raw rows, source hashes, reviewer
notes, or old model-run outputs.

## 6. Firm deployment and security baseline

The supported deployment baseline is an auditor-controlled laptop, server, or
private VPC. Engagement data must remain within the firm-approved environment.

- Bind the review service to `127.0.0.1` by default. A network deployment must
  add firm SSO, role-based access control, TLS, session expiry, CSRF protection,
  audit-log retention, encrypted backups, and tenancy isolation before use.
- Encrypt devices/disks and backups using firm-approved controls. Restrict the
  engagement directory to assigned team members.
- Do not route client data to hosted LLM, embedding, telemetry, spreadsheet
  conversion, or third-party model services by default.
- Preserve original import files under the firm retention policy. On engagement
  closure, archive or delete through the firm's approved records process—not a
  silent application cleanup task.
- Capture tool version, model configuration, population acknowledgement, and
  export timestamp in each formal workpaper package.

## 7. Review workflow

1. The engagement team creates the engagement and imports the GL/COA extracts.
2. The preparer reconciles accepted entry count and calculated totals to the
   client-provided population/control totals; rejected rows are investigated.
3. A reviewer acknowledges the import with a specific note. This unlocks
   analysis but does not imply audit evidence has been obtained.
4. The team runs the hybrid analytics and reviews population limitations.
5. The reviewer filters/ranks cues, obtains support as necessary, records a
   disposition and rationale, and selects substantive testing items where
   appropriate.
6. The team exports the reviewed population and dispositions into the firm's
   workpaper structure, including methodology, limitations, and conclusion by
   the responsible auditor.

## 8. Planned releases

### Release 1.1 — audit-methodology hardening

- Add import-mapping preview and a saved client/ERP field mapping per
  engagement.
- Capture external client control totals, compare them to accepted data, and
  require an explicit quantified reconciliation before acknowledgement.
- Add materiality and performance-materiality settings used only as disclosed
  ranking/sampling thresholds.
- Add account labels, account-type filters, fiscal calendar controls, and
  workbook/PDF workpaper outputs.
- Add a model-run comparison view and a formal methodology/limitations report.

### Release 1.2 — review governance

- Add local user roles: preparer, reviewer, engagement manager, and read-only
  quality reviewer.
- Require second-level approval for cleared high-severity entries and lock a
  completed review set while allowing additive reopening records.
- Add assignment, due date, reviewer filters, search, and reviewer sampling
  queues.
- Add signed export manifests listing source imports, file hashes, run IDs, and
  reviewed exception counts.

### Release 2 — controlled ERP connectors

- Implement read-only adapter interfaces for SAP, Oracle, Tally, QuickBooks,
  and other approved systems only after a firm provides authorized access and a
  data dictionary.
- Each adapter must produce the same canonical import data and a connector-run
  manifest: authorization identity, query/version, extraction timestamp,
  record count, control totals, and source-system identifiers.
- Do not make connectors silently refresh a reviewed engagement population;
  each refresh is a new import version requiring reconciliation and
  acknowledgement.

### Release 3 — expanded forensic and audit datasets

- Add vendor/customer masters, bank extracts, invoices, purchase orders, and
  related-party datasets as separate normalized evidence types.
- Build graph and text-similarity analysis only with explicit coverage and
  false-positive controls.
- Keep document ingestion separate from GL scoring; missing supporting evidence
  is a review state, not an inferred fraud feature.

### Release 4 — validated advanced models

- Replace the compact isolation-style scorer with a governed model registry
  only after documented validation across representative, authorised audit
  populations.
- Record training data provenance, version, feature schema, calibration,
  performance, drift checks, approval owner, and rollback process.
- Continue to require deterministic explanations, human review, and sampling
  methodology independent of any model score.

## 9. Acceptance and regression checks

Every release must retain these checks:

- Valid CSV/XLSX import maps standard aliases, copies evidence, and maintains
  correct row identity even with blank spreadsheet cells.
- Invalid required fields and dates become visible rejected rows; they never
  become scored exceptions.
- No analysis is possible before all GL imports are acknowledged.
- Calculated accepted-population counts/debits/credits are visible before the
  acknowledgement action.
- Synthetic datasets verify each deterministic cue, robust outlier threshold,
  reversal matching, Benford minimum-population guard, and isolation-model
  minimum-population guard.
- Each exception traces to an import, evidence file, original source row, and
  stored raw fields.
- A review note is mandatory; the audit log retains every disposition action.
- Exported workpapers include no language treating a score as fraud, an audit
  finding, or an audit opinion.
- Static and runtime checks confirm no outbound network call is introduced for
  engagement data without an explicitly approved connector/feature.

## 10. Known MVP limits

- The first UI is local and deliberately has no multi-user authentication;
  serve it only on the controlled host until Release 1.2 governance is built.
- XLSX support targets ordinary tabular first-sheet exports; complex workbooks,
  macros, protected files, and multi-sheet mappings require the mapping preview
  work in Release 1.1.
- The current import acknowledgement captures calculated totals and a reviewer
  note; structured client-supplied control-total reconciliation is planned for
  Release 1.1.
- The isolation-style algorithm is a compact local ranking aid with a stated
  ceiling, not a validated fraud model. It can be disabled per run.
- CSV is the current workpaper export. Formatted Excel/PDF output and audit
  suite integration are planned additions.

```


## Assistant

<thinking>


**Verifying file integrity**
</thinking>

**Tool Call: Read file '/Users/Mitesh Gada/Documents/Projects/audit-analytics/IMPLEMENTATION_PLAN.md'**
Status: Completed

```json
{
  "formatted_output": "     275 IMPLEMENTATION_PLAN.md\n# Audit Analytics — Implementation and Evolution Plan\n\n## 1. Purpose and operating boundary\n\nAudit Analytics is a local-first journal-entry analytics system for audit and\naccounting firms conducting Indian external statutory audits. Its purpose is to\nhelp engagement teams profile a ledger population, identify explainable risk\ncues, select and document responsive procedures, and retain an evidence-linked\nreview trail.\n\nIt is deliberately **not** an automated audit engine. It must never express an\naudit opinion, determine that fraud occurred, treat a risk score as a finding,\nor replace the auditor's professional judgement. A flagged entry is a review\ncue. A reviewer must assess the entry, obtain appropriate evidence, and record\ntheir disposition.\n\nThe initial product boundary is general-ledger (GL) and chart-of-accounts (COA)\ndata. Supporting documents, OCR, bank data, vendor/customer masters,\nrelated-party graphs, continuous controls monitoring, and ERP integrations are\nfuture additions behind the same normalized-data boundary.\n\nThe documentation and review controls are intended to support engagement teams\nworking under SA 230 and SA 240. The firm remains responsible for applying the\ncurrent standards, its audit methodology, quality-management policies, and any\n",
  "exit_code": 0
}
```

## Assistant

Added the detailed 275-line implementation and evolution plan: [IMPLEMENTATION_PLAN.md](/Users/Mitesh%20Gada/Documents/Projects/audit-analytics/IMPLEMENTATION_PLAN.md).

It covers architecture, data lineage, controls, review workflow, security baseline, phased releases, acceptance tests, and MVP limitations.

## User

I want to tackle semantic search for a type of transaction since oftentimes due to multiple accountants or even as a method of making the accounts confusing, the same type of entries for commplex transactions may be done differently, may use similar account heads to avoid its finding and other tactics to confuse the accountants. I want to tackle this by using token classification and embedding models that will run locally

## Assistant

<thinking>


**Inspecting local model availability and dependencies**

**Verifying source code origins and structure**
</thinking>

I’ll add this as a local-only semantic layer: transparent token/account-head similarity first, then an optional Ollama embedding provider that never sends ledger data off-device. The results will be “similar transaction candidates” with token and semantic evidence, not automated matches or findings.

**Tool Call: rg -n "class EmbedClient|def (embed|search_vectors|backfill_catalog)|ollama|cosine" qcom-scraping/src/embed.py && sed -n '1,260p' audit-analytics/src/audit_analytics/{store.py,cli.py,server.py} && command -v ollama || true && python3 - <<'PY'
for m in ('numpy','requests'):
 try:
  __import__(m); print(f'{m}: available')
 except ImportError: print(f'{m}: unavailable')
PY**
Status: Completed

Terminal:
```
numpy: available
requests: available

```


## Assistant

<thinking>


**Planning model listing implementation**
</thinking>

**Tool Call: ollama list 2>&1 || true; sed -n '90,330p' qcom-scraping/src/embed.py**
Status: Completed

Terminal:
```
Error: could not connect to ollama server, run 'ollama serve' to start it
    dims  INTEGER,
    name  TEXT,
    vec   BLOB,
    ts    REAL,
    PRIMARY KEY (model, dims, name)
);
"""


class RPDExhausted(RuntimeError):
    """All keys' daily request budget is spent (free tier). Not an endpoint
    failure: the backfill re-runs cleanly after the provider's reset
    (OpenRouter midnight UTC, Gemini midnight PT)."""


def _map(cos, lo=SEM_LO, hi=SEM_HI):
    """Rescale a cosine onto the token-match scale (0..1). lo/hi are the cosine
    bounds mapped to 0/1 (per-model overridable via ai.embedding_sem_lo/hi)."""
    return max(0.0, min(1.0, (cos - lo) / (hi - lo)))


def embed_text(name, brand="", category="", variant="", pack_size=""):
    """Phase 3A structured context: prepend parsed grocery fields to the raw
    name. Falls back to the raw name when no parsed field is present.
    ponytail: one OR-joined guard instead of per-field branches."""
    parts = [str(p or "").strip() for p in (brand, category, variant, pack_size)]
    prefix = " | ".join(p for p in parts if p)
    name = (name or "").strip()
    return f"{prefix} | {name}" if prefix and name else (prefix or name)


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _norm(a):
    return math.sqrt(_dot(a, a)) or 1.0


def _cos(a, na, b):
    return max(-1.0, min(1.0, _dot(a, b) / (na * _norm(b))))


def _as_vec(raw, dims):
    """API vector -> array('f') truncated to dims. Matryoshka training makes
    the PREFIX a valid lower-dim embedding, so truncating a 3072-vector to 768
    is sound; a short vector means the endpoint ignored `dimensions` AND
    returned fewer dims than configured — unusable."""
    v = array.array("f", (float(x) for x in raw or []))
    if len(v) < dims:
        return None
    del v[dims:]
    return v


class Embedder:
    """Batched embeddings client + sqlite cache. All network work happens in
    ensure(); matching (boost_many/cos_score) is pure math after that."""

    def __init__(self, cfg, db_path="deals.db"):
        ai = (cfg or {}).get("ai") or {}
        self.enabled = bool(ai.get("enabled")) and bool(ai.get("semantic_matching", True))
        # Provider: "openai" (default — any OpenAI-compatible /embeddings host,
        # currently NVIDIA's integrate.api.nvidia.com) or "ollama" (a LOCAL
        # Ollama server: no API key, its own /api/embed request shape). Adding a
        # provider NEVER disturbs the others — rows are keyed by (model,dims) so
        # Ollama's vectors live beside NVIDIA's in the same additive table.
        self.provider = str(ai.get("embedding_provider") or "openai").strip().lower()
        if self.provider == "ollama":
            self.base = (str(ai.get("embedding_base_url") or "").strip()
                         or "http://localhost:11434").rstrip("/")
            self.model = str(ai.get("embedding_model") or "embeddinggemma").strip()
            _def_dims, _def_batch = 768, 256
            self.num_ctx = int(ai.get("embedding_ollama_num_ctx") or 512)
            self.query_prefix = str(ai.get("embedding_query_prefix") or "").strip()
            self.passage_prefix = str(ai.get("embedding_passage_prefix") or "").strip()
        else:
            self.base = (str(ai.get("embedding_base_url") or "").strip()
                         or "https://integrate.api.nvidia.com/v1").rstrip("/")
            self.model = str(ai.get("embedding_model") or DEFAULT_MODEL).strip()
            _def_dims, _def_batch = DIMS, BATCH
            self.query_prefix = ""
            self.passage_prefix = ""
        try:
            self.dims = int(ai.get("embedding_dims") or _def_dims)
        except (TypeError, ValueError):
            self.dims = _def_dims
        try:
            self.batch = max(1, int(ai.get("embedding_batch") or _def_batch))
        except (TypeError, ValueError):
            self.batch = _def_batch
        try:
            self.sem_lo = float(ai.get("embedding_sem_lo") or SEM_LO)
        except (TypeError, ValueError):
            self.sem_lo = SEM_LO
        try:
            self.sem_hi = float(ai.get("embedding_sem_hi") or SEM_HI)
        except (TypeError, ValueError):
            self.sem_hi = SEM_HI
        self.input_type = str(ai.get("embedding_input_type") or "passage").strip() or "passage"
        try:
            self.batch_pause = float(ai.get("embedding_batch_pause") or BATCH_PAUSE_SEC)
        except (TypeError, ValueError):
            self.batch_pause = BATCH_PAUSE_SEC
        # NVIDIA-only request fields (input_type/modality/truncate). Other
        # OpenAI-compatible endpoints (Gemini's /v1beta/openai/) REJECT unknown
        # fields with a 400, so providers that want plain semantics set
        # embedding_send_extras: false — the body then carries only
        # model/input/encoding_format(/dimensions).
        self.send_extras = bool(ai.get("embedding_send_extras", True))
        self.db_path = db_path
        self.key_tag = "none"   # masked key that served the last batch (logging)
        self._conn = None       # lazy sqlite (created on first ensure)
        self._cache = {}        # name -> array('f')
        self._known = None      # names already in the DB for this model/dims
        self._lock = threading.RLock()   # RLock: boost_many/cos_score hold
        self._down_until = 0.0  #  it while calling ensure() — not re-entrant
        try:
            from .alert import _load_env
            env = _load_env(os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
        except Exception:
            env = {}
        # Quota is PER API KEY: round-robin the pool (EMB_KEY, EMB_KEY_2, …,
        # default names OPENROUTER_API_KEY*) per batch so per-minute limits
        # are spread before they're hit, and a 429 on one key fails over to
        # the next instead of stalling. Scan EVERY slot (never break on a
        # missing one — .env edits land while processes run); dedupe; empty
        # pool = auth-free endpoint (Ollama).
        key_env = str(ai.get("embedding_key_env") or "NVIDIA_Build_API_KEY").strip()
        self.keys = []
        for suffix in [""] + [f"_{i}" for i in range(1, 10)]:
            k = (env.get(f"{key_env}{suffix}")
                 or os.environ.get(f"{key_env}{suffix}") or "").strip()
            if k and k not in self.keys:
                self.keys.append(k)
        if self.provider == "ollama":
            self.keys = []   # local server — auth-free, no API key

    @property
    def available(self):
        return self.enabled and time.time() >= self._down_until

    # -- network ----------------------------------------------------------

    def _post(self, texts, input_type="passage"):
        """Dispatch to the provider transport. Both return raw vectors in the
        SAME ORDER as `texts` (a list parallel to it)."""
        if self.provider == "ollama":
            return self._post_ollama(texts, input_type)
        return self._post_openai(texts, input_type)

    def _post_ollama(self, texts, input_type="passage"):
        """Local Ollama /api/embed (no API key). Optional query/passage prefixes
        tune the asymmetric embedding — embeddinggemma ignores input_type but
        responds to an instruction prefix. Returns ONE vector per input, or None
        for an input Ollama refused (see _embed_batch)."""
        prefix = self.query_prefix if input_type == "query" else self.passage_prefix
        if prefix:
            texts = [prefix + t for t in texts]
        return self._embed_batch(texts)

    def _ollama_body(self, texts):
        body = {"model": self.model, "input": list(texts)}
        if self.dims and self.dims != 768:   # 768 is embeddinggemma's native dim
            body["dimensions"] = self.dims
        return body

    def _ollama_call(self, body):
        req = urllib.request.Request(
            f"{self.base}/api/embed",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read().decode())

    def _embed_batch(self, texts):
        """Embed a batch; returns a list parallel to `texts` with None for any
        input Ollama refused. Resilient to a 400 from a SINGLE bad name in an
        otherwise-fine batch: drops `dimensions` if that's the complaint, then
        binary-searches to isolate and skip the offending input(s) instead of
        aborting the whole backfill. ponytail: a handful of un-embeddable names
        out of 44k is noise — skip, don't crash."""
        body = self._ollama_body(texts)
        try:
            d = self._ollama_call(body)
        except urllib.error.HTTPError as ex:
            if ex.code != 400:
                raise
            msg = (ex.read().decode()[:400] or "").lower()
            if "dimensions" in msg and "dimensions" in body:
                body.pop("dimensions", None)
                try:
                    d = self._ollama_call(body)
                except urllib.error.HTTPError as ex2:
                    if ex2.code != 400:
                        raise
                    if len(texts) == 1:
                        print(f"[embed] skipping un-embeddable name: {texts[0]!r}",
                              flush=True)
                        return [None]
                    return self._embed_batch(texts[:len(texts) // 2]) + \
                        self._embed_batch(texts[len(texts) // 2:])
            if len(texts) == 1:
                print(f"[embed] skipping un-embeddable name: {texts[0]!r}", flush=True)
                return [None]
            return self._embed_batch(texts[:len(texts) // 2]) + \
                self._embed_batch(texts[len(texts) // 2:])
        vecs = d.get("embeddings")
        if not isinstance(vecs, list) or len(vecs) != len(texts):
            raise RuntimeError(
                f"ollama /api/embed returned "
                f"{len(vecs) if isinstance(vecs, list) else 0}/{len(texts)} "
                f"vectors (model={self.model})")
        return vecs

    def _post_openai(self, texts, input_type="passage"):
        """One POST /embeddings with up to self.batch texts. Returns raw
        vectors in input order. Key handling (quota is PER KEY — distinct
        accounts have separate buckets):
          * every SUCCESSFUL batch rotates to the next key (round-robin),
          * a 429 fails over to the next key immediately (no sleep),
          * only when EVERY key was throttled within this call does it sleep
            (Retry-After or 60s) and retry the round — max MAX_WALL_ROUNDS
            consecutive whole-pool walls, then raise RPDExhausted (an RPM
            wall clears after ONE sleep; only the spent daily budget
            persists). Callers: ensure() degrades to token-only; the
            backfill prints the re-run hint."""
        body = {"model": self.model, "input": list(texts),
                "encoding_format": "float"}
        if self.send_extras:
            body.update({"input_type": input_type,
                         "modality": ["text"] * len(texts),
                         "truncate": "NONE"})
        if self.dims:
            body["dimensions"] = self.dims
        rounds, throttled, no_dims = 0, set(), False
        while True:
            key = self.keys[0]
            req = urllib.request.Request(
                f"{self.base}/embeddings",

```


## Assistant

<thinking>


**Planning semantic.py implementation**

**Designing token classification and embedding features**

**Applying semantic endpoint patch**
</thinking>

**Tool Call: Editing files**
Status: Completed

Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/src/audit_analytics/semantic.py
```
"""Local token classification and Ollama-backed transaction similarity."""
from __future__ import annotations

import array
import hashlib
import json
import math
import re
import time
import urllib.error
import urllib.request
from collections import Counter

from .store import Store

STOPWORDS = frozenset("a an and as at by for from in is of on or the to with being entry journal voucher".split())
TOKEN_CLASSES = {
    "cash_bank": frozenset("cash bank cheque chequeing transfer upi neft rtgs payment receipt deposit withdrawal".split()),
    "revenue": frozenset("revenue sales income billing invoice turnover service commission".split()),
    "expense": frozenset("expense rent utility utilities travel repair maintenance professional fee".split()),
    "payroll": frozenset("salary salaries payroll wage bonus pf esi gratuity".split()),
    "inventory": frozenset("inventory stock purchase goods material consumable cogs".split()),
    "tax": frozenset("gst tds tax cgst sgst igst vat duty".split()),
    "intercompany": frozenset("intercompany related party group affiliate reimbursement".split()),
    "fixed_asset": frozenset("asset equipment machinery computer vehicle depreciation capex".split()),
}


def tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z][a-z0-9]{1,}", (text or "").lower()) if t not in STOPWORDS}


def classify(text: str) -> list[str]:
    found = tokens(text)
    return sorted(label for label, terms in TOKEN_CLASSES.items() if found & terms)


def _text(entry: dict) -> str:
    return " | ".join(str(entry.get(k) or "") for k in ("account_code", "account_name", "description", "reference", "entity"))


def _cosine(a, b):
    denom = math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(x*x for x in b))
    return sum(x*y for x, y in zip(a, b)) / denom if denom else 0.0


class LocalEmbedder:
    """Minimal local Ollama transport. No API key and no external endpoint."""
    def __init__(self, model="embeddinggemma", base_url="http://127.0.0.1:11434"):
        self.model, self.base_url = model, base_url.rstrip("/")

    def embed(self, texts: list[str]) -> list[array.array]:
        body = json.dumps({"model": self.model, "input": texts}).encode()
        request = urllib.request.Request(self.base_url + "/api/embed", data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=180) as response: data = json.loads(response.read().decode())
        except (urllib.error.URLError, urllib.error.HTTPError) as exc:
            raise ValueError("local Ollama embedding failed; start `ollama serve` and run `ollama pull embeddinggemma` on this host") from exc
        vectors = data.get("embeddings")
        if not isinstance(vectors, list) or len(vectors) != len(texts): raise ValueError("local Ollama returned an invalid embedding batch")
        return [array.array("f", (float(x) for x in vector)) for vector in vectors]


def _entries(store: Store):
    return [dict(row) for row in store.conn.execute("""SELECT l.*, c.account_name FROM ledger_entries l
        LEFT JOIN coa c ON c.account_code=l.account_code ORDER BY l.id""")]


def embed_ledger(store: Store, model="embeddinggemma", batch_size=64, actor="system"):
    """Backfill locally generated vectors; unchanged text is never re-embedded."""
    embedder = LocalEmbedder(model); todo = []
    for entry in _entries(store):
        text = _text(entry); digest = hashlib.sha256(text.encode()).hexdigest()
        row = store.conn.execute("SELECT text_hash FROM ledger_embeddings WHERE ledger_id=? AND model=? ORDER BY embedded_at DESC LIMIT 1", (entry["id"], model)).fetchone()
        if not row or row[0] != digest: todo.append((entry["id"], text, digest))
    done = 0
    for start in range(0, len(todo), batch_size):
        group = todo[start:start + batch_size]; vectors = embedder.embed([x[1] for x in group])
        for (ledger_id, _, digest), vector in zip(group, vectors):
            store.conn.execute("DELETE FROM ledger_embeddings WHERE ledger_id=? AND model=?", (ledger_id, model))
            store.conn.execute("INSERT INTO ledger_embeddings VALUES(?,?,?,?,?,?)", (ledger_id, model, len(vector), digest, vector.tobytes(), time.time()))
            done += 1
    store.log(actor, "embed_ledger_local", "embedding", model, {"embedded": done, "skipped": len(todo) - done, "model": model})
    store.conn.commit(); return done


def similar_transactions(store: Store, query: str, limit=25, model="embeddinggemma"):
    """Rank ledger candidates with token overlap plus optional local cosine.

    Embedding similarity can add semantically related candidates, but never
    suppresses a strong transparent token/account-head match.
    """
    query_tokens = tokens(query)
    if not query_tokens: raise ValueError("query must contain meaningful transaction or account-head terms")
    rows = _entries(store); doc_freq = Counter(t for e in rows for t in tokens(_text(e)))
    n = max(1, len(rows)); query_vector = None; dims = None
    embedded = store.conn.execute("SELECT dims FROM ledger_embeddings WHERE model=? LIMIT 1", (model,)).fetchone()
    if embedded:
        dims = embedded[0]; query_vector = LocalEmbedder(model).embed([query])[0]
        if len(query_vector) != dims: raise ValueError("local model dimensions changed; rerun embed-ledger for this model")
    scored = []
    for entry in rows:
        text = _text(entry); entry_tokens = tokens(text); union = query_tokens | entry_tokens
        weighted_shared = sum(math.log((n + 1) / (doc_freq[t] + 1)) + 1 for t in query_tokens & entry_tokens)
        weighted_all = sum(math.log((n + 1) / (doc_freq[t] + 1)) + 1 for t in union)
        token_score = weighted_shared / weighted_all if weighted_all else 0.0
        semantic_score = None
        if query_vector is not None:
            row = store.conn.execute("SELECT vector FROM ledger_embeddings WHERE ledger_id=? AND model=? AND dims=?", (entry["id"], model, dims)).fetchone()
            if row: semantic_score = max(0.0, _cosine(query_vector, array.array("f", row[0])))
        score = max(token_score, semantic_score or 0.0)
        if score:
            scored.append({"ledger_id": entry["id"], "entry_id": entry["entry_id"], "posting_date": entry["posting_date"], "account_code": entry["account_code"], "account_name": entry.get("account_name"), "signed_amount": entry["signed_amount"], "description": entry["description"], "preparer": entry["preparer"], "reference": entry["reference"], "token_score": round(token_score, 3), "semantic_score": round(semantic_score, 3) if semantic_score is not None else None, "score": round(score, 3), "shared_tokens": sorted(query_tokens & entry_tokens), "token_classes": classify(text)})
    return sorted(scored, key=lambda r: (-r["score"], -r["token_score"], r["ledger_id"]))[:limit]

```


## Assistant

<thinking>


**Planning LocalEmbedder query improvements**
</thinking>

**Tool Call: Editing files**
Status: Completed

Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/IMPLEMENTATION_PLAN.md
```
# Audit Analytics — Implementation and Evolution Plan

## 1. Purpose and operating boundary

Audit Analytics is a local-first journal-entry analytics system for audit and
accounting firms conducting Indian external statutory audits. Its purpose is to
help engagement teams profile a ledger population, identify explainable risk
cues, select and document responsive procedures, and retain an evidence-linked
review trail.

It is deliberately **not** an automated audit engine. It must never express an
audit opinion, determine that fraud occurred, treat a risk score as a finding,
or replace the auditor's professional judgement. A flagged entry is a review
cue. A reviewer must assess the entry, obtain appropriate evidence, and record
their disposition.

The initial product boundary is general-ledger (GL) and chart-of-accounts (COA)
data. Supporting documents, OCR, bank data, vendor/customer masters,
related-party graphs, continuous controls monitoring, and ERP integrations are
future additions behind the same normalized-data boundary.

The documentation and review controls are intended to support engagement teams
working under SA 230 and SA 240. The firm remains responsible for applying the
current standards, its audit methodology, quality-management policies, and any
jurisdiction-specific legal requirements.

## 2. Design translated from qcom-scraping

The source project supplied reusable pipeline principles rather than an audit
domain model:

| Source-pipeline pattern | Audit Analytics equivalent |
| --- | --- |
| Captured observation with time, source, and location | Imported GL record with import version, source row, hash, and evidence-file path |
| Entity-specific statistical baseline | Account, preparer, entity, and period peer groups |
| Unknown is not an out-of-stock event | Missing or invalid financial data is a coverage limitation, never a suspicious transaction |
| Debounced state/event handling | Versioned model runs, reviewed exceptions, and append-only dispositions |
| Ranked demand-pressure signal | Ranked, explainable journal-entry risk cue |
| Dashboard, export, and human review | Engagement review queue, reviewer note/disposition, and workpaper export |
| Additive migrations and reproducibility | Versioned imports/runs, immutable logs, and no destructive data rewrite |

The web crawler, consumer-product semantics, pricing logic, and demand claims
are intentionally not reused. Financial data enters only through trusted,
controlled imports and future read-only connector adapters.

## 3. Delivered foundation

The current implementation is a functional local MVP.

### 3.1 Engagement and data controls

- `init` creates one engagement database with client and audit-period metadata.
- `import-gl` accepts CSV and ordinary first-sheet XLSX exports without sending
  data to an external conversion service.
- Common header aliases are mapped to a canonical GL contract. Required fields
  are entry ID, posting date, account code, and signed amount or debit/credit.
- Accepted rows retain their complete original row JSON, SHA-256 row hash,
  source row number, import identifier, and evidence-file reference.
- Each source file is copied to an engagement-local `evidence/` directory and
  hash recorded before processing.
- Invalid rows are preserved with a rejection reason rather than silently
  discarded.
- The import records accepted/rejected counts and calculated debit/credit
  control totals. Analytics is blocked until the reviewer explicitly
  acknowledges every GL import and records a note.

### 3.2 Statistical and deterministic analytics

The analysis run is versioned and stores configuration, population size,
limitations, and every exception's component evidence.

- Repeated-entry tests identify repeated account/date/amount/description and
  repeated account/reference/amount patterns.
- Amount tests identify material round-number entries.
- Timing tests identify period-end and weekend postings.
- Relationship tests identify rare account/preparer combinations and potential
  opposite-sign reversals in the same account within 30 days.
- Robust peer outliers use the account-level median and median absolute
  deviation (MAD), avoiding fragile mean/standard-deviation assumptions.
- Benford analysis runs only when at least 100 non-zero amounts exist and is
  kept as a population-level indicator, not an entry-level accusation.
- An optional local isolation-style random-cut model operates only for
  populations of at least 256 entries. It is explicitly an additional ranking
  feature, not the sole basis for an exception or audit response.

Scores are bounded and severity-labelled for prioritisation. Reasons and peer
context remain visible so the reviewer can understand why an entry appeared.

### 3.3 Local semantic transaction search

- Transaction search text combines account code, optional COA account name,
  narration, reference, and entity. It does not use a remote service.
- A transparent token classifier labels terms associated with cash/bank,
  revenue, expense, payroll, inventory, tax, intercompany, and fixed assets.
- Token search uses weighted shared terms, where uncommon terms contribute more
  than generic transaction vocabulary.
- Optional Ollama `embeddinggemma` vectors are stored in the engagement SQLite
  database, keyed by ledger ID, model, dimensions, and a source-text hash.
  Unchanged records are not re-embedded.
- Query vectors are transient and never persisted. Similarity is local cosine
  similarity; the final candidate score is `max(token_score, semantic_score)`.
  Thus semantic retrieval expands candidates but never suppresses a strong
  transparent token/account-head match.
- Search candidates are review leads, not a statement that two entries are the
  same transaction or evidence of concealment.

### 3.4 Review and workpapers

- The local HTTP review UI shows entry context, score, reasons, model evidence,
  current status, and a required reviewer note.
- Supported dispositions are `open`, `cleared`, `follow_up`, and
  `selected_for_testing`.
- Each disposition creates an append-only `reviews` record and an `audit_log`
  event with actor, time, target, and structured details.
- `export` creates a CSV workpaper containing risk information, original GL
  context, reasons, and evidence. Firms can load this into their prescribed
  workpaper template.

## 4. Canonical data contract

### Required GL fields

| Canonical field | Purpose | Typical aliases |
| --- | --- | --- |
| `entry_id` | Stable journal/voucher-line identifier | journal_entry_id, voucher_no, transaction_id |
| `posting_date` | Accounting posting date | date, entry_date |
| `account_code` | GL account identifier | account, gl_code, ledger_code |
| `signed_amount` or `debit`/`credit` | Transaction value | amount, net_amount, debit_amount, credit_amount |

### Recommended optional fields

`document_date`, `description`, `preparer`, `reference`, `entity`, and
`is_manual` improve population profiling and analytical precision. Their
absence is recorded as a coverage limitation; it does not become a risk cue.

### COA contract

COA imports are optional enrichment and accept account code plus account name
and type where present. Future account-risk taxonomy mappings should be stored
separately from the raw client COA so firm methodology does not overwrite
client evidence.

## 5. Data model and lineage

The SQLite database is the engagement's system of record. Its logical flow is:

```text
evidence file -> imports -> ledger_entries / rejected_rows
                               |
                               v
                         model_runs -> exceptions -> reviews
                               \             \-> audit_log
                                \-> workpaper export
```

- `imports` stores file lineage, hash, counts, control totals, and reviewer
  acknowledgement.
- `ledger_entries` holds normalized data and immutable source identity.
- `rejected_rows` makes quality issues inspectable and countable.
- `model_runs` captures run configuration and limitations for reproducibility.
- `exceptions` links a particular run to a particular original ledger record.
- `reviews` is append-only; status changes do not erase earlier reviewer work.
- `audit_log` records administrative, import, analysis, and review actions.

Schema evolution must be additive: new tables or nullable columns plus
backfills where appropriate. Never overwrite raw rows, source hashes, reviewer
notes, or old model-run outputs.

## 6. Firm deployment and security baseline

The supported deployment baseline is an auditor-controlled laptop, server, or
private VPC. Engagement data must remain within the firm-approved environment.

- Bind the review service to `127.0.0.1` by default. A network deployment must
  add firm SSO, role-based access control, TLS, session expiry, CSRF protection,
  audit-log retention, encrypted backups, and tenancy isolation before use.
- Encrypt devices/disks and backups using firm-approved controls. Restrict the
  engagement directory to assigned team members.
- Do not route client data to hosted LLM, embedding, telemetry, spreadsheet
  conversion, or third-party model services by default.
- Preserve original import files under the firm retention policy. On engagement
  closure, archive or delete through the firm's approved records process—not a
  silent application cleanup task.
- Capture tool version, model configuration, population acknowledgement, and
  export timestamp in each formal workpaper package.

## 7. Review workflow

1. The engagement team creates the engagement and imports the GL/COA extracts.
2. The preparer reconciles accepted entry count and calculated totals to the
   client-provided population/control totals; rejected rows are investigated.
3. A reviewer acknowledges the import with a specific note. This unlocks
   analysis but does not imply audit evidence has been obtained.
4. The team runs the hybrid analytics and reviews population limitations.
5. The reviewer filters/ranks cues, obtains support as necessary, records a
   disposition and rationale, and selects substantive testing items where
   appropriate.
6. The team exports the reviewed population and dispositions into the firm's
   workpaper structure, including methodology, limitations, and conclusion by
   the responsible auditor.

## 8. Planned releases

### Release 1.1 — audit-methodology hardening

- Add import-mapping preview and a saved client/ERP field mapping per
  engagement.
- Capture external client control totals, compare them to accepted data, and
  require an explicit quantified reconciliation before acknowledgement.
- Add materiality and performance-materiality settings used only as disclosed
  ranking/sampling thresholds.
- Add account labels, account-type filters, fiscal calendar controls, and
  workbook/PDF workpaper outputs.
- Add a model-run comparison view and a formal methodology/limitations report.

### Release 1.2 — review governance

- Add local user roles: preparer, reviewer, engagement manager, and read-only
  quality reviewer.
- Require second-level approval for cleared high-severity entries and lock a
  completed review set while allowing additive reopening records.
- Add assignment, due date, reviewer filters, search, and reviewer sampling
  queues.
- Add signed export manifests listing source imports, file hashes, run IDs, and
  reviewed exception counts.

### Release 2 — controlled ERP connectors

- Implement read-only adapter interfaces for SAP, Oracle, Tally, QuickBooks,
  and other approved systems only after a firm provides authorized access and a
  data dictionary.
- Each adapter must produce the same canonical import data and a connector-run
  manifest: authorization identity, query/version, extraction timestamp,
  record count, control totals, and source-system identifiers.
- Do not make connectors silently refresh a reviewed engagement population;
  each refresh is a new import version requiring reconciliation and
  acknowledgement.

### Release 3 — expanded forensic and audit datasets

- Add vendor/customer masters, bank extracts, invoices, purchase orders, and
  related-party datasets as separate normalized evidence types.
- Build graph and text-similarity analysis only with explicit coverage and
  false-positive controls.
- Keep document ingestion separate from GL scoring; missing supporting evidence
  is a review state, not an inferred fraud feature.

### Release 4 — validated advanced models

- Replace the compact isolation-style scorer with a governed model registry
  only after documented validation across representative, authorised audit
  populations.
- Record training data provenance, version, feature schema, calibration,
  performance, drift checks, approval owner, and rollback process.
- Continue to require deterministic explanations, human review, and sampling
  methodology independent of any model score.

## 9. Acceptance and regression checks

Every release must retain these checks:

- Valid CSV/XLSX import maps standard aliases, copies evidence, and maintains
  correct row identity even with blank spreadsheet cells.
- Invalid required fields and dates become visible rejected rows; they never
  become scored exceptions.
- No analysis is possible before all GL imports are acknowledged.
- Calculated accepted-population counts/debits/credits are visible before the
  acknowledgement action.
- Synthetic datasets verify each deterministic cue, robust outlier threshold,
  reversal matching, Benford minimum-population guard, and isolation-model
  minimum-population guard.
- Each exception traces to an import, evidence file, original source row, and
  stored raw fields.
- A review note is mandatory; the audit log retains every disposition action.
- Exported workpapers include no language treating a score as fraud, an audit
  finding, or an audit opinion.
- Static and runtime checks confirm no outbound network call is introduced for
  engagement data without an explicitly approved connector/feature.

## 10. Known MVP limits

- The first UI is local and deliberately has no multi-user authentication;
  serve it only on the controlled host until Release 1.2 governance is built.
- XLSX support targets ordinary tabular first-sheet exports; complex workbooks,
  macros, protected files, and multi-sheet mappings require the mapping preview
  work in Release 1.1.
- The current import acknowledgement captures calculated totals and a reviewer
  note; structured client-supplied control-total reconciliation is planned for
  Release 1.1.
- The isolation-style algorithm is a compact local ranking aid with a stated
  ceiling, not a validated fraud model. It can be disabled per run.
- CSV is the current workpaper export. Formatted Excel/PDF output and audit
  suite integration are planned additions.

```


Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/README.md
```
# Audit Analytics

Local-first journal-entry analytics for Indian statutory-audit teams. It ranks
explainable risk cues for auditor review; it does not make audit conclusions or
issue an opinion.

## Quick start

```sh
cd audit-analytics
python3 run.py init --db demo/audit.db --client "Example Ltd" --period 2025-04-01:2026-03-31
python3 run.py import-gl --db demo/audit.db --file journal_entries.csv
python3 run.py acknowledge-population --db demo/audit.db --reviewer "A. Auditor" --note "Agreed to client GL control totals"
python3 run.py analyze --db demo/audit.db
python3 run.py serve --db demo/audit.db
```

Open `http://127.0.0.1:8788` to review and disposition flagged entries. Export
an evidence-linked CSV workpaper with `python3 run.py export --db demo/audit.db
--out demo/workpaper.csv`.

## Local semantic transaction search

Token classification works immediately and labels account/narration concepts
such as cash/bank, revenue, payroll, tax, inventory, and intercompany. To add
meaning-level similarity without moving ledger data off the engagement host,
install and run Ollama locally, then build a local vector index:

```sh
ollama serve                 # in a separate terminal
ollama pull embeddinggemma
python3 run.py embed-ledger --db demo/audit.db
python3 run.py similar --db demo/audit.db --query "manual year-end tax provision" --limit 20
```

The `similar` command falls back to transparent token/account-head matching
when no vectors have been built. Once vectors exist, its final score is the
maximum of token and cosine similarity, so semantic matching can surface a
worded-differently transaction but cannot hide a strong lexical match. The API
equivalent is `GET /api/similar?q=manual%20year-end%20tax%20provision`.

## Local semantic transaction search

Token classification works immediately and labels account/narration concepts
such as cash/bank, revenue, payroll, tax, inventory, and intercompany. To add
meaning-level similarity without moving ledger data off the engagement host,
install and run Ollama locally, then build a local vector index:

```sh
ollama serve                 # in a separate terminal
ollama pull embeddinggemma
python3 run.py embed-ledger --db demo/audit.db
python3 run.py similar --db demo/audit.db --query "manual year-end tax provision" --limit 20
```

The `similar` command falls back to transparent token/account-head matching
when no vectors have been built. Once vectors exist, its final score is the
maximum of token and cosine similarity, so semantic matching can surface a
worded-differently transaction but cannot hide a strong lexical match. The API
equivalent is `GET /api/similar?q=manual%20year-end%20tax%20provision`.

## Supported GL fields

Headers are matched case-insensitively with common aliases. Required: entry ID,
posting date, account code, and either signed amount or debit and credit.
Optional fields include document date, description/narration, preparer/user,
reference/document number, entity, and manual/system indicator. COA imports
are supported through `import-coa` and enrich account labels only.

CSV and ordinary first-sheet `.xlsx` exports are supported with the standard
library; no client data is uploaded or sent to a conversion service.

## Controls and limitations

- Every imported source file is copied into `evidence/` beside the engagement
  database and is SHA-256 hashed; each entry retains source row identity.
- Import validation separates rejected/missing data from risk cues.
- Analysis is blocked until a reviewer acknowledges the accepted population and
  control totals.
- The statistical suite includes deterministic tests, account-peer robust
  outliers, Benford population checks, reversal matching, and an optional local
  isolation-style model for populations of at least 256 entries.
- Risk scores are prioritisation cues. Reviewer dispositions and audit-log
  records are append-only; no result is labelled fraud or an audit conclusion.

The controls are designed to support documentation under SA 230 and journal
entry procedures under SA 240; the engagement team remains responsible for
audit design, evidence evaluation, and conclusions.

```


Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/src/audit_analytics/cli.py
```
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .analytics import analyze
from .importer import import_coa, import_gl
from .semantic import embed_ledger, similar_transactions
from .server import serve
from .store import Store

def _store(path): return Store(path)

def main():
    p = argparse.ArgumentParser(description="Local journal-entry audit analytics")
    sub = p.add_subparsers(dest="cmd", required=True)
    init = sub.add_parser("init"); init.add_argument("--db", required=True); init.add_argument("--client", required=True); init.add_argument("--period", required=True, help="YYYY-MM-DD:YYYY-MM-DD")
    for name in ("import-gl", "import-coa"):
        x=sub.add_parser(name); x.add_argument("--db", required=True); x.add_argument("--file", required=True); x.add_argument("--actor", default="system")
    ack=sub.add_parser("acknowledge-population"); ack.add_argument("--db", required=True); ack.add_argument("--reviewer", required=True); ack.add_argument("--note", required=True)
    a=sub.add_parser("analyze"); a.add_argument("--db", required=True); a.add_argument("--actor", default="system"); a.add_argument("--no-isolation", action="store_true")
    e=sub.add_parser("export"); e.add_argument("--db", required=True); e.add_argument("--out", required=True)
    em=sub.add_parser("embed-ledger", help="create local Ollama vectors; no data leaves this host"); em.add_argument("--db", required=True); em.add_argument("--model", default="embeddinggemma"); em.add_argument("--batch-size", type=int, default=64); em.add_argument("--actor", default="system")
    si=sub.add_parser("similar", help="find semantically and token-similar transactions"); si.add_argument("--db", required=True); si.add_argument("--query", required=True); si.add_argument("--limit", type=int, default=25); si.add_argument("--model", default="embeddinggemma")
    s=sub.add_parser("serve"); s.add_argument("--db", required=True); s.add_argument("--port", type=int, default=8788)
    args=p.parse_args(); store=_store(args.db)
    try:
        if args.cmd == "init":
            start, end=args.period.split(":", 1); store.conn.execute("INSERT INTO engagement VALUES(1,?,?,?,strftime('%s','now'))", (args.client,start,end)); store.log("system","init","engagement",1,{"client":args.client}); store.conn.commit(); print(f"created engagement for {args.client}")
        elif args.cmd == "import-gl":
            iid,n,b,d,c=import_gl(store,args.file,args.actor); print(f"GL import {iid}: accepted={n}, rejected={b}, debit={d:.2f}, credit={c:.2f}")
        elif args.cmd == "import-coa": print(f"COA import {import_coa(store,args.file,args.actor)} complete")
        elif args.cmd == "acknowledge-population":
            pending=store.conn.execute("SELECT id,accepted_rows,rejected_rows,control_debits,control_credits FROM imports WHERE kind='gl' AND acknowledged_at IS NULL").fetchall()
            if not pending: raise ValueError("no unacknowledged GL imports")
            for r in pending: store.conn.execute("UPDATE imports SET acknowledged_at=strftime('%s','now'),acknowledged_by=?,acknowledgement_note=? WHERE id=?",(args.reviewer,args.note,r["id"])); store.log(args.reviewer,"acknowledge_population","import",r["id"],dict(r))
            store.conn.commit(); print(f"acknowledged {len(pending)} GL import(s)")
        elif args.cmd == "analyze": print(f"analysis run {analyze(store,args.actor,not args.no_isolation)} complete")
        elif args.cmd == "export":
            rows=store.conn.execute("""SELECT e.*,l.entry_id,l.posting_date,l.account_code,l.signed_amount,l.description,l.preparer,l.reference,e.reasons_json,e.evidence_json
              FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id ORDER BY e.risk_score DESC""").fetchall(); out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
            with out.open("w",newline="",encoding="utf-8") as f:
                w=csv.writer(f); w.writerow(["exception_id","risk_score","severity","status","entry_id","posting_date","account_code","signed_amount","description","preparer","reference","reasons","evidence"]); w.writerows([[r[k] for k in ("id","risk_score","severity","status","entry_id","posting_date","account_code","signed_amount","description","preparer","reference","reasons_json","evidence_json")] for r in rows])
            print(f"wrote {len(rows)} review cues to {out}")
        elif args.cmd == "embed-ledger": print(f"embedded {embed_ledger(store,args.model,args.batch_size,args.actor)} changed ledger entries locally")
        elif args.cmd == "similar":
            rows=similar_transactions(store,args.query,args.limit,args.model)
            print(json.dumps({"query":args.query,"count":len(rows),"results":rows},indent=2))
        else: serve(args.db,args.port)
    finally: store.close()

```


Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/src/audit_analytics/server.py
```
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .store import Store
from .semantic import similar_transactions

PAGE = """<!doctype html><title>Audit Analytics Review</title><style>body{font:14px system-ui;margin:2rem;max-width:1200px}table{border-collapse:collapse;width:100%}th,td{border:1px solid #ddd;padding:.5rem;text-align:left}th{background:#f5f5f5}.high{color:#a00;font-weight:bold}.medium{color:#a60;font-weight:bold}textarea{width:100%;height:3rem}</style><h1>Journal-entry review</h1><p id=summary></p><table><thead><tr><th>Risk</th><th>Entry</th><th>Context</th><th>Reasons / evidence</th><th>Disposition</th></tr></thead><tbody id=rows></tbody></table><script>
async function load(){let x=await (await fetch('/api/exceptions')).json();document.querySelector('#summary').textContent=`${x.count} review cues · outputs support auditor judgement and are not conclusions.`;let body=document.querySelector('#rows');body.innerHTML=x.rows.map(r=>`<tr><td class="${r.severity}">${r.risk_score} (${r.severity})<br>${r.status}</td><td>${r.entry_id}<br>${r.posting_date}<br>${r.account_code}: ${r.signed_amount}</td><td>${r.description||''}<br>Preparer: ${r.preparer||'—'}<br>Ref: ${r.reference||'—'}</td><td>${r.reasons.join('<br>')}<hr><small>${JSON.stringify(r.evidence)}</small></td><td><select id=s${r.id}><option>open</option><option>cleared</option><option>follow_up</option><option>selected_for_testing</option></select><textarea id=n${r.id} placeholder="Audit rationale / evidence requested"></textarea><button onclick="review(${r.id})">Save</button></td></tr>`).join('')}
async function review(id){let reviewer=prompt('Reviewer name');if(!reviewer)return;let disposition=document.querySelector('#s'+id).value,note=document.querySelector('#n'+id).value;if(!note){alert('A review note is required');return}let r=await fetch('/api/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id,reviewer,disposition,note})});if(!r.ok)alert(await r.text());else load()}load();</script>"""

def serve(db_path: str, port=8788):
    class Handler(BaseHTTPRequestHandler):
        def _json(self, value, status=200):
            payload=json.dumps(value, default=str).encode(); self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(payload))); self.end_headers(); self.wfile.write(payload)
        def do_GET(self):
            if urlparse(self.path).path == "/":
                payload=PAGE.encode(); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(payload))); self.end_headers(); self.wfile.write(payload); return
            if urlparse(self.path).path == "/api/exceptions":
                s=Store(db_path)
                try:
                    rows=s.conn.execute("""SELECT e.*,l.entry_id,l.posting_date,l.account_code,l.signed_amount,l.description,l.preparer,l.reference
                    FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id ORDER BY e.risk_score DESC""").fetchall()
                    out=[]
                    for r in rows:
                        x=dict(r); x["reasons"]=json.loads(x.pop("reasons_json")); x["evidence"]=json.loads(x.pop("evidence_json")); out.append(x)
                    self._json({"count":len(out),"rows":out})
                finally: s.close()
                return
            if urlparse(self.path).path == "/api/similar":
                parsed = urlparse(self.path); query = parse_qs(parsed.query).get("q", [""])[0]
                try:
                    s=Store(db_path)
                    try: self._json({"query":query,"results":similar_transactions(s,query)})
                    finally: s.close()
                except ValueError as e: self._json({"error":str(e)},400)
                return
            self._json({"error":"not found"},404)
        def do_POST(self):
            if urlparse(self.path).path != "/api/review": self._json({"error":"not found"},404); return
            try:
                data=json.loads(self.rfile.read(int(self.headers.get("Content-Length","0"))))
                if not all(isinstance(data.get(k),str) and data[k].strip() for k in ("reviewer","disposition","note")): raise ValueError("reviewer, disposition, and note are required")
                if data["disposition"] not in {"open","cleared","follow_up","selected_for_testing"}: raise ValueError("invalid disposition")
                s=Store(db_path)
                try:
                    exists=s.conn.execute("SELECT 1 FROM exceptions WHERE id=?",(data.get("id"),)).fetchone()
                    if not exists: raise ValueError("exception not found")
                    cur=s.conn.execute("INSERT INTO reviews(exception_id,reviewer,disposition,note,created_at) VALUES(?,?,?,?,strftime('%s','now'))",(data["id"],data["reviewer"].strip(),data["disposition"],data["note"].strip()))
                    s.conn.execute("UPDATE exceptions SET status=? WHERE id=?",(data["disposition"],data["id"])); s.log(data["reviewer"],"review_exception","exception",data["id"],{"review_id":cur.lastrowid,"disposition":data["disposition"]}); s.conn.commit()
                finally: s.close()
                self._json({"ok":True})
            except (ValueError, json.JSONDecodeError) as e: self._json({"error":str(e)},400)
        def log_message(self,*args): pass
    print(f"Audit review UI: http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1",port),Handler).serve_forever()

```


Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/tests/test_semantic.py
```
import tempfile
import unittest
from pathlib import Path

from audit_analytics.semantic import classify, similar_transactions
from audit_analytics.store import Store

class SemanticTest(unittest.TestCase):
    def test_token_classes_and_similarity_work_without_a_model_service(self):
        self.assertEqual(classify("NEFT bank transfer for GST tax"), ["cash_bank", "tax"])
        with tempfile.TemporaryDirectory() as d:
            store=Store(str(Path(d)/"audit.db")); store.conn.execute("INSERT INTO engagement VALUES(1,'Client','2025-04-01','2026-03-31',0)")
            for i, desc in enumerate(("Year end GST provision manual journal", "Office rent paid", "Payroll accrual"), 1):
                store.conn.execute("""INSERT INTO imports(kind,original_name,evidence_path,sha256,imported_at,accepted_rows,rejected_rows) VALUES('gl','g.csv','g.csv','x',0,1,0)""")
                iid=store.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                store.conn.execute("""INSERT INTO ledger_entries(import_id,entry_id,posting_date,account_code,debit,credit,signed_amount,description,source_row,source_hash,raw_json)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?)""",(iid,str(i),'2026-03-31','2200',100,0,100,desc,i,'h'+str(i),'{}'))
            store.conn.commit(); rows=similar_transactions(store,"manual tax provision",limit=2)
            self.assertEqual(rows[0]['description'],"Year end GST provision manual journal")
            self.assertGreater(rows[0]['token_score'],0)

if __name__ == '__main__': unittest.main()

```


## Assistant

<thinking>


**Inspecting semantic bug handling**
</thinking>

The semantic layer now combines account-head/narration token evidence with a cached local-vector index. It is usable immediately in token-only mode; local Ollama vectors are an opt-in enhancement once the firm starts its own model server.

**Tool Call: python3 run.py --help >/dev/null && PYTHONPATH=src python3 -m unittest discover -s tests -v && python3 -m py_compile run.py src/audit_analytics/*.py && python3 run.py similar --help | sed -n '1,120p'**
Status: Completed

Terminal:
```
test_import_requires_acknowledgement_then_creates_traceable_exception (test_pipeline.PipelineTest.test_import_requires_acknowledgement_then_creates_traceable_exception) ... ok
test_token_classes_and_similarity_work_without_a_model_service (test_semantic.SemanticTest.test_token_classes_and_similarity_work_without_a_model_service) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.132s

OK
usage: run.py similar [-h] --db DB --query QUERY [--limit LIMIT]
                      [--model MODEL]

options:
  -h, --help     show this help message and exit
  --db DB
  --query QUERY
  --limit LIMIT
  --model MODEL

```


## Assistant

<thinking>


**Planning UI search integration**

**Refining embedding dimension handling**
</thinking>

Implemented local semantic transaction search in [audit-analytics](/Users/Mitesh%20Gada/Documents/Projects/audit-analytics).

- Added transparent token classification for cash/bank, revenue, payroll, inventory, tax, intercompany, etc.
- Added token-weighted similarity across account code/name, narration, reference, and entity.
- Added optional local Ollama/`embeddinggemma` embeddings, cached in the engagement SQLite DB.
- Semantic score expands candidates but never suppresses strong token/account-head matches.
- Added commands:
  - `python3 run.py embed-ledger --db demo/audit.db`
  - `python3 run.py similar --db demo/audit.db --query "manual year-end tax provision"`
- Added API endpoint: `/api/similar?q=...`
- Updated [README.md](/Users/Mitesh%20Gada/Documents/Projects/audit-analytics/README.md) and [IMPLEMENTATION_PLAN.md](/Users/Mitesh%20Gada/Documents/Projects/audit-analytics/IMPLEMENTATION_PLAN.md).

Verified with two automated tests, including token-only search without an Ollama server.

## User

suggest recomended models to the user in readme files

## Assistant

<thinking>


**Planning local embedding model research**
</thinking>

I’ll add a concise local-model recommendation section, with a default and hardware/quality alternatives. I’m checking current model availability and capabilities first so the README doesn’t recommend stale names.

**Tool Call: XDG_CONFIG_HOME="/Users/Mitesh Gada/Documents/Projects/.monid/xdg" /Users/Mitesh\ Gada/.npm-global/bin/monid discover --query "Ollama local embedding models embeddinggemma nomic-embed-text mxbai-embed-large current" && XDG_CONFIG_HOME="/Users/Mitesh Gada/Documents/Projects/.monid/xdg" /Users/Mitesh\ Gada/.npm-global/bin/monid inspect --provider tinyfish --endpoint /search && XDG_CONFIG_HOME="/Users/Mitesh Gada/Documents/Projects/.monid/xdg" /Users/Mitesh\ Gada/.npm-global/bin/monid run --provider tinyfish --endpoint /search --query '{"query":"site:ollama.com/library embeddinggemma nomic-embed-text mxbai-embed-large embedding models","purpose":"Recommend current local-only embedding models for a financial audit transaction similarity feature","include_domains":"ollama.com"}' --wait 90 -j**
Status: Completed

Terminal:
```
- Searching for "Ollama local embedding models embeddinggemma nomic-embed-text mxbai-embed-large current"...
✔ Found 5 result(s)
Provider    Endpoint                Price            Description                                        Verified
octen       /embedding              $0.01-$0.07 / 1M Convert text into embedding vectors.                  ✓
exa         /contents               $0.002/call      Fetch clean, LLM-ready content for a list of URLs.    ✓
lmarena     /get_best_coding_models $0.01/call       Get a combined summary of the best AI coding mo...    ✓
mrscraper   /gemini/ask             $0.01/call       Ask Google Gemini a question and get its answer...    ✓
context.dev /web/scrape/markdown    $0.0009/call     Scrape any URL into clean, LLM-ready Markdown.        ✓

Update available: 0.1.6 → 0.1.7.
  Run `npm update -g @monid-ai/cli` to update monid-cli.
  Download the latest version of skill at https://monid.ai/SKILL.md.
- Inspecting tinyfish//search...
✔ Fetched details about /search from tinyfish

Provider
  TinyFish (tinyfish)

Endpoint
  /search

Description
  Search the live web, news, or research papers and get ranked results.

✓ Verified

Summary
  Browser-rendered search over the live web — results are never cached, so pricing pages, earnings releases, and breaking news are current at query time. Set 'domain_type' to 'web' (default), 'news' (adds publisher and date), or 'research_paper' (adds authors, venue, year, cited_by_count, and pdf_url). Filters cover geo ('location') and 'language', domain allow/block lists ('include_domains' / 'exclude_domains'), a freshness window ('recency_minutes') or calendar bounds ('after_date' / 'before_date'), publication-year bounds for papers, and paging ('page', 0-10). Pass 'purpose' — a short statement of the task the results are for — to sharpen ranking. Returns position, title, url, site_name, and snippet per result. Snippets only: this endpoint does not return page content — pipe the result URLs into TinyFish /fetch, which is also free, when you need the full text.

Pricing
  Type:   PER_CALL
  Amount: $0/call

Input
  Query Params
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "minLength": 1,
      "description": "Search query. Accepts natural language and still honours site:/-site: operators, though include_domains / exclude_domains are preferred because they do not collide with other query syntax. Example: 'NVIDIA Q4 FY2025 revenue'."
    },
    "purpose": {
      "type": "string",
      "minLength": 1,
      "maxLength": 2000,
      "description": "Optional short statement of the task these results are for — the goal behind the request, not the request itself. TinyFish uses it as an extra ranking signal. Example: 'Compare pricing tiers across vendors for a procurement report'. Max 2000 characters."
    },
    "location": {
      "description": "Country code for geo-targeted results. Example: US, GB, FR, DE. Auto-resolves from `language` when omitted; defaults to US if neither is set.",
      "type": "string",
      "minLength": 1
    },
    "language": {
      "description": "Language code for result language. Example: en, fr, de. Auto-resolves from `location` when omitted; defaults to en if neither is set.",
      "type": "string",
      "minLength": 1
    },
    "include_domains": {
      "description": "Comma-separated domains to restrict results to. Example: github.com,arxiv.org.",
      "type": "string",
      "minLength": 1
    },
    "exclude_domains": {
      "description": "Comma-separated domains to exclude from results. Example: pinterest.com,quora.com.",
      "type": "string",
      "minLength": 1
    },
    "recency_minutes": {
      "description": "Freshness window in minutes, relative to now. Example: 60 for the last hour. Cannot be combined with after_date or before_date, and is not supported for domain_type=research_paper.",
      "type": "integer",
      "minimum": 1,
      "maximum": 5256000
    },
    "after_date": {
      "description": "Lower calendar bound, YYYY-MM-DD. Example: 2026-06-01. Cannot be combined with recency_minutes, and is not supported for domain_type=research_paper.",
      "type": "string",
      "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
    },
    "before_date": {
      "description": "Upper calendar bound, YYYY-MM-DD. Example: 2026-06-18. Cannot be combined with recency_minutes, and is not supported for domain_type=research_paper.",
      "type": "string",
      "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
    },
    "domain_type": {
      "description": "Corpus to search. 'web' (default) returns general results; 'news' adds publisher and date; 'research_paper' searches academic work and adds authors, venue, year, cited_by_count, and pdf_url.",
      "type": "string",
      "enum": [
        "web",
        "news",
        "research_paper"
      ]
    },
    "pub_year_min": {
      "description": "Inclusive lower publication-year bound. Only supported for domain_type=research_paper. Example: 2017.",
      "type": "integer",
      "minimum": 0,
      "maximum": 9999
    },
    "pub_year_max": {
      "description": "Inclusive upper publication-year bound. Only supported for domain_type=research_paper. Example: 2024.",
      "type": "integer",
      "minimum": 0,
      "maximum": 9999
    },
    "page": {
      "description": "Zero-indexed result page. Example: 2 returns the third page. Maximum 10.",
      "type": "integer",
      "minimum": 0,
      "maximum": 10
    }
  },
  "required": [
    "query"
  ],
  "additionalProperties": false,
  "~standard": {
    "vendor": "zod",
    "version": 1,
    "jsonSchema": {}
  }
}

Documentation
  https://docs.tinyfish.ai/search-api/reference

Hints
  find other endpoints: monid discover -q '<QUERY>'
  run this endpoint: monid run -p tinyfish -e /search -i '<BODY>' --query '<QUERY_PARAMS>' --path '<PATH_PARAMS>'
  get the full page text for these results: monid inspect -p tinyfish -e /fetch  # also free, up to 10 URLs per call
  search and get page content in one call: monid discover -q 'web search with inline page content'  # several providers return content in one round-trip
  semantic search rather than keyword matching: monid inspect -p exa -e /search  # neural search with highlights


Update available: 0.1.6 → 0.1.7.
  Run `npm update -g @monid-ai/cli` to update monid-cli.
  Download the latest version of skill at https://monid.ai/SKILL.md.
{
  "runId": "01M226C1K0RBT1NZ396S93NXGM",
  "provider": "tinyfish",
  "endpoint": "/search",
  "status": "COMPLETED",
  "output": {
    "query": "site:ollama.com/library embeddinggemma nomic-embed-text mxbai-embed-large embedding models",
    "results": [
      {
        "position": 1,
        "site_name": "ollama.com",
        "snippet": "nomic-embed-text . A high-performing open embedding model with a large token context window. embedding. 84.8M Pulls 3 Tags Updated 2 years ago · llama3.2. Meta's ...",
        "title": "library",
        "url": "https://ollama.com"
      },
      {
        "position": 2,
        "site_name": "ollama.com",
        "snippet": "nomic-embed-text is a large context length text encoder that surpasses OpenAI text-embedding-ada-002 and text-embedding-3-small performance on short and ...",
        "title": "nomic-embed-text - Ollama",
        "url": "https://ollama.com/library/nomic-embed-text"
      },
      {
        "position": 3,
        "site_name": "ollama.com",
        "snippet": "mxbai-embed-large was trained with no overlap of the MTEB data, which indicates that the model generalizes well across several domains, tasks and text length.",
        "title": "mxbai-embed-large - Ollama",
        "url": "https://ollama.com/library/mxbai-embed-large"
      },
      {
        "position": 4,
        "site_name": "ollama.com",
        "snippet": "nomic-embed-text. A high-performing open embedding model with a large token context window. · mxbai-embed-large. State-of-the-art large embedding model from ...",
        "title": "library - Ollama",
        "url": "https://ollama.com/library?q=embe"
      },
      {
        "position": 5,
        "site_name": "ollama.com",
        "snippet": "nomic-embed-text. A high-performing open embedding model with a large token context window. embedding.",
        "title": "library - Ollama",
        "url": "https://ollama.com/library?ref=timwappat.info"
      }
    ],
    "total_results": 5,
    "page": 0
  },
  "providerResponse": {
    "httpStatus": 200
  },
  "price": {
    "type": "PER_CALL",
    "amount": {
      "value": 0,
      "currency": "USD"
    }
  },
  "billing": {
    "reportedCost": {
      "currency": "USD",
      "value": 0,
      "unit": "MICRO_DOLLAR"
    }
  },
  "resultCount": 0,
  "billedUnits": 0,
  "createdAt": "2026-09-09T04:21:14.174Z",
  "completedAt": "2026-09-09T04:21:15.994Z",
  "hints": {
    "retrieve the response later": "monid runs get -r 01M226C1K0RBT1NZ396S93NXGM",
    "get the full page text for these results": "monid inspect -p tinyfish -e /fetch  # also free, up to 10 URLs per call",
    "semantic search rather than keyword matching": "monid inspect -p exa -e /search  # neural search with highlights",
    "search and get page content in one call": "monid discover -q 'web search with inline page content'  # several providers return content in one round-trip"
  },
  "notes": [
    "Update available: 0.1.6 → 0.1.7. Run `npm update -g @monid-ai/cli` to update monid-cli. Download the latest version of skill at https://monid.ai/SKILL.md."
  ]
}

```


## Assistant

<thinking>


**Evaluating embedding model options**
</thinking>

**Tool Call: XDG_CONFIG_HOME="/Users/Mitesh Gada/Documents/Projects/.monid/xdg" /Users/Mitesh\ Gada/.npm-global/bin/monid run --provider tinyfish --endpoint /search --query '{"query":"embeddinggemma Ollama official model embedding gemma local","purpose":"Verify a local embedding model recommendation for audit transaction semantic search","include_domains":"ollama.com,ai.google.dev"}' --wait 90 -j**
Status: Completed

Terminal:
```
{
  "runId": "01M226CBFPS0C9794663CH62AK",
  "provider": "tinyfish",
  "endpoint": "/search",
  "status": "COMPLETED",
  "output": {
    "query": "embeddinggemma Ollama official model embedding gemma local",
    "results": [
      {
        "position": 1,
        "site_name": "ollama.com",
        "snippet": "EmbeddingGemma produces vector representations of text, making it well-suited for search and retrieval tasks, including classification, clustering, and semantic ...",
        "title": "embeddinggemma - Ollama",
        "url": "https://ollama.com/library/embeddinggemma"
      },
      {
        "position": 2,
        "site_name": "ollama.com",
        "snippet": "embeddinggemma EmbeddingGemma is a 300M parameter embedding model from Google. A suite of text embedding models by Snowflake, optimized for performance.",
        "title": "Embedding models - Ollama",
        "url": "https://ollama.com/search?c=embedding"
      },
      {
        "position": 3,
        "site_name": "docs.ollama.com",
        "snippet": "Embeddings turn text into numeric vectors you can store in a vector database, search with cosine similarity, or use in RAG pipelines.",
        "title": "Embeddings - Ollama documentation",
        "url": "https://docs.ollama.com/capabilities/embeddings"
      },
      {
        "date": "Apr 16, 2026",
        "position": 4,
        "site_name": "ai.google.dev",
        "snippet": "EmbeddingGemma is a 308M parameter multilingual text embedding model based on Gemma 3. It is optimized for use in everyday devices, ...",
        "title": "EmbeddingGemma model overview - Google AI for Developers",
        "url": "https://ai.google.dev/gemma/docs/embeddinggemma"
      },
      {
        "date": "Apr 8, 2024",
        "position": 5,
        "site_name": "ollama.com",
        "snippet": "Embedding models are available in Ollama, making it easy to generate vector embeddings for use in search and retrieval augmented generation ...",
        "title": "Embedding models · Ollama Blog",
        "url": "https://ollama.com/blog/embedding-models"
      },
      {
        "position": 6,
        "site_name": "ollama.com",
        "snippet": "EmbeddingGemma is a 300M parameter embedding model from Google. s using one immutable model across cloud and local Ollama deployments. supporting multiple ...",
        "title": "gemma - Ollama",
        "url": "https://ollama.com/search?c=embedding&q=gemma"
      },
      {
        "date": "Apr 2, 2026",
        "position": 7,
        "site_name": "ai.google.dev",
        "snippet": "Ollama provides a set of official Gemma model variants for immediate use which are quantized and saved in GGUF format. You can use your own ...",
        "title": "Run Gemma with Ollama | Google AI for Developers",
        "url": "https://ai.google.dev/gemma/docs/integrations/ollama"
      },
      {
        "position": 8,
        "site_name": "ollama.com",
        "snippet": "EmbeddingGemma is a 300M parameter embedding model from Google. embedding ... embeddings using one immutable model across cloud and local Ollama deployments.",
        "title": "embedding - Ollama",
        "url": "https://ollama.com/search?p=4&q=embedding"
      },
      {
        "position": 9,
        "site_name": "ollama.com",
        "snippet": "EmbeddingGemma is a 300M parameter embedding model from Google. embedding ... Meta's latest open model built for always-on local agents. 30B parameters ...",
        "title": "library - Ollama",
        "url": "https://ollama.com/library"
      },
      {
        "position": 10,
        "site_name": "ollama.com",
        "snippet": "Note: this model requires Ollama 0.1.26 or later. Download it here. It can only be used to generate embeddings. nomic-embed-text is a large context ...",
        "title": "nomic-embed-text - Ollama",
        "url": "https://ollama.com/library/nomic-embed-text"
      }
    ],
    "total_results": 10,
    "page": 0
  },
  "providerResponse": {
    "httpStatus": 200
  },
  "price": {
    "type": "PER_CALL",
    "amount": {
      "value": 0,
      "currency": "USD"
    }
  },
  "billing": {
    "reportedCost": {
      "currency": "USD",
      "value": 0,
      "unit": "MICRO_DOLLAR"
    }
  },
  "resultCount": 0,
  "billedUnits": 0,
  "createdAt": "2026-09-09T04:21:24.309Z",
  "completedAt": "2026-09-09T04:21:27.343Z",
  "hints": {
    "retrieve the response later": "monid runs get -r 01M226CBFPS0C9794663CH62AK",
    "get the full page text for these results": "monid inspect -p tinyfish -e /fetch  # also free, up to 10 URLs per call",
    "semantic search rather than keyword matching": "monid inspect -p exa -e /search  # neural search with highlights",
    "search and get page content in one call": "monid discover -q 'web search with inline page content'  # several providers return content in one round-trip"
  },
  "notes": [
    "Update available: 0.1.6 → 0.1.7. Run `npm update -g @monid-ai/cli` to update monid-cli. Download the latest version of skill at https://monid.ai/SKILL.md."
  ]
}

```


## Assistant

<thinking>


**Planning README model recommendations**

**Planning README and MODELS.md updates**
</thinking>

**Tool Call: Editing files**
Status: Completed

Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/IMPLEMENTATION_PLAN.md
```
# Audit Analytics — Implementation and Evolution Plan

## 1. Purpose and operating boundary

Audit Analytics is a local-first journal-entry analytics system for audit and
accounting firms conducting Indian external statutory audits. Its purpose is to
help engagement teams profile a ledger population, identify explainable risk
cues, select and document responsive procedures, and retain an evidence-linked
review trail.

It is deliberately **not** an automated audit engine. It must never express an
audit opinion, determine that fraud occurred, treat a risk score as a finding,
or replace the auditor's professional judgement. A flagged entry is a review
cue. A reviewer must assess the entry, obtain appropriate evidence, and record
their disposition.

The initial product boundary is general-ledger (GL) and chart-of-accounts (COA)
data. Supporting documents, OCR, bank data, vendor/customer masters,
related-party graphs, continuous controls monitoring, and ERP integrations are
future additions behind the same normalized-data boundary.

The documentation and review controls are intended to support engagement teams
working under SA 230 and SA 240. The firm remains responsible for applying the
current standards, its audit methodology, quality-management policies, and any
jurisdiction-specific legal requirements.

## 2. Design translated from qcom-scraping

The source project supplied reusable pipeline principles rather than an audit
domain model:

| Source-pipeline pattern | Audit Analytics equivalent |
| --- | --- |
| Captured observation with time, source, and location | Imported GL record with import version, source row, hash, and evidence-file path |
| Entity-specific statistical baseline | Account, preparer, entity, and period peer groups |
| Unknown is not an out-of-stock event | Missing or invalid financial data is a coverage limitation, never a suspicious transaction |
| Debounced state/event handling | Versioned model runs, reviewed exceptions, and append-only dispositions |
| Ranked demand-pressure signal | Ranked, explainable journal-entry risk cue |
| Dashboard, export, and human review | Engagement review queue, reviewer note/disposition, and workpaper export |
| Additive migrations and reproducibility | Versioned imports/runs, immutable logs, and no destructive data rewrite |

The web crawler, consumer-product semantics, pricing logic, and demand claims
are intentionally not reused. Financial data enters only through trusted,
controlled imports and future read-only connector adapters.

## 3. Delivered foundation

The current implementation is a functional local MVP.

### 3.1 Engagement and data controls

- `init` creates one engagement database with client and audit-period metadata.
- `import-gl` accepts CSV and ordinary first-sheet XLSX exports without sending
  data to an external conversion service.
- Common header aliases are mapped to a canonical GL contract. Required fields
  are entry ID, posting date, account code, and signed amount or debit/credit.
- Accepted rows retain their complete original row JSON, SHA-256 row hash,
  source row number, import identifier, and evidence-file reference.
- Each source file is copied to an engagement-local `evidence/` directory and
  hash recorded before processing.
- Invalid rows are preserved with a rejection reason rather than silently
  discarded.
- The import records accepted/rejected counts and calculated debit/credit
  control totals. Analytics is blocked until the reviewer explicitly
  acknowledges every GL import and records a note.

### 3.2 Statistical and deterministic analytics

The analysis run is versioned and stores configuration, population size,
limitations, and every exception's component evidence.

- Repeated-entry tests identify repeated account/date/amount/description and
  repeated account/reference/amount patterns.
- Amount tests identify material round-number entries.
- Timing tests identify period-end and weekend postings.
- Relationship tests identify rare account/preparer combinations and potential
  opposite-sign reversals in the same account within 30 days.
- Robust peer outliers use the account-level median and median absolute
  deviation (MAD), avoiding fragile mean/standard-deviation assumptions.
- Benford analysis runs only when at least 100 non-zero amounts exist and is
  kept as a population-level indicator, not an entry-level accusation.
- An optional local isolation-style random-cut model operates only for
  populations of at least 256 entries. It is explicitly an additional ranking
  feature, not the sole basis for an exception or audit response.

Scores are bounded and severity-labelled for prioritisation. Reasons and peer
context remain visible so the reviewer can understand why an entry appeared.

### 3.3 Local semantic transaction search

- Transaction search text combines account code, optional COA account name,
  narration, reference, and entity. It does not use a remote service.
- A transparent token classifier labels terms associated with cash/bank,
  revenue, expense, payroll, inventory, tax, intercompany, and fixed assets.
- Token search uses weighted shared terms, where uncommon terms contribute more
  than generic transaction vocabulary.
- Optional Ollama `embeddinggemma` vectors are stored in the engagement SQLite
  database, keyed by ledger ID, model, dimensions, and a source-text hash.
  Unchanged records are not re-embedded.
- Query vectors are transient and never persisted. Similarity is local cosine
  similarity; the final candidate score is `max(token_score, semantic_score)`.
  Thus semantic retrieval expands candidates but never suppresses a strong
  transparent token/account-head match.
- Search candidates are review leads, not a statement that two entries are the
  same transaction or evidence of concealment.
- Recommended default: `embeddinggemma`, a compact multilingual local model.
  `nomic-embed-text` is the fast English-language comparison baseline, while
  `mxbai-embed-large` is the higher-resource candidate for a controlled
  quality pilot. The firm must validate the selected model on authorised,
  labelled transaction pairs and record the model in its methodology.

### 3.4 Review and workpapers

- The local HTTP review UI shows entry context, score, reasons, model evidence,
  current status, and a required reviewer note.
- Supported dispositions are `open`, `cleared`, `follow_up`, and
  `selected_for_testing`.
- Each disposition creates an append-only `reviews` record and an `audit_log`
  event with actor, time, target, and structured details.
- `export` creates a CSV workpaper containing risk information, original GL
  context, reasons, and evidence. Firms can load this into their prescribed
  workpaper template.

## 4. Canonical data contract

### Required GL fields

| Canonical field | Purpose | Typical aliases |
| --- | --- | --- |
| `entry_id` | Stable journal/voucher-line identifier | journal_entry_id, voucher_no, transaction_id |
| `posting_date` | Accounting posting date | date, entry_date |
| `account_code` | GL account identifier | account, gl_code, ledger_code |
| `signed_amount` or `debit`/`credit` | Transaction value | amount, net_amount, debit_amount, credit_amount |

### Recommended optional fields

`document_date`, `description`, `preparer`, `reference`, `entity`, and
`is_manual` improve population profiling and analytical precision. Their
absence is recorded as a coverage limitation; it does not become a risk cue.

### COA contract

COA imports are optional enrichment and accept account code plus account name
and type where present. Future account-risk taxonomy mappings should be stored
separately from the raw client COA so firm methodology does not overwrite
client evidence.

## 5. Data model and lineage

The SQLite database is the engagement's system of record. Its logical flow is:

```text
evidence file -> imports -> ledger_entries / rejected_rows
                               |
                               v
                         model_runs -> exceptions -> reviews
                               \             \-> audit_log
                                \-> workpaper export
```

- `imports` stores file lineage, hash, counts, control totals, and reviewer
  acknowledgement.
- `ledger_entries` holds normalized data and immutable source identity.
- `rejected_rows` makes quality issues inspectable and countable.
- `model_runs` captures run configuration and limitations for reproducibility.
- `exceptions` links a particular run to a particular original ledger record.
- `reviews` is append-only; status changes do not erase earlier reviewer work.
- `audit_log` records administrative, import, analysis, and review actions.

Schema evolution must be additive: new tables or nullable columns plus
backfills where appropriate. Never overwrite raw rows, source hashes, reviewer
notes, or old model-run outputs.

## 6. Firm deployment and security baseline

The supported deployment baseline is an auditor-controlled laptop, server, or
private VPC. Engagement data must remain within the firm-approved environment.

- Bind the review service to `127.0.0.1` by default. A network deployment must
  add firm SSO, role-based access control, TLS, session expiry, CSRF protection,
  audit-log retention, encrypted backups, and tenancy isolation before use.
- Encrypt devices/disks and backups using firm-approved controls. Restrict the
  engagement directory to assigned team members.
- Do not route client data to hosted LLM, embedding, telemetry, spreadsheet
  conversion, or third-party model services by default.
- Preserve original import files under the firm retention policy. On engagement
  closure, archive or delete through the firm's approved records process—not a
  silent application cleanup task.
- Capture tool version, model configuration, population acknowledgement, and
  export timestamp in each formal workpaper package.

## 7. Review workflow

1. The engagement team creates the engagement and imports the GL/COA extracts.
2. The preparer reconciles accepted entry count and calculated totals to the
   client-provided population/control totals; rejected rows are investigated.
3. A reviewer acknowledges the import with a specific note. This unlocks
   analysis but does not imply audit evidence has been obtained.
4. The team runs the hybrid analytics and reviews population limitations.
5. The reviewer filters/ranks cues, obtains support as necessary, records a
   disposition and rationale, and selects substantive testing items where
   appropriate.
6. The team exports the reviewed population and dispositions into the firm's
   workpaper structure, including methodology, limitations, and conclusion by
   the responsible auditor.

## 8. Planned releases

### Release 1.1 — audit-methodology hardening

- Add import-mapping preview and a saved client/ERP field mapping per
  engagement.
- Capture external client control totals, compare them to accepted data, and
  require an explicit quantified reconciliation before acknowledgement.
- Add materiality and performance-materiality settings used only as disclosed
  ranking/sampling thresholds.
- Add account labels, account-type filters, fiscal calendar controls, and
  workbook/PDF workpaper outputs.
- Add a model-run comparison view and a formal methodology/limitations report.

### Release 1.2 — review governance

- Add local user roles: preparer, reviewer, engagement manager, and read-only
  quality reviewer.
- Require second-level approval for cleared high-severity entries and lock a
  completed review set while allowing additive reopening records.
- Add assignment, due date, reviewer filters, search, and reviewer sampling
  queues.
- Add signed export manifests listing source imports, file hashes, run IDs, and
  reviewed exception counts.

### Release 2 — controlled ERP connectors

- Implement read-only adapter interfaces for SAP, Oracle, Tally, QuickBooks,
  and other approved systems only after a firm provides authorized access and a
  data dictionary.
- Each adapter must produce the same canonical import data and a connector-run
  manifest: authorization identity, query/version, extraction timestamp,
  record count, control totals, and source-system identifiers.
- Do not make connectors silently refresh a reviewed engagement population;
  each refresh is a new import version requiring reconciliation and
  acknowledgement.

### Release 3 — expanded forensic and audit datasets

- Add vendor/customer masters, bank extracts, invoices, purchase orders, and
  related-party datasets as separate normalized evidence types.
- Build graph and text-similarity analysis only with explicit coverage and
  false-positive controls.
- Keep document ingestion separate from GL scoring; missing supporting evidence
  is a review state, not an inferred fraud feature.

### Release 4 — validated advanced models

- Replace the compact isolation-style scorer with a governed model registry
  only after documented validation across representative, authorised audit
  populations.
- Record training data provenance, version, feature schema, calibration,
  performance, drift checks, approval owner, and rollback process.
- Continue to require deterministic explanations, human review, and sampling
  methodology independent of any model score.

## 9. Acceptance and regression checks

Every release must retain these checks:

- Valid CSV/XLSX import maps standard aliases, copies evidence, and maintains
  correct row identity even with blank spreadsheet cells.
- Invalid required fields and dates become visible rejected rows; they never
  become scored exceptions.
- No analysis is possible before all GL imports are acknowledged.
- Calculated accepted-population counts/debits/credits are visible before the
  acknowledgement action.
- Synthetic datasets verify each deterministic cue, robust outlier threshold,
  reversal matching, Benford minimum-population guard, and isolation-model
  minimum-population guard.
- Each exception traces to an import, evidence file, original source row, and
  stored raw fields.
- A review note is mandatory; the audit log retains every disposition action.
- Exported workpapers include no language treating a score as fraud, an audit
  finding, or an audit opinion.
- Static and runtime checks confirm no outbound network call is introduced for
  engagement data without an explicitly approved connector/feature.

## 10. Known MVP limits

- The first UI is local and deliberately has no multi-user authentication;
  serve it only on the controlled host until Release 1.2 governance is built.
- XLSX support targets ordinary tabular first-sheet exports; complex workbooks,
  macros, protected files, and multi-sheet mappings require the mapping preview
  work in Release 1.1.
- The current import acknowledgement captures calculated totals and a reviewer
  note; structured client-supplied control-total reconciliation is planned for
  Release 1.1.
- The isolation-style algorithm is a compact local ranking aid with a stated
  ceiling, not a validated fraud model. It can be disabled per run.
- CSV is the current workpaper export. Formatted Excel/PDF output and audit
  suite integration are planned additions.

```


Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/README.md
```
# Audit Analytics

Local-first journal-entry analytics for Indian statutory-audit teams. It ranks
explainable risk cues for auditor review; it does not make audit conclusions or
issue an opinion.

## Quick start

```sh
cd audit-analytics
python3 run.py init --db demo/audit.db --client "Example Ltd" --period 2025-04-01:2026-03-31
python3 run.py import-gl --db demo/audit.db --file journal_entries.csv
python3 run.py acknowledge-population --db demo/audit.db --reviewer "A. Auditor" --note "Agreed to client GL control totals"
python3 run.py analyze --db demo/audit.db
python3 run.py serve --db demo/audit.db
```

Open `http://127.0.0.1:8788` to review and disposition flagged entries. Export
an evidence-linked CSV workpaper with `python3 run.py export --db demo/audit.db
--out demo/workpaper.csv`.

## Local semantic transaction search

Token classification works immediately and labels account/narration concepts
such as cash/bank, revenue, payroll, tax, inventory, and intercompany. To add
meaning-level similarity without moving ledger data off the engagement host,
install and run Ollama locally, then build a local vector index:

```sh
ollama serve                 # in a separate terminal
ollama pull embeddinggemma
python3 run.py embed-ledger --db demo/audit.db
python3 run.py similar --db demo/audit.db --query "manual year-end tax provision" --limit 20
```

The `similar` command falls back to transparent token/account-head matching
when no vectors have been built. Once vectors exist, its final score is the
maximum of token and cosine similarity, so semantic matching can surface a
worded-differently transaction but cannot hide a strong lexical match. The API
equivalent is `GET /api/similar?q=manual%20year-end%20tax%20provision`.

### Recommended local embedding models

Use one approved model per engagement and rebuild that model's ledger index
before comparing results. Model choice changes retrieval candidates; it must be
recorded in the engagement methodology/workpaper, validated on representative
approved data, and never be used as an automatic conclusion.

| Model | Recommendation | Use it when | Command |
| --- | --- | --- | --- |
| `embeddinggemma` | **Default.** A compact multilingual embedding model suited to local retrieval, classification, and clustering. | Most engagements, especially where narrations include Indian-language or mixed-language terms, or workstation resources are limited. | `ollama pull embeddinggemma` |
| `nomic-embed-text` | Fast English-first comparison baseline with a large text context window. | Narrations and account heads are predominantly English and the firm wants a second retrieval benchmark. | `ollama pull nomic-embed-text` |
| `mxbai-embed-large` | Quality-focused alternative with a larger local resource footprint. | A controlled pilot shows that it retrieves materially better complex-transaction candidates on the firm's labelled evaluation set. | `ollama pull mxbai-embed-large` |

Start with `embeddinggemma`; do not select a model from generic benchmark claims
alone. Build a small, authorised evaluation set of known same-transaction,
same-business-process, and deliberately non-matching pairs. Compare precision
among the top 10–20 results, false positives across similar account heads, and
runtime/RAM on the actual firm workstation. Keep token-only matching enabled as
an explainable fallback and record the selected model with every formal export.

To test a different model without overwriting the default index:

```sh
ollama pull mxbai-embed-large
python3 run.py embed-ledger --db demo/audit.db --model mxbai-embed-large
python3 run.py similar --db demo/audit.db --model mxbai-embed-large --query "manual year-end tax provision"
```

### Recommended local embedding models

Use one approved model per engagement and rebuild that model's ledger index
before comparing results. Model choice changes retrieval candidates; it must be
recorded in the engagement methodology/workpaper, validated on representative
approved data, and never be used as an automatic conclusion.

| Model | Recommendation | Use it when | Command |
| --- | --- | --- | --- |
| `embeddinggemma` | **Default.** A compact multilingual embedding model suited to local retrieval, classification, and clustering. | Most engagements, especially where narrations include Indian-language or mixed-language terms, or workstation resources are limited. | `ollama pull embeddinggemma` |
| `nomic-embed-text` | Fast English-first comparison baseline with a large text context window. | Narrations and account heads are predominantly English and the firm wants a second retrieval benchmark. | `ollama pull nomic-embed-text` |
| `mxbai-embed-large` | Quality-focused alternative with a larger local resource footprint. | A controlled pilot shows that it retrieves materially better complex-transaction candidates on the firm's labelled evaluation set. | `ollama pull mxbai-embed-large` |

Start with `embeddinggemma`; do not select a model from generic benchmark claims
alone. Build a small, authorised evaluation set of known same-transaction,
same-business-process, and deliberately non-matching pairs. Compare precision
among the top 10–20 results, false positives across similar account heads, and
runtime/RAM on the actual firm workstation. Keep token-only matching enabled as
an explainable fallback and record the selected model with every formal export.

To test a different model without overwriting the default index:

```sh
ollama pull mxbai-embed-large
python3 run.py embed-ledger --db demo/audit.db --model mxbai-embed-large
python3 run.py similar --db demo/audit.db --model mxbai-embed-large --query "manual year-end tax provision"
```

## Supported GL fields

Headers are matched case-insensitively with common aliases. Required: entry ID,
posting date, account code, and either signed amount or debit and credit.
Optional fields include document date, description/narration, preparer/user,
reference/document number, entity, and manual/system indicator. COA imports
are supported through `import-coa` and enrich account labels only.

CSV and ordinary first-sheet `.xlsx` exports are supported with the standard
library; no client data is uploaded or sent to a conversion service.

## Controls and limitations

- Every imported source file is copied into `evidence/` beside the engagement
  database and is SHA-256 hashed; each entry retains source row identity.
- Import validation separates rejected/missing data from risk cues.
- Analysis is blocked until a reviewer acknowledges the accepted population and
  control totals.
- The statistical suite includes deterministic tests, account-peer robust
  outliers, Benford population checks, reversal matching, and an optional local
  isolation-style model for populations of at least 256 entries.
- Risk scores are prioritisation cues. Reviewer dispositions and audit-log
  records are append-only; no result is labelled fraud or an audit conclusion.

The controls are designed to support documentation under SA 230 and journal
entry procedures under SA 240; the engagement team remains responsible for
audit design, evidence evaluation, and conclusions.

```


## Assistant

<thinking>


**Identifying typo and confirming model version**
</thinking>

Added a “Recommended local embedding models” section to [README.md](/Users/Mitesh%20Gada/Documents/Projects/audit-analytics/README.md).

It recommends:

- `embeddinggemma` as the default local, multilingual choice.
- `nomic-embed-text` as an English-first comparison baseline.
- `mxbai-embed-large` for controlled quality pilots with more available compute.

It also documents evaluation criteria, local Ollama commands, and the requirement to record the selected model in engagement methodology. The recommendation is reflected in [IMPLEMENTATION_PLAN.md](/Users/Mitesh%20Gada/Documents/Projects/audit-analytics/IMPLEMENTATION_PLAN.md) too.

## User

does the readme include a detailed instruction set for how to use this project step by step

## Assistant

<thinking>


**Planning README inspection for quick start**
</thinking>

I’ll check the current README against an end-to-end first-use workflow so I can answer precisely and fill any practical gaps.

**Tool Call: Read file '/Users/Mitesh Gada/Documents/Projects/audit-analytics/README.md'**
Status: Completed

```json
{
  "formatted_output": "# Audit Analytics\n\nLocal-first journal-entry analytics for Indian statutory-audit teams. It ranks\nexplainable risk cues for auditor review; it does not make audit conclusions or\nissue an opinion.\n\n## Quick start\n\n```sh\ncd audit-analytics\npython3 run.py init --db demo/audit.db --client \"Example Ltd\" --period 2025-04-01:2026-03-31\npython3 run.py import-gl --db demo/audit.db --file journal_entries.csv\npython3 run.py acknowledge-population --db demo/audit.db --reviewer \"A. Auditor\" --note \"Agreed to client GL control totals\"\npython3 run.py analyze --db demo/audit.db\npython3 run.py serve --db demo/audit.db\n```\n\nOpen `http://127.0.0.1:8788` to review and disposition flagged entries. Export\nan evidence-linked CSV workpaper with `python3 run.py export --db demo/audit.db\n--out demo/workpaper.csv`.\n\n## Local semantic transaction search\n\nToken classification works immediately and labels account/narration concepts\nsuch as cash/bank, revenue, payroll, tax, inventory, and intercompany. To add\nmeaning-level similarity without moving ledger data off the engagement host,\ninstall and run Ollama locally, then build a local vector index:\n\n```sh\nollama serve                 # in a separate terminal\nollama pull embeddinggemma\npython3 run.py embed-ledger --db demo/audit.db\npython3 run.py similar --db demo/audit.db --query \"manual year-end tax provision\" --limit 20\n```\n\nThe `similar` command falls back to transparent token/account-head matching\nwhen no vectors have been built. Once vectors exist, its final score is the\nmaximum of token and cosine similarity, so semantic matching can surface a\nworded-differently transaction but cannot hide a strong lexical match. The API\nequivalent is `GET /api/similar?q=manual%20year-end%20tax%20provision`.\n\n### Recommended local embedding models\n\nUse one approved model per engagement and rebuild that model's ledger index\nbefore comparing results. Model choice changes retrieval candidates; it must be\nrecorded in the engagement methodology/workpaper, validated on representative\napproved data, and never be used as an automatic conclusion.\n\n| Model | Recommendation | Use it when | Command |\n| --- | --- | --- | --- |\n| `embeddinggemma` | **Default.** A compact multilingual embedding model suited to local retrieval, classification, and clustering. | Most engagements, especially where narrations include Indian-language or mixed-language terms, or workstation resources are limited. | `ollama pull embeddinggemma` |\n| `nomic-embed-text` | Fast English-first comparison baseline with a large text context window. | Narrations and account heads are predominantly English and the firm wants a second retrieval benchmark. | `ollama pull nomic-embed-text` |\n| `mxbai-embed-large` | Quality-focused alternative with a larger local resource footprint. | A controlled pilot shows that it retrieves materially better complex-transaction candidates on the firm's labelled evaluation set. | `ollama pull mxbai-embed-large` |\n\nStart with `embeddinggemma`; do not select a model from generic benchmark claims\nalone. Build a small, authorised evaluation set of known same-transaction,\nsame-business-process, and deliberately non-matching pairs. Compare precision\namong the top 10–20 results, false positives across similar account heads, and\nruntime/RAM on the actual firm workstation. Keep token-only matching enabled as\nan explainable fallback and record the selected model with every formal export.\n\nTo test a different model without overwriting the default index:\n\n```sh\nollama pull mxbai-embed-large\npython3 run.py embed-ledger --db demo/audit.db --model mxbai-embed-large\npython3 run.py similar --db demo/audit.db --model mxbai-embed-large --query \"manual year-end tax provision\"\n```\n\n## Supported GL fields\n\nHeaders are matched case-insensitively with common aliases. Required: entry ID,\nposting date, account code, and either signed amount or debit and credit.\nOptional fields include document date, description/narration, preparer/user,\nreference/document number, entity, and manual/system indicator. COA imports\nare supported through `import-coa` and enrich account labels only.\n\nCSV and ordinary first-sheet `.xlsx` exports are supported with the standard\nlibrary; no client data is uploaded or sent to a conversion service.\n\n## Controls and limitations\n\n- Every imported source file is copied into `evidence/` beside the engagement\n  database and is SHA-256 hashed; each entry retains source row identity.\n- Import validation separates rejected/missing data from risk cues.\n- Analysis is blocked until a reviewer acknowledges the accepted population and\n  control totals.\n- The statistical suite includes deterministic tests, account-peer robust\n  outliers, Benford population checks, reversal matching, and an optional local\n  isolation-style model for populations of at least 256 entries.\n- Risk scores are prioritisation cues. Reviewer dispositions and audit-log\n  records are append-only; no result is labelled fraud or an audit conclusion.\n\nThe controls are designed to support documentation under SA 230 and journal\nentry procedures under SA 240; the engagement team remains responsible for\naudit design, evidence evaluation, and conclusions.\n",
  "exit_code": 0
}
```

## Assistant

<thinking>


**Clarifying documentation completeness**
</thinking>

Not yet. It has a working quick start and semantic-search setup, but it lacks a full step-by-step guide for preparing GL files, validating imports, handling rejected rows, reviewing exceptions, recording dispositions, exporting workpapers, and troubleshooting.

The detailed workflow exists in [IMPLEMENTATION_PLAN.md](/Users/Mitesh%20Gada/Documents/Projects/audit-analytics/IMPLEMENTATION_PLAN.md), but should be distilled into the README as a practical “First engagement” guide.

## User

take the project from mvp to full fledged utility and then add the instruction set.

## Assistant

<thinking>


**Planning full utility implementation**
</thinking>

I’ll turn the MVP into a usable engagement workflow: stronger import/reconciliation controls, saved mappings, methodology/run reporting, review governance, safer local UI, richer workpaper exports, semantic-search review tooling, and a genuinely step-by-step README. I’ll keep it local-first and clearly label the remaining enterprise deployment boundary rather than pretending a localhost tool is production SaaS.

**Tool Call: find . -maxdepth 3 -type f -not -path '*/__pycache__/*' -print | sort && PYTHONPATH=src python3 -m unittest discover -s tests -v**
Status: Completed

Terminal:
```
test_import_requires_acknowledgement_then_creates_traceable_exception (test_pipeline.PipelineTest.test_import_requires_acknowledgement_then_creates_traceable_exception) ... ok
test_token_classes_and_similarity_work_without_a_model_service (test_semantic.SemanticTest.test_token_classes_and_similarity_work_without_a_model_service) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.114s

OK

```


## Assistant

<thinking>


**Listing potential feature implementations**

**Planning ledger grouping and UI security improvements**

**Implementing UI escaping with patched string**
</thinking>

<thinking>


**Designing user roles and initialization flow**

**Implementing user role validation and mapping management**
</thinking>

<thinking>


**Clarifying reconciliation and sampling methods**

**Planning sample selection and reporting modules**
</thinking>

**Tool Call: Editing files**
Status: Completed

Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/src/audit_analytics/store.py
```
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path


SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS engagement (
  id INTEGER PRIMARY KEY CHECK(id=1), client TEXT NOT NULL, period_start TEXT NOT NULL,
  period_end TEXT NOT NULL, created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS imports (
  id INTEGER PRIMARY KEY, kind TEXT NOT NULL, original_name TEXT NOT NULL,
  evidence_path TEXT NOT NULL, sha256 TEXT NOT NULL, imported_at REAL NOT NULL,
  accepted_rows INTEGER NOT NULL, rejected_rows INTEGER NOT NULL, control_debits REAL,
  control_credits REAL, acknowledged_at REAL, acknowledged_by TEXT, acknowledgement_note TEXT
);
CREATE TABLE IF NOT EXISTS users (
  username TEXT PRIMARY KEY, role TEXT NOT NULL CHECK(role IN ('preparer','reviewer','manager','partner','quality_reviewer','read_only')),
  active INTEGER NOT NULL DEFAULT 1, created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY, value_json TEXT NOT NULL, updated_at REAL NOT NULL, updated_by TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS import_mappings (
  name TEXT PRIMARY KEY, mapping_json TEXT NOT NULL, created_at REAL NOT NULL, created_by TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS coa (
  account_code TEXT PRIMARY KEY, account_name TEXT, account_type TEXT, import_id INTEGER REFERENCES imports(id)
);
CREATE TABLE IF NOT EXISTS ledger_entries (
  id INTEGER PRIMARY KEY, import_id INTEGER NOT NULL REFERENCES imports(id), entry_id TEXT NOT NULL,
  posting_date TEXT NOT NULL, document_date TEXT, account_code TEXT NOT NULL, debit REAL NOT NULL,
  credit REAL NOT NULL, signed_amount REAL NOT NULL, description TEXT, preparer TEXT,
  reference TEXT, entity TEXT, is_manual INTEGER, source_row INTEGER NOT NULL,
  source_hash TEXT NOT NULL, raw_json TEXT NOT NULL, UNIQUE(import_id, source_row)
);
CREATE INDEX IF NOT EXISTS ledger_account_date ON ledger_entries(account_code, posting_date);
CREATE INDEX IF NOT EXISTS ledger_entry_id ON ledger_entries(entry_id);
CREATE TABLE IF NOT EXISTS rejected_rows (
  id INTEGER PRIMARY KEY, import_id INTEGER NOT NULL REFERENCES imports(id), source_row INTEGER NOT NULL,
  reason TEXT NOT NULL, raw_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS model_runs (
  id INTEGER PRIMARY KEY, started_at REAL NOT NULL, completed_at REAL, configuration TEXT NOT NULL,
  population_count INTEGER NOT NULL, status TEXT NOT NULL, limitation_note TEXT
);
CREATE TABLE IF NOT EXISTS exceptions (
  id INTEGER PRIMARY KEY, run_id INTEGER NOT NULL REFERENCES model_runs(id), ledger_id INTEGER NOT NULL REFERENCES ledger_entries(id),
  risk_score REAL NOT NULL, severity TEXT NOT NULL, reasons_json TEXT NOT NULL,
  evidence_json TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'open', UNIQUE(run_id, ledger_id)
);
CREATE TABLE IF NOT EXISTS reviews (
  id INTEGER PRIMARY KEY, exception_id INTEGER NOT NULL REFERENCES exceptions(id), reviewer TEXT NOT NULL,
  disposition TEXT NOT NULL, note TEXT NOT NULL, created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY, created_at REAL NOT NULL, actor TEXT NOT NULL, action TEXT NOT NULL,
  target_type TEXT NOT NULL, target_id TEXT NOT NULL, detail_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ledger_embeddings (
  ledger_id INTEGER NOT NULL REFERENCES ledger_entries(id), model TEXT NOT NULL,
  dims INTEGER NOT NULL, text_hash TEXT NOT NULL, vector BLOB NOT NULL,
  embedded_at REAL NOT NULL, PRIMARY KEY(ledger_id, model, dims)
);
CREATE INDEX IF NOT EXISTS ledger_embeddings_model ON ledger_embeddings(model, dims);
CREATE TABLE IF NOT EXISTS sample_sets (
  id INTEGER PRIMARY KEY, run_id INTEGER NOT NULL REFERENCES model_runs(id), name TEXT NOT NULL,
  method_json TEXT NOT NULL, created_at REAL NOT NULL, created_by TEXT NOT NULL, UNIQUE(run_id, name)
);
CREATE TABLE IF NOT EXISTS sample_items (
  sample_set_id INTEGER NOT NULL REFERENCES sample_sets(id), ledger_id INTEGER NOT NULL REFERENCES ledger_entries(id),
  rationale TEXT NOT NULL, PRIMARY KEY(sample_set_id, ledger_id)
);
"""


class Store:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript(SCHEMA)
        self._migrate()
        self.conn.commit()

    def _migrate(self):
        """Keep engagement databases additive as features are introduced."""
        migrations = [
            ("imports", "expected_rows", "INTEGER"), ("imports", "expected_debits", "REAL"),
            ("imports", "expected_credits", "REAL"), ("imports", "reconciled_at", "REAL"),
            ("imports", "reconciled_by", "TEXT"), ("imports", "reconciliation_note", "TEXT"),
            ("exceptions", "assigned_to", "TEXT"), ("exceptions", "due_date", "TEXT"),
        ]
        for table, column, definition in migrations:
            try: self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
            except sqlite3.OperationalError: pass

    def log(self, actor: str, action: str, target_type: str, target_id: str | int, detail: dict):
        self.conn.execute("INSERT INTO audit_log VALUES(NULL,?,?,?,?,?,?)",
                          (time.time(), actor, action, target_type, str(target_id), json.dumps(detail, sort_keys=True)))

    def engagement(self):
        return self.conn.execute("SELECT * FROM engagement WHERE id=1").fetchone()

    def set_setting(self, key: str, value, actor: str):
        self.conn.execute("INSERT INTO settings(key,value_json,updated_at,updated_by) VALUES(?,?,?,?) ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json,updated_at=excluded.updated_at,updated_by=excluded.updated_by", (key, json.dumps(value), time.time(), actor))

    def get_setting(self, key: str, default=None):
        row = self.conn.execute("SELECT value_json FROM settings WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else default

    def add_user(self, username: str, role: str, actor="system"):
        if role not in {"preparer", "reviewer", "manager", "partner", "quality_reviewer", "read_only"}: raise ValueError("invalid role")
        self.conn.execute("INSERT INTO users(username,role,active,created_at) VALUES(?,?,1,?) ON CONFLICT(username) DO UPDATE SET role=excluded.role,active=1", (username, role, time.time()))
        self.log(actor, "add_or_update_user", "user", username, {"role": role})

    def require_role(self, username: str, allowed: set[str]):
        row = self.conn.execute("SELECT role,active FROM users WHERE username=?", (username,)).fetchone()
        if not row or not row["active"]: raise ValueError(f"unknown or inactive user: {username}")
        if row["role"] not in allowed: raise ValueError(f"{username} has role {row['role']}; required: {', '.join(sorted(allowed))}")
        return row["role"]

    def reconciliation(self, import_id: int, tolerance=0.01):
        row = self.conn.execute("SELECT * FROM imports WHERE id=? AND kind='gl'", (import_id,)).fetchone()
        if not row: raise ValueError("GL import not found")
        supplied = all(row[k] is not None for k in ("expected_rows", "expected_debits", "expected_credits"))
        matches = supplied and row["accepted_rows"] == row["expected_rows"] and abs(row["control_debits"] - row["expected_debits"]) <= tolerance and abs(row["control_credits"] - row["expected_credits"]) <= tolerance
        return {"import_id": import_id, "supplied": supplied, "matches": matches, "accepted_rows": row["accepted_rows"], "expected_rows": row["expected_rows"], "control_debits": row["control_debits"], "expected_debits": row["expected_debits"], "control_credits": row["control_credits"], "expected_credits": row["expected_credits"], "reconciled_at": row["reconciled_at"]}

    def population_acknowledged(self):
        row = self.conn.execute("SELECT COUNT(*) FROM imports WHERE kind='gl' AND acknowledged_at IS NULL").fetchone()
        return row[0] == 0 and self.conn.execute("SELECT COUNT(*) FROM imports WHERE kind='gl'").fetchone()[0] > 0

    def close(self):
        self.conn.close()

```


## Assistant

<thinking>


**Planning importer enhancements and preview implementation**

**Designing preview function with mapping inference**
</thinking>

**Tool Call: Editing files**
Status: Completed

## Assistant

<thinking>


**Verifying SQL placeholders and planning reports**

**Designing configurable sampling thresholds**
</thinking>

**Tool Call: Editing files**
Status: Completed

Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/src/audit_analytics/reports.py
```
"""Portable workpaper exports and engagement status summaries."""
from __future__ import annotations

import csv
import html
import json
import time
from pathlib import Path

from .store import Store


def engagement_summary(store: Store):
    imports = [dict(r) for r in store.conn.execute("SELECT * FROM imports ORDER BY id")]
    return {
        "engagement": dict(store.engagement() or {}),
        "population_acknowledged": store.population_acknowledged(),
        "imports": [{**r, "reconciliation": store.reconciliation(r["id"]) if r["kind"] == "gl" else None} for r in imports],
        "entries": store.conn.execute("SELECT COUNT(*) FROM ledger_entries").fetchone()[0],
        "rejected_rows": store.conn.execute("SELECT COUNT(*) FROM rejected_rows").fetchone()[0],
        "latest_run": dict(store.conn.execute("SELECT * FROM model_runs ORDER BY id DESC LIMIT 1").fetchone() or {}),
        "exceptions": {r[0]: r[1] for r in store.conn.execute("SELECT severity,COUNT(*) FROM exceptions GROUP BY severity")},
        "review_status": {r[0]: r[1] for r in store.conn.execute("SELECT status,COUNT(*) FROM exceptions GROUP BY status")},
        "sample_sets": [dict(r) for r in store.conn.execute("SELECT * FROM sample_sets ORDER BY id DESC")],
        "settings": {r[0]: json.loads(r[1]) for r in store.conn.execute("SELECT key,value_json FROM settings ORDER BY key")},
    }


def _workpaper_rows(store: Store):
    return store.conn.execute("""WITH latest_review AS (
        SELECT r.*, ROW_NUMBER() OVER(PARTITION BY exception_id ORDER BY id DESC) n FROM reviews r
    ) SELECT e.id exception_id,e.run_id,e.risk_score,e.severity,e.status,e.assigned_to,e.due_date,
        l.entry_id,l.posting_date,l.document_date,l.account_code,c.account_name,l.debit,l.credit,l.signed_amount,
        l.description,l.preparer,l.reference,l.entity,l.is_manual,l.import_id,l.source_row,l.source_hash,
        e.reasons_json,e.evidence_json,lr.reviewer,lr.disposition,lr.note,lr.created_at review_at
        FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id LEFT JOIN coa c ON c.account_code=l.account_code
        LEFT JOIN latest_review lr ON lr.exception_id=e.id AND lr.n=1 ORDER BY e.risk_score DESC,e.id""").fetchall()


def export_workpaper(store: Store, out: str, actor="system"):
    destination = Path(out); destination.parent.mkdir(parents=True, exist_ok=True)
    rows = _workpaper_rows(store)
    fields = ["exception_id","run_id","risk_score","severity","status","assigned_to","due_date","entry_id","posting_date","document_date","account_code","account_name","debit","credit","signed_amount","description","preparer","reference","entity","is_manual","import_id","source_row","source_hash","reasons_json","evidence_json","reviewer","disposition","note","review_at"]
    with destination.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(dict(row) for row in rows)
    manifest = {"created_at": time.time(), "workpaper": str(destination), "summary": engagement_summary(store), "source_imports": [{k:r[k] for k in ("id","original_name","sha256","evidence_path")} for r in store.conn.execute("SELECT id,original_name,sha256,evidence_path FROM imports")], "exception_count": len(rows), "limitation": "Risk cues support auditor judgement; they are not findings, fraud determinations, or audit conclusions."}
    manifest_path = destination.with_suffix(destination.suffix + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    store.log(actor, "export_workpaper", "export", str(destination), {"manifest": str(manifest_path), "rows": len(rows)})
    store.conn.commit(); return destination, manifest_path, len(rows)


def write_engagement_report(store: Store, out: str, actor="system"):
    summary = engagement_summary(store); destination = Path(out); destination.parent.mkdir(parents=True, exist_ok=True)
    def cell(value): return html.escape(str(value if value is not None else "—"))
    import_rows = "".join(f"<tr><td>{cell(r['id'])}</td><td>{cell(r['original_name'])}</td><td>{cell(r['accepted_rows'])}</td><td>{cell(r['rejected_rows'])}</td><td>{cell((r['reconciliation'] or {}).get('matches'))}</td></tr>" for r in summary["imports"])
    exception_rows = "".join(f"<li>{cell(k)}: {cell(v)}</li>" for k,v in summary["exceptions"].items()) or "<li>None</li>"
    content = f"""<!doctype html><meta charset=utf-8><title>Audit analytics engagement report</title><style>body{{font:15px system-ui;margin:2rem;max-width:960px}}table{{border-collapse:collapse}}td,th{{border:1px solid #ccc;padding:.45rem}}</style><h1>Audit analytics engagement report</h1><p><strong>Client:</strong> {cell(summary['engagement'].get('client'))}<br><strong>Period:</strong> {cell(summary['engagement'].get('period_start'))} to {cell(summary['engagement'].get('period_end'))}</p><h2>Population and reconciliation</h2><p>Accepted ledger entries: {cell(summary['entries'])}; rejected rows: {cell(summary['rejected_rows'])}; population acknowledgement: {cell(summary['population_acknowledged'])}</p><table><tr><th>Import</th><th>File</th><th>Accepted</th><th>Rejected</th><th>Reconciled</th></tr>{import_rows}</table><h2>Analysis</h2><p>Latest run: {cell(summary['latest_run'].get('id'))}; population: {cell(summary['latest_run'].get('population_count'))}; status: {cell(summary['latest_run'].get('status'))}</p><ul>{exception_rows}</ul><h2>Limitations and conclusion boundary</h2><p>Outputs are risk-prioritisation cues only. The engagement team must evaluate evidence, determine audit procedures, document work performed, and reach conclusions under its approved methodology.</p>"""
    destination.write_text(content, encoding="utf-8")
    store.log(actor, "write_engagement_report", "report", str(destination), {"entries": summary["entries"]})
    store.conn.commit(); return destination

```


Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/src/audit_analytics/sampling.py
```
"""Reproducible risk-directed and random sample selection for review planning."""
from __future__ import annotations

import json
import random
import time

from .store import Store


def create_sample(store: Store, name: str, actor: str, run_id=None, risk_count=20, random_count=10, seed=1):
    run_id = run_id or store.conn.execute("SELECT id FROM model_runs WHERE status='complete' ORDER BY id DESC LIMIT 1").fetchone()
    if not run_id: raise ValueError("no completed analysis run")
    run_id = run_id[0] if not isinstance(run_id, int) else run_id
    if risk_count < 0 or random_count < 0: raise ValueError("sample counts must be non-negative")
    method = {"risk_count": risk_count, "random_count": random_count, "seed": seed, "run_id": run_id, "note": "Planning aid only; engagement team determines final sample and procedures."}
    cur = store.conn.execute("INSERT INTO sample_sets(run_id,name,method_json,created_at,created_by) VALUES(?,?,?,?,?)", (run_id, name, json.dumps(method, sort_keys=True), time.time(), actor))
    sample_id = cur.lastrowid; selected = set()
    # High risk is always retained. The risk-count cap applies to additional ranked cues.
    high = store.conn.execute("SELECT ledger_id FROM exceptions WHERE run_id=? AND severity='high' ORDER BY risk_score DESC,ledger_id", (run_id,)).fetchall()
    for row in high:
        selected.add(row[0]); store.conn.execute("INSERT INTO sample_items VALUES(?,?,?)", (sample_id, row[0], "high-risk exception"))
    ranked = store.conn.execute("SELECT ledger_id FROM exceptions WHERE run_id=? ORDER BY risk_score DESC,ledger_id", (run_id,)).fetchall()
    for row in ranked:
        if len(selected) >= len(high) + risk_count: break
        if row[0] not in selected:
            selected.add(row[0]); store.conn.execute("INSERT INTO sample_items VALUES(?,?,?)", (sample_id, row[0], "top ranked risk cue"))
    universe = [row[0] for row in store.conn.execute("SELECT id FROM ledger_entries ORDER BY id") if row[0] not in selected]
    rng = random.Random(seed)
    for ledger_id in rng.sample(universe, min(random_count, len(universe))):
        selected.add(ledger_id); store.conn.execute("INSERT INTO sample_items VALUES(?,?,?)", (sample_id, ledger_id, "seeded random coverage selection"))
    store.log(actor, "create_sample", "sample_set", sample_id, {**method, "selected": len(selected)})
    store.conn.commit(); return sample_id, len(selected)

```


## Assistant

<thinking>


**Identifying run_id handling bug**
</thinking>

**Tool Call: Editing files**
Status: Completed

Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/src/audit_analytics/analytics.py
```
from __future__ import annotations

import json
import math
import random
import statistics
import time
from collections import Counter, defaultdict
from datetime import date, timedelta

from .store import Store


def _median_mad(values):
    median = statistics.median(values)
    mad = statistics.median([abs(x - median) for x in values])
    return median, mad

def _benford(entries):
    numbers = [abs(e["signed_amount"]) for e in entries if abs(e["signed_amount"]) >= 1]
    if len(numbers) < 100: return {"applicable": False, "n": len(numbers), "reason": "requires at least 100 non-zero amounts"}
    observed = Counter(str(int(x)).lstrip("0")[0] for x in numbers if str(int(x)).lstrip("0"))
    expected = {str(i): math.log10(1 + 1 / i) for i in range(1, 10)}
    mad = sum(abs(observed[str(i)] / len(numbers) - expected[str(i)]) for i in range(1, 10)) / 9
    return {"applicable": True, "n": len(numbers), "mad": round(mad, 4), "flag": mad > 0.015,
            "note": "Population-level indicator only; it does not identify fraudulent entries."}

def _isolation_scores(entries, trees=40, seed=7):
    """Small deterministic isolation-style scorer; retains all data locally.

    ponytail: this is a compact random-cut forest, not a replacement for a
    governed ML platform; upgrade to a validated model registry when needed.
    """
    if len(entries) < 256: return {}
    amounts = [math.log1p(abs(e["signed_amount"])) for e in entries]
    account_counts, user_counts = Counter(e["account_code"] for e in entries), Counter(e["preparer"] or "" for e in entries)
    points = [(amounts[i], -math.log(account_counts[e["account_code"]] / len(entries)), -math.log(user_counts[e["preparer"] or ""] / len(entries))) for i, e in enumerate(entries)]
    rng = random.Random(seed); depths = [0.0] * len(entries)
    for _ in range(trees):
        active = list(range(len(entries))); depth = [0] * len(entries)
        while len(active) > 1:
            dim = rng.randrange(3); vals = [points[i][dim] for i in active]; lo, hi = min(vals), max(vals)
            if lo == hi: break
            cut = rng.uniform(lo, hi); left = [i for i in active if points[i][dim] < cut]; right = [i for i in active if points[i][dim] >= cut]
            if not left or not right: break
            for i in active: depth[i] += 1
            # Recursively isolate the smaller partition first; one cut per tree level keeps runtime bounded.
            active = left if len(left) <= len(right) else right
        for i in range(len(entries)): depths[i] += depth[i]
    max_depth = max(depths) or 1
    return {entries[i]["id"]: round(1 - depths[i] / max_depth, 3) for i in range(len(entries))}

def analyze(store: Store, actor="system", include_isolation=True):
    if not store.population_acknowledged(): raise ValueError("analysis blocked: acknowledge every GL import's accepted population and control totals first")
    entries = [dict(r) for r in store.conn.execute("SELECT * FROM ledger_entries ORDER BY id")]
    if not entries: raise ValueError("no GL entries imported")
    policy = store.get_setting("analysis_policy", {"round_amount_threshold": 1000, "period_end_days": 3, "outlier_robust_z": 3.5})
    cfg = {"tests": ["duplicate", "round_amount", "period_end", "weekend", "rare_account_user", "reversal", "robust_peer_outlier", "benford"], "isolation": include_isolation and len(entries) >= 256, "policy": policy, "materiality": store.get_setting("materiality", {})}
    run = store.conn.execute("INSERT INTO model_runs(started_at,configuration,population_count,status) VALUES(?,?,?,?)", (time.time(), json.dumps(cfg), len(entries), "running")).lastrowid
    reasons, evidence = defaultdict(list), defaultdict(dict)
    by_key = defaultdict(list); by_account = defaultdict(list); by_user_pair = Counter(); ref_key = defaultdict(list)
    for e in entries:
        amount = round(abs(e["signed_amount"]), 2); by_account[e["account_code"]].append(e)
        by_user_pair[(e["account_code"], e["preparer"] or "")]+=1
        if e["reference"]: by_key[(e["account_code"], e["reference"], amount)].append(e)
        by_key[(e["account_code"], e["posting_date"], amount, e["description"] or "")].append(e)
        ref_key[(e["account_code"], amount)].append(e)
    for group in by_key.values():
        if len(group) > 1:
            for e in group: reasons[e["id"]].append("duplicate_or_repeated_entry"); evidence[e["id"]]["duplicate_count"] = len(group)
    end = date.fromisoformat(store.engagement()["period_end"])
    for e in entries:
        eid, amount = e["id"], abs(e["signed_amount"]); posted = date.fromisoformat(e["posting_date"])
        threshold = float(policy.get("round_amount_threshold", 1000))
        if amount and amount >= threshold and amount % 1000 == 0: reasons[eid].append("round_amount")
        if posted >= end - timedelta(days=int(policy.get("period_end_days", 3))): reasons[eid].append("period_end_posting")
        if posted.weekday() >= 5: reasons[eid].append("weekend_posting")
        if by_user_pair[(e["account_code"], e["preparer"] or "")] <= 2: reasons[eid].append("rare_account_preparer_pair")
        peer = [abs(x["signed_amount"]) for x in by_account[e["account_code"]]]
        if len(peer) >= 8:
            med, mad = _median_mad(peer)
            if mad and abs(amount-med)/(1.4826*mad) >= float(policy.get("outlier_robust_z", 3.5)):
                reasons[eid].append("robust_account_peer_outlier"); evidence[eid]["peer_median"] = round(med, 2); evidence[eid]["robust_z"] = round(abs(amount-med)/(1.4826*mad), 2)
        for other in ref_key[(e["account_code"], round(amount, 2))]:
            if other["id"] != eid and other["signed_amount"] * e["signed_amount"] < 0 and abs((date.fromisoformat(other["posting_date"])-posted).days) <= 30:
                reasons[eid].append("possible_reversal_within_30_days"); evidence[eid]["reversal_ledger_id"] = other["id"]; break
    benford = _benford(entries)
    if benford["applicable"] and benford["flag"]:
        for e in entries: evidence[e["id"]]["benford_population_indicator"] = benford
    isolation = _isolation_scores(entries) if cfg["isolation"] else {}
    for e in entries:
        iso = isolation.get(e["id"], 0)
        if iso >= 0.72: reasons[e["id"]].append("isolation_style_anomaly"); evidence[e["id"]]["isolation_score"] = iso
        if not reasons[e["id"]]: continue
        score = min(100, 20 * len(set(reasons[e["id"]])) + (15 if evidence[e["id"]].get("robust_z", 0) >= 5 else 0) + (15 if iso >= .85 else 0))
        severity = "high" if score >= 70 else "medium" if score >= 40 else "low"
        store.conn.execute("INSERT INTO exceptions(run_id,ledger_id,risk_score,severity,reasons_json,evidence_json) VALUES(?,?,?,?,?,?)", (run, e["id"], score, severity, json.dumps(sorted(set(reasons[e["id"]]))), json.dumps(evidence[e["id"]], sort_keys=True)))
    limitation = "Benford: " + (benford.get("note") or benford.get("reason", "not applicable"))
    store.conn.execute("UPDATE model_runs SET completed_at=?,status='complete',limitation_note=? WHERE id=?", (time.time(), limitation, run))
    store.log(actor, "analyze", "model_run", run, {"population": len(entries), "benford": benford, "isolation_enabled": bool(isolation)})
    store.conn.commit(); return run

```


## Assistant

<thinking>


**Planning CLI commands and error handling**

**Defining CLI role permissions and patch strategy**

**Enhancing CLI error handling and JSON output**
</thinking>

<thinking>


**Refining actor argument handling**
</thinking>

<thinking>


**Planning file update with patch strategy**
</thinking>

**Tool Call: Editing files**
Status: Completed

Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/src/audit_analytics/cli.py
```

```


## Assistant

<thinking>


**Adding new file**
</thinking>

**Tool Call: Editing files**
Status: Completed

Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/src/audit_analytics/cli.py
```
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analytics import analyze
from .importer import import_coa, import_gl, preview_gl
from .reports import engagement_summary, export_workpaper, write_engagement_report
from .sampling import create_sample
from .semantic import embed_ledger, similar_transactions
from .server import serve
from .store import Store

DEFAULT_ACTOR = "engagement-owner"


def _mapping(args, store):
    if getattr(args, "mapping", None):
        return json.loads(Path(args.mapping).read_text(encoding="utf-8"))
    if getattr(args, "mapping_name", None):
        row = store.conn.execute("SELECT mapping_json FROM import_mappings WHERE name=?", (args.mapping_name,)).fetchone()
        if not row:
            raise ValueError(f"mapping profile not found: {args.mapping_name}")
        return json.loads(row[0])
    return None


def _require(store, actor, roles):
    store.require_role(actor, set(roles))


def main():
    p = argparse.ArgumentParser(description="Local-first journal-entry audit analytics")
    sub = p.add_subparsers(dest="cmd", required=True)
    init = sub.add_parser("init", help="create an isolated engagement")
    init.add_argument("--db", required=True); init.add_argument("--client", required=True)
    init.add_argument("--period", required=True, help="YYYY-MM-DD:YYYY-MM-DD")
    init.add_argument("--owner", default=DEFAULT_ACTOR)

    for name in ("import-gl", "import-coa"):
        command = sub.add_parser(name)
        command.add_argument("--db", required=True); command.add_argument("--file", required=True)
        command.add_argument("--actor", default=DEFAULT_ACTOR)
    gl = sub.choices["import-gl"]
    gl.add_argument("--mapping", help="JSON canonical-field to source-header mapping")
    gl.add_argument("--mapping-name")
    gl.add_argument("--expected-rows", type=int); gl.add_argument("--expected-debits", type=float)
    gl.add_argument("--expected-credits", type=float)

    preview = sub.add_parser("preview-gl", help="inspect detected source headers before import")
    preview.add_argument("--db", required=True); preview.add_argument("--file", required=True)
    preview.add_argument("--mapping")
    save_mapping = sub.add_parser("save-mapping", help="save a reviewed mapping profile")
    save_mapping.add_argument("--db", required=True); save_mapping.add_argument("--name", required=True)
    save_mapping.add_argument("--mapping", required=True); save_mapping.add_argument("--actor", default=DEFAULT_ACTOR)
    list_mappings = sub.add_parser("list-mappings"); list_mappings.add_argument("--db", required=True)

    ack = sub.add_parser("acknowledge-population", help="record reconciliation and unlock analysis")
    ack.add_argument("--db", required=True); ack.add_argument("--reviewer", required=True); ack.add_argument("--note", required=True)
    ack.add_argument("--override-reconciliation", action="store_true", help="requires a note explaining a known difference")

    configure = sub.add_parser("configure", help="set engagement methodology thresholds")
    configure.add_argument("--db", required=True); configure.add_argument("--actor", default=DEFAULT_ACTOR)
    configure.add_argument("--materiality", type=float); configure.add_argument("--performance-materiality", type=float)
    configure.add_argument("--round-amount-threshold", type=float); configure.add_argument("--period-end-days", type=int)
    configure.add_argument("--outlier-robust-z", type=float)
    user = sub.add_parser("add-user", help="add/update a local workflow user")
    user.add_argument("--db", required=True); user.add_argument("--username", required=True); user.add_argument("--role", required=True); user.add_argument("--actor", default=DEFAULT_ACTOR)

    analyze_cmd = sub.add_parser("analyze"); analyze_cmd.add_argument("--db", required=True)
    analyze_cmd.add_argument("--actor", default=DEFAULT_ACTOR); analyze_cmd.add_argument("--no-isolation", action="store_true")
    embed = sub.add_parser("embed-ledger", help="create local Ollama vectors; no data leaves this host")
    embed.add_argument("--db", required=True); embed.add_argument("--model", default="embeddinggemma")
    embed.add_argument("--batch-size", type=int, default=64); embed.add_argument("--actor", default=DEFAULT_ACTOR)
    similar = sub.add_parser("similar", help="find semantically and token-similar transactions")
    similar.add_argument("--db", required=True); similar.add_argument("--query", required=True)
    similar.add_argument("--limit", type=int, default=25); similar.add_argument("--model", default="embeddinggemma")

    review = sub.add_parser("review", help="record a reviewer disposition")
    review.add_argument("--db", required=True); review.add_argument("--exception", type=int, required=True)
    review.add_argument("--reviewer", required=True); review.add_argument("--disposition", choices=("open", "cleared", "follow_up", "selected_for_testing"), required=True); review.add_argument("--note", required=True)
    assign = sub.add_parser("assign", help="assign an exception for review")
    assign.add_argument("--db", required=True); assign.add_argument("--exception", type=int, required=True)
    assign.add_argument("--assignee", required=True); assign.add_argument("--due-date"); assign.add_argument("--actor", default=DEFAULT_ACTOR)
    sample = sub.add_parser("create-sample", help="create a reproducible risk and random coverage sample")
    sample.add_argument("--db", required=True); sample.add_argument("--name", required=True); sample.add_argument("--run", type=int)
    sample.add_argument("--risk-count", type=int, default=20); sample.add_argument("--random-count", type=int, default=10)
    sample.add_argument("--seed", type=int, default=1); sample.add_argument("--actor", default=DEFAULT_ACTOR)
    export = sub.add_parser("export", help="export exception workpaper plus evidence manifest")
    export.add_argument("--db", required=True); export.add_argument("--out", required=True); export.add_argument("--actor", default=DEFAULT_ACTOR)
    report = sub.add_parser("report", help="write an HTML engagement summary")
    report.add_argument("--db", required=True); report.add_argument("--out", required=True); report.add_argument("--actor", default=DEFAULT_ACTOR)
    status = sub.add_parser("status", help="show engagement, reconciliation, analysis, and review state"); status.add_argument("--db", required=True)
    serve_cmd = sub.add_parser("serve"); serve_cmd.add_argument("--db", required=True); serve_cmd.add_argument("--port", type=int, default=8788)

    args = p.parse_args(); store = Store(args.db)
    try:
        if args.cmd == "init":
            start, end = args.period.split(":", 1)
            store.conn.execute("INSERT INTO engagement VALUES(1,?,?,?,strftime('%s','now'))", (args.client, start, end))
            store.add_user(args.owner, "manager", "system")
            store.set_setting("analysis_policy", {"round_amount_threshold": 1000, "period_end_days": 3, "outlier_robust_z": 3.5}, args.owner)
            store.set_setting("materiality", {}, args.owner)
            store.log(args.owner, "init", "engagement", 1, {"client": args.client}); store.conn.commit()
            print(f"created engagement for {args.client}; owner={args.owner}")
        elif args.cmd == "preview-gl":
            print(json.dumps(preview_gl(args.file, _mapping(args, store)), indent=2, default=str))
        elif args.cmd == "save-mapping":
            _require(store, args.actor, ("manager", "partner")); mapping = json.loads(Path(args.mapping).read_text(encoding="utf-8"))
            store.conn.execute("INSERT INTO import_mappings VALUES(?,?,strftime('%s','now'),?) ON CONFLICT(name) DO UPDATE SET mapping_json=excluded.mapping_json,created_at=excluded.created_at,created_by=excluded.created_by", (args.name, json.dumps(mapping, sort_keys=True), args.actor))
            store.log(args.actor, "save_mapping", "mapping", args.name, mapping); store.conn.commit(); print(f"saved mapping profile {args.name}")
        elif args.cmd == "list-mappings":
            print(json.dumps([dict(r) for r in store.conn.execute("SELECT name,created_at,created_by FROM import_mappings ORDER BY name")], indent=2))
        elif args.cmd == "import-gl":
            _require(store, args.actor, ("preparer", "reviewer", "manager", "partner"))
            iid, accepted, rejected, debits, credits = import_gl(store, args.file, args.actor, _mapping(args, store), args.expected_rows, args.expected_debits, args.expected_credits)
            print(json.dumps({"import_id": iid, "accepted": accepted, "rejected": rejected, "debits": debits, "credits": credits, "reconciliation": store.reconciliation(iid)}, indent=2))
        elif args.cmd == "import-coa":
            _require(store, args.actor, ("preparer", "reviewer", "manager", "partner")); print(f"COA import {import_coa(store, args.file, args.actor)} complete")
        elif args.cmd == "acknowledge-population":
            _require(store, args.reviewer, ("reviewer", "manager", "partner", "quality_reviewer"))
            pending = store.conn.execute("SELECT id FROM imports WHERE kind='gl' AND acknowledged_at IS NULL").fetchall()
            if not pending: raise ValueError("no unacknowledged GL imports")
            for row in pending:
                rec = store.reconciliation(row["id"])
                if not rec["matches"] and not args.override_reconciliation:
                    raise ValueError(f"import {row['id']} has no matching supplied control totals; use --override-reconciliation only with a documented difference")
                store.conn.execute("UPDATE imports SET reconciled_at=strftime('%s','now'),reconciled_by=?,reconciliation_note=?,acknowledged_at=strftime('%s','now'),acknowledged_by=?,acknowledgement_note=? WHERE id=?", (args.reviewer, args.note, args.reviewer, args.note, row["id"]))
                store.log(args.reviewer, "acknowledge_population", "import", row["id"], {"reconciliation": rec, "override": args.override_reconciliation, "note": args.note})
            store.conn.commit(); print(f"acknowledged {len(pending)} reconciled GL import(s)")
        elif args.cmd == "configure":
            _require(store, args.actor, ("manager", "partner")); policy = store.get_setting("analysis_policy", {}); materiality = store.get_setting("materiality", {})
            for value, key in ((args.round_amount_threshold, "round_amount_threshold"), (args.period_end_days, "period_end_days"), (args.outlier_robust_z, "outlier_robust_z")):
                if value is not None: policy[key] = value
            if args.materiality is not None: materiality["overall"] = args.materiality
            if args.performance_materiality is not None: materiality["performance"] = args.performance_materiality
            store.set_setting("analysis_policy", policy, args.actor); store.set_setting("materiality", materiality, args.actor)
            store.log(args.actor, "configure", "engagement", 1, {"analysis_policy": policy, "materiality": materiality}); store.conn.commit(); print(json.dumps({"analysis_policy": policy, "materiality": materiality}, indent=2))
        elif args.cmd == "add-user":
            _require(store, args.actor, ("manager", "partner")); store.add_user(args.username, args.role, args.actor); store.conn.commit(); print(f"user {args.username} is {args.role}")
        elif args.cmd == "analyze":
            _require(store, args.actor, ("preparer", "reviewer", "manager", "partner")); print(f"analysis run {analyze(store, args.actor, not args.no_isolation)} complete")
        elif args.cmd == "embed-ledger":
            _require(store, args.actor, ("preparer", "reviewer", "manager", "partner")); print(f"embedded {embed_ledger(store, args.model, args.batch_size, args.actor)} changed ledger entries locally")
        elif args.cmd == "similar":
            rows = similar_transactions(store, args.query, args.limit, args.model); print(json.dumps({"query": args.query, "count": len(rows), "results": rows}, indent=2))
        elif args.cmd == "review":
            _require(store, args.reviewer, ("reviewer", "manager", "partner", "quality_reviewer"))
            if not store.conn.execute("SELECT 1 FROM exceptions WHERE id=?", (args.exception,)).fetchone(): raise ValueError("exception not found")
            review_id = store.conn.execute("INSERT INTO reviews(exception_id,reviewer,disposition,note,created_at) VALUES(?,?,?,?,strftime('%s','now'))", (args.exception, args.reviewer, args.disposition, args.note)).lastrowid
            store.conn.execute("UPDATE exceptions SET status=? WHERE id=?", (args.disposition, args.exception)); store.log(args.reviewer, "review_exception", "exception", args.exception, {"review_id": review_id, "disposition": args.disposition}); store.conn.commit(); print(f"recorded review {review_id}")
        elif args.cmd == "assign":
            _require(store, args.actor, ("manager", "partner")); store.require_role(args.assignee, {"preparer", "reviewer", "manager", "partner", "quality_reviewer"})
            if not store.conn.execute("UPDATE exceptions SET assigned_to=?,due_date=? WHERE id=?", (args.assignee, args.due_date, args.exception)).rowcount: raise ValueError("exception not found")
            store.log(args.actor, "assign_exception", "exception", args.exception, {"assignee": args.assignee, "due_date": args.due_date}); store.conn.commit(); print(f"assigned exception {args.exception} to {args.assignee}")
        elif args.cmd == "create-sample":
            _require(store, args.actor, ("reviewer", "manager", "partner", "quality_reviewer")); sample_id, count = create_sample(store, args.name, args.actor, args.run, args.risk_count, args.random_count, args.seed); print(f"sample set {sample_id}: {count} entries")
        elif args.cmd == "export":
            _require(store, args.actor, ("preparer", "reviewer", "manager", "partner", "quality_reviewer")); out, manifest, count = export_workpaper(store, args.out, args.actor); print(f"wrote {count} review cues to {out}; manifest={manifest}")
        elif args.cmd == "report":
            _require(store, args.actor, ("preparer", "reviewer", "manager", "partner", "quality_reviewer")); print(f"wrote engagement report to {write_engagement_report(store, args.out, args.actor)}")
        elif args.cmd == "status":
            print(json.dumps(engagement_summary(store), indent=2, default=str))
        else:
            serve(args.db, args.port)
    except (ValueError, json.JSONDecodeError) as exc:
        p.exit(2, f"error: {exc}\n")
    finally:
        store.close()

```


## Assistant

<thinking>


**Planning server API updates**

**Patching server for read-only mode**
</thinking>

**Tool Call: Editing files**
Status: Completed

Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/src/audit_analytics/server.py
```
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .store import Store
from .semantic import similar_transactions
from .reports import engagement_summary

PAGE = """<!doctype html><title>Audit Analytics Review</title><style>body{font:14px system-ui;margin:2rem;max-width:1200px}table{border-collapse:collapse;width:100%}th,td{border:1px solid #ddd;padding:.5rem;text-align:left}th{background:#f5f5f5}.high{color:#a00;font-weight:bold}.medium{color:#a60;font-weight:bold}textarea{width:100%;height:3rem}</style><h1>Journal-entry review</h1><p id=summary></p><table><thead><tr><th>Risk</th><th>Entry</th><th>Context</th><th>Reasons / evidence</th><th>Disposition</th></tr></thead><tbody id=rows></tbody></table><script>
async function load(){let x=await (await fetch('/api/exceptions')).json();document.querySelector('#summary').textContent=`${x.count} review cues · outputs support auditor judgement and are not conclusions.`;let body=document.querySelector('#rows');body.innerHTML=x.rows.map(r=>`<tr><td class="${r.severity}">${r.risk_score} (${r.severity})<br>${r.status}</td><td>${r.entry_id}<br>${r.posting_date}<br>${r.account_code}: ${r.signed_amount}</td><td>${r.description||''}<br>Preparer: ${r.preparer||'—'}<br>Ref: ${r.reference||'—'}</td><td>${r.reasons.join('<br>')}<hr><small>${JSON.stringify(r.evidence)}</small></td><td><select id=s${r.id}><option>open</option><option>cleared</option><option>follow_up</option><option>selected_for_testing</option></select><textarea id=n${r.id} placeholder="Audit rationale / evidence requested"></textarea><button onclick="review(${r.id})">Save</button></td></tr>`).join('')}
async function review(id){let reviewer=prompt('Reviewer name');if(!reviewer)return;let disposition=document.querySelector('#s'+id).value,note=document.querySelector('#n'+id).value;if(!note){alert('A review note is required');return}let r=await fetch('/api/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id,reviewer,disposition,note})});if(!r.ok)alert(await r.text());else load()}load();</script>"""

def serve(db_path: str, port=8788):
    class Handler(BaseHTTPRequestHandler):
        def _json(self, value, status=200):
            payload=json.dumps(value, default=str).encode(); self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(payload))); self.end_headers(); self.wfile.write(payload)
        def do_GET(self):
            if urlparse(self.path).path == "/":
                payload=PAGE.encode(); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(payload))); self.end_headers(); self.wfile.write(payload); return
            if urlparse(self.path).path == "/api/exceptions":
                s=Store(db_path)
                try:
                    rows=s.conn.execute("""SELECT e.*,l.entry_id,l.posting_date,l.account_code,l.signed_amount,l.description,l.preparer,l.reference
                    FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id ORDER BY e.risk_score DESC""").fetchall()
                    out=[]
                    for r in rows:
                        x=dict(r); x["reasons"]=json.loads(x.pop("reasons_json")); x["evidence"]=json.loads(x.pop("evidence_json")); out.append(x)
                    self._json({"count":len(out),"rows":out})
                finally: s.close()
                return
            if urlparse(self.path).path == "/api/status":
                s=Store(db_path)
                try: self._json(engagement_summary(s))
                finally: s.close()
                return
            if urlparse(self.path).path == "/api/users":
                s=Store(db_path)
                try: self._json([dict(row) for row in s.conn.execute("SELECT username,role FROM users WHERE active=1 ORDER BY username")])
                finally: s.close()
                return
            if urlparse(self.path).path == "/api/similar":
                parsed = urlparse(self.path); query = parse_qs(parsed.query).get("q", [""])[0]
                try:
                    s=Store(db_path)
                    try: self._json({"query":query,"results":similar_transactions(s,query)})
                    finally: s.close()
                except ValueError as e: self._json({"error":str(e)},400)
                return
            self._json({"error":"not found"},404)
        def do_POST(self):
            if urlparse(self.path).path != "/api/review": self._json({"error":"not found"},404); return
            try:
                data=json.loads(self.rfile.read(int(self.headers.get("Content-Length","0"))))
                if not all(isinstance(data.get(k),str) and data[k].strip() for k in ("reviewer","disposition","note")): raise ValueError("reviewer, disposition, and note are required")
                if data["disposition"] not in {"open","cleared","follow_up","selected_for_testing"}: raise ValueError("invalid disposition")
                s=Store(db_path)
                try:
                    s.require_role(data["reviewer"].strip(), {"reviewer", "manager", "partner", "quality_reviewer"})
                    exists=s.conn.execute("SELECT 1 FROM exceptions WHERE id=?",(data.get("id"),)).fetchone()
                    if not exists: raise ValueError("exception not found")
                    cur=s.conn.execute("INSERT INTO reviews(exception_id,reviewer,disposition,note,created_at) VALUES(?,?,?,?,strftime('%s','now'))",(data["id"],data["reviewer"].strip(),data["disposition"],data["note"].strip()))
                    s.conn.execute("UPDATE exceptions SET status=? WHERE id=?",(data["disposition"],data["id"])); s.log(data["reviewer"],"review_exception","exception",data["id"],{"review_id":cur.lastrowid,"disposition":data["disposition"]}); s.conn.commit()
                finally: s.close()
                self._json({"ok":True})
            except (ValueError, json.JSONDecodeError) as e: self._json({"error":str(e)},400)
        def log_message(self,*args): pass
    print(f"Audit review UI: http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1",port),Handler).serve_forever()

```


## Assistant

<thinking>


**Planning dashboard UI and schema tests**
</thinking>

The workflow is now expanding beyond analysis into governed engagement operations: explicit population reconciliation, local roles, configurable methodology, reproducible sampling, assignment/review history, and manifest-backed workpaper exports. I’m running the existing tests now before adding the user guide and end-to-end coverage.

**Tool Call: python3 -m py_compile run.py src/audit_analytics/*.py && PYTHONPATH=src python3 -m unittest discover -s tests -v && python3 run.py --help**
Status: Completed

Terminal:
```
test_import_requires_acknowledgement_then_creates_traceable_exception (test_pipeline.PipelineTest.test_import_requires_acknowledgement_then_creates_traceable_exception) ... ok
test_token_classes_and_similarity_work_without_a_model_service (test_semantic.SemanticTest.test_token_classes_and_similarity_work_without_a_model_service) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.247s

OK
usage: run.py [-h]
              {init,import-gl,import-coa,preview-gl,save-mapping,list-mappings,acknowledge-population,configure,add-user,analyze,embed-ledger,similar,review,assign,create-sample,export,report,status,serve}
              ...

Local-first journal-entry audit analytics

positional arguments:
  {init,import-gl,import-coa,preview-gl,save-mapping,list-mappings,acknowledge-population,configure,add-user,analyze,embed-ledger,similar,review,assign,create-sample,export,report,status,serve}
    init                create an isolated engagement
    preview-gl          inspect detected source headers before import
    save-mapping        save a reviewed mapping profile
    acknowledge-population
                        record reconciliation and unlock analysis
    configure           set engagement methodology thresholds
    add-user            add/update a local workflow user
    embed-ledger        create local Ollama vectors; no data leaves this host
    similar             find semantically and token-similar transactions
    review              record a reviewer disposition
    assign              assign an exception for review
    create-sample       create a reproducible risk and random coverage sample
    export              export exception workpaper plus evidence manifest
    report              write an HTML engagement summary
    status              show engagement, reconciliation, analysis, and review
                        state

options:
  -h, --help            show this help message and exit

```


## Assistant

<thinking>


**Designing end-to-end CLI testing workflow**

**Configuring tests for import and export validation**
</thinking>

**Tool Call: Editing files**
Status: Completed

Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/tests/test_engagement_workflow.py
```
import csv
import tempfile
import unittest
from pathlib import Path

from audit_analytics.analytics import analyze
from audit_analytics.importer import import_gl, preview_gl
from audit_analytics.reports import engagement_summary, export_workpaper, write_engagement_report
from audit_analytics.sampling import create_sample
from audit_analytics.store import Store


class EngagementWorkflowTest(unittest.TestCase):
    def test_reconciled_import_to_exportable_review_workflow(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / "journal.csv"
            with source.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["Voucher Number", "Date", "GL Code", "Amount", "Narration", "User"])
                writer.writeheader()
                for i in range(12):
                    writer.writerow({"Voucher Number": f"V{i}", "Date": "31/03/2026" if i == 11 else "01/02/2026", "GL Code": "6000", "Amount": 1000 if i == 11 else 101 + i, "Narration": "year-end accrual", "User": "preparer"})
            preview = preview_gl(str(source))
            self.assertEqual(preview["missing_required"], [])
            store = Store(str(root / "engagement.db"))
            store.conn.execute("INSERT INTO engagement VALUES(1,'Client','2025-04-01','2026-03-31',0)")
            store.add_user("manager", "manager"); store.add_user("reviewer", "reviewer")
            store.set_setting("analysis_policy", {"round_amount_threshold": 1000, "period_end_days": 3, "outlier_robust_z": 3.5}, "manager")
            expected = sum([101 + i for i in range(11)] + [1000])
            import_id, accepted, rejected, _, _ = import_gl(store, str(source), "manager", expected_rows=12, expected_debits=expected, expected_credits=0)
            self.assertEqual((accepted, rejected), (12, 0)); self.assertTrue(store.reconciliation(import_id)["matches"])
            store.conn.execute("UPDATE imports SET acknowledged_at=1,reconciled_at=1,acknowledged_by='reviewer',reconciled_by='reviewer',acknowledgement_note='agreed',reconciliation_note='agreed' WHERE id=?", (import_id,)); store.conn.commit()
            run_id = analyze(store, "manager", include_isolation=False)
            sample_id, selected = create_sample(store, "planning sample", "reviewer", run_id, risk_count=2, random_count=2, seed=9)
            self.assertGreater(selected, 0); self.assertGreater(sample_id, 0)
            exception = store.conn.execute("SELECT id FROM exceptions ORDER BY risk_score DESC LIMIT 1").fetchone()[0]
            store.conn.execute("INSERT INTO reviews(exception_id,reviewer,disposition,note,created_at) VALUES(?,?,?,?,0)", (exception, "reviewer", "selected_for_testing", "client support requested")); store.conn.execute("UPDATE exceptions SET status='selected_for_testing' WHERE id=?", (exception,)); store.conn.commit()
            workpaper, manifest, count = export_workpaper(store, str(root / "workpaper.csv"), "manager")
            report = write_engagement_report(store, str(root / "report.html"), "manager")
            summary = engagement_summary(store)
            self.assertTrue(workpaper.exists()); self.assertTrue(manifest.exists()); self.assertTrue(report.exists())
            self.assertGreater(count, 0); self.assertTrue(summary["population_acknowledged"]); self.assertEqual(summary["imports"][0]["reconciliation"]["matches"], True)


if __name__ == "__main__":
    unittest.main()

```


**Tool Call: PYTHONPATH=src python3 -m unittest discover -s tests -v**
Status: Failed

Terminal:
```
test_reconciled_import_to_exportable_review_workflow (test_engagement_workflow.EngagementWorkflowTest.test_reconciled_import_to_exportable_review_workflow) ... FAIL
test_import_requires_acknowledgement_then_creates_traceable_exception (test_pipeline.PipelineTest.test_import_requires_acknowledgement_then_creates_traceable_exception) ... ok
test_token_classes_and_similarity_work_without_a_model_service (test_semantic.SemanticTest.test_token_classes_and_similarity_work_without_a_model_service) ... ok

======================================================================
FAIL: test_reconciled_import_to_exportable_review_workflow (test_engagement_workflow.EngagementWorkflowTest.test_reconciled_import_to_exportable_review_workflow)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/Mitesh Gada/Documents/Projects/audit-analytics/tests/test_engagement_workflow.py", line 23, in test_reconciled_import_to_exportable_review_workflow
    self.assertEqual(preview["missing_required"], [])
AssertionError: Lists differ: ['entry_id', 'account_code'] != []

First list contains 2 additional elements.
First extra element 0:
'entry_id'

- ['entry_id', 'account_code']
+ []

----------------------------------------------------------------------
Ran 3 tests in 0.188s

FAILED (failures=1)

```


## Assistant

<thinking>


**Fixing alias normalization to ignore underscores**
</thinking>

**Tool Call: Editing files**
Status: Completed

## Assistant

<thinking>


**Planning test execution**
</thinking>

**Tool Call: PYTHONPATH=src python3 -m unittest discover -s tests -v**
Status: Completed

Terminal:
```
test_reconciled_import_to_exportable_review_workflow (test_engagement_workflow.EngagementWorkflowTest.test_reconciled_import_to_exportable_review_workflow) ... ok
test_import_requires_acknowledgement_then_creates_traceable_exception (test_pipeline.PipelineTest.test_import_requires_acknowledgement_then_creates_traceable_exception) ... ok
test_token_classes_and_similarity_work_without_a_model_service (test_semantic.SemanticTest.test_token_classes_and_similarity_work_without_a_model_service) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.217s

OK

```


## Assistant

<thinking>


**Planning detailed README expansion**

**Outlining comprehensive step-by-step README**

**Updating README with override and user details**
</thinking>

**Tool Call: Editing files**
Status: Completed

Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/README.md
```
# Audit Analytics

Local-first journal-entry analytics for Indian statutory-audit teams. It ranks
explainable risk cues for auditor review; it does not make audit conclusions or
issue an opinion.

## Step-by-step: first engagement

This guide creates a separate local database for one client and one audit
period. Run commands from this directory. Nothing in this workflow uploads the
client ledger; the only optional service is Ollama running on the same machine.

### 1. Check prerequisites and choose an engagement folder

Python 3.10+ is sufficient for the core tool. No package installation is
required. Use a firm-approved encrypted local folder or private VPC volume and
keep one database per engagement:

```sh
cd audit-analytics
python3 run.py --help
mkdir -p engagements/example-ltd-fy26
```

Do not place the engagement database in a shared public folder. The database,
its neighbouring `evidence/` folder, exports, and backups contain client data.

### 2. Prepare the source extracts

Request a line-level GL extract and, where available, a COA extract. CSV or an
ordinary first-sheet XLSX export is accepted. Keep the received original file
unchanged; the application makes a hash-addressed evidence copy on import.

The GL needs these canonical concepts:

| Required concept | Common accepted headers |
| --- | --- |
| Entry identifier | `entry_id`, `journal_entry_id`, `voucher_no`, `voucher number`, `transaction_id` |
| Posting date | `posting_date`, `date`, `entry_date` |
| Account code | `account_code`, `account`, `gl_code`, `GL Code`, `ledger_code` |
| Amount | `amount`/`signed_amount`, or separate `debit` and `credit` columns |

Recommended fields are narration/description, preparer/user, reference or
document number, entity/cost centre, document date, and manual/system flag.
Use ISO dates (`YYYY-MM-DD`) where possible; `DD/MM/YYYY`, `DD-MM-YYYY`, and
`MM/DD/YYYY` are also accepted. Do not pre-filter “unimportant” accounts or
delete blank/malformed rows—those are population-quality evidence.

Before importing, obtain the client/source-system control totals: extracted row
count, total debit, and total credit. They are used to reconcile the accepted
population, not to infer a conclusion.

### 3. Create the engagement and local users

```sh
python3 run.py init \
  --db engagements/example-ltd-fy26/audit.db \
  --client "Example Ltd" \
  --period 2025-04-01:2026-03-31 \
  --owner engagement-manager

python3 run.py add-user --db engagements/example-ltd-fy26/audit.db \
  --actor engagement-manager --username audit-preparer --role preparer
python3 run.py add-user --db engagements/example-ltd-fy26/audit.db \
  --actor engagement-manager --username audit-reviewer --role reviewer
```

The owner starts as a local `manager`. Roles are workflow guardrails for this
local utility, not a substitute for firm SSO or access control on a shared
server. Use `manager`/`partner` for configuration and assignment;
`preparer`/`reviewer` for analytical work; and `quality_reviewer` for read and
review functions.

### 4. Preview and map the GL before import

Preview headers and the first few rows; do this before writing any engagement
data:

```sh
python3 run.py preview-gl --db engagements/example-ltd-fy26/audit.db \
  --file received/example_gl.csv
```

If `missing_required` is non-empty or an auto-detected field is wrong, create a
small JSON mapping. Values are the exact source headers:

```json
{
  "entry_id": "Voucher Number",
  "posting_date": "Posting Dt",
  "account_code": "GL Code",
  "amount": "Amount",
  "description": "Narration",
  "preparer": "Created By",
  "reference": "Document Number"
}
```

Save it as `engagements/example-ltd-fy26/gl-mapping.json`, validate with
`preview-gl --mapping ...`, then preserve the approved profile for repeat
imports:

```sh
python3 run.py save-mapping --db engagements/example-ltd-fy26/audit.db \
  --actor engagement-manager --name client-gl-v1 \
  --mapping engagements/example-ltd-fy26/gl-mapping.json
```

### 5. Import, inspect, and reconcile the population

Import the COA first if available, then the GL. Replace the example totals with
the actual totals received from the client/source system.

```sh
python3 run.py import-coa --db engagements/example-ltd-fy26/audit.db \
  --actor audit-preparer --file received/chart_of_accounts.csv

python3 run.py import-gl --db engagements/example-ltd-fy26/audit.db \
  --actor audit-preparer --file received/example_gl.csv \
  --mapping-name client-gl-v1 \
  --expected-rows 125430 \
  --expected-debits 987654321.50 \
  --expected-credits 987654321.50
```

Read the JSON response and confirm accepted rows, rejected rows, calculated
debits/credits, and `reconciliation.matches`. Investigate rejected rows and
mapping errors before proceeding. Check the current state at any time:

```sh
python3 run.py status --db engagements/example-ltd-fy26/audit.db
```

An exact reconciliation can be acknowledged by an authorised reviewer:

```sh
python3 run.py acknowledge-population --db engagements/example-ltd-fy26/audit.db \
  --reviewer audit-reviewer \
  --note "Accepted row count and debit/credit totals agreed to the client GL control report dated 2026-04-12."
```

If the source totals are genuinely unavailable or a known difference remains,
the reviewer must document why it is acceptable; use the override deliberately,
never as a shortcut:

```sh
python3 run.py acknowledge-population --db engagements/example-ltd-fy26/audit.db \
  --reviewer audit-reviewer --override-reconciliation \
  --note "Client control report excludes opening-balance conversion lines; 42-line difference is documented in WP A-12."
```

The application blocks analysis until every GL import is acknowledged.

### 6. Set engagement methodology parameters

The defaults are transparent, conservative starting points. The engagement
team—not the tool—must decide whether they fit the client and methodology.

```sh
python3 run.py configure --db engagements/example-ltd-fy26/audit.db \
  --actor engagement-manager \
  --materiality 500000 \
  --performance-materiality 350000 \
  --round-amount-threshold 100000 \
  --period-end-days 3 \
  --outlier-robust-z 3.5
```

Each analysis run captures these settings. A changed policy requires a new run;
old runs remain reproducible.

### 7. Run analysis and understand the output

```sh
python3 run.py analyze --db engagements/example-ltd-fy26/audit.db \
  --actor audit-preparer
```

The hybrid suite includes repeated-entry patterns, round amounts, weekend and
period-end postings, rare account/preparer pairs, potential reversals, robust
account-peer outliers, and Benford applicability checks. The optional local
isolation-style scorer runs only for populations of 256+ entries; disable it
with `--no-isolation` if it is outside the approved engagement methodology.

Each output is a risk cue with reasons and evidence. It is not a fraud finding,
an audit exception, or an audit opinion.

### 8. Review, assign, and disposition exceptions

Start the local UI:

```sh
python3 run.py serve --db engagements/example-ltd-fy26/audit.db
```

Open `http://127.0.0.1:8788`. Enter the name of a configured reviewer when
saving a disposition. The UI is intentionally bound to localhost. For a fully
documented command-line workflow:

```sh
python3 run.py assign --db engagements/example-ltd-fy26/audit.db \
  --actor engagement-manager --exception 17 \
  --assignee audit-reviewer --due-date 2026-04-20

python3 run.py review --db engagements/example-ltd-fy26/audit.db \
  --exception 17 --reviewer audit-reviewer \
  --disposition selected_for_testing \
  --note "Selected for vouching. Obtain approval, contract, invoice, and subsequent-payment evidence."
```

Permitted dispositions are `open`, `cleared`, `follow_up`, and
`selected_for_testing`. Every review creates a new immutable review record and
audit-log entry; it does not overwrite earlier reasoning.

### 9. Create a reproducible review sample

The sample tool includes all high-risk cues, then the requested top-ranked
cues, then a seed-controlled random coverage selection. It is a sampling aid;
the engagement team documents and approves the final audit sample.

```sh
python3 run.py create-sample --db engagements/example-ltd-fy26/audit.db \
  --actor audit-reviewer --name "FY26 JE testing selection" \
  --risk-count 30 --random-count 15 --seed 20260412
```

### 10. Export the workpaper package and back up the engagement

```sh
python3 run.py export --db engagements/example-ltd-fy26/audit.db \
  --actor audit-reviewer --out engagements/example-ltd-fy26/exports/je-review.csv

python3 run.py report --db engagements/example-ltd-fy26/audit.db \
  --actor audit-reviewer --out engagements/example-ltd-fy26/exports/engagement-report.html
```

`export` writes the review CSV and a companion JSON manifest listing source
imports, hashes, run state, and limitations. `report` produces a readable HTML
engagement summary. Archive the database, `evidence/` directory, exports, and
firm-prescribed workpapers together using the firm’s approved retention and
backup process.

## Local semantic transaction search

Token classification works immediately and labels account/narration concepts
such as cash/bank, revenue, payroll, tax, inventory, and intercompany. To add
meaning-level similarity without moving ledger data off the engagement host,
install and run Ollama locally, then build a local vector index:

```sh
ollama serve                 # in a separate terminal
ollama pull embeddinggemma
python3 run.py embed-ledger --db demo/audit.db
python3 run.py similar --db demo/audit.db --query "manual year-end tax provision" --limit 20
```

The `similar` command falls back to transparent token/account-head matching
when no vectors have been built. Once vectors exist, its final score is the
maximum of token and cosine similarity, so semantic matching can surface a
worded-differently transaction but cannot hide a strong lexical match. The API
equivalent is `GET /api/similar?q=manual%20year-end%20tax%20provision`.

### Recommended local embedding models

Use one approved model per engagement and rebuild that model's ledger index
before comparing results. Model choice changes retrieval candidates; it must be
recorded in the engagement methodology/workpaper, validated on representative
approved data, and never be used as an automatic conclusion.

| Model | Recommendation | Use it when | Command |
| --- | --- | --- | --- |
| `embeddinggemma` | **Default.** A compact multilingual embedding model suited to local retrieval, classification, and clustering. | Most engagements, especially where narrations include Indian-language or mixed-language terms, or workstation resources are limited. | `ollama pull embeddinggemma` |
| `nomic-embed-text` | Fast English-first comparison baseline with a large text context window. | Narrations and account heads are predominantly English and the firm wants a second retrieval benchmark. | `ollama pull nomic-embed-text` |
| `mxbai-embed-large` | Quality-focused alternative with a larger local resource footprint. | A controlled pilot shows that it retrieves materially better complex-transaction candidates on the firm's labelled evaluation set. | `ollama pull mxbai-embed-large` |

Start with `embeddinggemma`; do not select a model from generic benchmark claims
alone. Build a small, authorised evaluation set of known same-transaction,
same-business-process, and deliberately non-matching pairs. Compare precision
among the top 10–20 results, false positives across similar account heads, and
runtime/RAM on the actual firm workstation. Keep token-only matching enabled as
an explainable fallback and record the selected model with every formal export.

To test a different model without overwriting the default index:

```sh
ollama pull mxbai-embed-large
python3 run.py embed-ledger --db demo/audit.db --model mxbai-embed-large
python3 run.py similar --db demo/audit.db --model mxbai-embed-large --query "manual year-end tax provision"
```

## Supported GL fields

Headers are matched case-insensitively with common aliases. Required: entry ID,
posting date, account code, and either signed amount or debit and credit.
Optional fields include document date, description/narration, preparer/user,
reference/document number, entity, and manual/system indicator. COA imports
are supported through `import-coa` and enrich account labels only.

CSV and ordinary first-sheet `.xlsx` exports are supported with the standard
library; no client data is uploaded or sent to a conversion service.

## Controls and limitations

- Every imported source file is copied into `evidence/` beside the engagement
  database and is SHA-256 hashed; each entry retains source row identity.
- Import validation separates rejected/missing data from risk cues.
- Analysis is blocked until a reviewer acknowledges the accepted population and
  control totals.
- The statistical suite includes deterministic tests, account-peer robust
  outliers, Benford population checks, reversal matching, and an optional local
  isolation-style model for populations of at least 256 entries.
- Risk scores are prioritisation cues. Reviewer dispositions and audit-log
  records are append-only; no result is labelled fraud or an audit conclusion.

The controls are designed to support documentation under SA 230 and journal
entry procedures under SA 240; the engagement team remains responsible for
audit design, evidence evaluation, and conclusions.

```


## Assistant

<thinking>


**Planning UI semantic search and documentation updates**

**Designing escaped UI inputs and server patching**
</thinking>

**Tool Call: Editing files**
Status: Completed

Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/src/audit_analytics/server.py
```

```


**Tool Call: Editing files**
Status: Completed

Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/src/audit_analytics/server.py
```
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .reports import engagement_summary
from .semantic import similar_transactions
from .store import Store

PAGE = """<!doctype html><meta charset=utf-8><title>Audit Analytics Review</title>
<style>body{font:14px system-ui;margin:2rem;max-width:1300px;color:#18212b}table{border-collapse:collapse;width:100%;margin:.5rem 0 2rem}th,td{border:1px solid #d7dce2;padding:.55rem;text-align:left;vertical-align:top}th{background:#f2f5f8}.high{color:#a00;font-weight:700}.medium{color:#9a5b00;font-weight:700}textarea{width:100%;height:3.5rem}input,select,button{font:inherit;padding:.35rem;margin:.15rem}section{margin:1.5rem 0;padding:1rem;background:#fafbfc;border:1px solid #e0e5ea}.small{font-size:.85em;color:#506070}#semantic-results li{margin:.5rem 0}</style>
<h1>Journal-entry review</h1><p id=summary>Loading engagement state…</p>
<section><h2>Reviewer session</h2><label>Reviewer <input id=reviewer list=users placeholder="Select configured reviewer"></label><datalist id=users></datalist><span class=small>Local workflow role checks apply when a disposition is saved.</span></section>
<section><h2>Semantic transaction search</h2><label>Transaction type, narration, or account-head phrase <input id=query size=52 placeholder="manual year-end tax provision"></label><button onclick=searchSimilar()>Find similar transactions</button><p class=small>Token matching always runs. Local vector similarity is included only after an approved Ollama model has indexed the ledger.</p><ol id=semantic-results></ol></section>
<section><h2>Exception review queue</h2><table><thead><tr><th>Risk</th><th>Entry</th><th>Context</th><th>Reasons / evidence</th><th>Disposition</th></tr></thead><tbody id=rows></tbody></table></section>
<script>
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const options=(current)=>['open','cleared','follow_up','selected_for_testing'].map(v=>`<option ${v===current?'selected':''}>${v}</option>`).join('');
async function load(){let [queue,status,users]=await Promise.all([fetch('/api/exceptions').then(r=>r.json()),fetch('/api/status').then(r=>r.json()),fetch('/api/users').then(r=>r.json())]);let state=`${queue.count} review cues · ${status.entries} accepted entries · population acknowledgement: ${status.population_acknowledged?'yes':'NO'}`;document.querySelector('#summary').textContent=state;document.querySelector('#users').innerHTML=users.filter(u=>['reviewer','manager','partner','quality_reviewer'].includes(u.role)).map(u=>`<option value="${esc(u.username)}">${esc(u.role)}</option>`).join('');let body=document.querySelector('#rows');body.innerHTML=queue.rows.map(r=>`<tr><td class="${esc(r.severity)}">${esc(r.risk_score)} (${esc(r.severity)})<br>${esc(r.status)}${r.assigned_to?'<br>Assigned: '+esc(r.assigned_to):''}</td><td>${esc(r.entry_id)}<br>${esc(r.posting_date)}<br>${esc(r.account_code)}: ${esc(r.signed_amount)}</td><td>${esc(r.description)}<br>Preparer: ${esc(r.preparer||'—')}<br>Ref: ${esc(r.reference||'—')}</td><td>${r.reasons.map(esc).join('<br>')}<hr><small>${esc(JSON.stringify(r.evidence))}</small></td><td><select id=s${r.id}>${options(r.status)}</select><textarea id=n${r.id} placeholder="Audit rationale / evidence requested"></textarea><button onclick="review(${r.id})">Save</button></td></tr>`).join('')}
async function review(id){let reviewer=document.querySelector('#reviewer').value.trim();let disposition=document.querySelector('#s'+id).value,note=document.querySelector('#n'+id).value.trim();if(!reviewer){alert('Enter a configured reviewer');return}if(!note){alert('A review note is required');return}let r=await fetch('/api/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id,reviewer,disposition,note})});let body=await r.json();if(!r.ok)alert(body.error||'Could not save review');else load()}
async function searchSimilar(){let q=document.querySelector('#query').value.trim();if(!q)return;let r=await fetch('/api/similar?q='+encodeURIComponent(q)),data=await r.json();let out=document.querySelector('#semantic-results');if(!r.ok){out.innerHTML='<li>'+esc(data.error||'Search failed')+'</li>';return}out.innerHTML=data.results.map(x=>`<li><strong>${esc(x.score)}</strong> · ${esc(x.entry_id)} · ${esc(x.account_code)} · ${esc(x.description)}<br><span class=small>token ${esc(x.token_score)}; semantic ${esc(x.semantic_score??'not indexed')}; shared: ${esc(x.shared_tokens.join(', ')||'—')}; classes: ${esc(x.token_classes.join(', ')||'—')}</span></li>`).join('')||'<li>No matching candidates.</li>'}
load();</script>"""


def serve(db_path: str, port=8788):
    class Handler(BaseHTTPRequestHandler):
        def _json(self, value, status=200):
            payload = json.dumps(value, default=str).encode()
            self.send_response(status); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload))); self.end_headers(); self.wfile.write(payload)

        def do_GET(self):
            path = urlparse(self.path)
            if path.path == "/":
                payload = PAGE.encode(); self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(payload))); self.end_headers(); self.wfile.write(payload); return
            if path.path == "/api/exceptions":
                s = Store(db_path)
                try:
                    rows = s.conn.execute("""SELECT e.*,l.entry_id,l.posting_date,l.account_code,l.signed_amount,l.description,l.preparer,l.reference
                    FROM exceptions e JOIN ledger_entries l ON l.id=e.ledger_id ORDER BY e.risk_score DESC""").fetchall()
                    out = []
                    for row in rows:
                        item = dict(row); item["reasons"] = json.loads(item.pop("reasons_json")); item["evidence"] = json.loads(item.pop("evidence_json")); out.append(item)
                    self._json({"count": len(out), "rows": out})
                finally: s.close()
                return
            if path.path == "/api/status":
                s = Store(db_path)
                try: self._json(engagement_summary(s))
                finally: s.close()
                return
            if path.path == "/api/users":
                s = Store(db_path)
                try: self._json([dict(row) for row in s.conn.execute("SELECT username,role FROM users WHERE active=1 ORDER BY username")])
                finally: s.close()
                return
            if path.path == "/api/similar":
                query = parse_qs(path.query).get("q", [""])[0]
                try:
                    s = Store(db_path)
                    try: self._json({"query": query, "results": similar_transactions(s, query)})
                    finally: s.close()
                except ValueError as exc: self._json({"error": str(exc)}, 400)
                return
            self._json({"error": "not found"}, 404)

        def do_POST(self):
            if urlparse(self.path).path != "/api/review": self._json({"error": "not found"}, 404); return
            try:
                data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
                if not all(isinstance(data.get(key), str) and data[key].strip() for key in ("reviewer", "disposition", "note")): raise ValueError("reviewer, disposition, and note are required")
                if data["disposition"] not in {"open", "cleared", "follow_up", "selected_for_testing"}: raise ValueError("invalid disposition")
                s = Store(db_path)
                try:
                    s.require_role(data["reviewer"].strip(), {"reviewer", "manager", "partner", "quality_reviewer"})
                    if not s.conn.execute("SELECT 1 FROM exceptions WHERE id=?", (data.get("id"),)).fetchone(): raise ValueError("exception not found")
                    review_id = s.conn.execute("INSERT INTO reviews(exception_id,reviewer,disposition,note,created_at) VALUES(?,?,?,?,strftime('%s','now'))", (data["id"], data["reviewer"].strip(), data["disposition"], data["note"].strip())).lastrowid
                    s.conn.execute("UPDATE exceptions SET status=? WHERE id=?", (data["disposition"], data["id"])); s.log(data["reviewer"], "review_exception", "exception", data["id"], {"review_id": review_id, "disposition": data["disposition"]}); s.conn.commit()
                finally: s.close()
                self._json({"ok": True})
            except (ValueError, json.JSONDecodeError) as exc: self._json({"error": str(exc)}, 400)

        def log_message(self, *args): pass

    print(f"Audit review UI: http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()

```


## Assistant

<thinking>


**Verifying JavaScript syntax within strings**
</thinking>

**Tool Call: python3 -m py_compile run.py src/audit_analytics/*.py && PYTHONPATH=src python3 -m unittest discover -s tests -v && python3 run.py --help >/dev/null**
Status: Completed

Terminal:
```
test_reconciled_import_to_exportable_review_workflow (test_engagement_workflow.EngagementWorkflowTest.test_reconciled_import_to_exportable_review_workflow) ... ok
test_import_requires_acknowledgement_then_creates_traceable_exception (test_pipeline.PipelineTest.test_import_requires_acknowledgement_then_creates_traceable_exception) ... ok
test_token_classes_and_similarity_work_without_a_model_service (test_semantic.SemanticTest.test_token_classes_and_similarity_work_without_a_model_service) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.402s

OK

```


## Assistant

<thinking>


**Planning CLI workflow testing with temp files**

**Designing comprehensive CLI subprocess tests**
</thinking>

**Tool Call: Editing files**
Status: Completed

Diff: /Users/Mitesh Gada/Documents/Projects/audit-analytics/tests/test_cli_workflow.py
```
import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CliWorkflowTest(unittest.TestCase):
    def test_first_engagement_commands_complete_with_exact_reconciliation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); db = root / "audit.db"; source = root / "gl.csv"
            with source.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["entry_id", "posting_date", "account_code", "debit", "credit", "description"])
                writer.writeheader()
                for i in range(12): writer.writerow({"entry_id": f"J{i}", "posting_date": "2026-03-31" if i == 11 else "2026-02-01", "account_code": "6000", "debit": 1000 if i == 11 else 100 + i, "credit": 0, "description": "accrual"})
            def run(*args):
                return subprocess.run([sys.executable, "run.py", *args], cwd=ROOT, text=True, capture_output=True, check=True)
            run("init", "--db", str(db), "--client", "Client", "--period", "2025-04-01:2026-03-31", "--owner", "manager")
            run("add-user", "--db", str(db), "--actor", "manager", "--username", "reviewer", "--role", "reviewer")
            total = sum([100 + i for i in range(11)] + [1000])
            imported = run("import-gl", "--db", str(db), "--actor", "manager", "--file", str(source), "--expected-rows", "12", "--expected-debits", str(total), "--expected-credits", "0")
            self.assertTrue(json.loads(imported.stdout)["reconciliation"]["matches"])
            run("acknowledge-population", "--db", str(db), "--reviewer", "reviewer", "--note", "Agreed to source control report")
            run("analyze", "--db", str(db), "--actor", "manager", "--no-isolation")
            status = json.loads(run("status", "--db", str(db)).stdout)
            self.assertTrue(status["population_acknowledged"])


if __name__ == "__main__":
    unittest.main()

```


## Assistant

<thinking>


**Running tests**
</thinking>

**Tool Call: PYTHONPATH=src python3 -m unittest discover -s tests -v**
Status: Completed

Terminal:
```
test_first_engagement_commands_complete_with_exact_reconciliation (test_cli_workflow.CliWorkflowTest.test_first_engagement_commands_complete_with_exact_reconciliation) ... ok
test_reconciled_import_to_exportable_review_workflow (test_engagement_workflow.EngagementWorkflowTest.test_reconciled_import_to_exportable_review_workflow) ... ok
test_import_requires_acknowledgement_then_creates_traceable_exception (test_pipeline.PipelineTest.test_import_requires_acknowledgement_then_creates_traceable_exception) ... ok
test_token_classes_and_similarity_work_without_a_model_service (test_semantic.SemanticTest.test_token_classes_and_similarity_work_without_a_model_service) ... ok

----------------------------------------------------------------------
Ran 4 tests in 2.918s

OK

```


## Assistant

<thinking>


**Updating implementation plan with delivered features**

**Documenting partial deliveries and security observations**

**Verifying import and export CLI behaviors**
</thinking>

<thinking>


**Planning materiality threshold logic**

**Refining materiality evidence handling**
</thinking>

The full first-engagement workflow is now executable end to end and covered by a CLI integration test. I’m doing the last documentation pass now so the implementation plan accurately distinguishes delivered local functionality from remaining enterprise controls.

## User

token limits nearing exhaustion. write down what to do for resuming in future or for another ai agent

## Assistant

You've hit your usage limit. Upgrade to Plus to continue using Codex (https://chatgpt.com/explore/plus), or try again at Oct 9th, 2026 9:12 AM.
