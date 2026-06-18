# MarketPulse AI — Problem Statement & Proposed Solution (v3)

---

## 1. The Core Problem: Markets React to Surprise, Not to News

Every financial NLP system built today makes the same foundational mistake: it reads news in a vacuum.
It scores a headline as "positive" or "negative" based on words alone, completely ignoring the single
most important variable in market price formation — what was already expected.

Financial markets are not absolute systems. They are expectation-clearing machines. As Fama (1970)
established in his foundational efficient markets hypothesis, asset prices at each moment incorporate
all available information about future values [1]. A consequence of this is that prices already embed
every piece of information the market collectively anticipates — and it is only the *variance* between
expectation and realisation that drives price movement. A company posting 20% revenue growth can
trigger a violent sell-off if analysts expected 25%. A company posting a loss can trigger a relief
rally if the loss was smaller than feared. In both cases, a traditional sentiment model scores the
wrong direction entirely.

This is not an edge case. It is the dominant dynamic in every earnings season, every Fed announcement,
every macro data release. The market does not react to what happened — it reacts to the delta between
what happened and what was priced in.

---

### The Seven Structural Failures of Existing Systems

**Failure 1 — The Vacuum Effect**
Standard NLP pipelines assign a sentiment score to raw news text with no knowledge of pre-existing
market expectations, analyst consensus, or options market pricing. General-purpose models are not
effective enough for financial text because of the specialised language used in a financial context,
as documented by Araci (2019) in the introduction of FinBERT [2]. The output is systematically
misleading because it has no reference frame.

**Failure 2 — The Valuation Blindspot**
A 10% revenue beat sounds positive in isolation. If consensus was expecting 18%, it is a catastrophic
miss. No sentiment score captures this. The model fires a buy signal; the market sells off 8%. This
is not model noise — it is a deterministic flaw in the architecture. Ball and Brown (1968), cited
in Brockman et al. (2011) [3], established that stock returns drift in the direction of *unexpected*
earnings — not reported earnings — a finding that directly indicts systems which ignore the
expectation baseline.

**Failure 3 — Single-Source Consensus**
Analyst EPS estimates are one view of market expectations. Options market pricing — implied
volatility, put/call ratios, unusual flow — is a faster, money-weighted, forward-looking second view.
Bali and Hovakimian (2009) and Cremers and Weinbaum (2010), as summarised by Muravyev et al. (2025)
[4], document that transformations of options-implied volatilities predict the cross-section of stock
returns over one to several weeks. Systems that read only analyst estimates are missing a predictive
signal that operates on a shorter and often more accurate timeframe than sell-side research.

**Failure 4 — Temporal Disconnect**
A surprise at 4:30 PM after market close behaves differently from the same surprise at 11:00 AM
during peak intraday liquidity. Static thresholds calibrated at a single point in time cannot adapt
to market microstructure. No existing NLP trading system models how alpha decays differently across
overnight, intraday, and multi-day correction windows — they treat all signals as equally urgent.

**Failure 5 — Static Thresholds on a Dynamic Market**
The market's sensitivity to surprise changes continuously with regime. A surprise classified as HIGH
confidence in a low-volatility bull market may be noise in the middle of a systemic correction.
Static classifiers cannot track this.

**Failure 6 — No Cross-Asset Contagion Awareness and Latency in Primary Sources**
Individual company surprises propagate. A TSMC earnings miss moves NVDA, AMD, AMAT, and ASML within
hours. Existing systems wait for RSS feeds, which are downstream derivatives of the SEC EDGAR filing
system. Under U.S. securities law, publicly traded companies are required to file material events on
Form 8-K within four business days — and in many cases on the same day — of the triggering event
[5]. EDGAR is the primary source; all news wires are secondary. Plugging in downstream introduces
unnecessary latency and coverage gaps.

**Failure 7 — No Signal Accountability**
Existing systems emit signals but never measure whether they were correct. Without a feedback loop
connecting predicted returns to realised returns, there is no way to detect model drift, identify
which regime and sector combinations produce reliable signals, or progressively improve the model
over time.

---

## 2. The Solution: MarketPulse AI v3

MarketPulse AI is an expectation-aware, self-improving, regime-conditioned, outcome-tracked alpha
generation framework built on the base GCSV (Generative Counterfactual Surprise Vectoring)
architecture, extended by ten integrated innovations.

### Base Architecture: Generative Counterfactual Surprise Vectoring (GCSV)

The system computes surprise as the geometric distance between two high-dimensional representations
in transformer latent space, using FinBERT [2] — a language model pre-trained on financial corpora
including Reuters news articles, 10-K filings, and earnings call transcripts — as its embedding
engine.

- `v_actual`    — embedding of the real published event text
- `v_consensus` — embedding of a synthetically generated "zero-surprise" narrative

$$\mathbf{v}_{\text{surprise}} = \mathbf{v}_{\text{actual}} - \mathbf{v}_{\text{consensus}}$$

The resulting vector isolates only the structural narrative anomalies that the market had not priced
in. By operating in the full 768-dimensional latent space rather than collapsing to a scalar
sentiment score, GCSV preserves the contextual and positional richness of what changed — not merely
how much.

---

## 3. The Ten Integrated Innovations

### Innovation 1 — Dual-Source Consensus (Analyst + Options)

The options market prices surprises before analysts update their models. Research by Lipkin,
Tatevossian, and Arjun (2024) [6] shows that in most cases the options market does a good job of
predicting the price impact in magnitude of an earnings event. Patell and Wolfson (1979, 1981),
as referenced in multiple subsequent studies [7], documented the well-established phenomenon that
implied volatility increases ahead of earnings announcements and decreases sharply after. The system
builds two independent consensus vectors per ticker: `v_consensus_analyst` (from EPS and revenue
estimates) and `v_consensus_options` (from implied volatility term structure, put/call ratio, and
unusual options flow). The divergence between the two consensus sources is itself a signal: when
analysts and the options market disagree sharply, that uncertainty modifies the confidence tier of
the GCSV output.

### Innovation 2 — SEC EDGAR 8-K Primary Source Ingestion

Under Section 13 of the Securities Exchange Act of 1934 and the SEC's 2004 amendments to Form 8-K
[5], publicly traded companies are required to disclose material events within four business days
of occurrence — and in many cases on the day itself. The system plugs directly into the EDGAR
full-text search API (`efts.sec.gov`) to receive filings within minutes of submission, ahead of
RSS feeds and news wires. Events with no analyst consensus (CEO resignation, unexpected contract
loss) are processed with a special single-vector mode: the absolute magnitude of `v_actual` drives
the classification, with no subtraction applied.

### Innovation 3 — Earnings Call Q&A Separation

Brockman, Khurana, and Martin (2008) [3], in a study of over 2,800 conference call transcripts
spanning 16 consecutive quarters, differentiated between management's prepared remarks and the
more spontaneous question-and-answer portion of the call, finding that the Q&A section carries
incremental information beyond the written press release. Matsumoto et al. (2011), cited in
subsequent engagement research [8], confirmed that the Q&A session is the most informative portion
of the earnings call. The system splits transcripts into two segments and embeds them independently:
`v_prepared` and `v_qa`. The divergence between the two resulting surprise vectors — management
communicated one position in prepared remarks but hedged under analyst Q&A pressure — is a leading
indicator of guidance revision risk.

### Innovation 4 — Scoped Insider Trading Signal

The academic literature on insider trading is unusually consistent. Lakonishok and Lee (2001) [9],
studying NYSE, AMEX, and Nasdaq exchanges from 1975 to 1995, found that stocks with the highest
insider net purchase ratios outperformed those with the lowest by approximately 7.5% over 12 months.
Cohen, Malloy, and Pomorski (2012) [10], published in the Journal of Finance, refined this result
by distinguishing between "routine" insider trades (predictable, calendar-based) and "opportunistic"
trades (irregular timing, often preceding material news), finding that opportunistic purchases
produced approximately 5.2% six-month alpha. Jeng, Metrick, and Zeckhauser (2003) [11] found that
insider purchases yield abnormal returns exceeding 6% per year, while insider sales do not produce
significant abnormal returns. The system ingests only open-market purchases (SEC Form 4 transaction
code "P") within 30 days of an earnings date, above a materiality threshold relative to the
insider's historical trading volume. Routine 10b5-1 plan sales and stock compensation grants are
excluded entirely — as the research consistently confirms, it is purchases, not sales, that carry
the predictive signal.

### Innovation 5 — Management Tone Drift Detection

Research by Angelo et al. (2025) [12], published in *Financial Review*, documents that differences
in managerial tone within and across earnings calls are informative to markets and positively predict
stock volatility and operational risks. Meursault and Kogan, as discussed by the Philadelphia Federal
Reserve [13], find that CEOs and CFOs use more subjective language in the Q&A section than during
opening remarks, and that a higher concentration of subjective language in earnings calls is
associated with higher post-call investor disagreement. The system maintains a per-executive
embedding centroid built from historical transcript archives. A CFO whose language centroid drifts
toward hedging vocabulary across three consecutive quarters produces a `tone_drift_score` that
feeds into the consensus baseline as a soft prior — a leading indicator of a potential miss before
any numerical signal exists.

### Innovation 6 — Signal Self-Evaluation Feedback Loop

No production ML system can be calibrated without measuring its own predictions. The system adds
a `signal_outcome` table that, 24 hours and 5 days after every signal, records the realised price
return and computes an accuracy score against the predicted return distribution. Over time this
builds a calibration dataset identifying which regime, sector, and confidence tier combinations
produce reliable signals and which produce noise. Categories with poor historical accuracy are
automatically down-weighted in the signal tier classifier. Accuracy drop-off above a defined
threshold triggers a Slack alert and a retraining flag.

### Innovation 7 — Pre-Announcement Drift Detector

If a stock moves unusually in the 48 hours before an earnings release, information may be leaking
or the market may already be partially pricing the expected surprise. The system computes a z-score
of the 48-hour pre-event return against the historical distribution of pre-earnings returns for
the same ticker. A high `pre_drift_z` score feeds into the uncertainty scorer as an additional
input: high pre-announcement drift either confirms the expected surprise is partially priced in
(reducing the alpha window) or signals potential information leakage (which modifies confidence
downward). This is a lightweight statistical test applied to price data already being fetched.

### Innovation 8 — Short Interest Direction Modifier

A bearish surprise signal on a stock with high short interest carries a different risk profile from
the same signal on a lightly shorted stock. High short interest combined with a positive earnings
surprise is a well-documented trigger for short squeezes — events in which short sellers are forced
to buy back shares at accelerating prices [14]. Conversely, as documented in academic research on
short selling as an informed activity [15], positive surprises in short interest themselves predict
lower unexpected earnings and lower cumulative abnormal returns around earnings announcements.
The system fetches biweekly FINRA short interest data for all tracked tickers. A hard override rule
applies: if a signal is BEARISH, short interest exceeds 20% of float, and the surprise magnitude is
below the MEDIUM threshold, the signal is downgraded to UNCERTAIN due to short squeeze risk. Short
interest is also included as a feature in the XGBoost decay model.

### Innovation 9 — Kelly Criterion Position Sizing

Kelly (1956) [16], published in the Bell System Technical Journal, derived the formula for the
optimal fraction of capital to commit to a wager as a function of the win probability and the
payoff ratio. The system outputs not just direction and confidence but a `suggested_allocation_pct`
computed from the Kelly formula using the predicted return (p50 from the decay model) and the
confidence interval width (p10 to p90) as the return-to-risk ratio, combined with the historical
hit rate for the current confidence tier. A conservative half-Kelly variant is applied with a
maximum allocation cap to prevent the formula's tendency toward overbet in the presence of
estimation error. This converts a signal service into an actionable execution guide.

### Innovation 10 — Signal Performance Dashboard + Alpaca Paper Trading

All HIGH and MEDIUM confidence signals are simultaneously forwarded to an Alpaca paper trading
account with Kelly-sized position quantities, producing forward-tested P&L with real slippage.
A React dashboard visualises signal accuracy by regime, sector, horizon, and confidence tier from
the `signal_outcome` table. Model drift is immediately visible: a drop in hit rate for a specific
configuration triggers a retraining alert. Forward-tested paper trading provides far more credible
evidence of system quality than historical backtests, which are subject to survivorship bias,
lookahead bias, and perfect fill assumptions.

---

## 4. Scope Decisions

**Cross-lingual full NLP translation**: Full multilingual ingestion with Japanese, Korean, and
Taiwanese filing parsing and machine translation was evaluated and scoped down. The accepted version
adds English-language investor relations RSS feeds for TSMC, Samsung, and ASML only. These three
companies already publish English IR content and represent the highest-impact non-US events for the
US technology contagion graph. The full translation layer introduces unreliable free API
dependencies and inconsistent data quality.

**Full Form 4 ingestion**: Routine 10b5-1 plan sales, stock compensation grants, and tax-related
sells dominate Form 4 volume. The academic literature consistently confirms that only open-market
purchases carry a reliable predictive signal [9][10][11]. The system is scoped accordingly.

---

## 5. System Capabilities Summary

| Dimension | v1 (Base) | v2 (+5 Novelties) | v3 (+10 Innovations) |
|---|---|---|---|
| Consensus sources | Analyst estimates only | Analyst only | Analyst + Options market |
| Primary data source | RSS feeds | RSS feeds | RSS + EDGAR 8-K direct |
| Event types | Earnings articles | Earnings articles | Articles + transcripts + 8-K + insider + tone drift |
| Signal confidence | Magnitude threshold | Uncertainty scoring | Uncertainty + pre-drift + short interest + tone drift |
| Position guidance | None | None | Kelly Criterion sizing |
| Outcome tracking | None | None | signal_outcome feedback loop |
| Execution | Webhook only | Webhook only | Webhook + Alpaca paper trading |
| Monitoring | Supabase tables | Supabase tables | Live React dashboard |
| Contagion | US tickers | US tickers | US tickers + TSMC/Samsung/ASML English IR |

---

## References

[1] Fama, E.F. (1970). Efficient Capital Markets: A Review of Theory and Empirical Work.
    *Journal of Finance*, 25(2), 383–417.
    https://doi.org/10.2307/2325486

[2] Araci, D. (2019). FinBERT: Financial Sentiment Analysis with Pre-trained Language Models.
    *arXiv preprint*, arXiv:1908.10063.
    https://arxiv.org/abs/1908.10063

[3] Brockman, P., Khurana, I.K., & Martin, X. (2008). Voluntary disclosures around share
    repurchases. *Journal of Financial Economics*, 89(1). [Referenced for the underlying
    Ball and Brown (1968) post-earnings announcement drift finding and the earnings conference
    call textual tone study of 2,800+ transcripts across 16 quarters (2004–2007).]
    See also: Brockman, P., Li, X., & Price, S.M. (2011). Earnings conference calls and stock
    returns: The incremental informativeness of textual tone.
    *Journal of Banking & Finance*, 35(4), 992–1011.
    https://doi.org/10.1016/j.jbankfin.2010.09.017

[4] Muravyev, D., Pearson, N.D., & Pollet, J.M. (2025). Why does options market information
    predict stock returns? *Journal of Financial Economics*, 169.
    https://doi.org/10.1016/j.jfineco.2025.103901
    [Summarises the findings of Bali & Hovakimian (2009) and Cremers & Weinbaum (2010) on
    implied volatility spread and stock return predictability.]

[5] U.S. Securities and Exchange Commission (2004). Additional Form 8-K Disclosure Requirements
    and Acceleration of Filing Date. Final Rule, Release No. 33-8400.
    https://www.sec.gov/rules-regulations/2004/03/additional-form-8-k-disclosure-requirements-acceleration-filing-date
    See also: SEC Form 8-K Instructions.
    https://www.sec.gov/files/form8-k.pdf

[6] Lipkin, M., Tatevossian, L., & Arjun, K.M. (2024). Earnings Moves and Pre-Earnings Implied
    Volatility. *SSRN Working Paper*, No. 4701633.
    https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4701633

[7] Patell, J.M., & Wolfson, M.A. (1979). Anticipated information releases reflected in call
    option prices. *Journal of Accounting and Economics*, 1(2), 117–140.
    https://doi.org/10.1016/0165-4101(79)90003-7
    [Established the foundational finding that implied volatility increases ahead of earnings
    announcements and decreases sharply after, as subsequently referenced across the options
    market literature.]

[8] Noh, S., & Zhou, T. (2022). Engagement in Earnings Conference Calls.
    *Journal of Accounting and Economics*, 74(1).
    https://doi.org/10.1016/j.jacceco.2022.101488
    [Documents that the Q&A portion of earnings calls is the most informative section,
    citing Matsumoto et al. (2011) as the seminal finding.]

[9] Lakonishok, J., & Lee, I. (2001). Are Insider Trades Informative?
    *Review of Financial Studies*, 14(1), 79–111.
    https://doi.org/10.1093/rfs/14.1.79

[10] Cohen, L., Malloy, C., & Pomorski, L. (2012). Decoding Inside Information.
     *Journal of Finance*, 67(3), 1009–1043.
     https://doi.org/10.1111/j.1540-6261.2012.01740.x
     [Distinguishes routine from opportunistic insider trades; opportunistic purchases produce
     approximately 5.2% six-month alpha relative to benchmark.]

[11] Jeng, L.A., Metrick, A., & Zeckhauser, R. (2003). Estimating the Returns to Insider Trading:
     A Performance-Evaluation Perspective. *Review of Economics and Statistics*, 85(2), 453–471.
     https://doi.org/10.1162/003465303765299936

[12] Angelo, B., Johnston, M., Singh, A., & Wan, Y.Q. (2025). Tone Distance: Managerial Tone
     Divergence and Market Reaction to Earnings Announcements.
     *Financial Review*, 60, 1415–1435.
     https://doi.org/10.1111/fire.70002

[13] Meursault, V., & Kogan, L. (referenced in Philadelphia Federal Reserve, 2024).
     Disentangling the Content of Earnings Calls: How Corporate Messaging Affects Firms'
     Financial Performance.
     https://www.philadelphiafed.org/the-economy/banking-and-financial-markets/disentangling-the-content-of-earnings-calls
     [Documents that CEOs and CFOs use more subjective language in Q&A than in opening remarks,
     and that subjective language concentration predicts post-call investor disagreement.]

[14] Wall Street Prep (2024). Short Squeeze: Definition, Mechanics, and Examples.
     https://www.wallstreetprep.com/knowledge/short-squeeze/
     [Documents the well-established mechanism by which positive earnings surprises trigger
     short covering in heavily shorted stocks, accelerating upward price momentum.]

[15] Čorić, T., et al. (2023). Surprise in Short Interest.
     *International Review of Financial Analysis*, 88.
     https://doi.org/10.1016/j.irfa.2023.102612
     [Finds that positive surprises in short interest predict lower unexpected earnings and
     lower cumulative abnormal returns around earnings announcements, confirming short sellers
     as informed market participants.]

[16] Kelly, J.L. Jr. (1956). A New Interpretation of Information Rate.
     *Bell System Technical Journal*, 35(4), 917–926.
     https://doi.org/10.1002/j.1538-7305.1956.tb03809.x
     [Original derivation of the Kelly Criterion for optimal bet sizing; subsequently adopted
     in portfolio management literature as a position sizing framework.]
