<div align="center">

# ⚡ MarketPulse AI v3
### Expectation-Aware Institutional Alpha Engine & Indo-Global Cross-Market Transmission Network

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.2%2B-EE4C2C.svg?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![FinBERT](https://img.shields.io/badge/HuggingFace-FinBERT-FFD21E.svg?logo=huggingface&logoColor=black)](https://huggingface.co/ProsusAI/finbert)
[![XGBoost](https://img.shields.io/badge/XGBoost-Quantile--Reg-217346.svg)](https://xgboost.readthedocs.io/)
[![Supabase pgvector](https://img.shields.io/badge/Supabase-pgvector--768D-3ECF8E.svg?logo=supabase&logoColor=white)](https://supabase.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Terminal-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*A production-grade algorithmic quantitative finance platform bridging real-time expectation-aware financial NLP, 768-D geometric vector subtraction, macro regime switching, cross-asset contagion, and cross-market Indo-Global multicorrelation modeling.*

</div>

---

## 📌 Executive Summary

Traditional financial Natural Language Processing (NLP) fundamentally fails in capital markets because it evaluates corporate disclosures and news in a **semantic vacuum**. When a mega-cap tech bellwether reports **+18% year-over-year revenue growth**, standard sentiment classifiers (VADER, Loughran-McDonald dictionaries, naive FinBERT) classify the text as overwhelmingly **bullish**. However, if Wall Street consensus priced in **+24% growth**, the equity drops **-7%** upon release.

**MarketPulse AI** solves this systemic mispricing through **Geometric Consensus Subtraction Vectors (GCSV)**. Rather than scoring raw text sentiment:
$$\mathbf{v}_{\text{surprise}} = \mathbf{v}_{\text{actual}} - \mathbf{v}_{\text{consensus}}$$

Where $\mathbf{v}_{\text{actual}} \in \mathbb{R}^{768}$ is the FinBERT latent embedding of the live disclosure, and $\mathbf{v}_{\text{consensus}} \in \mathbb{R}^{768}$ is the dynamic multi-scenario Wall Street expectation manifold anchored across Bear, Base, and Bull trajectories.

---

## 🏛 10 Core Architectural Innovations

| # | Innovation | Technical Realization |
|---|---|---|
| **1** | **Geometric Consensus Subtraction (GCSV)** | 768-D differential vector operations ($\mathbf{v}_{\text{actual}} - \mathbf{v}_{\text{consensus}}$) isolating net unexpected alpha. |
| **2** | **Analyst-Options Expectations Divergence** | Cross-entropy comparison between sell-side analyst consensus and options risk-neutral density ($D_{KL}(P_{\text{opt}} \parallel P_{\text{analyst}})$). |
| **3** | **Transcript Q&A Separation & Tone Divergence** | Isolates prepared remarks from spontaneous executive Q&A; flags managerial hedging ($1 - \text{cosine\_sim}(\mathbf{v}_{\text{prep}}, \mathbf{v}_{\text{qa}}) > 0.25$). |
| **4** | **Macroeconomic Regime Conditioning** | Real-time 4-state classifier (CBOE VIX, 10Y-3M Treasury Yield Slope, SPX 20d Trend) gating signal execution tiers. |
| **5** | **Welford Online Tone Drift Tracker** | Tracks individual C-suite vocal centroids across rolling earnings calls via Welford's algorithm to catch subtle tone shifts. |
| **6** | **Cross-Asset Contagion Directed Graph** | NetworkX supply-chain graph ($ASML \to TSM \to NVDA \to MSFT/AAPL$) with BFS shock propagation and attenuation. |
| **7** | **Multi-Horizon Quantile Alpha Decay** | 9 XGBoost quantile regressors predicting returns at $T+1\text{h}$, $T+\text{overnight}$, $T+5\text{d}$ at 10th, 50th, and 90th percentiles. |
| **8** | **Short-Interest Squeeze Shield** | Asymmetric volume & days-to-cover filter preventing false bearish entries on heavily shorted equities. |
| **9** | **Calibrated Half-Kelly Position Sizing** | Dynamic fractional Kelly allocator bounded by model confidence and downside tail risk ($f^*_{\text{half}} \le 10\%$). |
| **10** | **Indo-Global Multicorrelation Engine** | High-dimensional cross-market lead-lag transmission modeling the impact of US/global macro variables on NIFTY 50, BANK NIFTY, and NIFTY IT. |

---

## 🇮🇳 Indo-Global Cross-Market Transmission & Multicorrelation

Indian equity markets (NSE/BSE) exhibit profound structural sensitivity to global macro drivers, yet simple bivariate correlations fail to capture simultaneous regime shifts. MarketPulse AI integrates a calibrated **Multivariate OLS & Lead-Lag Transmission Engine**:

### 1. Calibrated Transmission Elasticities ($\beta$)

$$\Delta \text{NIFTY} = \alpha + \beta_{\text{SPX}} \Delta \text{SPX} + \beta_{\text{NDX}} \Delta \text{NDX} + \beta_{\text{Oil}} \Delta \text{Brent} + \beta_{\text{US10Y}} \Delta \text{US10Y} + \beta_{\text{DXY}} \Delta \text{DXY} + \epsilon$$

* **NIFTY 50** ($R^2 = 0.58$): Highly responsive to S&P 500 ($\beta = +0.42$) and Brent Crude ($\beta = -0.31$, energy import dependency).
* **NIFTY IT** ($R^2 = 0.74$): Predominantly driven by NASDAQ-100 ($\beta = +0.76$, US enterprise tech spending) with a USD tailwind ($\beta_{\text{DXY}} = +0.22$).
* **BANK NIFTY** ($R^2 = 0.49$): Most sensitive to US 10Y Yields ($\beta = -0.34$, global liquidity tightening) and S&P 500 ($\beta = +0.38$).

### 2. Time-Zone Lead-Lag Dynamics
Because the US market closes at 01:30 / 02:30 IST and Indian markets open at 09:15 IST, US overnight price action acts as a **deterministic lead** ($Lag \approx +7.5\text{h}$) for morning gap openings in NIFTY 50 and GIFT NIFTY.

---

## 💻 Streamlit Institutional Terminal

The platform features an 8-tab, Bloomberg Dark Terminal-themed Streamlit dashboard (`streamlit_app.py`):

1. **🔴 Live Signals & Ingestion**: Real-time Supabase signal feed, Finnhub news & SEC EDGAR ingestion triggers, signal blotters.
2. **📐 GCSV Engine & Vector Subtraction**: Visual 768-D latent geometry, consensus scenario anchors, FinBERT polarity fusion.
3. **🎙️ Q&A Separation & Tone Drift**: Prepared vs Q&A divergence metrics, Welford C-suite executive language drift monitoring.
4. **🌐 Contagion & Squeeze Shields**: Interactive network graph shock propagation and short squeeze protection shields.
5. **⌛ Quantile Alpha Decay**: Multi-horizon XGBoost prediction fan charts ($T+1\text{h}$, $T+\text{overnight}$, $T+5\text{d}$) with 80% CI.
6. **⚖️ Kelly Sizing & Execution**: Fractional Kelly sizing surface, Alpaca paper trading broker execution gateway.
7. **🇮🇳 Indo-Global & Multicorrelation**: Interactive correlation heatmaps, partial correlation tables, lead-lag curves, and live Indian market impact simulator.
8. **📊 Empirical Benchmark & IEEE Validation**: Complete 18-month backtest matrix, equity curves, and publication figures.

---

## 📂 Repository Structure

```
Market_Pulse_AI/
├── .github/workflows/
│   └── ingest_news.yml           # Automated cron news ingestion pipeline
├── .streamlit/
│   └── config.toml               # Institutional Bloomberg Dark UI configuration
├── api/
│   ├── __init__.py
│   └── main.py                   # FastAPI REST service (/api/signals/latest)
├── config/
│   ├── __init__.py
│   └── settings.py               # Supabase, API credentials & threshold params
├── consensus/
│   ├── __init__.py
│   ├── baseline_aggregator.py    # Wall Street consensus EPS & price target fetcher
│   └── narrative_generator.py    # Generates 3-state (Bear/Base/Bull) semantic narratives
├── contagion_graph/
│   ├── __init__.py
│   ├── graph_builder.py          # NetworkX semiconductor/tech supply chain topology
│   ├── indian_market_engine.py   # Indo-Global multicorrelation & lead-lag engine
│   └── propagator.py             # BFS geometric attenuation shock engine
├── database/
│   └── schema.sql                # Complete Supabase pgvector (768-D) schema
├── decay_model/
│   ├── __init__.py
│   ├── feature_builder.py        # 10-feature assembly for alpha decay models
│   └── trainer.py                # 9 XGBoost Quantile Regressors (Pinball loss)
├── evaluations/
│   ├── benchmark_runner.py       # 1,250-event empirical evaluation runner
│   ├── empirical_evaluation_matrix.csv
│   └── figures/                  # 8 publication-grade 300 DPI figures
│       ├── fig1_gcsv_latent_geometry.png
│       ├── fig2_regime_performance.png
│       ├── fig3_temporal_decay_fan.png
│       ├── fig4_equity_curves.png
│       ├── fig5_kelly_sizing_surface.png
│       ├── fig6_contagion_network.png
│       ├── fig7_indo_global_correlation_heatmap.png
│       └── fig8_multicorrelation_lead_lag.png
├── execution/
│   ├── __init__.py
│   └── alpaca_executor.py        # Alpaca Paper Trading REST execution gateway
├── gcsv_engine/
│   ├── __init__.py
│   ├── decay_mapper.py           # Multi-horizon return mapper
│   ├── pre_drift_detector.py     # 48-hour pre-announcement drift z-score
│   ├── short_interest_modifier.py# Short-squeeze asymmetric modifier
│   ├── transcript_gcsv.py        # Prepared vs Q&A divergence scorer
│   ├── uncertainty_scorer.py     # FinBERT fusion & latent uncertainty classifier
│   └── vector_ops.py             # 768-D vector subtraction & magnitude
├── ingestion/
│   ├── __init__.py
│   ├── edgar_fetcher.py          # SEC EDGAR 8-K / 10-Q filing ingestion
│   └── regime_classifier.py      # Macro regime classification wrapper
├── portfolio/
│   ├── __init__.py
│   └── kelly_sizer.py            # Half-Kelly sizing with downside risk floors
├── reports/
│   ├── MarketPulse_AI_IEEE_Research_Paper.docx # 14-page IEEE Transactions paper
│   ├── MarketPulse_AI_Streamlit_App_Operational_Manual.docx
│   ├── DEFENSE_PRESENTATION_SCRIPT.docx
│   ├── PRESENTATION_DEFENSE_GUIDE.md
│   └── STREAMLIT_APP_OPERATIONAL_MANUAL.md
├── scripts/
│   ├── __init__.py
│   ├── fetch_news.py             # Finnhub live news fetcher
│   ├── generate_app_manual_docx.py
│   ├── generate_defense_docx.py
│   ├── generate_ieee_paper.py
│   ├── models.py
│   ├── process_articles.py       # End-to-end signal assembly pipeline
│   ├── regime_classifier.py      # VIX, Yield Slope & SPX 20d classifier
│   ├── surprise_scorer.py
│   └── test_ml.py
├── signal_emitter/
│   ├── __init__.py
│   └── signal_builder.py         # Full v3 signal generator with semantic anchors
├── signal_feedback/
│   ├── __init__.py
│   └── outcome_recorder.py       # 24-hour realized return evaluation feedback loop
├── strategies/
│   ├── __init__.py
│   └── finbert_analyzer.py       # FinBERT classification head inference
├── tone_drift/
│   ├── __init__.py
│   ├── drift_scorer.py           # Executive tone drift calculator
│   └── executive_tracker.py      # Welford online algorithm centroid tracker
├── vectorizer/
│   ├── __init__.py
│   ├── embed_article.py          # Overlapping chunking & mean pooling
│   ├── embed_consensus.py        # 3-state consensus narrative vectorizer
│   └── hf_client.py              # FinBERT 768-D feature extractor
├── web/                          # Next.js 14 Real-Time Web Dashboard
│   ├── src/app/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   └── src/lib/supabase.ts
├── webhook_receiver/
│   ├── __init__.py
│   ├── main.py                   # FastAPI Finnhub WebSocket daemon
│   ├── render.yaml               # Cloud deployment configuration
│   └── requirements.txt
├── requirements.txt              # Root Python dependencies
├── streamlit_app.py              # Main Bloomberg Dark Streamlit application
└── README.md
```

---

## ⚙️ Quickstart & Installation

### 1. Prerequisites
* Python 3.10+ (tested on Python 3.12 / 3.13)
* Git
* Supabase Account with `pgvector` enabled

### 2. Clone Repository
```bash
git clone https://github.com/Jay-salot-2210/MarketPulseAI.git
cd MarketPulseAI
```

### 3. Create & Activate Virtual Environment
```bash
python -m venv .venv

# Windows:
.venv\Scripts\activate

# Linux / macOS:
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Environment Configuration
Create a `.env` file in the project root:
```env
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY="your-supabase-service-or-anon-key"
FINNHUB_API_KEY="your-finnhub-api-key"
HF_API_TOKEN="your-huggingface-token"
ALPHA_VANTAGE_API_KEY="your-alpha-vantage-key"
ALPACA_API_KEY="your-alpaca-paper-api-key"
ALPACA_SECRET_KEY="your-alpaca-paper-secret-key"
```

### 6. Database Initialization
Execute the SQL script in your Supabase SQL Editor:
```sql
-- Located at database/schema.sql
-- Enables vector extension and creates all 6 core tables
```

### 7. Launch the Streamlit Terminal
```bash
streamlit run streamlit_app.py
```
Open your browser at `http://localhost:8501`.

### 8. Run FastAPI Service (Optional)
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📈 Empirical Performance Summary

Benchmarked across 1,250 earnings disclosures and 8-K events over an 18-month simulated out-of-sample window (with 8 bps institutional slippage):

| Architecture | Directional Hit Rate | Macro F1 | Sharpe Ratio | Sortino Ratio | Max Drawdown |
|---|:---:|:---:|:---:|:---:|:---:|
| Naive FinBERT (Vacuum) | 51.4% | 0.508 | 0.35 | 0.42 | -24.8% |
| TF-IDF + Ridge | 54.8% | 0.539 | 0.72 | 0.88 | -19.4% |
| FinBERT + Logistic | 58.2% | 0.574 | 0.98 | 1.15 | -16.2% |
| GCSV-Base (Static Consensus) | 67.4% | 0.669 | 1.48 | 1.82 | -12.1% |
| **MarketPulse AI v3 (Proposed)** | **72.6%** | **0.721** | **2.34** | **3.12** | **-7.4%** |

---

## 📜 Academic & Defense Deliverables

All deliverables are generated and stored under `reports/`:
* **`MarketPulse_AI_IEEE_Research_Paper.docx`**: Full IEEE Transactions on Computational Finance format research paper including Section VI on Indo-Global Multicorrelation and Figures 1–8.
* **`MarketPulse_AI_Streamlit_App_Operational_Manual.docx` & `.md`**: Step-by-step operational manual for each tab in the terminal.
* **`DEFENSE_PRESENTATION_SCRIPT.docx` & `PRESENTATION_DEFENSE_GUIDE.md`**: Master defense guide and Q&A covering 10 technical examination questions.

---

## 📄 License
This project is licensed under the MIT License. See `LICENSE` for details.

*Disclaimer: MarketPulse AI is an advanced research and engineering platform designed for academic and quantitative testing. Past simulated performance is no guarantee of future trading results.*
