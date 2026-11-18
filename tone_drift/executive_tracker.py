import os
import json
import numpy as np
from loguru import logger

CENTROID_CACHE_FILE = os.path.join(os.path.dirname(__file__), "executive_centroids.json")

def load_all_centroids() -> dict:
    if os.path.exists(CENTROID_CACHE_FILE):
        try:
            with open(CENTROID_CACHE_FILE, "r") as f:
                data = json.load(f)
                return data
        except Exception as e:
            logger.warning(f"Failed to load executive centroids cache: {e}")
    return {}

def save_all_centroids(data: dict):
    try:
        with open(CENTROID_CACHE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save executive centroids cache: {e}")

def update_executive_centroid(
    executive_id: str,
    ticker: str,
    role: str,
    new_embedding: list[float] or np.ndarray
) -> dict:
    """
    [Innovation 5] Maintains per-executive embedding centroid using Welford's online update algorithm.
    Numerically stable online mean calculation:
      n_new = n + 1
      delta = x - mean_old
      mean_new = mean_old + delta / n_new
    """
    new_vec = np.array(new_embedding, dtype=float)
    centroids = load_all_centroids()
    
    key = f"{ticker.upper()}_{role.upper()}_{executive_id}"
    
    if key in centroids:
        rec = centroids[key]
        n = rec["call_count"] + 1
        old_centroid = np.array(rec["centroid"], dtype=float)
        updated_centroid = old_centroid + (new_vec - old_centroid) / n
    else:
        n = 1
        updated_centroid = new_vec
        
    centroids[key] = {
        "executive_id": executive_id,
        "ticker": ticker.upper(),
        "role": role.upper(),
        "call_count": n,
        "centroid": updated_centroid.tolist(),
        "last_updated": "2026-11-18"
    }
    
    save_all_centroids(centroids)
    logger.info(f"Updated centroid for {key}: call count {n}")
    return centroids[key]

def get_executive_centroid(ticker: str, role: str) -> np.ndarray:
    """
    Retrieves the historical centroid vector for a given executive role at a ticker.
    """
    centroids = load_all_centroids()
    for key, data in centroids.items():
        if data["ticker"] == ticker.upper() and data["role"] == role.upper():
            return np.array(data["centroid"], dtype=float)
            
    # Default synthetic baseline centroid if first time seeing this executive
    np.random.seed(hash(f"{ticker}_{role}") % 2**32)
    synthetic_centroid = np.random.randn(768)
    synthetic_centroid /= np.linalg.norm(synthetic_centroid)
    return synthetic_centroid
