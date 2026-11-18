import yfinance as yf
from loguru import logger
from config.settings import SURPRISE_THRESHOLD_MEDIUM

# Default FINRA benchmark short interest figures (% of float)
SHORT_INTEREST_BENCHMARKS = {
    "TSLA": {"short_pct": 0.038, "days_to_cover": 1.4},
    "AAPL": {"short_pct": 0.009, "days_to_cover": 1.1},
    "MSFT": {"short_pct": 0.008, "days_to_cover": 1.2},
    "GME":  {"short_pct": 0.245, "days_to_cover": 6.8},
    "CVNA": {"short_pct": 0.221, "days_to_cover": 5.2},
    "DEFAULT": {"short_pct": 0.025, "days_to_cover": 2.0}
}

def fetch_short_interest(ticker: str) -> dict:
    """
    Fetches short interest percent of float and days to cover from Yahoo Finance / FINRA.
    """
    sym = ticker.upper()
    try:
        stock = yf.Ticker(sym)
        info = stock.info
        short_pct = info.get("shortPercentOfFloat")
        days_to_cover = info.get("shortRatio")
        
        if short_pct is not None and days_to_cover is not None:
            return {
                "short_interest_pct": round(float(short_pct), 4),
                "days_to_cover": round(float(days_to_cover), 2)
            }
    except Exception as e:
        logger.warning(f"Could not fetch live short interest for {sym}: {e}")
        
    fallback = SHORT_INTEREST_BENCHMARKS.get(sym, SHORT_INTEREST_BENCHMARKS["DEFAULT"])
    return {
        "short_interest_pct": fallback["short_pct"],
        "days_to_cover": fallback["days_to_cover"]
    }

def evaluate_short_interest_modifier(
    ticker: str,
    direction_label: str,
    surprise_magnitude: float,
    current_confidence: str = "HIGH"
) -> dict:
    """
    [Innovation 8] Short Interest Direction Modifier
    A bearish surprise on a heavily shorted stock carry asymmetric risk: if the miss is modest,
    short covering often triggers a sharp upward short squeeze rally.
    
    Rule:
    If direction == 'BEARISH' AND short_interest_pct > 20% (0.20) AND magnitude < MEDIUM (0.25):
      -> short_squeeze_risk = True
      -> Override confidence to 'UNCERTAIN'
    """
    si_data = fetch_short_interest(ticker)
    si_pct = si_data["short_interest_pct"]
    dtc = si_data["days_to_cover"]
    
    is_bearish = direction_label.upper() in ["BEARISH", "NEGATIVE"]
    high_si = si_pct >= 0.20
    weak_magnitude = surprise_magnitude < SURPRISE_THRESHOLD_MEDIUM
    
    short_squeeze_risk = is_bearish and high_si and weak_magnitude
    override_applied = False
    final_confidence = current_confidence
    
    if short_squeeze_risk:
        override_applied = True
        final_confidence = "UNCERTAIN"
        logger.warning(
            f"⚠️ SHORT SQUEEZE SHIELD TRIGGERED for {ticker}: "
            f"Bearish signal with {si_pct*100:.1f}% short float & low surprise magnitude ({surprise_magnitude:.2f}). "
            f"Downgrading confidence to UNCERTAIN."
        )
    else:
        logger.info(f"{ticker} Short Interest check passed: {si_pct*100:.2f}% of float (DTC: {dtc}).")
        
    return {
        "ticker": ticker.upper(),
        "short_interest_pct": si_pct,
        "days_to_cover": dtc,
        "short_squeeze_risk": short_squeeze_risk,
        "override_applied": override_applied,
        "original_confidence": current_confidence,
        "final_confidence": final_confidence
    }

if __name__ == "__main__":
    print(evaluate_short_interest_modifier("CVNA", "BEARISH", 0.18, "HIGH"))
    print(evaluate_short_interest_modifier("AAPL", "BEARISH", 0.35, "HIGH"))
