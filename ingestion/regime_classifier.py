# Regime classifier ingestion wrapper
# Re-exports core regime classification logic from scripts/regime_classifier.py
from scripts.regime_classifier import (
    fetch_vix_level,
    fetch_yield_slope,
    fetch_spx_20d_return,
    classify_regime,
    write_regime_to_db,
    run_regime_classification,
)

__all__ = [
    "fetch_vix_level",
    "fetch_yield_slope",
    "fetch_spx_20d_return",
    "classify_regime",
    "write_regime_to_db",
    "run_regime_classification",
]

if __name__ == "__main__":
    run_regime_classification()
