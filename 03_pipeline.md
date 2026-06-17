# MarketPulse AI — End-to-End Data Pipeline (v3)

Complete walkthrough of all pipelines including 10 new innovations and all risk mitigations.
Where a step is unchanged from v2, it is noted as such.

---

## Pipeline Overview

```
                       ┌─────────────────────────────────────────────────────────┐
                       │          GitHub Actions — 9 Workflow Files              │
                       └──┬───────────────────┬───────────────┬──────────────────┘
                          │                   │               │
         ┌────────────────┼───────────┐       │         ┌─────┴──────────────────────────┐
         ▼                ▼           ▼       ▼         ▼                                ▼
   [PIPELINE A]     [PIPELINE B]  [PIPELINE C] [PIPELINE D]   [PIPELINE E]        [PIPELINE F]
   News Ingest      Consensus     Signal Scan  Fine-Tune       Decay Retrain      Contagion Rebuild
   */15 min         daily 06:00   */15 min     (manual)        (weekly)           (monthly)

         ▼
   [PIPELINE G]     [PIPELINE H]
   Signal Outcome   Tone Baseline
   Evaluation       Update
   (daily)          (weekly)
```

---

## Pipeline A — News & Event Ingestion (every 15 min + webhook_dispatch)

**Trigger**: `ingest_news.yml` — cron fallback + immediate `workflow_dispatch` from Render.com
WebSocket receiver on Finnhub news push.

### Step A1 — Multi-Source Fetch

**Scripts**: `rss_fetcher.py` + `api_fetcher.py` + `edgar_fetcher.py` [Innovation 2] + `global_ir_fetcher.py` [Innovation 10-scoped]

**What happens**:

*RSS / API (unchanged from v2)*: Polls Yahoo Finance, Reuters, Seeking Alpha, CNBC; calls Finnhub
/news for company-specific articles.

*EDGAR 8-K Direct Feed [Innovation 2]*: `edgar_fetcher.py` calls EDGAR full-text search API:
```
GET https://efts.sec.gov/LATEST/search-index?q="{ticker}"&dateRange=custom&startdt={15min_ago}
    &forms=8-K
```
Parses returned filing metadata and fetches the primary document text. Classifies the 8-K event type
from the item number declared in the filing:
- Item 2.02 → Results of Operations (earnings release)
- Item 5.02 → Management change (CEO/CFO resignation/appointment)
- Item 7.01 → Regulation FD disclosure (guidance update)
- Item 8.01 → Other events (material contracts, legal settlements)

**Special handling for zero-consensus 8-K events** (CEO resignation, surprise guidance cut):
These events have no analyst EPS estimate to build a consensus narrative against. They enter the
pipeline with `has_consensus = False` and are processed in single-vector mode:
`confidence_score = norm(v_actual)` — classified purely on absolute embedding magnitude,
not on surprise delta. This is flagged in the signal object as `signal_type = "zero_consensus"`.

*Global IR feeds [Innovation 10-scoped]*: `global_ir_fetcher.py` polls English-language investor
relations RSS for TSMC (`ir.tsmc.com/rss`), Samsung IR, and ASML IR. These three companies publish
English earnings releases and guidance updates. Their articles enter the standard pipeline as
`source = "global_ir"` and their tickers (TSM, SSNLF, ASML) are in `config/tickers.json`.

### Step A2 — Deduplication (unchanged from v2)

SHA256(url) hash check against Supabase `raw_articles`. Skips already-seen items.

### Step A3 — Clean + Tag (unchanged from v2)

`cleaner.py` strips HTML, removes boilerplate, truncates to 800 words.
`entity_tagger.py` runs spaCy NER → ticker extraction.

### Step A4 — Transcript Fetch + Split [Innovation 3]

*Triggered only when article is classified as earnings release (8-K Item 2.02 or RSS earnings tag).*

`transcript_fetcher.py` calls Finnhub `/stock/transcripts` for the matching ticker and quarter.

`transcript_splitter.py` splits the transcript at the Q&A boundary:
```python
# Boundary detection: look for operator cues marking Q&A start
QA_BOUNDARY_PATTERNS = [
    r"operator.*?question.and.answer",
    r"we.will.now.begin.*?question",
    r"open.*?line.*?question",
    r"first.question.*?comes.from",
]
```
Returns: `{prepared_remarks: str, qa_section: str, speaker_map: {name: role}}`

The prepared remarks and Q&A are stored separately in `raw_articles` as `body_prepared` and
`body_qa` columns. Both pass through the embedding pipeline independently.

### Step A5 — Embed v_actual (+ Transcript Vectors) [Novelty 1 + Innovation 3]

`embed_article.py` → `v_actual` for the main article body (via FinBERT-Surprise if enabled).

`embed_transcript.py` [Innovation 3]: separately embeds `body_prepared` and `body_qa`:
```python
v_prepared = embed(prepared_remarks)   # management's scripted language
v_qa       = embed(qa_section)         # live, unscripted responses
```

All vectors stored to Supabase `embeddings` table.

---

## Pipeline B — Consensus Builder (daily 06:00 UTC + updated with all v3 additions)

### Step B1 — Fetch Analyst Consensus (unchanged from v2)

Finnhub + Alpha Vantage → EPS estimates, revenue guidance, analyst buy/hold/sell distribution.

### Step B2 — Fetch Options Market Data [Innovation 1]

**Script**: `ingestion/options_fetcher.py`

**What happens**:
- Calls Tradier sandbox API for each tracked ticker's options chain
  - Fetches IV for 30-day and 60-day expiry contracts → IV term structure slope
  - Fetches put volume / call volume ratio for front-month contracts → put/call ratio
  - Flags unusual flow: contracts with volume > 5× open interest in current session
- Fetches CBOE equity put/call ratio from `cdn.cboe.com/api/global/put_call_ratios/options-pc-ratios.csv`

**Output**: Options consensus dict per ticker:
```python
{
  "ticker": "AAPL",
  "iv_30d": 0.28,
  "iv_60d": 0.22,
  "iv_term_slope": -0.06,          # downward slope = elevated near-term uncertainty
  "put_call_ratio": 1.34,           # > 1.0 = more puts than calls = bearish positioning
  "unusual_flow_flag": True,
  "unusual_flow_direction": "PUT",  # unusual put buying = market expects downside
  "analyst_options_divergence": None  # computed in next step
}
```

### Step B3 — Classify Market Regime [Novelty 4 — unchanged from v2]

VIX (CBOE CSV) + yield slope (FRED) + SPX 20-day return (yfinance) → 4-regime classification.
Written to Supabase `market_regimes`.

### Step B4 — Insider Prior Modifier [Innovation 4]

**Script**: `consensus_builder/insider_prior_modifier.py`

**What happens**:
- `insider_fetcher.py` queries EDGAR Form 4 API for the ticker, filtering:
  - `transactionCode = "P"` (open-market purchase only — excludes plan sales and grants)
  - Filing within 30 calendar days of next earnings date
  - Transaction value > 2× the insider's median historical transaction (materiality filter)
- If qualifying purchases found:
  - `insider_buy_flag = True`
  - `insider_buy_score` = sum of qualifying purchase values / insider's rolling 12-month trade volume
  - The **bull scenario consensus narrative is weighted upward** in the prompt:
    `"Note: [N] insiders made open-market purchases worth $[X] in the past 30 days."`

### Step B5 — Fetch Short Interest [Innovation 8]

**Script**: `ingestion/short_interest_fetcher.py`

**What happens**:
- Fetches FINRA short interest data (published biweekly) for all tracked tickers
- Stores `short_interest_pct` (shares short / float) and `days_to_cover` in Supabase `short_interest` table
- Used by `short_interest_modifier.py` in Pipeline C

### Step B6 — Tone Drift Prior [Innovation 5]

**Script**: `tone_drift/drift_scorer.py` + `executive_tracker.py`

**What happens**:
- Fetches the current quarter's transcript embedding centroid for the CEO/CFO of the ticker
- Computes cosine distance from current call embedding to historical centroid
- Returns `tone_drift_score` ∈ [0, 2] and `drift_direction` (toward_hedging / toward_confident)
- A `tone_drift_score > 0.3` toward hedging language is appended to the base consensus narrative
  as a soft prior: adjusts `guidance_tone` field to "cautious" even if analyst consensus says neutral

### Step B7 — Generate 3× Scenario Narratives [Novelty 4+5 — with v3 enhancements]

**Script**: `consensus_builder/narrative_generator.py`

**Changes from v2**: Prompts now incorporate insider_buy_flag and tone_drift_score as context:
```
Insider context: {{ "Multiple insiders made open-market purchases this quarter." if insider_buy_flag else "" }}
Executive tone: {{ "CFO language has drifted toward hedging over 3 consecutive quarters." if drift_flag else "" }}
```

**Output**: {bear: str, base: str, bull: str} — same as v2.

### Step B8 — Build Options Consensus Narrative [Innovation 1]

**Script**: `consensus_builder/options_consensus_builder.py`

**What happens**:
- Converts the options dict into a text narrative suitable for FinBERT embedding:
```jinja2
The options market for {{ ticker }} is pricing {{ "elevated" if iv_30d > 0.30 else "moderate" }}
near-term uncertainty (30-day IV: {{ iv_30d|percent }}). The put/call ratio of {{ put_call_ratio }}
suggests {{ "bearish" if put_call_ratio > 1.2 else "neutral" }} market positioning.
{{ "Unusual put flow was detected, indicating institutional hedging." if unusual_flow_flag and unusual_flow_direction == "PUT" else "" }}
```
- Embeds this narrative → `v_consensus_options` (768-dim)
- Computes `analyst_options_divergence`:
```python
analyst_options_divergence = cosine_distance(v_consensus_analyst_base, v_consensus_options)
# High divergence = analyst and options market have very different expectations
# This itself is a signal modifier: high divergence → widen confidence intervals
```

### Step B9 — Embed All Consensus Vectors [Novelty 5 + Innovation 1]

- `v_consensus_bear`, `v_consensus_base`, `v_consensus_bull` — via FinBERT-Surprise
- `v_consensus_options` — same embedding pipeline
- All four upserted to Supabase `consensus_baselines`

---

## Pipeline C — Signal Scanner (every 15 min)

### Step C1 — Fetch Unprocessed Embeddings (unchanged)

`SELECT * FROM embeddings WHERE signal_id IS NULL`

### Step C2 — Pre-Announcement Drift Check [Innovation 7]

**Script**: `gcsv_engine/pre_drift_detector.py`

**What happens**:
- For each article with `days_to_next_earnings < 3`:
  - Fetches the ticker's 48h pre-event return from yfinance
  - Fetches the historical distribution of pre-earnings 48h returns for this ticker (rolling 3-year window)
  - Computes z-score: `pre_drift_z = (current_48h_return - mean) / std`
  - Flags if `|pre_drift_z| > 2.0` → `pre_drift_flag = True`
- `pre_drift_z` is passed as a feature to the decay model and as an input to the uncertainty scorer

### Step C3 — GCSV Triple Subtraction [Novelty 5 — unchanged]

```python
v_surprise_bear = v_actual - v_consensus_bear
v_surprise_base = v_actual - v_consensus_base
v_surprise_bull = v_actual - v_consensus_bull
```

### Step C4 — Transcript GCSV [Innovation 3]

**Script**: `gcsv_engine/transcript_gcsv.py`

**What happens** (only runs for earnings events with transcript available):
```python
v_surprise_prepared = v_prepared - v_consensus_base
v_surprise_qa       = v_qa       - v_consensus_base

# Divergence: how different are prepared vs Q&A surprise signals?
divergence_score = cosine_distance(v_surprise_prepared, v_surprise_qa)
# High divergence = management said one thing, hedged another in Q&A
# This is a negative soft prior on signal confidence
```

### Step C5 — Options Consensus Cross-Check [Innovation 1]

```python
v_surprise_options = v_actual - v_consensus_options

# If analyst and options surprise vectors point in opposite directions:
#   → signal is ambiguous; uncertainty_score increases
options_direction = sign(dot(v_surprise_options, positive_axis))
analyst_direction = sign(dot(v_surprise_base, positive_axis))
consensus_source_agreement = (options_direction == analyst_direction)
```

### Step C6 — Short Interest Modifier [Innovation 8]

**Script**: `gcsv_engine/short_interest_modifier.py`

**What happens**:
```python
short_interest_pct = supabase.fetch_short_interest(ticker)

# Hard override: BEARISH signal + high short interest + below MEDIUM magnitude
# → potential short squeeze; suppress signal
if (
    analyst_direction == -1          # BEARISH
    and short_interest_pct > 0.20   # > 20% of float shorted
    and magnitude_base < settings.SURPRISE_THRESHOLD_MEDIUM
):
    short_squeeze_risk = True
    # Signal downgraded to UNCERTAIN in uncertainty_scorer
```

`short_interest_pct` also appended to the decay model feature dict.

### Step C7 — Uncertainty Scoring [Novelty 5 — extended]

**Script**: `gcsv_engine/uncertainty_scorer.py`

**v3 additions** to the uncertainty score inputs:
- `transcript_divergence_score` [Innovation 3]: high Q&A/prepared divergence → increases uncertainty
- `consensus_source_agreement` [Innovation 1]: analyst/options direction mismatch → UNCERTAIN
- `short_squeeze_risk` [Innovation 8]: forced UNCERTAIN on squeeze conditions
- `pre_drift_flag` [Innovation 7]: high pre-drift → widens CI in uncertainty but doesn't auto-suppress

**Combined confidence logic**:
```python
if short_squeeze_risk or not consensus_source_agreement:
    confidence = "UNCERTAIN"
elif not direction_consensus_across_scenarios:
    confidence = "UNCERTAIN"
elif transcript_divergence_score > THRESH_HIGH_DIVERGENCE:
    confidence = max("LOW", one_tier_down(base_confidence))  # degrade by one tier
elif uncertainty_score < THRESH_LOW and pre_drift_z < 2.0:
    confidence = "HIGH"
else:
    confidence = classify_by_magnitude_variance()
```

### Step C8 — Regime-Gated Classification [Novelty 4 — unchanged]

Regime multipliers applied to surprise magnitude threshold.

### Step C9 — Decay Prediction [Novelty 2 — with new features]

XGBoost models now include `short_interest_pct`, `pre_drift_z`, `analyst_options_divergence`,
and `tone_drift_score` as features. All 9 quantile models run → {T1h, Tovernight, T5d} × {p10, p50, p90}.

### Step C10 — Kelly Criterion Sizing [Innovation 9]

**Script**: `execution/kelly_sizer.py`

**What happens**:
```python
# Fetch historical hit rate for this confidence tier + regime from accuracy_calibration table
hit_rate = db.fetch_hit_rate(confidence_tier=regime_adjusted_tier, regime=regime)

p50  = decay_predictions[best_horizon]["p50"]
p10  = decay_predictions[best_horizon]["p10"]
p90  = decay_predictions[best_horizon]["p90"]
odds = abs(p50) / (p90 - p10)   # return-to-risk ratio

f_star = (hit_rate * odds - (1 - hit_rate)) / odds

kelly_params = load_kelly_params()
f_applied = min(
    f_star * kelly_params["half_kelly_fraction"],
    kelly_params["max_allocation_cap"],
    kelly_params["per_regime_limits"][regime]
)
```

Output: `suggested_allocation_pct = max(0, f_applied)` — clamped at zero (never short Kelly).

### Step C11 — Contagion Propagation [Novelty 3 — unchanged]

BFS walk of contagion_edges from primary ticker → secondary signals with attenuation.

### Step C12 — Signal Assembly & Emission

**Script**: `signal_emitter/signal_builder.py`

**Full v3 signal object** (key fields):
```python
{
  # Core
  "ticker": "AAPL",
  "direction_label": "BEARISH",
  "signal_type": "standard",          # or "zero_consensus" for 8-K events without consensus

  # Surprise metrics (3 scenarios + options)
  "magnitude_base": 0.41,
  "magnitude_options": 0.38,
  "analyst_options_divergence": 0.12, # low → both agree; high → divergent expectations

  # Transcript analysis (Innovation 3)
  "transcript_divergence_score": 0.19, # high → Q&A contradicts prepared remarks
  "v_surprise_qa_direction": "BEARISH",

  # Insider signal (Innovation 4)
  "insider_buy_flag": False,
  "insider_buy_score": 0.0,

  # Short interest (Innovation 8)
  "short_interest_pct": 0.031,
  "short_squeeze_risk": False,

  # Tone drift (Innovation 5)
  "tone_drift_score": 0.41,
  "tone_drift_direction": "toward_hedging",

  # Pre-announcement drift (Innovation 7)
  "pre_drift_z": 1.3,
  "pre_drift_flag": False,

  # Uncertainty (Novelty 5)
  "confidence": "HIGH",
  "uncertainty_score": 0.009,
  "direction_consensus": True,
  "consensus_source_agreement": True,

  # Regime (Novelty 4)
  "regime": "Risk-Off Volatile",
  "regime_adjusted_tier": "MEDIUM",

  # Decay predictions (Novelty 2)
  "predicted_returns": {
    "T1h":        {"p10": -0.021, "p50": -0.009, "p90": -0.002},
    "Tovernight": {"p10": -0.034, "p50": -0.018, "p90": -0.005},
    "T5d":        {"p10": -0.019, "p50": -0.006, "p90": +0.004}
  },
  "best_horizon": "Tovernight",

  # Kelly sizing (Innovation 9)
  "suggested_allocation_pct": 0.038,   # 3.8% of portfolio
  "kelly_half_f": 0.019,

  # Contagion (Novelty 3)
  "secondary_signals": [...],

  # Metadata
  "embedding_model": "finbert-surprise",
  "signal_created_at": "2025-08-14T18:31:52Z"
}
```

**Alpaca paper trading [Innovation 10]**:
For HIGH/MEDIUM confidence signals with `suggested_allocation_pct > 0`:
```
signal → alpaca_executor.py → Alpaca paper order (Kelly-sized notional)
                            → fill recorded in alpaca_fills table
                            → fill price written to signal_outcome for slippage tracking
```

---

## Pipeline G — Signal Outcome Evaluation [Innovation 6]
*(Daily — `evaluate_signals.yml`)*

### Step G1 — Identify Signals Due for Evaluation

```sql
SELECT id, ticker, signal_created_at, predicted_returns, direction
FROM trading_signals
WHERE signal_created_at < NOW() - INTERVAL '24 hours'
  AND id NOT IN (SELECT signal_id FROM signal_outcome WHERE horizon = 'T24h')
```

### Step G2 — Fetch Realised Returns

`outcome_recorder.py` calls Polygon.io for each ticker:
- T+24h return: close price 1 trading day after `signal_created_at` vs close at signal time
- T+5d return: close price 5 trading days after signal

### Step G3 — Compute Accuracy Score

```python
accuracy_score_24h = 1 if (realised_24h * predicted_direction > 0) else 0
return_error_24h   = abs(realised_24h - predicted_T1d_p50)
ci_covered_24h     = (p10_T1d <= realised_24h <= p90_T1d)

# Write to signal_outcome table
signal_outcome = {
    "signal_id": id,
    "horizon": "T24h",
    "realised_return": realised_24h,
    "accuracy_score": accuracy_score_24h,
    "return_error": return_error_24h,
    "ci_covered": ci_covered_24h,
}
```

### Step G4 — Drift Alert [Innovation 6]

`drift_alerter.py` computes rolling 4-week accuracy per (regime, sector, confidence_tier) group.
If any group drops > 15 percentage points from its 12-week baseline:
- Fires Slack alert with group details and current vs baseline hit rate
- Writes drift event to `data_quality_log`
- Sets a `RETRAIN_NEEDED` flag in Supabase `calibration` table, which triggers
  `train_decay_model.yml` workflow_dispatch on next run

---

## Pipeline H — Tone Baseline Update [Innovation 5]
*(Weekly — `update_tone_baselines.yml`)*

### Step H1 — Fetch New Transcripts

For each tracked ticker that has reported earnings in the past week, fetch transcript from Finnhub.

### Step H2 — Embed + Update Centroid

`transcript_fetcher.py` → `embed_transcript.py` → `centroid_updater.py`

Welford online mean update:
```python
# Numerically stable incremental mean — no need to store all historical embeddings
n_new = centroid_record["call_count"] + 1
delta = current_embedding - old_centroid
new_centroid = old_centroid + delta / n_new
```

Upserts to `executive_centroids` table. The tone drift detection in Pipeline B now uses
the updated centroid on the next run.

---

## Full v3 Data Flow

```
EDGAR 8-K ──────────────────────────────────────────────────────────────────────►┐
RSS / Finnhub News ──────────────────────────────────────────────────────────────►│
Global IR Feeds (TSMC/Samsung/ASML) ─────────────────────────────────────────────►│  raw_articles
Transcript (Finnhub) ────────────────────────────────────────────────────────────►│  (Supabase)
                                                                                  │
         ┌────────────────────────────────────────────────────────────────────────┘
         │ clean → tag → split transcript → embed (FinBERT-Surprise)
         ▼
   embeddings table: v_actual + v_prepared + v_qa
         │
         │         consensus_baselines (Supabase)
         │         ↑ built daily:
         │         │  Analyst estimates → 3× narratives (regime-conditioned, insider-modified, tone-drift-prior)
         │         │  Options market → v_consensus_options + analyst_options_divergence
         │         │  All 4 vectors embedded + stored
         │         │
         ▼         ▼
   GCSV ×3 (bear/base/bull) + options cross-check + transcript dual-GCSV
         │
         ├── Pre-drift detector (z-score 48h pre-earnings return)
         ├── Short interest modifier (hard override if squeeze risk)
         ├── Uncertainty scorer (variance + direction consensus + all modifiers)
         ├── Regime-gated classifier
         ├── XGBoost decay prediction (9 models, new features)
         ├── Kelly Criterion sizer
         └── Contagion propagator → secondary signals
         │
         ▼
   trading_signals (Supabase) ──────────────────────────────────────────────────►
         │                                                                        │
         ├── Slack alert (HIGH/MEDIUM)                              Dashboard (React)
         └── Alpaca paper order (Kelly-sized)    signal_outcome feedback loop
                                                 (daily outcome evaluation)
```

---

## Latency Profile (v3)

| Event Type | Trigger | End-to-End Latency |
|---|---|---|
| Intraday earnings (market hours) | Finnhub WebSocket → workflow_dispatch | ~30–60 sec |
| EDGAR 8-K filing (any time) | EDGAR cron poll or WebSocket | ~2–5 min (EDGAR poll interval) |
| Pre-market earnings | Cron sweep (sufficient; hours before open) | < 15 min |
| Known macro release | Macro calendar pre-warm (60s advance) | < 30 sec |
| Transcript processing | Triggered after earnings event detected | ~5–10 min (Finnhub transcript availability) |
| HF embedding (warm model) | — | ~200ms |
| HF embedding (cold start) | ONNX fallback triggered | ~800ms |
| Signal outcome evaluation | Daily cron (non-latency-sensitive) | 24h + 5d post-signal |
