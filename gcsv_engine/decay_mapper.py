import numpy as np
from loguru import logger
from decay_model.feature_builder import build_feature_vector
from decay_model.trainer import load_quantile_decay_models, HORIZONS, QUANTILES

def predict_temporal_decay(
    surprise_magnitude: float,
    direction_label: str,
    vix_level: float = 16.5,
    yield_slope: float = 0.45,
    spx_20d_return: float = 1.8,
    regime: str = "Cautious Neutral",
    short_interest_pct: float = 0.025,
    pre_drift_z: float = 0.0,
    analyst_options_divergence: float = 0.08,
    tone_drift_score: float = 0.12
) -> dict:
    """
    [Novelty 2] Runs inference across all 9 XGBoost quantile decay models.
    Produces calibrated return forecasts:
      - 3 temporal horizons (T+1h, T+overnight, T+5d)
      - 3 quantile bounds: p10 (downside tail), p50 (median expectation), p90 (upside tail)
      
    Selects best_horizon using maximum return-to-uncertainty ratio: |p50| / (p90 - p10).
    """
    models = load_quantile_decay_models()
    X = build_feature_vector(
        surprise_magnitude=surprise_magnitude,
        direction_label=direction_label,
        vix_level=vix_level,
        yield_slope=yield_slope,
        spx_20d_return=spx_20d_return,
        regime=regime,
        short_interest_pct=short_interest_pct,
        pre_drift_z=pre_drift_z,
        analyst_options_divergence=analyst_options_divergence,
        tone_drift_score=tone_drift_score
    )
    
    predictions = {}
    horizon_sharpe = {}
    
    for h in HORIZONS:
        p10 = float(models[h]["p10"].predict(X)[0])
        p50 = float(models[h]["p50"].predict(X)[0])
        p90 = float(models[h]["p90"].predict(X)[0])
        
        # Enforce quantile monotonicity: p10 <= p50 <= p90
        p10_sorted = min(p10, p50)
        p90_sorted = max(p90, p50)
        
        ci_width = max(0.001, p90_sorted - p10_sorted)
        # Expected Sharpe proxy
        sharpe_proxy = abs(p50) / ci_width
        horizon_sharpe[h] = sharpe_proxy
        
        predictions[h] = {
            "p10": round(p10_sorted, 4),
            "p50": round(p50, 4),
            "p90": round(p90_sorted, 4),
            "ci_width": round(ci_width, 4)
        }
        
    best_horizon = max(horizon_sharpe, key=horizon_sharpe.get)
    logger.info(f"Quantile decay mapped: Best Horizon = {best_horizon} with p50 = {predictions[best_horizon]['p50']*100:.2f}%")
    
    return {
        "predicted_returns": predictions,
        "best_horizon": best_horizon,
        "best_p50": predictions[best_horizon]["p50"],
        "best_ci_width": predictions[best_horizon]["ci_width"]
    }

if __name__ == "__main__":
    out = predict_temporal_decay(
        surprise_magnitude=0.45,
        direction_label="BULLISH",
        regime="Risk-On Bull"
    )
    print("Predictions:", out)
