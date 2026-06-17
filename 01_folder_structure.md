# MarketPulse AI — Project Folder Structure (v3)

Complete file tree including all original modules, 5 novelties, 4 risk mitigations,
and 10 new innovations accepted in v3.

```
marketpulse-ai/
│
├── .github/
│   └── workflows/
│       ├── ingest_news.yml             # Cron */15 + workflow_dispatch: RSS + EDGAR 8-K ingestion
│       ├── build_consensus.yml         # Daily 06:00 UTC: regime + dual consensus (analyst + options)
│       ├── signal_scan.yml             # Cron */15 + workflow_dispatch: GCSV + all modifiers → signal
│       ├── keepwarm.yml                # Cron */12: ping HF endpoints to prevent cold starts
│       ├── train_finbert.yml           # Manual: fine-tune FinBERT-Surprise on Lightning AI
│       ├── train_decay_model.yml       # Weekly: retrain XGBoost decay regressors
│       ├── rebuild_contagion.yml       # Monthly: rebuild cross-asset contagion graph
│       ├── evaluate_signals.yml        # Daily: fetch realised returns, write signal_outcome records
│       └── update_tone_baselines.yml   # Weekly: recompute per-executive embedding centroids
│
├── ingestion/
│   ├── __init__.py
│   ├── rss_fetcher.py                  # RSS/Atom polling: Yahoo Finance, Reuters, CNBC, Seeking Alpha
│   ├── edgar_fetcher.py                # [INNOVATION 2] EDGAR full-text search API (efts.sec.gov)
│   │                                   #   Polls 8-K filings for tracked tickers in real time
│   │                                   #   Special handling for zero-consensus events (CEO resign, etc.)
│   ├── transcript_fetcher.py           # [INNOVATION 3] Finnhub earnings call transcript API
│   │                                   #   Returns full transcript text per ticker per quarter
│   ├── options_fetcher.py              # [INNOVATION 1] Fetches options chain data for consensus:
│   │                                   #   implied volatility term structure (Tradier sandbox API)
│   │                                   #   put/call ratio (CBOE free data)
│   │                                   #   unusual options flow flags (Tradier)
│   ├── insider_fetcher.py              # [INNOVATION 4] EDGAR Form 4 open-market purchase filter
│   │                                   #   Only ingests: open-market buys, within 30 days of earnings,
│   │                                   #   above materiality threshold vs executive's trading history
│   ├── short_interest_fetcher.py       # [INNOVATION 8] FINRA biweekly short interest data
│   │                                   #   Fetches short_interest_pct and days_to_cover per ticker
│   ├── global_ir_fetcher.py            # [INNOVATION 10-scoped] English IR RSS for TSMC, Samsung, ASML
│   │                                   #   These three companies publish English investor relations feeds
│   ├── api_fetcher.py                  # Finnhub /news company-specific news by ticker
│   ├── consensus_scraper.py            # Analyst EPS/revenue estimates from Finnhub + Alpha Vantage
│   ├── macro_fetcher.py                # VIX (CBOE CSV), yield curve (FRED), SPX trend (yfinance)
│   └── deduplicator.py                 # SHA256(url) hash check; skips already-processed items
│
├── preprocessing/
│   ├── __init__.py
│   ├── cleaner.py                      # Strip HTML, remove boilerplate, normalise, truncate 800 words
│   ├── entity_tagger.py                # spaCy NER → company names → ticker symbols
│   ├── chunker.py                      # Split to ≤450-token overlapping chunks for FinBERT
│   ├── transcript_splitter.py          # [INNOVATION 3] Splits transcript into:
│   │                                   #   prepared_remarks: text before "Operator: questions"
│   │                                   #   qa_section: text from "Operator: questions" onward
│   │                                   #   Returns {prepared: str, qa: str, speaker_map: dict}
│   └── price_validator.py              # [RISK 4 FIX] Flags |return| > 50% as split artifact; aborts
│                                       #   training if flag rate > 2%; logs to data_quality_log
│
├── regime_classifier/
│   ├── __init__.py
│   ├── regime_model.py                 # [NOVELTY 4] VIX + yield curve + SPX → 4 regime labels
│   ├── regime_store.py                 # Writes regime to Supabase market_regimes table
│   └── regime_prompt_adapter.py        # Injects regime context string into Jinja2 prompt templates
│
├── consensus_builder/
│   ├── __init__.py
│   ├── baseline_aggregator.py          # Merges Finnhub + Alpha Vantage estimates into consensus dict
│   ├── options_consensus_builder.py    # [INNOVATION 1] Converts IV/put-call/flow into options-derived
│   │                                   #   consensus narrative and v_consensus_options vector
│   │                                   #   Computes analyst_options_divergence score
│   ├── narrative_generator.py          # [NOVELTY 4+5] Generates bear/base/bull narratives, regime-conditioned
│   ├── insider_prior_modifier.py       # [INNOVATION 4] Adjusts bull scenario weight if insider buys detected
│   │                                   #   within 30 days of earnings above materiality threshold
│   └── consensus_store.py              # Upserts all consensus records + vectors to Supabase
│
├── fine_tuning/
│   ├── __init__.py
│   ├── dataset_builder.py              # Earnings articles + EPS surprise labels + next-day return
│   ├── contrastive_dataset.py          # BEAT/MISS pair construction for SupConLoss
│   ├── trainer.py                      # Dual-loss fine-tuning on Lightning AI Studios
│   ├── evaluator.py                    # Cosine separation validation metric
│   └── push_to_hub.py                  # Progressive checkpoint push to HF Hub
│
├── vectorizer/
│   ├── __init__.py
│   ├── hf_client.py                    # [RISK 2 FIX] HF API primary + ONNX CPU fallback
│   ├── embed_article.py                # Article → v_actual (mean-pool chunks, L2-normalise)
│   ├── embed_consensus.py              # [NOVELTY 5] Embeds bear/base/bull → v_consensus ×3
│   ├── embed_transcript.py             # [INNOVATION 3] Embeds prepared_remarks and qa_section separately
│   │                                   #   Returns {v_prepared: ndarray, v_qa: ndarray}
│   └── batch_embedder.py               # Batches calls with retry; respects HF rate limits
│
├── gcsv_engine/
│   ├── __init__.py
│   ├── vector_ops.py                   # [NOVELTY 5] Triple GCSV: v_surprise = v_actual − v_consensus ×3
│   ├── transcript_gcsv.py              # [INNOVATION 3] Dual GCSV on transcript:
│   │                                   #   v_surprise_prepared = v_prepared − v_consensus_base
│   │                                   #   v_surprise_qa = v_qa − v_consensus_base
│   │                                   #   divergence_score = cosine_distance(v_surprise_prepared, v_surprise_qa)
│   ├── surprise_classifier.py          # [NOVELTY 4] Regime-gated tier: HIGH/MEDIUM/LOW/NOISE
│   ├── uncertainty_scorer.py           # [NOVELTY 5] Variance across 3 scenarios → confidence + uncertainty_score
│   ├── pre_drift_detector.py           # [INNOVATION 7] Z-score of 48h pre-event return vs historical
│   │                                   #   pre-earnings distribution for the same ticker
│   │                                   #   Outputs: pre_drift_z, pre_drift_flag (bool)
│   ├── short_interest_modifier.py      # [INNOVATION 8] Hard override: BEARISH + high SI + low mag → UNCERTAIN
│   │                                   #   Also passes short_interest_pct to decay model as feature
│   └── decay_mapper.py                 # [NOVELTY 2] XGBoost quantile models → predicted_returns + CI
│
├── tone_drift/                         # [INNOVATION 5] Management tone drift detection
│   ├── __init__.py
│   ├── executive_tracker.py            # Maintains per-executive embedding centroid from historical transcripts
│   │                                   #   Schema: {executive_id, ticker, role, centroid_vector, call_count,
│   │                                   #            last_updated}
│   ├── drift_scorer.py                 # Computes cosine drift between current call embedding and
│   │                                   #   historical centroid: tone_drift_score ∈ [0, 2]
│   │                                   #   High drift + hedging direction → negative soft prior
│   └── centroid_updater.py             # Updates centroid after each new transcript (Welford online mean)
│                                       #   Runs weekly via update_tone_baselines.yml workflow
│
├── decay_model/
│   ├── __init__.py
│   ├── feature_builder.py              # Constructs feature row per signal:
│   │                                   #   surprise_magnitude, sector, market_cap_bucket, vix,
│   │                                   #   time_of_day, day_of_week, days_to_earnings, momentum_20d,
│   │                                   #   regime, short_interest_pct [INNOVATION 8],
│   │                                   #   pre_drift_z [INNOVATION 7],
│   │                                   #   analyst_options_divergence [INNOVATION 1]
│   ├── trainer.py                      # XGBoost ×9: 3 horizons × 3 quantiles (pinball loss)
│   ├── evaluator.py                    # Sharpe, hit rate, CI coverage backtest
│   └── model_store.py                  # Pkl serialise/deserialise to Supabase Storage
│
├── signal_feedback/                    # [INNOVATION 6] Signal self-evaluation feedback loop
│   ├── __init__.py
│   ├── outcome_recorder.py             # Runs daily: for signals 24h and 5d old, fetches realised
│   │                                   #   return from Polygon.io, computes accuracy_score, writes
│   │                                   #   to signal_outcome table
│   ├── accuracy_analyser.py            # Aggregates hit rates by regime, sector, horizon, confidence tier
│   │                                   #   Outputs calibration table used by surprise_classifier.py
│   └── drift_alerter.py                # Compares rolling 4-week hit rate to baseline; fires Slack
│                                       #   alert if any category drops > 15 percentage points
│
├── contagion_graph/
│   ├── __init__.py
│   ├── graph_builder.py                # [NOVELTY 3] Statistical contagion graph from 18-month history
│   ├── graph_store.py                  # Supabase contagion_edges persistence
│   ├── propagator.py                   # BFS walk → secondary signals with magnitude attenuation
│   └── graph_visualiser.py             # GEXF export for Gephi; also feeds dashboard graph view
│
├── execution/                          # [INNOVATION 9 + 10]
│   ├── __init__.py
│   ├── kelly_sizer.py                  # [INNOVATION 9] Kelly Criterion position sizing
│   │                                   #   Inputs: p50 predicted return, CI width (p10/p90),
│   │                                   #           historical hit rate for this confidence tier
│   │                                   #   Output: suggested_allocation_pct (fraction of portfolio)
│   │                                   #           kelly_half_f (conservative half-Kelly variant)
│   └── alpaca_executor.py              # [INNOVATION 10] Alpaca paper trading integration
│                                       #   Converts HIGH/MEDIUM signals → paper orders with Kelly sizing
│                                       #   Records fill price, actual slippage in signal_outcome table
│
├── signal_emitter/
│   ├── __init__.py
│   ├── signal_builder.py               # Convergence point: assembles full v3 signal object
│   │                                   #   Integrates all modifiers: uncertainty, regime, short interest,
│   │                                   #   pre-drift, insider, tone drift, transcript divergence, Kelly size
│   ├── supabase_writer.py              # Writes primary + secondary signals to trading_signals table
│   └── alert_dispatcher.py             # Fires Slack webhook for HIGH/MEDIUM; suppresses UNCERTAIN
│
├── dashboard/                          # [INNOVATION 11] Signal Performance Dashboard
│   ├── src/
│   │   ├── App.jsx                     # Root React component; tab navigation
│   │   ├── components/
│   │   │   ├── AccuracyByRegime.jsx    # Bar chart: hit rate per regime over rolling 4-week window
│   │   │   ├── AccuracyBySector.jsx    # Bar chart: hit rate per sector
│   │   │   ├── AccuracyByHorizon.jsx   # Line chart: accuracy at T+1h vs T+overnight vs T+5d
│   │   │   ├── SignalFeed.jsx          # Live signal list with direction, confidence, Kelly size
│   │   │   ├── DriftAlert.jsx          # Red banner when any category drops > 15pp from baseline
│   │   │   ├── ContagionGraph.jsx      # Interactive force-directed graph of contagion edges
│   │   │   └── PaperPnL.jsx           # Running P&L from Alpaca paper account via Alpaca API
│   │   └── lib/
│   │       └── supabase.js             # Supabase JS client for real-time subscriptions
│   ├── package.json
│   └── vite.config.js
│
├── webhook_receiver/
│   ├── main.py                         # [RISK 1 FIX] Render.com FastAPI: Finnhub WebSocket → workflow_dispatch
│   ├── macro_warmer.py                 # Fires workflow_dispatch 60s before FOMC/CPI/NFP from macro_calendar.json
│   ├── requirements.txt
│   └── render.yaml
│
├── models/
│   ├── export_onnx.py                  # [RISK 2 FIX] Export FinBERT → INT8 ONNX via optimum
│   └── finbert_int8.onnx               # Quantised fallback model (~45MB, in Supabase Storage)
│
├── database/
│   ├── schema.sql                      # Complete Supabase schema (all tables, pgvector, indexes)
│   └── migrations/
│       ├── 001_initial_schema.sql
│       ├── 002_add_decay_windows.sql
│       ├── 003_add_regime_table.sql
│       ├── 004_add_three_consensus.sql
│       ├── 005_add_contagion.sql
│       ├── 006_add_uncertainty.sql
│       ├── 007_add_options_consensus.sql   # v_consensus_options, analyst_options_divergence
│       ├── 008_add_signal_outcome.sql      # signal_outcome table for feedback loop
│       ├── 009_add_executive_centroids.sql # executive_centroids table for tone drift
│       ├── 010_add_insider_signals.sql     # insider_signals table
│       ├── 011_add_short_interest.sql      # short_interest lookup table
│       └── 012_add_kelly_fields.sql        # suggested_allocation_pct, kelly_half_f in trading_signals
│
├── config/
│   ├── settings.py                     # All constants: thresholds, endpoints, model IDs, Kelly params
│   ├── tickers.json                    # Tracked US tickers + sector, market_cap_bucket, supply_chain_group
│   ├── feeds.json                      # RSS + API source definitions
│   ├── regime_thresholds.json          # VIX/yield/SPX cutoffs for 4 regime buckets
│   ├── macro_calendar.json             # Pre-scheduled FOMC/CPI/NFP/PCE release times
│   ├── data_sources.json               # Tiered source config (Polygon/CBOE/FRED/yfinance routing)
│   ├── global_ir_feeds.json            # English IR RSS for TSMC, Samsung, ASML
│   └── kelly_params.json               # Max allocation cap, half-Kelly fraction, per-regime limits
│
├── tests/
│   ├── test_rss_fetcher.py
│   ├── test_edgar_fetcher.py           # Mock EDGAR response → correct 8-K event type classification
│   ├── test_transcript_splitter.py     # Sample transcript → correct prepared/QA boundary detection
│   ├── test_options_consensus.py       # Mock IV/put-call data → v_consensus_options shape + values
│   ├── test_cleaner.py
│   ├── test_vector_ops.py
│   ├── test_uncertainty_scorer.py
│   ├── test_regime_classifier.py
│   ├── test_pre_drift_detector.py      # Known z-score inputs → correct flag output
│   ├── test_short_interest_modifier.py # High-SI BEARISH signal → UNCERTAIN override
│   ├── test_kelly_sizer.py             # Known p50/CI/hit-rate → correct allocation pct
│   ├── test_propagator.py
│   ├── test_decay_model.py
│   ├── test_outcome_recorder.py        # Mock price fetch → correct accuracy_score computation
│   └── test_signal_builder.py          # Full integration: all v3 fields present and schema-valid
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_embedding_analysis.ipynb     # PCA/UMAP: base FinBERT vs FinBERT-Surprise clusters
│   ├── 03_surprise_backtesting.ipynb
│   ├── 04_decay_model_tuning.ipynb
│   ├── 05_contagion_graph_eda.ipynb
│   ├── 06_regime_analysis.ipynb
│   ├── 07_uncertainty_calibration.ipynb
│   ├── 08_options_consensus_eda.ipynb  # IV term structure vs analyst estimate divergence analysis
│   ├── 09_transcript_qa_analysis.ipynb # Prepared vs Q&A surprise vector divergence distributions
│   ├── 10_tone_drift_eda.ipynb         # Per-executive centroid drift vs next-quarter EPS miss rate
│   ├── 11_short_interest_impact.ipynb  # Short interest pct vs signal accuracy by direction
│   └── 12_kelly_backtest.ipynb         # Kelly sizing vs fixed-size position P&L comparison
│
├── requirements.txt
├── .env.example
├── README.md
└── pyproject.toml
```

---

## Key File Responsibilities — v3 Additions Only

| File | Innovation | What It Does |
|---|---|---|
| `ingestion/edgar_fetcher.py` | #2 | Polls EDGAR efts.sec.gov for 8-K filings; classifies event type (earnings, guidance, personnel, material contract) |
| `ingestion/options_fetcher.py` | #1 | Fetches IV term structure, put/call ratio, unusual flow from Tradier sandbox (free) + CBOE |
| `ingestion/transcript_fetcher.py` | #3 | Pulls full earnings call transcripts from Finnhub API |
| `ingestion/insider_fetcher.py` | #4 | Filters Form 4 to open-market purchases only, within 30d of earnings, above materiality threshold |
| `ingestion/short_interest_fetcher.py` | #8 | Fetches biweekly FINRA short interest data for all tracked tickers |
| `preprocessing/transcript_splitter.py` | #3 | Splits transcript text at Q&A boundary; returns {prepared, qa, speaker_map} |
| `consensus_builder/options_consensus_builder.py` | #1 | Converts options data into text narrative → v_consensus_options; computes analyst_options_divergence |
| `consensus_builder/insider_prior_modifier.py` | #4 | Shifts bull consensus weight upward if open-market insider buys detected |
| `gcsv_engine/transcript_gcsv.py` | #3 | Runs GCSV on prepared and Q&A segments separately; computes divergence_score between them |
| `gcsv_engine/pre_drift_detector.py` | #7 | Z-score test on 48h pre-earnings return vs historical distribution |
| `gcsv_engine/short_interest_modifier.py` | #8 | Hard override rule for high-SI BEARISH signals; short_interest_pct as decay model feature |
| `tone_drift/executive_tracker.py` | #5 | Per-executive embedding centroid from historical transcript archive |
| `tone_drift/drift_scorer.py` | #5 | Cosine distance from current call to historical centroid → tone_drift_score |
| `tone_drift/centroid_updater.py` | #5 | Welford online mean update after each new transcript |
| `signal_feedback/outcome_recorder.py` | #6 | Daily: fetch realised returns, compute accuracy, write signal_outcome |
| `signal_feedback/accuracy_analyser.py` | #6 | Aggregates hit rates by category; outputs calibration table |
| `signal_feedback/drift_alerter.py` | #6 | Fires Slack alert if rolling hit rate drops > 15pp from baseline |
| `execution/kelly_sizer.py` | #9 | Kelly Criterion: predicted return + CI + historical hit rate → suggested_allocation_pct |
| `execution/alpaca_executor.py` | #10 | Sends paper orders to Alpaca sandbox; records fills in signal_outcome |
| `dashboard/src/` | #11 | React dashboard: accuracy charts, live signal feed, contagion graph, paper P&L |
