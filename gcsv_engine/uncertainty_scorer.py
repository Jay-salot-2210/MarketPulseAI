import numpy as np
from loguru import logger
from gcsv_engine.vector_ops import magnitude


# Confidence thresholds based on dominance margin (winner vs runner-ups)
# These are starting points — will be tuned later using real backtest data
CONF_HIGH = 0.40
CONF_MED  = 0.15


def cosine_similarity(a, b) -> float:
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def classify_direction(v_actual, consensus_dict: dict) -> tuple:
    """
    Determines which consensus scenario the actual news most closely
    resembles, using cosine similarity.
    """
    similarities = {
        "bear": cosine_similarity(v_actual, consensus_dict["v_consensus_bear"]),
        "base": cosine_similarity(v_actual, consensus_dict["v_consensus_base"]),
        "bull": cosine_similarity(v_actual, consensus_dict["v_consensus_bull"]),
    }
    closest_scenario = max(similarities, key=similarities.get)
    return closest_scenario, similarities


def compute_confidence_score(closest_scenario: str, similarities: dict) -> float:
    """
    Measures how decisively the actual news matches the winning scenario
    compared to the other two. A bigger gap = more confident classification.

        confidence_score = winner_similarity - average(other two similarities)
    """
    winner_sim = similarities[closest_scenario]
    others = [v for k, v in similarities.items() if k != closest_scenario]
    avg_others = sum(others) / len(others)
    return winner_sim - avg_others


def score_uncertainty(v_actual, surprises: dict, consensus_dict: dict) -> dict:
    """
    Classifies signal direction and confidence.

    Direction  — which scenario (bear/base/bull) the news resembles most
    Confidence — how decisively it matches that scenario vs the other two
    """

    mags = {
        "bear": magnitude(surprises["v_surprise_bear"]),
        "base": magnitude(surprises["v_surprise_base"]),
        "bull": magnitude(surprises["v_surprise_bull"]),
    }

    closest_scenario, similarities = classify_direction(v_actual, consensus_dict)
    confidence_score = compute_confidence_score(closest_scenario, similarities)

    logger.info(f"Magnitudes: {mags}")
    logger.info(f"Similarities: { {k: round(v,4) for k,v in similarities.items()} }")
    logger.info(f"Closest scenario: {closest_scenario}")
    logger.info(f"Confidence score (dominance margin): {confidence_score:.4f}")

    direction_map = {"bear": "BEARISH", "base": "NEUTRAL", "bull": "BULLISH"}
    direction_label = direction_map[closest_scenario]

    if confidence_score > CONF_HIGH:
        confidence = "HIGH"
    elif confidence_score > CONF_MED:
        confidence = "MEDIUM"
    else:
        confidence = "UNCERTAIN"

    logger.success(f"Direction: {direction_label}, Confidence: {confidence} "
                   f"(score={confidence_score:.4f})")

    return {
        "direction": direction_label,
        "confidence": confidence,
        "confidence_score": confidence_score,
        "magnitudes": mags,
        "similarities": similarities,
    }