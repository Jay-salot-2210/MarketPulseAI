# MarketPulse AI — Tech Stack Reference (v3)

Every technology used in the full system across all layers.
Organised by system layer. Cost column shows free-tier viability.

---

## 1. Orchestration & Scheduling

| Technology | Used For | Cost |
|---|---|---|
| **GitHub Actions** | 9 workflow files: cron ingestion, daily consensus, signal scan, keepwarm, fine-tune trigger, decay retrain, contagion rebuild, daily outcome evaluation, weekly tone baseline update | $0 |
| **GitHub Secrets + Vars** | All API keys and feature flags (USE_FINETUNED_MODEL) | $0 |
| **`ubuntu-latest` runner** | Stateless Python execution environment for all pipeline scripts | $0 |

---

## 2. Data Ingestion

### News & Events

| Technology | Used For | Why | Cost |
|---|---|---|---|
| **`feedparser`** | RSS/Atom parsing: Yahoo Finance, Reuters, Seeking Alpha, CNBC, MarketWatch | Battle-tested; handles malformed feeds | $0 |
| **`httpx`** | All outbound HTTP (APIs, EDGAR, CBOE, FRED) | Async-capable; clean API | $0 |
| **EDGAR Full-Text Search API** (`efts.sec.gov`) | [Innovation 2] Real-time 8-K filings: earnings, guidance cuts, CEO changes, material contracts | Primary legal source; filings appear here before any news wire; completely free | $0 |
| **Finnhub API** | Company news, analyst estimates, EPS history, earnings call transcripts | Richest free tier for consensus + transcript data | $0 |
| **Alpha Vantage API** | Historical earnings, revenue consensus | 25 calls/day free; supplements Finnhub | $0 |

### Options Market Data (Innovation 1)

| Technology | Used For | Why | Cost |
|---|---|---|---|
| **Tradier Sandbox API** | Implied volatility term structure, put/call ratio, options chain data per ticker | Free sandbox account; no expiry; covers IV surface and flow flags | $0 |
| **CBOE Options Data** (`cdn.cboe.com`) | Daily put/call ratios for index and equity options | Authoritative source (CBOE publishes these); direct CSV download | $0 |

### Macro & Price Data

| Technology | Used For | Why | Cost |
|---|---|---|---|
| **FRED API** | 10Y-2Y yield curve slope (T10Y2Y); macro indicators for regime and consensus | Federal Reserve's own data; authoritative; unlimited free | $0 |
| **CBOE VIX CSV** | Daily VIX for regime classifier | Authoritative source; replaces yfinance ^VIX | $0 |
| **Polygon.io API** (free tier) | Split-adjusted EOD OHLCV for decay model training labels; signal outcome realised returns | Explicit `adjusted=True`; no split artifacts; replaces yfinance for critical training data | $0 |
| **`yfinance`** | SPX 20-day return (regime); intraday T+1h returns; contagion graph EOD with `auto_adjust=True` | Acceptable for directional/less-critical uses only | $0 |
| **FINRA Short Interest API** | [Innovation 8] Biweekly short interest data: short_interest_pct, days_to_cover per ticker | Free public FINRA data; published every two weeks | $0 |

### Alternative Data Sources

| Technology | Used For | Why | Cost |
|---|---|---|---|
| **SEC EDGAR Form 4 API** | [Innovation 4] Open-market insider purchase filings within 30 days of earnings | Free EDGAR API; filtered to open-market buys only (excludes plan sales and grants) | $0 |
| **`spaCy`** | NER for ticker/company extraction from article text | Faster than BERT for NER; `en_core_web_sm` is lightweight | $0 |

---

## 3. NLP & Embedding

| Technology | Used For | Why | Cost |
|---|---|---|---|
| **HuggingFace Serverless Inference API** | GPU inference for FinBERT and FinBERT-Surprise at runtime | Free GPU endpoint; eliminates $200/month GPU instance | $0 |
| **FinBERT** (`ProsusAI/finbert`) | Base model; frozen fallback before fine-tuning completes | Pre-trained on Reuters + 10-Ks + earnings calls | $0 |
| **FinBERT-Surprise** (fine-tuned private HF repo) | Primary embedding model post-fine-tuning; surprise-geometry-aware embedding space | [Novelty 1] beat/miss articles cluster apart; cleaner GCSV subtraction | $0 |
| **`transformers`** (HuggingFace) | Fine-tuning training loop; local tokenisation before API calls | HF Trainer handles mixed-precision, checkpointing | $0 |
| **`datasets`** (HuggingFace) | Fine-tuning training dataset iteration and batching | Integrates natively with HF Trainer | $0 |
| **HuggingFace Text Generation** | Generating 3× Synthetic Consensus Narratives + options-derived narrative | Same free serverless endpoint used for embeddings | $0 |
| **ONNX Runtime** (`onnxruntime`) | [Risk 2] INT8 quantised FinBERT local CPU fallback on cold start | ~800ms on ubuntu-latest CPU vs 45s cold start | $0 |
| **HuggingFace `optimum`** | Exporting fine-tuned FinBERT to ONNX INT8 format | Official HF optimisation library | $0 |

**Fine-tuning loss**: `0.7 × MSELoss(predicted_surprise, actual_surprise_pct) + 0.3 × SupConLoss(embeddings, direction_labels)`

---

## 4. Consensus Synthesis

| Technology | Used For | Why | Cost |
|---|---|---|---|
| **Jinja2** | Prompt templates for all narrative generation (analyst + options consensus, all 3 scenarios, regime-conditioned) | Clean, testable, version-controlled templates | $0 |
| **`pandas`** | Aggregating multi-source consensus estimates; building training datasets | Standard; handles Finnhub JSON and CSV outputs | $0 |
| **Regime Classifier** (custom) | [Novelty 4] 4-regime market classification feeding consensus prompt conditioning | VIX + yield + SPX; rule-based; deterministic | $0 |
| **Options Consensus Builder** (custom) | [Innovation 1] IV term structure + put/call → text narrative → v_consensus_options | Converts derivative market pricing into FinBERT-embeddable text | $0 |

---

## 5. Vector Database & Storage

| Technology | Used For | Why | Cost |
|---|---|---|---|
| **Supabase** | Primary database for all 15+ tables | Free tier: 500MB + 1GB file storage + 2GB bandwidth; replaces $70/mo Pinecone | $0 |
| **pgvector** (Postgres extension) | `vector(768)` columns for v_actual, v_consensus_bear/base/bull, v_consensus_options, executive centroids | `<=>` cosine operator; all vector math in SQL | $0 |
| **Supabase Storage** | XGBoost .pkl models, ONNX fallback model, contagion GEXF export | 1GB free; no extra file storage | $0 |
| **Supabase Realtime** | Live signal feed in React dashboard (WebSocket subscription to trading_signals table) | Built into Supabase; enables real-time dashboard without polling | $0 |
| **`supabase-py`** | All Python CRUD, vector upserts, storage operations | Official SDK | $0 |

**Full table list (v3)**:
`raw_articles` · `market_regimes` · `consensus_baselines` · `embeddings` · `contagion_edges` · `trading_signals` · `signal_outcome` · `executive_centroids` · `insider_signals` · `short_interest` · `calibration` · `data_quality_log` · `accuracy_calibration` · `alpaca_fills`

---

## 6. Temporal Decay Modelling (Novelty 2)

| Technology | Used For | Why | Cost |
|---|---|---|---|
| **XGBoost** | 9 quantile regressors: 3 horizons × 3 quantiles (10/50/90th pctile) | Handles tabular features without overfitting; interpretable via SHAP; CPU-trainable | $0 |
| **`shap`** | Feature importance for decay model outputs | Auditable predictions — shows which features drove each forecast | $0 |
| **`scikit-learn`** | TimeSeriesSplit cross-validation; quantile calibration | Standard ML utilities | $0 |
| **`joblib`** | Model serialisation | Native to sklearn; stored to Supabase Storage | $0 |

**New v3 decay model features** (additions to v2):
`short_interest_pct` [Innovation 8] · `pre_drift_z` [Innovation 7] · `analyst_options_divergence` [Innovation 1] · `tone_drift_score` [Innovation 5]

---

## 7. Contagion Graph (Novelty 3)

| Technology | Used For | Why | Cost |
|---|---|---|---|
| **`networkx`** | In-memory directed graph for contagion propagation | Standard Python graph library; sufficient for 500–2000 node universe | $0 |
| **`scipy.stats`** | Bootstrap permutation tests for edge statistical validation (p < 0.05) | Prevents spurious edges from chance correlations | $0 |

**v3 addition**: English IR RSS feeds for TSMC, Samsung, ASML added to contagion node universe — extends graph to highest-impact non-US events without full translation layer.

---

## 8. Signal Intelligence Additions (v3)

| Technology | Used For | Innovation | Cost |
|---|---|---|---|
| **Custom `pre_drift_detector.py`** | Z-score of 48h pre-earnings return vs rolling historical distribution | #7 | $0 |
| **Custom `short_interest_modifier.py`** | BEARISH + high SI + low magnitude → UNCERTAIN override; SI as decay feature | #8 | $0 |
| **Custom `transcript_splitter.py`** | Splits transcript at Q&A boundary using speaker pattern detection | #3 | $0 |
| **Custom `transcript_gcsv.py`** | Dual GCSV on prepared vs Q&A; divergence score between segments | #3 | $0 |
| **Custom `drift_scorer.py`** | Cosine distance from current executive embedding to historical centroid | #5 | $0 |
| **Welford online mean** (in `centroid_updater.py`) | Numerically stable incremental centroid update without storing all history | #5 | $0 |

---

## 9. Signal Feedback Loop (Innovation 6)

| Technology | Used For | Why | Cost |
|---|---|---|---|
| **Polygon.io API** | Realised return fetch for signal outcome evaluation (24h and 5d after signal) | Same source used for decay model labels; split-adjusted; consistent | $0 |
| **Custom `outcome_recorder.py`** | Fetches realised return, computes accuracy_score, writes signal_outcome | Closes the prediction→reality loop | $0 |
| **Custom `accuracy_analyser.py`** | Aggregates hit rates by regime/sector/horizon/confidence tier | Produces calibration table for classifier down-weighting | $0 |

---

## 10. Kelly Criterion Sizing (Innovation 9)

| Technology | Used For | Why | Cost |
|---|---|---|---|
| **Custom `kelly_sizer.py`** | Kelly Criterion position sizing from p50/CI/historical hit rate | One formula; uses data already computed in decay model output | $0 |
| **`config/kelly_params.json`** | Max allocation cap (e.g. 10%), half-Kelly fraction (0.5), per-regime limits | Conservative constraints prevent Kelly's tendency toward overbet | $0 |

**Kelly formula used**:
```
edge  = p50_predicted_return
odds  = p50 / (p90 - p10)           # return-to-risk ratio from CI
win_p = historical_hit_rate_for_tier
f*    = (win_p * odds - (1 - win_p)) / odds
f_applied = min(f* * kelly_half_fraction, max_allocation_cap)
```

---

## 11. Execution & Monitoring (Innovations 10 + 11)

| Technology | Used For | Why | Cost |
|---|---|---|---|
| **Alpaca Markets API** (paper tier) | [Innovation 10] Paper trading with real fill prices and slippage | Free paper trading; no credit card; real order execution on paper | $0 |
| **`alpaca-trade-api`** (Python SDK) | Placing and tracking paper orders from `alpaca_executor.py` | Official Alpaca SDK | $0 |
| **React + Vite** | [Innovation 11] Signal performance dashboard | Fast, lightweight; no Next.js overhead for a single-page tool | $0 |
| **Recharts** | All dashboard charts (bar, line, area) | Already in the Claude artifact stack; no extra dependency | $0 |
| **`react-force-graph`** | Interactive contagion graph visualisation in dashboard | Force-directed graph with D3 physics; free | $0 |
| **Supabase JS client** | Real-time signal feed in dashboard via WebSocket subscription | Built into Supabase; no additional backend needed | $0 |

---

## 12. Fine-Tuning & Training Infrastructure

| Technology | Used For | Cost |
|---|---|---|
| **Lightning AI Studios** | [Risk 3 fix] Persistent GPU sessions for FinBERT-Surprise fine-tuning | Free 22h/month GPU; sessions survive disconnection |  $0 |
| **`torch`** (PyTorch) | Fine-tuning training loop | Required by HuggingFace Trainer | $0 |
| **`pytorch-metric-learning`** | `SupConLoss` implementation for contrastive fine-tuning | Official implementation; numerically stable | $0 |

---

## 13. Event-Driven Infrastructure (Risk Mitigations)

| Technology | Used For | Cost |
|---|---|---|
| **Finnhub WebSocket** (`wss://ws.finnhub.io`) | Real-time news push stream; replaces cron polling for intraday events | Free tier | $0 |
| **FastAPI + uvicorn** | Webhook receiver web service on Render.com | Lightweight always-on process | $0 |
| **Render.com** (free web service tier) | Hosting always-on webhook receiver process | Free tier; persistent process unlike GitHub Actions | $0 |
| **`websockets`** | Persistent WebSocket connection maintenance with auto-reconnect | Standard async library | $0 |

---

## 14. Python Utilities

| Technology | Used For |
|---|---|
| **Python 3.11** | Runtime |
| **`pydantic` 2.x** | Schema validation for all data objects |
| **`tenacity`** | Retry with exponential backoff on all external API calls |
| **`loguru`** | Structured logging across all modules |
| **`python-dotenv`** | Local `.env` loading for development |
| **`pytest` + `pytest-asyncio`** | Unit and integration testing |
| **`ruff`** | Linting and formatting |

---

## Full Cost Summary (v3)

```
LAYER                                    TECHNOLOGY                        MONTHLY COST
────────────────────────────────────────────────────────────────────────────────────────
Scheduling / CI (9 workflows)            GitHub Actions                    $0
Event-driven trigger                     Render.com free tier              $0
GPU inference (runtime)                  HuggingFace Inference API         $0
Cold-start fallback                      ONNX Runtime (local CPU)          $0
GPU fine-tuning                          Lightning AI Studios              $0
Vector DB + storage + realtime           Supabase free tier                $0
Analyst consensus data                   Finnhub + Alpha Vantage           $0
Macro data                               FRED API + CBOE CSV               $0
EOD price data (clean)                   Polygon.io free tier              $0
Options market data                      Tradier sandbox + CBOE CSV        $0
Insider filings                          SEC EDGAR API                     $0
Short interest data                      FINRA public data                 $0
Paper trading execution                  Alpaca paper account              $0
Dashboard hosting                        Static deploy (Vercel free tier)  $0
────────────────────────────────────────────────────────────────────────────────────────
TOTAL MONTHLY INFRASTRUCTURE COST                                          $0
```
