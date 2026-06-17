# MarketPulse AI — Problem Statement & Proposed Solution (v3)

---

## 1. The Core Problem: Markets React to Surprise, Not to News

Every financial NLP system built today makes the same foundational mistake: it reads news in a vacuum.
It scores a headline as "positive" or "negative" based on words alone, completely ignoring the single
most important variable in market price formation — what was already expected.

Financial markets are not absolute systems. They are expectation-clearing machines. Prices already embed
every piece of information the market collectively anticipates. A company posting 20% revenue growth can
trigger a violent sell-off if analysts expected 25%. A company posting a loss can trigger a relief rally
if the loss was smaller than feared. In both cases, a traditional sentiment model scores the wrong
direction entirely.

### The Seven Structural Failures of Existing Systems

**Failure 1 — The Vacuum Effect**
Standard NLP pipelines assign a sentiment score to raw news text with no knowledge of pre-existing
market expectations, analyst consensus, or options market pricing. The output is systematically
misleading because it has no reference frame.

**Failure 2 — The Valuation Blindspot**
A 10% revenue beat sounds positive in isolation. If consensus was expecting 18%, it is a catastrophic
miss. No sentiment score captures this. The model fires a buy signal; the market sells off 8%. This is
not model noise — it is a deterministic flaw in the architecture.

**Failure 3 — Single-Source Consensus**
Analyst EPS estimates are one view of market expectations. Options market pricing — implied volatility,
put/call ratios, unusual flow — is a faster, money-weighted, forward-looking second view. Systems that
read only analyst estimates are missing the half of the market that speaks through derivatives.

**Failure 4 — Temporal Disconnect**
A surprise at 4:30 PM after market close behaves differently from the same surprise at 11:00 AM during
peak intraday liquidity. Static thresholds calibrated at a single point in time cannot adapt to market
microstructure. And no system models how alpha decays differently across overnight, intraday, and
multi-day correction windows — they treat all signals as equally urgent.

**Failure 5 — Static Thresholds on a Dynamic Market**
The market's sensitivity to surprise changes continuously with regime. A surprise classified HIGH
confidence in a low-volatility bull market is noise in the middle of a systemic correction. Static
classifiers cannot track this.

**Failure 6 — No Cross-Asset Contagion Awareness**
Individual company surprises propagate. A TSMC earnings miss moves NVDA, AMD, AMAT, and ASML within
hours — before English-language articles even publish. No existing NLP trading system models this
contagion graph. And no system catches the signal directly at the primary source (EDGAR 8-K filings)
before RSS feeds republish it.

**Failure 7 — No Signal Accountability**
Existing systems emit signals but never measure whether they were correct. Without a feedback loop
connecting predicted returns to realised returns, there is no way to detect model drift, identify
which regime/sector combinations produce reliable signals, or progressively improve the model over time.

---

## 2. The Solution: MarketPulse AI v3

MarketPulse AI is an expectation-aware, self-improving, regime-conditioned, outcome-tracked alpha
generation framework. It is built on the base GCSV architecture extended by ten integrated innovations
across data sourcing, model intelligence, signal evaluation, and execution.

### Base Architecture: Generative Counterfactual Surprise Vectoring (GCSV)

The system computes surprise as the geometric distance between two representations in transformer
latent space:

  v_actual     — FinBERT-Surprise embedding of the real published event text
  v_consensus  — FinBERT-Surprise embedding of a synthetically generated "zero-surprise" narrative

  v_surprise = v_actual − v_consensus

The resulting vector isolates only the structural narrative anomalies that the market had not priced in.

---

## 3. The Ten Integrated Innovations

### Innovation 1 — Dual-Source Consensus (Analyst + Options)
The options market often prices surprises before analysts update their models. The system builds two
independent consensus vectors per ticker: v_consensus_analyst (from EPS/revenue estimates) and
v_consensus_options (from implied volatility term structure, put/call ratio, and unusual options flow).
The divergence between the two consensus sources is itself a signal: when analysts and options markets
disagree sharply on expectations, that uncertainty amplifies the value of the GCSV surprise vector.

### Innovation 2 — SEC EDGAR 8-K Primary Source Ingestion
EDGAR 8-K filings are the legally mandated primary source for all material corporate events — earnings,
guidance cuts, CEO changes, material contracts. The system plugs directly into EDGAR's full-text search
API to receive filings within minutes of submission, ahead of RSS feeds and news wires. Events with no
analyst consensus (CEO resignation, unexpected contract loss) are processed with a special single-vector
mode: v_surprise = v_actual with no subtraction, classified purely on absolute magnitude.

### Innovation 3 — Earnings Call Q&A Separation
Prepared remarks are legal-reviewed and rehearsed. Analyst Q&A is live and unscripted. The system
splits transcripts into two segments and embeds them independently: v_prepared and v_qa. GCSV is run
on both. The divergence between the two surprise vectors — management said X in prepared remarks but
hedged heavily under Q&A pressure — is a leading indicator of guidance revision risk that no
point-in-time article captures.

### Innovation 4 — Scoped Insider Trading Signal
SEC Form 4 open-market purchase filings within 30 days of an earnings date, above a materiality
threshold relative to the insider's prior trading history, are a legitimate leading indicator. The
system flags these as a soft prior that modifies the consensus baseline: if multiple insiders are
buying, the bull consensus scenario is weighted upward. Routine plan sales and grants are excluded
entirely to control false positive rate.

### Innovation 5 — Management Tone Drift Detection
Each earnings call produces a FinBERT-Surprise embedding for the executive who delivered it. The
system maintains a per-executive embedding centroid built from historical transcripts. A CFO whose
language centroid drifts toward hedging vocabulary across three consecutive quarters is a leading
indicator of a miss — before any numerical signal exists. The tone_drift_score feeds into the
consensus baseline as a forward-looking soft prior.

### Innovation 6 — Signal Self-Evaluation Feedback Loop
24 hours and 5 days after every signal, the system fetches the realised price return, computes the
accuracy of the predicted return, and writes a signal_outcome record. Over time this builds a
calibration dataset: which regime + sector + confidence tier combinations produce reliable signals,
and which produce noise. Categories with poor historical accuracy are automatically down-weighted in
the signal tier classifier.

### Innovation 7 — Pre-Announcement Drift Detector
If a stock moves outside 2 standard deviations of its historical pre-earnings distribution in the
48 hours before an earnings release, information may be leaking. A high pre-announcement drift z-score
either confirms the expected surprise is partially priced in (reducing alpha window) or warns of
information leakage (which modifies signal confidence downward). This feeds directly into the
uncertainty scorer as an additional input dimension.

### Innovation 8 — Short Interest Direction Modifier
A bearish surprise signal on a stock with 30%+ short interest may trigger a short squeeze rather
than a continuation sell. The system fetches biweekly FINRA short interest data and applies a hard
override: if direction is BEARISH and short_interest_pct exceeds a threshold and magnitude is below
MEDIUM, the signal is downgraded to UNCERTAIN. Short interest is also a feature in the decay model
— high short interest increases predicted return volatility at all horizons.

### Innovation 9 — Kelly Criterion Position Sizing
The system outputs not just direction and confidence but an optimal position size. Using the Kelly
Criterion with the predicted return (p50 from the decay model) and confidence interval (p10/p90),
the system computes suggested_allocation_pct — the fraction of portfolio to commit to the position.
This converts a signal service into an actionable execution guide.

### Innovation 10 — Signal Performance Dashboard + Alpaca Paper Trading
A React dashboard visualises signal accuracy by regime, sector, horizon, and confidence tier in
real time from the signal_outcome table. Model drift is immediately visible — a drop in hit rate
for a specific configuration triggers a retraining alert. All HIGH/MEDIUM signals are simultaneously
forwarded to an Alpaca paper trading account with Kelly-sized position quantities, producing forward-
tested P&L with real slippage — far more credible evidence of system quality than backtests.

---

## 4. What Was Evaluated and Rejected (Scoped)

**Cross-lingual full NLP translation (from suggestion #10)**: Full multilingual ingestion with
Japanese/Korean/Taiwanese filing parsing and translation was evaluated and scoped down. The accepted
version adds English-language investor relations RSS feeds for TSMC, Samsung, and ASML only — these
three companies already publish English IR content and represent the highest-impact non-US events for
the US tech contagion graph. The full translation layer introduces unreliable free API dependencies
and inconsistent data quality that would degrade signal quality rather than improve it.

**Full Form 4 ingestion (from suggestion #4)**: Routine 10b5-1 plan sales, stock compensation grants,
and tax-related sells dominate Form 4 volume and are uninformative. Only open-market purchases
within 30 days of earnings above a materiality threshold are ingested. This scope control is what
makes the insider signal signal-positive rather than noise.

---

## 5. System Capabilities Summary

| Dimension | v1 (Base) | v2 (+5 Novelties) | v3 (+10 Innovations) |
|---|---|---|---|
| Consensus sources | Analyst estimates only | Analyst only | Analyst + Options market |
| Primary data source | RSS feeds | RSS feeds | RSS + EDGAR 8-K direct |
| Event types | Earnings articles | Earnings articles | Articles + transcripts + 8-K + insider + drift |
| Signal confidence | Magnitude threshold | Uncertainty scoring | Uncertainty + pre-drift + short interest + tone drift |
| Position guidance | None | None | Kelly Criterion sizing |
| Outcome tracking | None | None | signal_outcome feedback loop |
| Execution | Webhook only | Webhook only | Webhook + Alpaca paper trading |
| Monitoring | Supabase tables | Supabase tables | Live React dashboard |
| Contagion | US tickers | US tickers | US tickers + TSMC/Samsung/ASML English IR |
