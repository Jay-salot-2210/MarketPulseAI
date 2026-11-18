import json 
from loguru import logger
from config.settings import db

# Conservative portfolio risk parameters
MAX_ALLOCATION_CAP = 0.10  # 10% maximum portfolio allocation per asset
HALF_KELLY_FRACTION = 0.50 # Conservative half-Kelly to guard against estimation error
REGIME_ALLOCATION_LIMITS = {
    "Risk-On Bull": 0.10,
    "Cautious Neutral": 0.06,
    "Risk-Off Volatile": 0.03,
    "Crisis": 0.00
}

def calculate_kelly_fraction(win_prob: float, win_loss_ratio: float = 2.0, fractional_multiplier: float = 0.5) -> float:
    """
    Standard Kelly formula:
      f* = p - (1 - p) / b
    where p is win probability and b is win/loss payoff ratio.
    """
    if win_prob <= 0 or win_loss_ratio <= 0:
        return 0.0

    kelly_pct = win_prob - ((1.0 - win_prob) / win_loss_ratio)

    if kelly_pct < 0:
        return 0.0

    return round((kelly_pct * fractional_multiplier) * 100, 2)

def calculate_advanced_kelly_sizing(
    p50_predicted_return: float,
    p10_return: float,
    p90_return: float,
    confidence_tier: str = "HIGH",
    regime: str = "Cautious Neutral"
) -> dict:
    """
    [Innovation 9] Rigorous Kelly Criterion Position Sizing derived from Quantile Predictions.
    
    Formula:
      edge = |p50|
      odds (b) = |p50| / (p90 - p10)  [return-to-risk ratio from 80% CI width]
      win_p = empirical hit rate for confidence tier
      f* = (win_p * b - (1 - win_p)) / b
      f_applied = min(f* * 0.5, max_cap, regime_limit)
    """
    hit_rates = {
        "HIGH": 0.72,
        "MEDIUM": 0.61,
        "LOW": 0.52,
        "UNCERTAIN": 0.40
    }
    win_p = hit_rates.get(confidence_tier.upper(), 0.55)
    
    ci_width = max(0.001, p90_return - p10_return)
    edge = abs(p50_predicted_return)
    
    # Payoff odds: ratio of expected return to uncertainty band
    odds = max(0.1, edge / ci_width)
    
    f_star = (win_p * odds - (1.0 - win_p)) / odds
    
    # Half-Kelly for risk mitigation
    f_half = max(0.0, f_star * HALF_KELLY_FRACTION)
    
    # Impose regime ceiling & global cap
    regime_ceiling = REGIME_ALLOCATION_LIMITS.get(regime, 0.05)
    f_final = min(f_half, MAX_ALLOCATION_CAP, regime_ceiling)
    
    suggested_allocation_pct = round(f_final * 100, 2)
    
    logger.info(
        f"Kelly Sizing: WinP={win_p*100:.1f}%, Odds={odds:.2f}, f*={f_star*100:.1f}%, "
        f"Final Allocated={suggested_allocation_pct}% (Regime: {regime})"
    )
    
    return {
        "full_kelly_f": round(float(f_star), 4),
        "half_kelly_f": round(float(f_half), 4),
        "suggested_allocation_pct": suggested_allocation_pct,
        "odds_ratio": round(float(odds), 2),
        "win_probability": win_p,
        "regime_cap_applied": suggested_allocation_pct < round(f_half * 100, 2)
    }

def run_portfolio_allocator():
    print("Initializing Kelly Criterion Position Sizer...")

    try:
        response = db.table("trading_signals")\
            .select("id, ticker, direction_label, confidence, suggested_allocations_pct")\
            .order("created_at", desc=True)\
            .limit(10)\
            .execute()

        signals = response.data
        if not signals:
            print("No signal found to allocate")
            return
            
        for signal in signals:
            ticker = signal["ticker"]
            if ticker == "GEN" or signal.get("suggested_allocations_pct") is not None:
                continue

            conf_str = signal.get("confidence", "50.0%").replace('%', '')
            try:
                win_prob = float(conf_str) / 100.0
            except Exception:
                win_prob = 0.55

            allocation_pct = calculate_kelly_fraction(win_prob, win_loss_ratio=2.0)

            db.table("trading_signals")\
                .update({"suggested_allocations_pct": allocation_pct})\
                .eq("id", signal["id"])\
                .execute()

            print(f"{ticker} ({signal['direction_label'].upper()}): Allocated {allocation_pct}% of capital")

        print("\nPortfolio sizing complete. Capital allocated efficiently.")

    except Exception as e:
        print(f"Allocation failed: {e}")

if __name__ == "__main__":
    test_calc = calculate_advanced_kelly_sizing(
        p50_predicted_return=0.025,
        p10_return=0.005,
        p90_return=0.045,
        confidence_tier="HIGH",
        regime="Risk-On Bull"
    )
    print("Advanced Kelly Result:", test_calc)
