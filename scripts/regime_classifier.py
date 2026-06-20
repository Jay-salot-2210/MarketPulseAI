import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
from loguru import logger
from config.settings import db


def fetch_vix_level() -> float:
    """Current VIX (market fear gauge). Below 16 = calm, above 35 = crisis."""
    vix = yf.Ticker("^VIX")
    hist = vix.history(period="5d")
    latest = float(hist["Close"].iloc[-1])
    logger.info(f"VIX level: {latest:.2f}")
    return latest


def fetch_yield_slope() -> float:
    """
    Yield curve slope: 10-Year yield minus 3-Month yield.
    Negative slope (inverted curve) historically signals recession risk.
    """
    ten_year = yf.Ticker("^TNX").history(period="5d")["Close"].iloc[-1]
    three_month = yf.Ticker("^IRX").history(period="5d")["Close"].iloc[-1]
    slope = float(ten_year - three_month)
    logger.info(f"Yield slope (10Y - 3M): {slope:.2f}")
    return slope


def fetch_spx_20d_return() -> float:
    """S&P 500 percent return over the last 20 trading days."""
    spx = yf.Ticker("^GSPC")
    hist = spx.history(period="30d")["Close"]
    start_price = hist.iloc[-20]
    end_price = hist.iloc[-1]
    pct_return = float((end_price - start_price) / start_price * 100)
    logger.info(f"SPX 20-day return: {pct_return:.2f}%")
    return pct_return


def classify_regime(vix: float, yield_slope: float, spx_20d: float) -> str:
    """
    Classifies current market conditions into one of 4 regimes.
    Priority order: Crisis check first (VIX alone is enough to flag it),
    then Risk-On Bull, then Risk-Off Volatile, else Cautious Neutral.
    """
    if vix > 35:
        return "Crisis"

    if vix < 16 and yield_slope > 0 and spx_20d > 2:
        return "Risk-On Bull"

    if vix >= 22 and yield_slope < 0 and spx_20d < -2:
        return "Risk-Off Volatile"

    return "Cautious Neutral"


def write_regime_to_db(regime_label: str, vix: float, yield_slope: float, spx_20d: float):
    """Writes the classified regime into Jay's market_regimes table."""
    payload = {
        "regime_label": regime_label,
        "vix_level": round(vix, 2),
        "yield_slope": round(yield_slope, 2),
        "spx_20d_return": round(spx_20d, 2)
    }

    try:
        db.table("market_regimes").insert(payload).execute()
        logger.success(f"Regime written to DB: {regime_label}")
    except Exception as e:
        logger.error(f"Failed to write regime: {e}")


def run_regime_classification():
    logger.info("Starting market regime classification...")

    vix = fetch_vix_level()
    yield_slope = fetch_yield_slope()
    spx_20d = fetch_spx_20d_return()

    regime = classify_regime(vix, yield_slope, spx_20d)

    logger.info(f"Classification: VIX={vix:.2f}, slope={yield_slope:.2f}, "
                f"spx_20d={spx_20d:.2f}% → {regime}")

    write_regime_to_db(regime, vix, yield_slope, spx_20d)

    return regime


if __name__ == "__main__":
    run_regime_classification()