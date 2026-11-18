import os
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from loguru import logger
from decay_model.feature_builder import generate_synthetic_training_dataset

MODEL_DIR = os.path.join(os.path.dirname(__file__), "saved_models")
HORIZONS = ["T1h", "Tovernight", "T5d"]
QUANTILES = [0.10, 0.50, 0.90]

def train_quantile_decay_models(n_samples: int = 2500) -> dict:
    """
    [Novelty 2] Trains 9 XGBoost Quantile Regressors:
      3 Horizons (T+1h, T+overnight, T+5d) x 3 Quantiles (10th, 50th, 90th percentile).
      
    Objective:
      Pinball loss (reg:quantileerror in XGBoost) producing calibrated prediction intervals.
      Avoids single-point deterministic return assumptions.
    """
    os.makedirs(MODEL_DIR, exist_ok=True)
    logger.info(f"Generating training dataset with {n_samples} samples...")
    X, targets = generate_synthetic_training_dataset(n_samples=n_samples)
    
    models = {}
    
    for h in HORIZONS:
        models[h] = {}
        y = targets[h]
        for q in QUANTILES:
            q_label = f"p{int(q*100)}"
            logger.info(f"Training XGBoost Quantile Regressor for {h} @ quantile {q:.2f} ({q_label})...")
            
            # Using XGBoost with quantile regression objective
            model = xgb.XGBRegressor(
                objective="reg:quantileerror",
                quantile_alpha=q,
                n_estimators=120,
                max_depth=4,
                learning_rate=0.04,
                subsample=0.85,
                colsample_bytree=0.85,
                random_state=42
            )
            model.fit(X, y)
            
            model_path = os.path.join(MODEL_DIR, f"xgb_{h}_{q_label}.joblib")
            joblib.dump(model, model_path)
            models[h][q_label] = model
            
    logger.success("All 9 XGBoost Quantile models successfully trained and serialized.")
    return models

def load_quantile_decay_models() -> dict:
    """
    Loads pre-trained models from disk; trains them if missing.
    """
    models = {}
    all_present = True
    
    for h in HORIZONS:
        models[h] = {}
        for q in QUANTILES:
            q_label = f"p{int(q*100)}"
            model_path = os.path.join(MODEL_DIR, f"xgb_{h}_{q_label}.joblib")
            if not os.path.exists(model_path):
                all_present = False
                break
            models[h][q_label] = joblib.load(model_path)
            
    if not all_present:
        logger.info("Saved models missing. Triggering training...")
        models = train_quantile_decay_models()
        
    return models

if __name__ == "__main__":
    train_quantile_decay_models()
