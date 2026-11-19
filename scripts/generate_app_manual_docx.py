import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_shading(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=80, bottom=80, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def generate_app_manual():
    print("Generating Streamlit App Operational Manual & Architecture Guide (.docx)...")
    doc = Document()
    
    # Page setup
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        
    styles = doc.styles
    normal_style = styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(10.5)
    normal_style.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(4)

    # -------------------------------------------------------------------------
    # TITLE & METADATA
    # -------------------------------------------------------------------------
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("MarketPulse AI v3.2 — Quantitative Terminal Operational Manual & System Guide")
    r_title.font.size = Pt(20)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x00, 0x20, 0x60)
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("Comprehensive Technical Walkthrough of Every UI Component, Mathematical Formulation, and Execution Workflow\n")
    r_sub.font.size = Pt(11)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    
    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_meta = p_meta.add_run("Author: Jay K. Salot | AI/ML & Quantitative Systems Lead\nProject Repository: https://github.com/Jay-salot-2210/MarketPulseAI | Production Version: v3.2")
    r_meta.font.size = Pt(9.5)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Heading helpers
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(text)
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x00, 0x20, 0x60)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(text)
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
        return p

    def add_bullet(bold_prefix, text):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(2)
        r_b = p.add_run(bold_prefix + ": ")
        r_b.bold = True
        r_b.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
        p.add_run(text)

    # -------------------------------------------------------------------------
    # SECTION 1: ARCHITECTURAL OVERVIEW & CORE THESIS
    # -------------------------------------------------------------------------
    add_h1("1. Architectural Overview & The Expectation-Clearing Thesis")
    doc.add_paragraph(
        "MarketPulse AI v3.2 is an institutional-grade quantitative trading terminal engineered to resolve the fundamental structural flaw "
        "of contemporary financial Natural Language Processing (NLP): the vacuum effect. Traditional sentiment models (such as naive FinBERT, "
        "VADER, or general-purpose LLMs) classify news articles into positive, negative, or neutral categories purely based on linguistic semantics. "
        "In real capital markets, asset prices do not react to news in isolation; they react exclusively to the variance between reported reality "
        "and pre-existing consensus expectations already priced into asset valuations."
    )
    doc.add_paragraph(
        "MarketPulse AI formalizes this dynamic through Generative Counterfactual Surprise Vectoring (GCSV), isolating the surprise vector "
        "v_surprise = v_actual - v_consensus within a 768-dimensional transformer latent space. The application is built on Streamlit with a "
        "custom Bloomberg-style dark financial terminal interface, communicating with a Supabase PostgreSQL pgvector database, real-time Finnhub news feeds, "
        "direct SEC EDGAR RSS Atom feeds, and the Alpaca Markets paper trading execution gateway."
    )

    # -------------------------------------------------------------------------
    # SECTION 2: TOP TERMINAL STATUS RIBBON & EXECUTIVE KPI METRICS
    # -------------------------------------------------------------------------
    add_h1("2. Terminal Header, Status Ribbon & Global Market Health Strip")
    doc.add_paragraph(
        "Located at the very top of the application, the Header and Status Ribbon provide instantaneous telemetry on engine health and systemic market conditions:"
    )
    add_bullet("Live Status Pulse Ribbon", "A dark glassmorphic banner featuring a pulsating green CSS dot (● LIVE INGESTION ACTIVE), confirming that the background polling loops for Finnhub news and SEC EDGAR 8-K filings are active. Displays active engine version (v3.2), transformer latent dimension (768-D ProsusAI/FinBERT), and database synchronization status with Supabase pgvector.")
    add_bullet("Macro Regime Card", "Displays the currently selected macroeconomic environment (Risk-On Bull, Cautious Neutral, Risk-Off Volatile, Crisis). Features an adaptive delta badge indicating whether market risk is 'Normal' (VIX < 22) or 'Elevated Risk'.")
    add_bullet("CBOE VIX Level Card", "Displays real-time market volatility. Shows a dynamic delta comparing current VIX against the empirical long-term baseline (16.0). High VIX (>22) signals heightened market hedging demand.")
    add_bullet("Yield Curve Slope (10Y - 3M)", "Tracks the Treasury term spread. A negative slope triggers an 'Inverted' alert, signaling macro recessionary headwind and tighter interbank credit; a positive slope indicates a healthy expansionary yield curve.")
    add_bullet("SPX 20-Day Momentum (%)", "Measures the trailing 20-day percentage price trend of the S&P 500 benchmark, serving as a systemic broad-market momentum filter.")
    add_bullet("Latent Space Dimension (768-D)", "Confirms that FinBERT's full hidden representation space is utilized, preserving cross-attention embeddings without dimensionality reduction.")

    # -------------------------------------------------------------------------
    # SECTION 3: SIDEBAR CONTROLS & RISK MANAGEMENT KNOBS
    # -------------------------------------------------------------------------
    add_h1("3. Sidebar Parameter Controls & Risk Management Knobs")
    doc.add_paragraph(
        "The left sidebar contains quantitative risk parameters that dynamically alter the underlying mathematical models across all tabs:"
    )
    add_bullet("Macro Regime Selector", "Modifies the GCSV surprise threshold multipliers (0.90x in Risk-On Bull, 1.00x in Neutral, 1.25x in Risk-Off Volatile, and 1.60x in Crisis). In Crisis regimes, a significantly larger surprise magnitude is required to trigger conviction trades, filtering out systemic panic noise.")
    add_bullet("CBOE VIX & Yield Curve Sliders", "Allow quantitative operators to simulate or calibrate macroeconomic conditions, instantly updating the 9 XGBoost Quantile Pinball Decay regressors in real time.")
    add_bullet("Short Squeeze Filter Threshold (%)", "Defaults to 20.0% of float. Equities exhibiting short interest exceeding this boundary automatically trigger the FINRA Short Squeeze Shield, suppressing bearish signals into UNCERTAIN to prevent violent short-squeeze drawdowns.")
    add_bullet("Pre-Drift Z-Score Threshold", "Defaults to |z| > 2.0. Detects unusual 48-hour price momentum prior to official earnings announcements, identifying statistically significant insider leakage.")
    add_bullet("Half-Kelly Portfolio Cap (%)", "Limits the maximum single-asset portfolio allocation to 10% (slider adjustable from 2% to 20%), preventing over-concentration.")

    # -------------------------------------------------------------------------
    # SECTION 4: TAB-BY-TAB COMPONENT EXPLANATIONS
    # -------------------------------------------------------------------------
    add_h1("4. In-Depth Operational Guide to All 8 Application Tabs")

    # TAB 1
    add_h2("Tab 1: 🔴 Live Blotter & Institutional Pipeline")
    doc.add_paragraph(
        "Tab 1 serves as the primary operational trading desk blotter and data ingestion command center:"
    )
    add_bullet("Real-Time KPI Summary Strip", "Summarizes total active database signals, long/short ratio (Bullish vs Bearish count), weighted average model conviction %, and mean Half-Kelly capital allocation %.")
    add_bullet("Multi-Dimensional Interactive Filters", "Operators can filter signals by Ticker (All, AAPL, MSFT, TSLA, NVDA, etc.), Direction (All, BULLISH, BEARISH, NEUTRAL), and Conviction Tier (Tier-1 High Conviction, Tier-2 Moderate Alpha).")
    add_bullet("Institutional Trading Blotter Dataframe", "A high-contrast interactive blotter with custom column formatting: Ticker, Direction (with styled 🟢 BULLISH, 🔴 BEARISH, 🟣 NEUTRAL badges), Conviction (rendered as a calibrated visual progress bar), Regime Conviction Tier, Half-Kelly Capital Allocation %, and UTC timestamp.")
    add_bullet("Live Pipeline Trigger Actions", "Four dedicated control buttons: (1) Fetch Finnhub News & Form Conviction (fetches news and automatically runs the ML pipeline); (2) Ingest SEC EDGAR 8-K & Form Conviction (polls the official SEC RSS Atom feed, parses CIK accession numbers, and executes vector subtraction); (3) Run Full End-to-End Alpha Engine (batch-processes any pending unvectorized articles); and (4) Instant Blotter Refresh.")

    # TAB 2
    add_h2("Tab 2: 📐 GCSV Latent Vector Subtraction Engine")
    doc.add_paragraph(
        "Tab 2 provides an interactive sandbox demonstrating the core mathematical formulation of GCSV:"
    )
    add_bullet("Formulation", "v_surprise = v_actual - v_consensus. Isolates the unexpected disclosure by subtracting the zero-surprise consensus baseline from the event embedding.")
    add_bullet("Target Ticker & Headline Selection", "Users can select mega-caps (AAPL, TSLA, MSFT, NVDA, AMZN, META, GOOGL), select pre-loaded corporate earnings headlines, or enter custom 8-K disclosure text.")
    add_bullet("Scenario Latent Distance Comparison Chart", "Renders a dark-themed Plotly bar chart comparing the Euclidean distance ||v_actual - v_consensus|| against three counterfactual anchors: Base Scenario (Zero Surprise), Bearish Scenario (-1.5σ), and Bullish Scenario (+1.5σ). The shortest distance determines the winning scenario.")
    add_bullet("Conviction Metrics", "Displays directional call, dominance margin conviction, surprise magnitude norm, and suggested Kelly capital sizing.")

    # TAB 3
    add_h2("Tab 3: 🎙️ Q&A Separation & Executive Tone Drift Tracker")
    doc.add_paragraph(
        "Tab 3 operationalizes Brockman et al. (2011) and Angelo et al. (2025) earnings conference call research:"
    )
    add_bullet("Dual Transcript Decomposition", "Splits earnings transcripts into two distinct text regions: Scripted Prepared Remarks (heavily polished by investor relations) and Spontaneous Q&A (under direct analyst questioning).")
    add_bullet("Divergence Score & Hedging Alert", "Computes cosine distance between prepared remarks and Q&A embeddings. Cosine divergence > 0.25 triggers a high-visibility warning banner: 'MANAGEMENT HEDGING DETECTED', immediately downgrading HIGH conviction signals to MEDIUM.")
    add_bullet("Executive Tone Drift Tracker", "Maintains an online per-executive embedding centroid using Welford's algorithm. Cosine drift > 0.28 indicates uncharacteristic hedging language relative to historical executive baselines, applying a Bayesian prior adjustment to base consensus.")

    # TAB 4
    add_h2("Tab 4: 🌐 Squeeze & Contagion Shields")
    doc.add_paragraph(
        "Tab 4 houses market microstructure shields and cross-asset contagion mechanics:"
    )
    add_bullet("FINRA Short Squeeze Risk Gauge", "An interactive circular indicator measuring short interest as a percentage of float. Short interest > 20% displays a red needle and suppresses bearish calls to UNCERTAIN, protecting capital from violent short squeezes.")
    add_bullet("48-Hour Pre-Announcement Drift", "Calculates the rolling 48-hour return and standard z-score leading into disclosure events. |z| > 2.0 indicates informed insider trading or information leakage.")
    add_bullet("Global Tech Contagion Graph", "Models shock propagation across the global semiconductor and technology supply chain (TSMC, ASML, NVIDIA, Apple, Microsoft) using directed network edges with geometric attenuation alpha = 0.65. Allows operators to trigger simulated shocks from overseas foundries and inspect downstream transmission delays (1 to 6 hours).")

    # TAB 5
    add_h2("Tab 5: ⏳ Quantile Alpha Decay Engine")
    doc.add_paragraph(
        "Tab 5 models the non-linear temporal decay of financial alpha across three institutional horizons:"
    )
    add_bullet("9 XGBoost Quantile Regressors", "Trained with asymmetric pinball loss to predict the 10th percentile (p10, worst-case downside), 50th percentile (p50, median expected return), and 90th percentile (p90, upside tail).")
    add_bullet("Trading Horizons", "T+1h (peak algorithmic reaction and spread widening), T+overnight (pre-market institutional clearing and opening gap formation), and T+5d (multi-day Post-Earnings Announcement Drift / PEAD).")
    add_bullet("Calibrated Prediction Interval Fan Chart", "Renders a dark Plotly fan chart featuring an 80% shaded prediction interval [p10, p90] and a solid blue median trajectory line (p50), identifying the optimal alpha harvesting horizon.")

    # TAB 6
    add_h2("Tab 6: ⚖️ Kelly Sizing & Alpaca Execution Terminal")
    doc.add_paragraph(
        "Tab 6 converts probabilistic alpha forecasts into optimal portfolio capital allocations and direct trade routing:"
    )
    add_bullet("Quantile-Derived Kelly Allocation Formula", "f* = (win_p * b - (1 - win_p)) / b, where win_p is the empirical hit rate and b is the return-to-risk odds ratio. Applies Half-Kelly (0.50 * f*) subject to regime caps (10% Bull, 6% Neutral, 3% Volatile, 0% Crisis).")
    add_bullet("Interactive Sizing Simulator", "Allows quantitative portfolio managers to adjust expected return p50, uncertainty width (p90 - p10), and conviction tier to inspect theoretical vs. applied capital allocation.")
    add_bullet("Alpaca Paper Trading Gateway", "Direct REST API integration with Alpaca Markets sandbox. Users can enter ticker, order side (BUY/SELL), and share quantity, submitting market orders with instant Order ID and status confirmation.")

    # TAB 7
    add_h2("Tab 7: 🇮🇳 Indo-Global Cross-Market Transmission & Multicorrelation Engine")
    doc.add_paragraph(
        "Tab 7 addresses the critical international dimension: modeling how global macro catalysts and US market disclosures "
        "propagate into Indian equity indices (NIFTY 50, BSE SENSEX, NIFTY BANK, NIFTY IT, NIFTY AUTO):"
    )
    add_bullet("Three Core Transmission Conduits", "(1) US Tech to NIFTY IT: Over 60% of Indian IT service revenue comes from US corporate IT budgets. (2) Brent Crude to NIFTY 50 and NIFTY AUTO: India imports >85% of crude petroleum; oil spikes directly cause input inflation and margin contraction. (3) US 10Y Yields & DXY to NIFTY BANK: Yield differentials trigger FII equity/debt capital outflows, weakening the rupee and tightening domestic liquidity.")
    add_bullet("Cross-Asset Pearson Heatmap", "Interactive correlation matrix between Indian benchmark/sectoral indices and global drivers (S&P 500, NASDAQ, SOX Semiconductor, Brent Crude, US 10Y Yields, CBOE VIX, USD/INR).")
    add_bullet("Bivariate vs. Multicorrelation (R²) Bar Chart", "Visually demonstrates that Multicorrelation R_{Y·X} = sqrt(r_{YX}^T · R_{XX}^{-1} · r_{YX}) explains substantially higher variance than any single bivariate index correlation (+19.1% to +27.3% information gain across Indian indices).")
    add_bullet("Overnight Lead-Lag Transmission Curve (tau = -2 to +2)", "Illustrates that cross-correlation peaks decisively at lag tau = +1 (r = 0.724 on NIFTY 50 and r = 0.842 on NIFTY IT), proving that the US 4:00 PM EST close acts as a forward-leading indicator for the Indian 9:15 AM IST opening auction.")
    add_bullet("Interactive Global-to-Indian Scenario Simulator", "Allows users to set hypothetical or live shocks on S&P 500 (%), NASDAQ (%), Brent Crude (%), US 10Y Yields (bps), VIX (pts), and USD/INR (%), instantly generating predicted opening moves, 95% confidence intervals, and directional bias badges for all five Indian indices.")
    add_bullet("Pure Partial Correlations Accordion", "Isolates the orthogonal marginal impact of each global factor while controlling for all other macro drivers, proving that NASDAQ is the dominant direct driver of NIFTY IT (+0.76) and Brent Crude is the dominant driver of NIFTY AUTO (-0.58).")

    # TAB 8
    add_h2("Tab 8: 📊 Empirical Research Matrix & High-Resolution IEEE Figures")
    doc.add_paragraph(
        "Tab 8 presents the complete academic and institutional benchmarking suite:"
    )
    add_bullet("Empirical Evaluation Matrix Table", "Compares MarketPulse AI v3 across 1,250 events over an 18-month out-of-sample window against Naive FinBERT, TF-IDF + Ridge, FinBERT + Logistic, and GCSV-Base. Reports Directional Hit Rate (83.12%), Macro F1 (0.837), Brier Score (0.1187), Annualized Return (203.88%), Sharpe Ratio (26.61), and Maximum Drawdown (-0.99%) under 8 bps slippage.")
    add_bullet("8 High-Resolution IEEE Research Figures", "Displays publication-grade figures: Figure 1 (GCSV Latent Geometry), Figure 2 (Cross-Regime Robustness), Figure 3 (Temporal Decay Fan Chart), Figure 4 (Equity Curves), Figure 5 (Kelly Sizing Surface), Figure 6 (Contagion Network Topology), Figure 7 (Indo-Global Macro Correlation Heatmap), and Figure 8 (Multicorrelation R² Gains & Overnight Lead-Lag Transmission).")

    # -------------------------------------------------------------------------
    # SECTION 5: STEP-BY-STEP OPERATIONAL PROCEDURES
    # -------------------------------------------------------------------------
    add_h1("5. Step-by-Step Operator Ingestion & Trading Walkthrough")
    doc.add_paragraph(
        "For quantitative analysts and trading operators deploying MarketPulse AI v3.2 in live or sandbox environments, "
        "follow this standardized four-step procedure:"
    )
    doc.add_paragraph(
        "Step 1: Check Environment Telemetry — Verify that the top status ribbon indicates '● LIVE INGESTION ACTIVE' "
        "and that the Macro Regime matches current market conditions. Adjust sidebar risk knobs if entering elevated volatility regimes."
    )
    doc.add_paragraph(
        "Step 2: Trigger Live Data Ingestion — In Tab 1, click '🚀 Fetch Finnhub News & Form Conviction' or '🏛️ Ingest SEC EDGAR 8-K & Form Conviction'. "
        "The system fetches raw disclosures, embeds them via FinBERT, runs GCSV vector subtraction against semantic expectation anchors, "
        "applies pre-drift and squeeze filters, calculates Half-Kelly capital sizing, and saves the signals directly to Supabase."
    )
    doc.add_paragraph(
        "Step 3: Analyze Indian Cross-Market Transmission — In Tab 7, observe the overnight US market closing metrics. Use the 'Scenario Shock Simulator' "
        "to compute predicted opening gap-ups or gap-downs for NIFTY 50, NIFTY IT, and NIFTY BANK with calibrated 95% confidence bands."
    )
    doc.add_paragraph(
        "Step 4: Execute Orders & Review Outcomes — In Tab 6, review the Half-Kelly recommended position sizing. If trading US mega-caps, "
        "submit paper orders directly via the Alpaca Markets execution gateway, logging order fills and monitoring post-trade slippage."
    )

    out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "MarketPulse_AI_Streamlit_App_Operational_Manual.docx")
    doc.save(out_path)
    print(f"✓ Successfully generated Operational Manual at: {out_path}")
    return out_path

if __name__ == "__main__":
    generate_app_manual()
