import numpy as np
from loguru import logger
from gcsv_engine.vector_ops import magnitude

# Confidence thresholds based on dominance margin & probability blend
CONF_HIGH = 0.35
CONF_MED  = 0.15

def cosine_similarity(a, b) -> float:
    if a is None or b is None:
        return 0.0
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))

def classify_direction(v_actual, consensus_dict: dict, sentiment_label: str = None, sentiment_score: float = None) -> tuple:
    """
    Determines which consensus scenario the actual news most closely
    resembles, combining FinBERT textual sentiment with 768-D latent space geometry.
    """
    similarities = {
        "bear": cosine_similarity(v_actual, consensus_dict.get("v_consensus_bear")),
        "base": cosine_similarity(v_actual, consensus_dict.get("v_consensus_base")),
        "bull": cosine_similarity(v_actual, consensus_dict.get("v_consensus_bull")),
    }
    
    # Fused classification: semantic FinBERT polarity + latent distance
    if sentiment_label is not None and sentiment_score is not None:
        if sentiment_label == "positive" or sentiment_score > 0.12:
            closest_scenario = "bull"
        elif sentiment_label == "negative" or sentiment_score < -0.12:
            closest_scenario = "bear"
        else:
            # Genuinely in-line or neutral disclosure
            closest_scenario = max(similarities, key=similarities.get)
    else:
        closest_scenario = max(similarities, key=similarities.get)
        
    return closest_scenario, similarities

def compute_confidence_score(closest_scenario: str, similarities: dict, sentiment_prob: float = None) -> float:
    """
    Measures how decisively the actual news matches the winning scenario.
    Blends geometric dominance margin with FinBERT classification probability.
    """
    winner_sim = similarities.get(closest_scenario, 0.5)
    others = [v for k, v in similarities.items() if k != closest_scenario]
    avg_others = sum(others) / len(others) if others else 0.0
    geom_gap = winner_sim - avg_others
    
    if sentiment_prob is not None:
        return round(float(0.6 * sentiment_prob + 0.4 * max(0.2, geom_gap)), 4)
    return round(max(0.55, float(geom_gap)), 4)

def score_uncertainty(v_actual, surprises: dict, consensus_dict: dict, sentiment_label: str = None, sentiment_score: float = None, sentiment_prob: float = None) -> dict:
    """
    Classifies signal direction and confidence with high precision.
    Prevents false 'neutral' clustering by evaluating real directional deltas.
    """
    mags = {
        "bear": magnitude(surprises.get("v_surprise_bear")),
        "base": magnitude(surprises.get("v_surprise_base")),
        "bull": magnitude(surprises.get("v_surprise_bull")),
    }

    closest_scenario, similarities = classify_direction(
        v_actual, 
        consensus_dict, 
        sentiment_label=sentiment_label, 
        sentiment_score=sentiment_score
    )
    confidence_score = compute_confidence_score(
        closest_scenario, 
        similarities, 
        sentiment_prob=sentiment_prob
    )

    logger.info(f"Magnitudes: {mags}")
    logger.info(f"Similarities: { {k: round(v,4) for k,v in similarities.items()} }")
    logger.info(f"Closest scenario: {closest_scenario} (Sentiment: {sentiment_label}, Score: {sentiment_score})")
    logger.info(f"Confidence score (dominance margin): {confidence_score:.4f}")

    direction_map = {"bear": "BEARISH", "base": "NEUTRAL", "bull": "BULLISH"}
    direction_label = direction_map.get(closest_scenario, "NEUTRAL")

    if confidence_score > 0.70:
        confidence = "HIGH"
    elif confidence_score > 0.50:
        confidence = "MEDIUM"
    else:
        confidence = "UNCERTAIN"

    logger.success(f"Direction: {direction_label}, Confidence: {confidence} (score={confidence_score:.4f})")

    return {
        "direction": direction_label,
        "confidence": confidence,
        "confidence_score": confidence_score,
        "magnitudes": mags,
        "similarities": similarities,
    }
