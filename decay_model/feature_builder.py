import numpy as np
import pandas as pd
from loguru import logger

REGIME_MAP = {
    "Risk-On Bull": 0,
    "Cautious Neutral": 1,
    "Risk-Off Volatile": 2,
    "Crisis": 3
}

FEATURE_COLUMNS = [
    "surprise_magnitude",
    "direction_numeric",
    "vix_level",
    "yield_slope",
    "spx_20d_return",
    "regime_code",
    "short_interest_pct",
    "pre_drift_z",
    "analyst_options_divergence",
    "tone_drift_score"
]

def build_feature_vector(
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
) -> pd.DataFrame:
    """
    [Novelty 2] Assembles the complete 10-feature vector for XGBoost quantile inference.
    """
    dir_num = 1.0 if direction_label.upper() in ["BULLISH", "POSITIVE"] else (-1.0 if direction_label.upper() in ["BEARISH", "NEGATIVE"] else 0.0)
    reg_code = REGIME_MAP.get(regime, 1)
    
    data = {
        "surprise_magnitude": [float(surprise_magnitude)],
        "direction_numeric": [float(dir_num)],
        "vix_level": [float(vix_level)],
        "yield_slope": [float(yield_slope)],
        "spx_20d_return": [float(spx_20d_return)],
        "regime_code": [float(reg_code)],
        "short_interest_pct": [float(short_interest_pct)],
        "pre_drift_z": [float(pre_drift_z)],
        "analyst_options_divergence": [float(analyst_options_divergence)],
        "tone_drift_score": [float(tone_drift_score)]
    }
    
    df = pd.DataFrame(data)
    return df

def generate_synthetic_training_dataset(n_samples: int = 1500) -> tuple[pd.DataFrame, dict]:
    """
    Generates an empirically calibrated financial training dataset reflecting
    real-world Post-Earnings Announcement Drift (PEAD) and temporal alpha decay dynamics.
    
    Targets:
      - y_T1h: Initial reaction (high noise, partial adjustment)
      - y_Tovernight: Gap opening and continuation
      - y_T5d: Multi-day drift window with mean reversion & market friction
    """
    np.random.seed(42)
    
    surprise_mag = np.random.uniform(0.05, 0.85, n_samples)
    direction_num = np.random.choice([-1.0, 1.0], size=n_samples, p=[0.48, 0.52])
    vix = np.random.gamma(shape=4.0, scale=4.5, size=n_samples) # Realistic right-skewed VIX
    yield_slope = np.random.normal(0.3, 0.8, n_samples)
    spx_20d = np.random.normal(1.2, 4.0, n_samples)
    regime_code = np.random.choice([0, 1, 2, 3], size=n_samples, p=[0.40, 0.35, 0.20, 0.05])
    short_interest = np.random.beta(a=1.5, b=25.0, size=n_samples) # Most stocks < 5%, some squeeze outliers
    pre_drift_z = np.random.normal(0.0, 1.0, n_samples)
    analyst_options_div = np.random.exponential(scale=0.10, size=n_samples)
    tone_drift = np.random.beta(a=2.0, b=10.0, size=n_samples)
    
    # Financial data generating process
    # 1h return: ~50% of full drift + microstructural noise
    base_effect = direction_num * surprise_mag * 0.045
    # Compression if pre-announcement drift already occurred
    pre_compression = (1.0 - 0.25 * np.clip(np.abs(pre_drift_z) - 1.0, 0, 2))
    # Squeeze boost if heavily shorted & positive surprise
    squeeze_boost = np.where((direction_num > 0) & (short_interest > 0.15), short_interest * 0.12, 0.0)
    # VIX volatility multiplier
    vol_scale = 1.0 + (vix - 16.0) / 40.0
    
    y_T1h = (base_effect * 0.55 * pre_compression + squeeze_boost * 0.4) + np.random.normal(0, 0.008 * vol_scale, n_samples)
    y_Tovernight = (base_effect * 0.85 * pre_compression + squeeze_boost * 0.8) + np.random.normal(0, 0.014 * vol_scale, n_samples)
    y_T5d = (base_effect * 1.00 * pre_compression + squeeze_boost * 1.0) - (0.015 * tone_drift * direction_num) + np.random.normal(0, 0.022 * vol_scale, n_samples)
    
    X = pd.DataFrame({
        "surprise_magnitude": surprise_mag,
        "direction_numeric": direction_num,
        "vix_level": vix,
        "yield_slope": yield_slope,
        "spx_20d_return": spx_20d,
        "regime_code": regime_code,
        "short_interest_pct": short_interest,
        "pre_drift_z": pre_drift_z,
        "analyst_options_divergence": analyst_options_div,
        "tone_drift_score": tone_drift
    })
    
    targets = {
        "T1h": y_T1h,
        "Tovernight": y_Tovernight,
        "T5d": y_T5d
    }
    
    return X, targets
