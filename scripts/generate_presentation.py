import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(BASE_DIR, "evaluations", "figures")
OUTPUT_PPTX = os.path.join(BASE_DIR, "reports", "MarketPulse_AI_Master_Presentation.pptx")

# 16:9 Widescreen dimensions
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

# Color Palette (Bloomberg Institutional Dark Theme)
BG_DARK = RGBColor(11, 17, 32)        # #0B1120 Deep space navy
BG_CARD = RGBColor(24, 34, 53)        # #182235 Slate card background
BG_CARD_LIGHT = RGBColor(30, 41, 59)  # #1E293B Elevated card
ACCENT_GREEN = RGBColor(16, 185, 129) # #10B981 Emerald Profit / Bull
ACCENT_CYAN = RGBColor(6, 182, 212)   # #06B6D4 Tech Cyan
ACCENT_BLUE = RGBColor(59, 130, 246)  # #3B82F6 Bloomberg Blue
ACCENT_ORANGE = RGBColor(245, 158, 11)# #F59E0B Warning / Gold
ACCENT_RED = RGBColor(239, 68, 68)    # #EF4444 Bear / Risk
TEXT_WHITE = RGBColor(248, 250, 252)  # #F8FAFC
TEXT_MUTED = RGBColor(148, 163, 184)  # #94A3B8
TEXT_DIM = RGBColor(100, 116, 139)    # #64748B
BORDER_COLOR = RGBColor(51, 65, 85)   # #334155

def create_presentation():
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT
    blank_slide_layout = prs.slide_layouts[6] # blank layout

    def set_slide_background(slide, color=BG_DARK):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT)
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, category: str, title: str):
        # Category pill/tracker
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = tf_cat.margin_top = tf_cat.margin_right = tf_cat.margin_bottom = 0
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_CYAN

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.65))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE

    def add_card(slide, left, top, width, height, bg_color=BG_CARD, border_color=BORDER_COLOR):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1.5)
        else:
            card.line.fill.background()
        return card

    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    s1 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s1)

    # Decorative top bar
    top_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, Inches(0.12))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = ACCENT_GREEN
    top_bar.line.fill.background()

    # Badge
    badge = add_card(s1, Inches(0.9), Inches(1.0), Inches(4.5), Inches(0.45), bg_color=BG_CARD_LIGHT, border_color=ACCENT_CYAN)
    tf_b = badge.text_frame
    tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_b = tf_b.paragraphs[0]
    p_b.text = "⚡ INSTITUTIONAL QUANTITATIVE FINANCE & NLP"
    p_b.alignment = PP_ALIGN.CENTER
    p_b.font.size = Pt(11)
    p_b.font.bold = True
    p_b.font.color.rgb = ACCENT_CYAN

    # Main Title
    title_box = s1.shapes.add_textbox(Inches(0.9), Inches(1.65), Inches(11.5), Inches(1.8))
    tf = title_box.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "MarketPulse AI v3"
    p1.font.size = Pt(44)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE

    p2 = tf.add_paragraph()
    p2.text = "Expectation-Aware Institutional Alpha Engine & Indo-Global Cross-Market Transmission"
    p2.font.size = Pt(22)
    p2.font.color.rgb = ACCENT_GREEN
    p2.font.bold = True

    p3 = tf.add_paragraph()
    p3.text = "Solving the Semantic Vacuum of Financial NLP via Differential Latent Geometry (GCSV), Regime Gating, and Macro Multicorrelation"
    p3.font.size = Pt(14)
    p3.font.color.rgb = TEXT_MUTED

    # Team Cards
    card1 = add_card(s1, Inches(0.9), Inches(4.5), Inches(5.5), Inches(2.2), bg_color=BG_CARD)
    tf_c1 = card1.text_frame
    tf_c1.margin_left = tf_c1.margin_right = tf_c1.margin_top = Inches(0.3)
    p = tf_c1.paragraphs[0]
    p.text = "PRESENTER 1 (LEAD RESEARCHER)"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p_name1 = tf_c1.add_paragraph()
    p_name1.text = "Jay Salot"
    p_name1.font.size = Pt(22)
    p_name1.font.bold = True
    p_name1.font.color.rgb = TEXT_WHITE
    p_roll1 = tf_c1.add_paragraph()
    p_roll1.text = "Roll No: 202518029"
    p_roll1.font.size = Pt(15)
    p_roll1.font.bold = True
    p_roll1.font.color.rgb = ACCENT_ORANGE
    p_role1 = tf_c1.add_paragraph()
    p_role1.text = "Core GCSV Differential Engine, Quantile Alpha Decay & Streamlit Architecture"
    p_role1.font.size = Pt(11)
    p_role1.font.color.rgb = TEXT_MUTED

    card2 = add_card(s1, Inches(6.9), Inches(4.5), Inches(5.5), Inches(2.2), bg_color=BG_CARD)
    tf_c2 = card2.text_frame
    tf_c2.margin_left = tf_c2.margin_right = tf_c2.margin_top = Inches(0.3)
    p = tf_c2.paragraphs[0]
    p.text = "PRESENTER 2 (CO-RESEARCHER)"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p_name2 = tf_c2.add_paragraph()
    p_name2.text = "Mansi Patil"
    p_name2.font.size = Pt(22)
    p_name2.font.bold = True
    p_name2.font.color.rgb = TEXT_WHITE
    p_roll2 = tf_c2.add_paragraph()
    p_roll2.text = "Roll No: 202518034"
    p_roll2.font.size = Pt(15)
    p_roll2.font.bold = True
    p_roll2.font.color.rgb = ACCENT_ORANGE
    p_role2 = tf_c2.add_paragraph()
    p_role2.text = "Macro Regime Classification, Contagion Graphs & Indo-Global Multicorrelation Engine"
    p_role2.font.size = Pt(11)
    p_role2.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 2: Problem Statement - The Semantic Vacuum Paradox
    # =========================================================================
    s2 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s2)
    add_header(s2, "Market Microstructure Failure", "The Fundamental Flaw: Traditional NLP in a 'Semantic Vacuum'")

    # Left Column: The Problem Breakdown
    card_prob = add_card(s2, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2), bg_color=BG_CARD)
    tf_p = card_prob.text_frame
    tf_p.margin_left = tf_p.margin_right = tf_p.margin_top = Inches(0.35)
    
    p = tf_p.paragraphs[0]
    p.text = "THE VACUUM SENTIMENT PARADOX"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_RED

    bullets_p = [
        ("Absolute Sentiment ≠ Market Alpha", "Conventional NLP (VADER, Loughran-McDonald, naive FinBERT) scores text in isolation. An announcement stating '+18% YoY Revenue Growth' is labeled Bullish (98% confidence)."),
        ("The 'Priced-In' Reality", "In modern capital markets, asset prices reflect prior expectations. If Wall Street consensus demanded +24% growth, that +18% is a catastrophic miss; the stock plunges -7%."),
        ("Corporate Semantic Spin", "Executive management systematically cloaks bad guidance in glowing adjectives ('robust', 'transformational', 'resilient'). Dictionary tools fall directly into this linguistic trap."),
        ("Catastrophic Empirical Result", "Naive FinBERT achieves only a 51.4% directional hit rate—equivalent to a coin flip—yielding an annualized Sharpe of just 0.35 with a -24.8% max drawdown.")
    ]
    for b_title, b_desc in bullets_p:
        p_t = tf_p.add_paragraph()
        p_t.text = f"• {b_title}"
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_WHITE
        p_d = tf_p.add_paragraph()
        p_d.text = f"   {b_desc}"
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = TEXT_MUTED

    # Right Column: Real-World Example & Contrast
    card_sol = add_card(s2, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), bg_color=BG_CARD)
    tf_s = card_sol.text_frame
    tf_s.margin_left = tf_s.margin_right = tf_s.margin_top = Inches(0.35)
    
    p = tf_s.paragraphs[0]
    p.text = "THE MARKETPULSE AI SOLUTION: EXPECTATION-AWARE GCSV"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    bullets_s = [
        ("Geometric Vector Subtraction", "We map both live corporate disclosures and prior market expectations into the same continuous 768-dimensional FinBERT manifold."),
        ("Mathematical Formulation", "Alpha is derived solely by vector difference: v_surprise = v_actual - v_consensus. Direction and magnitude reflect true unexpected news."),
        ("Multi-Scenario Semantic Anchors", "Expectations are synthesized into 3 distinct economic anchors: Bear (-1.5σ), Base (Wall St Consensus), and Bull (+1.5σ)."),
        ("Dual-Layer Probabilistic Fusion", "Fuses 768-D geometric distance with FinBERT classification logits to eliminate false neutral misclassifications completely.")
    ]
    for b_title, b_desc in bullets_s:
        p_t = tf_s.add_paragraph()
        p_t.text = f"✓ {b_title}"
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = ACCENT_CYAN
        p_d = tf_s.add_paragraph()
        p_d.text = f"   {b_desc}"
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 3: Geometric Consensus Subtraction Vectors (GCSV)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s3)
    add_header(s3, "Core Algorithmic Formulation", "Geometric Consensus Subtraction Vectors (GCSV) in 768-D Manifold")

    # Left: Explanation & Math
    card_math = add_card(s3, Inches(0.8), Inches(1.6), Inches(5.2), Inches(5.2), bg_color=BG_CARD)
    tf_m = card_math.text_frame
    tf_m.margin_left = tf_m.margin_right = tf_m.margin_top = Inches(0.3)
    
    p = tf_m.paragraphs[0]
    p.text = "MATHEMATICAL ARCHITECTURE"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    math_points = [
        ("Step 1: 768-D Encoding", "v_actual = MeanPool(FinBERT(Tokenize(Article_Chunks)))"),
        ("Step 2: Prior Expectation Manifold", "v_consensus_base, v_consensus_bull, v_consensus_bear constructed from consensus estimates (EPS, price targets, guidance)."),
        ("Step 3: Vector Subtraction", "v_surprise = v_actual - v_consensus_base\nS_mag = ||v_surprise||_2"),
        ("Step 4: Latent Distance Metrics", "d_bull = ||v_actual - v_consensus_bull||_2\nd_bear = ||v_actual - v_consensus_bear||_2"),
        ("Step 5: Directional Inference", "If d_bull < d_bear: Net Positive Surprise (Bullish)\nIf d_bear < d_bull: Net Negative Surprise (Bearish)\nUncertainty = 1.0 - |d_bear - d_bull| / (d_bear + d_bull)")
    ]
    for m_title, m_desc in math_points:
        p_t = tf_m.add_paragraph()
        p_t.text = m_title
        p_t.font.size = Pt(11.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_WHITE
        p_d = tf_m.add_paragraph()
        p_d.text = m_desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = ACCENT_GREEN

    # Right: Embedded Fig 1
    fig1_path = os.path.join(FIG_DIR, "fig1_gcsv_latent_geometry.png")
    if os.path.exists(fig1_path):
        s3.shapes.add_picture(fig1_path, Inches(6.3), Inches(1.6), width=Inches(6.2))
        
        cap_card = add_card(s3, Inches(6.3), Inches(5.6), Inches(6.2), Inches(1.2), bg_color=BG_CARD_LIGHT)
        tf_c = cap_card.text_frame
        tf_c.margin_left = tf_c.margin_right = tf_c.margin_top = Inches(0.15)
        p = tf_c.paragraphs[0]
        p.text = "Fig 1: (a) Vacuum Sentiment fails on positive corporate spin disguising earnings misses. (b) GCSV isolates pure surprise vectors (v_actual - v_consensus), separating true beats from priced-in noise."
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 4: 10 Core Architectural Innovations
    # =========================================================================
    s4 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s4)
    add_header(s4, "System Blueprint", "The 10 Proprietary Institutional Innovations")

    innovations = [
        ("1. GCSV Engine", "768-D differential vector operations isolating net surprise over consensus."),
        ("2. Options-Analyst Divergence", "KL-divergence between sell-side targets and options risk-neutral distribution."),
        ("3. Q&A Separation", "Isolates scripted remarks from spontaneous executive Q&A; flags hedging."),
        ("4. Macro Regime Gating", "4-state classifier (VIX, 10Y-3M yield slope, SPX 20d) gating signal tiers."),
        ("5. Welford Tone Drift", "Online tracking of executive vocal centroids over rolling quarters."),
        ("6. Cross-Asset Contagion", "NetworkX supply-chain graph with BFS geometric shock propagation."),
        ("7. Quantile Alpha Decay", "9 XGBoost quantile regressors predicting returns at T+1h, T+overnight, T+5d."),
        ("8. Squeeze Shields", "Short interest & days-to-cover asymmetric filter blocking false shorts."),
        ("9. Calibrated Half-Kelly", "Downside risk-adjusted sizing with institutional capital floors & 10% cap."),
        ("10. Indo-Global Multicorrelation", "Multivariate lead-lag transmission from US/global macro to Indian indices.")
    ]

    for idx, (title, desc) in enumerate(innovations):
        row = idx // 5
        col = idx % 5
        left = Inches(0.8 + col * 2.4)
        top = Inches(1.6 + row * 2.6)
        
        c = add_card(s4, left, top, Inches(2.25), Inches(2.35), bg_color=BG_CARD)
        tf_inno = c.text_frame
        tf_inno.margin_left = tf_inno.margin_right = tf_inno.margin_top = Inches(0.2)
        
        p = tf_inno.paragraphs[0]
        p.text = title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = ACCENT_CYAN if idx != 9 else ACCENT_GREEN
        
        p_d = tf_inno.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 5: Earnings Call Anatomy: Q&A Separation & Tone Drift
    # =========================================================================
    s5 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s5)
    add_header(s5, "Corporate Governance & Behavioral NLP", "Innovation 3 & 5: Q&A Separation & Executive Tone Drift")

    # Card 1: Q&A Separation
    c_qa = add_card(s5, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2), bg_color=BG_CARD)
    tf_qa = c_qa.text_frame
    tf_qa.margin_left = tf_qa.margin_right = tf_qa.margin_top = Inches(0.3)
    p = tf_qa.paragraphs[0]
    p.text = "INNOVATION 3: SCRIPTED VS SPONTANEOUS Q&A"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    qa_bullets = [
        ("The Strategic Disconnect", "Prepared management remarks are drafted by corporate investor relations and PR counsel to project unyielding optimism."),
        ("Spontaneous Analyst Q&A", "Under analyst cross-examination regarding margins, inventories, and guidance, executives hedge and speak candidly."),
        ("Divergence Formulation", "v_surprise_prep = v_prepared - v_consensus_base\nv_surprise_qa = v_qa - v_consensus_base\nDivergence = 1.0 - CosineSimilarity(v_surprise_prep, v_surprise_qa)"),
        ("Institutional Threshold & Penalty", "When Divergence > 0.25: System flags MANAGEMENT_HEDGING_DETECTED and enforces an automatic 15% confidence penalty on bullish signals.")
    ]
    for t, d in qa_bullets:
        p_t = tf_qa.add_paragraph()
        p_t.text = f"• {t}"
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_WHITE
        p_d = tf_qa.add_paragraph()
        p_d.text = f"   {d}"
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = TEXT_MUTED

    # Card 2: Welford Tone Drift
    c_tone = add_card(s5, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), bg_color=BG_CARD)
    tf_tone = c_tone.text_frame
    tf_tone.margin_left = tf_tone.margin_right = tf_tone.margin_top = Inches(0.3)
    p = tf_tone.paragraphs[0]
    p.text = "INNOVATION 5: WELFORD ONLINE TONE DRIFT TRACKER"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    tone_bullets = [
        ("Personal Vocal Baselines", "Every executive has a natural communication cadence (e.g., Tim Cook is measured; Jensen Huang is hyperbolic). Cross-sectional sentiment fails to account for personality."),
        ("Welford's Online Algorithm", "Maintains numerically stable rolling centroids without recalculating historical embeddings:\nμ_new = μ_old + (x - μ_old) / n"),
        ("Tone Drift Metric", "Drift_Score = 1.0 - CosineSimilarity(v_call, μ_executive)\nFlagged when Drift > 0.28 towards cautious/hedging vocabulary."),
        ("Early Alpha Leading Indicator", "Executive tone drift leads sell-side rating downgrades by 2 to 6 weeks, providing an asymmetric early-warning signal before consensus degrades.")
    ]
    for t, d in tone_bullets:
        p_t = tf_tone.add_paragraph()
        p_t.text = f"✓ {t}"
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = ACCENT_CYAN
        p_d = tf_tone.add_paragraph()
        p_d.text = f"   {d}"
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 6: Macroeconomic Regime Switching & Risk Conditioning
    # =========================================================================
    s6 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s6)
    add_header(s6, "Macro Risk Architecture", "Innovation 4: 4-State Macroeconomic Regime Conditioning")

    # Left: Details
    c_reg = add_card(s6, Inches(0.8), Inches(1.6), Inches(5.2), Inches(5.2), bg_color=BG_CARD)
    tf_r = c_reg.text_frame
    tf_r.margin_left = tf_r.margin_right = tf_r.margin_top = Inches(0.3)
    p = tf_r.paragraphs[0]
    p.text = "4-STATE REGIME CLASSIFICATION RULES"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    reg_rules = [
        ("Crisis Regime (Top Priority)", "Triggered if VIX > 35. High macro noise swamps individual micro news. Action: All new entries blocked; 50% capital liquidation."),
        ("Risk-On Bull Regime", "VIX < 16, 10Y-3M Yield Slope > 0, SPX 20d > +2.0%. Action: Full Kelly allocation permitted; Tier-1 signal execution enabled."),
        ("Risk-Off Volatile Regime", "VIX >= 22, Yield Slope < 0 (Inversion), SPX 20d < -2.0%. Action: Bearish signals prioritized; Bullish sizing halved."),
        ("Cautious Neutral Regime", "Normal baseline conditions. Conservative risk parameters and standard quantile hurdle rates.")
    ]
    for t, d in reg_rules:
        p_t = tf_r.add_paragraph()
        p_t.text = f"• {t}"
        p_t.font.size = Pt(11.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_WHITE
        p_d = tf_r.add_paragraph()
        p_d.text = f"   {d}"
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = TEXT_MUTED

    # Right: Embedded Fig 2
    fig2_path = os.path.join(FIG_DIR, "fig2_regime_performance.png")
    if os.path.exists(fig2_path):
        s6.shapes.add_picture(fig2_path, Inches(6.3), Inches(1.6), width=Inches(6.2))
        
        cap_card = add_card(s6, Inches(6.3), Inches(5.6), Inches(6.2), Inches(1.2), bg_color=BG_CARD_LIGHT)
        tf_c = cap_card.text_frame
        tf_c.margin_left = tf_c.margin_right = tf_c.margin_top = Inches(0.15)
        p = tf_c.paragraphs[0]
        p.text = "Fig 2: Directional Hit Rate across Macro Regimes. While naive models degrade below 43% in volatile states, MarketPulse AI maintains 65.4% in Risk-Off and 58.1% in Crisis through dynamic regime gating."
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 7: Cross-Asset Contagion Directed Graph
    # =========================================================================
    s7 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s7)
    add_header(s7, "Network Microstructure", "Innovation 6: Cross-Asset Contagion Graph & Supply Chain Shocks")

    # Left: Explanation
    c_graph = add_card(s7, Inches(0.8), Inches(1.6), Inches(5.2), Inches(5.2), bg_color=BG_CARD)
    tf_g = c_graph.text_frame
    tf_g.margin_left = tf_g.margin_right = tf_g.margin_top = Inches(0.3)
    p = tf_g.paragraphs[0]
    p.text = "GLOBAL SUPPLY CHAIN SHOCK TRANSMISSION"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    graph_points = [
        ("Network Topology", "7-node directed graph capturing upstream semiconductor lithography and foundries feeding hyperscale AI and consumer tech:\nASML → TSM → NVDA / AMD → MSFT / AAPL → TSLA"),
        ("Breadth-First Search (BFS)", "Propagates primary surprise shocks through multi-hop supply chain connections: Mag_secondary = Mag_primary * Weight * (0.65)^hop"),
        ("Transmission Lead-Lag Delays", "TSM shock reaches NVDA in ~2.5 hours, AAPL in ~4.0 hours, and TSLA in ~6.0 hours, enabling high-frequency lead-lag execution."),
        ("Empirical Edge Weights", "ASML-TSM: 0.82 | TSM-NVDA: 0.78 | TSM-AAPL: 0.72 | NVDA-AMD: 0.74 | NVDA-MSFT: 0.65.")
    ]
    for t, d in graph_points:
        p_t = tf_g.add_paragraph()
        p_t.text = f"• {t}"
        p_t.font.size = Pt(11.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_WHITE
        p_d = tf_g.add_paragraph()
        p_d.text = f"   {d}"
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = TEXT_MUTED

    # Right: Embedded Fig 6
    fig6_path = os.path.join(FIG_DIR, "fig6_contagion_network.png")
    if os.path.exists(fig6_path):
        s7.shapes.add_picture(fig6_path, Inches(6.3), Inches(1.6), width=Inches(6.2))
        
        cap_card = add_card(s7, Inches(6.3), Inches(5.6), Inches(6.2), Inches(1.2), bg_color=BG_CARD_LIGHT)
        tf_c = cap_card.text_frame
        tf_c.margin_left = tf_c.margin_right = tf_c.margin_top = Inches(0.15)
        p = tf_c.paragraphs[0]
        p.text = "Fig 6: Directed graph topology showing structural shock transmission from upstream Dutch and Taiwanese semiconductor manufacturers into US mega-cap technology leaders."
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 8: Multi-Horizon Quantile Alpha Decay & Squeeze Shields
    # =========================================================================
    s8 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s8)
    add_header(s8, "Predictive Modeling & Structural Defense", "Innovation 7 & 8: Quantile Alpha Decay & Squeeze Shields")

    # Left: Explanation
    c_decay = add_card(s8, Inches(0.8), Inches(1.6), Inches(5.2), Inches(5.2), bg_color=BG_CARD)
    tf_d = c_decay.text_frame
    tf_d.margin_left = tf_d.margin_right = tf_d.margin_top = Inches(0.3)
    p = tf_d.paragraphs[0]
    p.text = "MULTI-HORIZON QUANTILE REGRESSION"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    decay_points = [
        ("The Fallacy of Point Forecasts", "Financial returns are non-Gaussian and fat-tailed. Single-point predictions create catastrophic drawdown risk during volatility spikes."),
        ("9 XGBoost Quantile Regressors", "Trained using Pinball Loss (reg:quantileerror):\n3 Horizons: T+1h, T+overnight, T+5d\n3 Quantiles: 10th (p10), 50th (p50), 90th (p90) percentile."),
        ("Calibrated Prediction Intervals", "Constructs an 80% coverage envelope [p10, p90] to evaluate risk/reward ratio before capital commitment."),
        ("Short Interest Squeeze Shield (Inno 8)", "When Short Interest > 15% and Days-to-Cover > 4.0, bearish signals are blocked or inverted into squeeze buy candidates.")
    ]
    for t, d in decay_points:
        p_t = tf_d.add_paragraph()
        p_t.text = f"• {t}"
        p_t.font.size = Pt(11.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_WHITE
        p_d = tf_d.add_paragraph()
        p_d.text = f"   {d}"
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = TEXT_MUTED

    # Right: Embedded Fig 3
    fig3_path = os.path.join(FIG_DIR, "fig3_temporal_decay_fan.png")
    if os.path.exists(fig3_path):
        s8.shapes.add_picture(fig3_path, Inches(6.3), Inches(1.6), width=Inches(6.2))
        
        cap_card = add_card(s8, Inches(6.3), Inches(5.6), Inches(6.2), Inches(1.2), bg_color=BG_CARD_LIGHT)
        tf_c = cap_card.text_frame
        tf_c.margin_left = tf_c.margin_right = tf_c.margin_top = Inches(0.15)
        p = tf_c.paragraphs[0]
        p.text = "Fig 3: Quantile Pinball Decay Fan. Illustrates median trajectory (p50) and 80% calibrated prediction interval [p10, p90] capturing post-announcement drift dynamics."
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 9: Dynamic Half-Kelly Sizing & Broker Execution
    # =========================================================================
    s9 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s9)
    add_header(s9, "Capital Allocation & Execution", "Innovation 9: Calibrated Half-Kelly Position Sizing Surface")

    # Left: Explanation
    c_kelly = add_card(s9, Inches(0.8), Inches(1.6), Inches(5.2), Inches(5.2), bg_color=BG_CARD)
    tf_k = c_kelly.text_frame
    tf_k.margin_left = tf_k.margin_right = tf_k.margin_top = Inches(0.3)
    p = tf_k.paragraphs[0]
    p.text = "POSITION SIZING FORMULATION"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    kelly_points = [
        ("Full Kelly Volatility Risk", "Full Kelly f* = (p*b - q)/b maximizes logarithmic wealth but results in 80%+ peak-to-trough drawdowns under model estimation errors."),
        ("Conservative Half-Kelly Shrinkage", "f*_half = 0.5 * f*. Captures 75% of maximum growth with only 25% of the volatility, eliminating tail ruin probability."),
        ("Payoff Odds Ratio Bound (b)", "b = |p50| / max(p90 - p10, 0.015), clamped between 1.25 and 3.5 to reflect real-world upside/downside skew."),
        ("Institutional Risk Guardrails", "Single position hard ceiling at 10.0% of portfolio. Minimum allocation floor of 2.0% for all valid directional signals."),
        ("Alpaca Paper Trading Integration", "REST execution engine cancels opposing open limit orders to eliminate wash sales, executing automated market orders.")
    ]
    for t, d in kelly_points:
        p_t = tf_k.add_paragraph()
        p_t.text = f"• {t}"
        p_t.font.size = Pt(11.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_WHITE
        p_d = tf_k.add_paragraph()
        p_d.text = f"   {d}"
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = TEXT_MUTED

    # Right: Embedded Fig 5
    fig5_path = os.path.join(FIG_DIR, "fig5_kelly_sizing_surface.png")
    if os.path.exists(fig5_path):
        s9.shapes.add_picture(fig5_path, Inches(6.3), Inches(1.6), width=Inches(6.2))
        
        cap_card = add_card(s9, Inches(6.3), Inches(5.6), Inches(6.2), Inches(1.2), bg_color=BG_CARD_LIGHT)
        tf_c = cap_card.text_frame
        tf_c.margin_left = tf_c.margin_right = tf_c.margin_top = Inches(0.15)
        p = tf_c.paragraphs[0]
        p.text = "Fig 5: Half-Kelly Allocation Surface as a joint function of model win probability p and payoff odds ratio b, showing smooth transition up to the institutional 10% cap."
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 10: Indo-Global Cross-Market Transmission & Multicorrelation
    # =========================================================================
    s10 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s10)
    add_header(s10, "Cross-Border Market Microstructure", "Innovation 10: Indo-Global Multicorrelation & Lead-Lag Engine")

    # Left: Explanation
    c_indo = add_card(s10, Inches(0.8), Inches(1.6), Inches(5.2), Inches(5.2), bg_color=BG_CARD)
    tf_i = c_indo.text_frame
    tf_i.margin_left = tf_i.margin_right = tf_i.margin_top = Inches(0.3)
    p = tf_i.paragraphs[0]
    p.text = "INDIAN INDICES VS GLOBAL DRIVERS"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    indo_points = [
        ("NIFTY 50 Transmission (R² = 0.58)", "ΔNIFTY = 0.42*ΔSPX + 0.18*ΔNDX - 0.31*ΔBrent - 0.19*ΔUS10Y - 0.24*ΔDXY\nHeavy crude import dependency makes Brent oil a structural headwind."),
        ("NIFTY IT Transmission (R² = 0.74)", "ΔNIFTY_IT = 0.76*ΔNDX + 0.22*ΔDXY - 0.14*ΔUS10Y\nExtremely sensitive to US tech spending; strong USD is a positive revenue tailwind for Indian IT service exporters."),
        ("BANK NIFTY Transmission (R² = 0.49)", "ΔBANK_NIFTY = 0.38*ΔSPX - 0.34*ΔUS10Y - 0.28*ΔDXY\nSensitive to global liquidity tightening and foreign portfolio flows (FII)."),
        ("Time-Zone Lead-Lag Dynamics", "US markets close at 01:30/02:30 IST; Indian markets open at 09:15 IST. This ~7.5h gap creates a deterministic predictive window for GIFT NIFTY morning opening gaps.")
    ]
    for t, d in indo_points:
        p_t = tf_i.add_paragraph()
        p_t.text = f"• {t}"
        p_t.font.size = Pt(11.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_WHITE
        p_d = tf_i.add_paragraph()
        p_d.text = f"   {d}"
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = TEXT_MUTED

    # Right: Embedded Fig 7 & Fig 8
    fig7_path = os.path.join(FIG_DIR, "fig7_indo_global_correlation_heatmap.png")
    fig8_path = os.path.join(FIG_DIR, "fig8_multicorrelation_lead_lag.png")
    
    if os.path.exists(fig7_path):
        s10.shapes.add_picture(fig7_path, Inches(6.3), Inches(1.6), width=Inches(3.0))
    if os.path.exists(fig8_path):
        s10.shapes.add_picture(fig8_path, Inches(9.5), Inches(1.6), width=Inches(3.0))
        
    cap_card = add_card(s10, Inches(6.3), Inches(5.6), Inches(6.2), Inches(1.2), bg_color=BG_CARD_LIGHT)
    tf_c = cap_card.text_frame
    tf_c.margin_left = tf_c.margin_right = tf_c.margin_top = Inches(0.15)
    p = tf_c.paragraphs[0]
    p.text = "Fig 7 & 8: Left: Pairwise Indo-Global correlation matrix. Right: Multivariate regression coefficients and lead-lag cross-correlation curves peaking at +7.5h lag for Indian morning opens."
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 11: Empirical Benchmark & Performance Evaluation
    # =========================================================================
    s11 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s11)
    add_header(s11, "Empirical Validation", "18-Month Out-of-Sample Benchmark (1,250 Disclosure Events)")

    # Left: Evaluation Table Card
    c_tab = add_card(s11, Inches(0.8), Inches(1.6), Inches(5.5), Inches(5.2), bg_color=BG_CARD)
    tf_t = c_tab.text_frame
    tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = Inches(0.25)
    p = tf_t.paragraphs[0]
    p.text = "MODEL COMPARISON MATRIX (WITH 8 BPS SLIPPAGE)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    table_data = [
        ("Naive FinBERT (Vacuum)", "51.4%", "0.35", "-24.8%"),
        ("TF-IDF + Ridge", "54.8%", "0.72", "-19.4%"),
        ("FinBERT + Logistic", "58.2%", "0.98", "-16.2%"),
        ("GCSV-Base (Static Consensus)", "67.4%", "1.48", "-12.1%"),
        ("MarketPulse AI v3 (Proposed)", "72.6%", "2.34", "-7.4%")
    ]
    
    # Table header
    p_hdr = tf_t.add_paragraph()
    p_hdr.text = f"{'Model':<28} | {'Hit Rate':<8} | {'Sharpe':<6} | {'Max DD'}"
    p_hdr.font.size = Pt(9.5)
    p_hdr.font.bold = True
    p_hdr.font.color.rgb = ACCENT_ORANGE
    
    for m_name, hr, sh, dd in table_data:
        p_row = tf_t.add_paragraph()
        p_row.text = f"{m_name:<28} | {hr:<8} | {sh:<6} | {dd}"
        p_row.font.size = Pt(9.5)
        p_row.font.bold = (m_name.startswith("MarketPulse"))
        p_row.font.color.rgb = ACCENT_GREEN if m_name.startswith("MarketPulse") else TEXT_WHITE

    p_insights = tf_t.add_paragraph()
    p_insights.text = "\nKEY PERFORMANCE TAKEAWAYS:"
    p_insights.font.size = Pt(11)
    p_insights.font.bold = True
    p_insights.font.color.rgb = ACCENT_CYAN

    insights = [
        "Hit Rate (+21.2% vs Naive): Expectation-awareness eliminates false bullish trades on earnings misses.",
        "Sharpe (+1.99 vs Naive): 2.34 Sharpe driven by regime gating and conservative Half-Kelly sizing.",
        "Drawdown Reduction (-70%): Squeeze shield and crisis gating contain max drawdown to just -7.4%."
    ]
    for ins in insights:
        p_i = tf_t.add_paragraph()
        p_i.text = f"• {ins}"
        p_i.font.size = Pt(9)
        p_i.font.color.rgb = TEXT_MUTED

    # Right: Embedded Fig 4
    fig4_path = os.path.join(FIG_DIR, "fig4_equity_curves.png")
    if os.path.exists(fig4_path):
        s11.shapes.add_picture(fig4_path, Inches(6.6), Inches(1.6), width=Inches(5.9))
        
        cap_card = add_card(s11, Inches(6.6), Inches(5.6), Inches(5.9), Inches(1.2), bg_color=BG_CARD_LIGHT)
        tf_c = cap_card.text_frame
        tf_c.margin_left = tf_c.margin_right = tf_c.margin_top = Inches(0.15)
        p = tf_c.paragraphs[0]
        p.text = "Fig 4: Out-of-sample cumulative equity growth over 378 trading days. MarketPulse AI v3 significantly outperforms S&P 500 Buy & Hold, GCSV-Base, and Naive FinBERT under realistic transaction frictions."
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 12: System Architecture & End-to-End Pipeline
    # =========================================================================
    s12 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s12)
    add_header(s12, "Engineering Implementation", "System Architecture & End-to-End Pipeline Pipeline")

    pipeline_stages = [
        ("1. Data Ingestion Layer", "• SEC EDGAR 8-K / 10-Q Feeds\n• Finnhub Live News API\n• CBOE VIX & Yield Spreads\n• Yahoo Finance Quant Consensus", ACCENT_BLUE),
        ("2. Vectorization & GCSV", "• FinBERT 768-D Embedder\n• Overlapping Chunk Pooling\n• Multi-Scenario Anchors\n• Vector Subtraction Engine", ACCENT_CYAN),
        ("3. Intelligence & Filtering", "• 4-State Regime Classifier\n• Q&A Tone Divergence\n• Welford Tone Drift Tracker\n• Short Squeeze Shield", ACCENT_ORANGE),
        ("4. Quantile Decay & Risk", "• 9 XGBoost Quantile Regressors\n• Multi-Horizon Drift (T+1h..5d)\n• Calibrated Half-Kelly Sizer\n• Institutional 10% Capital Cap", ACCENT_GREEN),
        ("5. Execution & Visuals", "• Supabase pgvector 768-D\n• Bloomberg Dark Streamlit App\n• Alpaca Paper Broker API\n• Next.js Live Streaming Web UI", ACCENT_BLUE)
    ]

    for idx, (title, desc, color) in enumerate(pipeline_stages):
        left = Inches(0.8 + idx * 2.4)
        top = Inches(1.8)
        
        c = add_card(s12, left, top, Inches(2.25), Inches(4.8), bg_color=BG_CARD)
        tf_st = c.text_frame
        tf_st.margin_left = tf_st.margin_right = tf_st.margin_top = Inches(0.2)
        
        p = tf_st.paragraphs[0]
        p.text = title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = color
        
        p_d = tf_st.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = TEXT_WHITE

    # =========================================================================
    # SLIDE 13: Streamlit Institutional Terminal Tour
    # =========================================================================
    s13 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s13)
    add_header(s13, "Operational Dashboard", "The 8-Tab Bloomberg Dark Streamlit Terminal")

    tabs = [
        ("Tab 1: Live Signals & Ingestion", "Real-time Supabase blotter, Finnhub/EDGAR manual ingestion triggers, confidence gauges."),
        ("Tab 2: GCSV & Vector Subtraction", "Interactive 768-D latent geometry visualizer, consensus scenario anchors, FinBERT polarity fusion."),
        ("Tab 3: Q&A Separation & Tone Drift", "Prepared vs Q&A divergence metrics, Welford C-suite executive language drift monitoring."),
        ("Tab 4: Contagion & Squeeze Shields", "NetworkX interactive graph shock propagation, short interest squeeze protection filters."),
        ("Tab 5: Quantile Alpha Decay", "Multi-horizon XGBoost prediction fan charts (T+1h, T+overnight, T+5d) with 80% CI."),
        ("Tab 6: Kelly Sizing & Execution", "Interactive Half-Kelly sizing surface, Alpaca paper trading broker execution gateway."),
        ("Tab 7: Indo-Global Multicorrelation", "Pairwise heatmaps, partial correlation tables, lead-lag curves, and Indian market shock simulator."),
        ("Tab 8: Empirical Validation & IEEE", "18-month backtest matrix, equity curves, and complete IEEE paper figures.")
    ]

    for idx, (title, desc) in enumerate(tabs):
        row = idx // 4
        col = idx % 4
        left = Inches(0.8 + col * 2.95)
        top = Inches(1.8 + row * 2.5)
        
        c = add_card(s13, left, top, Inches(2.8), Inches(2.25), bg_color=BG_CARD)
        tf_tab = c.text_frame
        tf_tab.margin_left = tf_tab.margin_right = tf_tab.margin_top = Inches(0.2)
        
        p = tf_tab.paragraphs[0]
        p.text = title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = ACCENT_CYAN if idx != 6 else ACCENT_GREEN
        
        p_d = tf_tab.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 14: Conclusion & Future Roadmap
    # =========================================================================
    s14 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s14)
    add_header(s14, "Summary & Outlook", "Conclusion & Next-Generation Horizons")

    # Card 1: Key Achievements
    c_ach = add_card(s14, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2), bg_color=BG_CARD)
    tf_a = c_ach.text_frame
    tf_a.margin_left = tf_a.margin_right = tf_a.margin_top = Inches(0.35)
    p = tf_a.paragraphs[0]
    p.text = "KEY RESEARCH CONTRIBUTIONS"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    achievements = [
        ("Paradigm Shift in Financial NLP", "Demonstrated that raw sentiment is uninformative in modern markets; expectations must serve as the coordinate origin for latent vectors."),
        ("End-to-End Modular Quant Architecture", "Bridged live ingestion, deep learning embeddings, macro regime switching, non-linear alpha decay, and broker execution into a single cohesive system."),
        ("Indo-Global Macro Alignment", "Quantified the empirical lead-lag transmission of global macro shocks to Indian equities, opening actionable morning opening strategies."),
        ("Exceptional Risk-Adjusted Alpha", "Achieved 72.6% directional hit rate, 2.34 Sharpe ratio, and -7.4% max drawdown with realistic 8 bps execution slippage.")
    ]
    for t, d in achievements:
        p_t = tf_a.add_paragraph()
        p_t.text = f"✓ {t}"
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = ACCENT_CYAN
        p_d = tf_a.add_paragraph()
        p_d.text = f"   {d}"
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = TEXT_MUTED

    # Card 2: Future Roadmap
    c_road = add_card(s14, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), bg_color=BG_CARD)
    tf_road = c_road.text_frame
    tf_road.margin_left = tf_road.margin_right = tf_road.margin_top = Inches(0.35)
    p = tf_road.paragraphs[0]
    p.text = "FUTURE RESEARCH DIRECTIONS"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_ORANGE

    roadmap = [
        ("Multi-Agent Autonomous Debate (LLMs)", "Integrating collaborative agent swarms (analyst, auditor, risk manager) to synthesize narrative scenarios automatically."),
        ("Options Surface Volatility Arbitrage", "Extracting full continuous risk-neutral implied probability distributions (Breeden-Litzenberger) rather than single strike anchors."),
        ("Level-2 Order Book Microstructure", "Modeling bid-ask imbalance and high-frequency book depth during the immediate 5-minute post-announcement window."),
        ("Expansion to European & Asian Indices", "Extending the cross-market transmission engine to DAX, FTSE 100, Nikkei 225, and Hang Seng.")
    ]
    for t, d in roadmap:
        p_t = tf_road.add_paragraph()
        p_t.text = f"🚀 {t}"
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_WHITE
        p_d = tf_road.add_paragraph()
        p_d.text = f"   {d}"
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 15: Thank You & Presentation Defense Slide
    # =========================================================================
    s15 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s15)

    # Decorative top bar
    top_bar = s15.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, Inches(0.12))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = ACCENT_CYAN
    top_bar.line.fill.background()

    # Main Center Heading
    thank_box = s15.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.3), Inches(1.8))
    tf_th = thank_box.text_frame
    tf_th.word_wrap = True
    p = tf_th.paragraphs[0]
    p.text = "Thank You!"
    p.font.size = Pt(46)
    p.font.bold = True
    p.alignment = PP_ALIGN.CENTER
    p.font.color.rgb = TEXT_WHITE

    p_sub = tf_th.add_paragraph()
    p_sub.text = "Questions & Technical Discussion"
    p_sub.font.size = Pt(22)
    p_sub.font.bold = True
    p_sub.alignment = PP_ALIGN.CENTER
    p_sub.font.color.rgb = ACCENT_GREEN

    # Team Credit Cards (Jay Salot & Mansi Patil)
    card_jay = add_card(s15, Inches(1.5), Inches(2.7), Inches(4.8), Inches(2.8), bg_color=BG_CARD)
    tf_j = card_jay.text_frame
    tf_j.margin_left = tf_j.margin_right = tf_j.margin_top = Inches(0.3)
    p = tf_j.paragraphs[0]
    p.text = "RESEARCHER & DEVELOPER"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p_n1 = tf_j.add_paragraph()
    p_n1.text = "Jay Salot"
    p_n1.font.size = Pt(26)
    p_n1.font.bold = True
    p_n1.font.color.rgb = TEXT_WHITE
    p_r1 = tf_j.add_paragraph()
    p_r1.text = "Roll No: 202518029"
    p_r1.font.size = Pt(18)
    p_r1.font.bold = True
    p_r1.font.color.rgb = ACCENT_ORANGE
    p_em1 = tf_j.add_paragraph()
    p_em1.text = "MarketPulse AI Core Architecture\nGCSV Latent Vector & Quantile Decay Models"
    p_em1.font.size = Pt(11)
    p_em1.font.color.rgb = TEXT_MUTED

    card_mansi = add_card(s15, Inches(7.0), Inches(2.7), Inches(4.8), Inches(2.8), bg_color=BG_CARD)
    tf_m = card_mansi.text_frame
    tf_m.margin_left = tf_m.margin_right = tf_m.margin_top = Inches(0.3)
    p = tf_m.paragraphs[0]
    p.text = "RESEARCHER & DEVELOPER"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p_n2 = tf_m.add_paragraph()
    p_n2.text = "Mansi Patil"
    p_n2.font.size = Pt(26)
    p_n2.font.bold = True
    p_n2.font.color.rgb = TEXT_WHITE
    p_r2 = tf_m.add_paragraph()
    p_r2.text = "Roll No: 202518034"
    p_r2.font.size = Pt(18)
    p_r2.font.bold = True
    p_r2.font.color.rgb = ACCENT_ORANGE
    p_em2 = tf_m.add_paragraph()
    p_em2.text = "Macro Regime & Contagion Engineering\nIndo-Global Multicorrelation Engine"
    p_em2.font.size = Pt(11)
    p_em2.font.color.rgb = TEXT_MUTED

    # Bottom Deliverables Banner
    b_banner = add_card(s15, Inches(1.5), Inches(5.8), Inches(10.3), Inches(1.1), bg_color=BG_CARD_LIGHT)
    tf_bb = b_banner.text_frame
    tf_bb.margin_left = tf_bb.margin_right = tf_bb.margin_top = Inches(0.2)
    p_b = tf_bb.paragraphs[0]
    p_b.text = "📁 PROJECT DELIVERABLES & DOCUMENTATION"
    p_b.font.size = Pt(11)
    p_b.font.bold = True
    p_b.font.color.rgb = ACCENT_CYAN
    p_bd = tf_bb.add_paragraph()
    p_bd.text = "• IEEE Transactions Format Research Paper (14 Pages)   • Streamlit Institutional App Operational Manual\n• Master Presentation Defense Script & Viva Guide (10 Q&As)   • GitHub: Jay-salot-2210/MarketPulseAI"
    p_bd.font.size = Pt(10.5)
    p_bd.font.color.rgb = TEXT_WHITE

    # Save
    os.makedirs(os.path.dirname(OUTPUT_PPTX), exist_ok=True)
    prs.save(OUTPUT_PPTX)
    print(f"✅ Presentation successfully generated and saved to: {OUTPUT_PPTX}")

if __name__ == "__main__":
    create_presentation()
