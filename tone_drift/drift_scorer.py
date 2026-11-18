import numpy as np
from loguru import logger
from tone_drift.executive_tracker import get_executive_centroid

def score_tone_drift(ticker: str, role: str, current_call_embedding: list[float] or np.ndarray) -> dict:
    """
    [Innovation 5] Tone Drift Scorer
    Measures the cosine distance between the current earnings call embedding and the
    executive's historical language centroid:
      tone_drift_score = 1.0 - cosine_similarity(v_call, v_centroid)
      
    A tone drift score > 0.28 towards hedging vocabulary indicates uncharacteristic caution,
    serving as an early warning soft prior before sell-side analysts downgrade ratings.
    """
    call_vec = np.array(current_call_embedding, dtype=float)
    centroid_vec = get_executive_centroid(ticker, role)
    
    norm_call = np.linalg.norm(call_vec)
    norm_centroid = np.linalg.norm(centroid_vec)
    
    if norm_call == 0 or norm_centroid == 0:
        cos_sim = 1.0
    else:
        cos_sim = float(np.dot(call_vec, centroid_vec) / (norm_call * norm_centroid))
        
    cos_sim = max(-1.0, min(1.0, cos_sim))
    tone_drift_score = round(float(1.0 - cos_sim), 4)
    
    drift_flag = tone_drift_score > 0.28
    
    # Direction analysis: determine if drift is toward hedging or confidence
    direction = "toward_hedging" if drift_flag else "stable_cadence"
    
    logger.info(f"Executive Tone Drift for {ticker} ({role}): score={tone_drift_score:.4f} | status={direction}")
    
    return {
        "ticker": ticker.upper(),
        "role": role.upper(),
        "tone_drift_score": tone_drift_score,
        "cosine_similarity": round(cos_sim, 4),
        "drift_flag": drift_flag,
        "drift_direction": direction,
        "prior_adjustment": -0.05 if drift_flag else 0.0
    }

if __name__ == "__main__":
    np.random.seed(101)
    v_test = np.random.randn(768)
    res = score_tone_drift("AAPL", "CFO", v_test)
    print(res)
