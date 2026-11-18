import numpy as np
from loguru import logger
from config.settings import THRESH_HIGH_DIVERGENCE

def parse_vector(vec):
    if isinstance(vec, np.ndarray):
        return vec
    return np.array(vec, dtype=float)

def compute_transcript_divergence(
    v_prepared,
    v_qa,
    v_consensus_base
) -> dict:
    """
    [Innovation 3] Transcript Q&A Separation & Divergence Scoring
    Separates earnings calls into scripted prepared remarks vs spontaneous Q&A.
    Computes surprise vector for both against zero-surprise baseline:
      v_surprise_prepared = v_prepared - v_consensus_base
      v_surprise_qa       = v_qa - v_consensus_base
      divergence_score    = 1 - cosine_similarity(v_surprise_prepared, v_surprise_qa)
      
    High divergence (> 0.25) implies management presented an optimistic prepared narrative
    but expressed caution or hedged when questioned by Wall Street analysts.
    """
    p_arr = parse_vector(v_prepared)
    qa_arr = parse_vector(v_qa)
    base_arr = parse_vector(v_consensus_base)
    
    v_surprise_prep = p_arr - base_arr
    v_surprise_qa = qa_arr - base_arr
    
    norm_prep = np.linalg.norm(v_surprise_prep)
    norm_qa = np.linalg.norm(v_surprise_qa)
    
    if norm_prep == 0 or norm_qa == 0:
        cos_sim = 1.0
    else:
        cos_sim = float(np.dot(v_surprise_prep, v_surprise_qa) / (norm_prep * norm_qa))
        
    # Clamp cosine similarity between -1 and 1 to prevent floating-point anomalies
    cos_sim = max(-1.0, min(1.0, cos_sim))
    
    divergence_score = round(float(1.0 - cos_sim), 4)
    divergence_flag = divergence_score > THRESH_HIGH_DIVERGENCE
    
    logger.info(
        f"Transcript GCSV: Cosine Sim = {cos_sim:.4f} | Divergence Score = {divergence_score:.4f} "
        f"| Flagged = {divergence_flag}"
    )
    
    return {
        "v_surprise_prepared": v_surprise_prep,
        "v_surprise_qa": v_surprise_qa,
        "cosine_similarity": round(cos_sim, 4),
        "transcript_divergence_score": divergence_score,
        "divergence_flag": divergence_flag,
        "confidence_penalty": 0.15 if divergence_flag else 0.0,
        "status": "MANAGEMENT_HEDGING_DETECTED" if divergence_flag else "PREPARED_QA_ALIGNED"
    }

if __name__ == "__main__":
    np.random.seed(42)
    # Simulated 768-dim vectors
    v_base = np.random.randn(768)
    v_p = v_base + np.random.randn(768) * 0.2
    v_q = v_base - np.random.randn(768) * 0.4  # Opposite direction
    res = compute_transcript_divergence(v_p, v_q, v_base)
    print("Divergence score:", res["transcript_divergence_score"], "Flag:", res["divergence_flag"])
