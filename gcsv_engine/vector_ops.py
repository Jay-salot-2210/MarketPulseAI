import numpy as np
from loguru import logger


def compute_surprise_vector(v_actual: list[float], v_consensus: list[float]) -> np.ndarray:
    """
    The core GCSV formula:
        v_surprise = v_actual - v_consensus

    Both inputs must be 768-dim vectors (lists of floats).
    Returns a numpy array (not a plain list) so we can do further
    math on it easily (norm, direction, etc.)
    """
    actual_arr = np.array(v_actual)
    consensus_arr = np.array(v_consensus)

    if actual_arr.shape != consensus_arr.shape:
        raise ValueError(
            f"Vector shape mismatch: v_actual has {actual_arr.shape}, "
            f"v_consensus has {consensus_arr.shape}"
        )

    v_surprise = actual_arr - consensus_arr
    return v_surprise


def compute_all_surprise_vectors(v_actual: list[float], consensus_dict: dict) -> dict:
    """
    Runs the GCSV subtraction against all 3 consensus scenarios.

    consensus_dict must have keys:
        "v_consensus_bear", "v_consensus_base", "v_consensus_bull"

    Returns a dict of numpy arrays:
        {
            "v_surprise_bear": ndarray,
            "v_surprise_base": ndarray,
            "v_surprise_bull": ndarray
        }
    """
    logger.info("Running GCSV subtraction against all 3 scenarios...")

    v_surprise_bear = compute_surprise_vector(v_actual, consensus_dict["v_consensus_bear"])
    v_surprise_base = compute_surprise_vector(v_actual, consensus_dict["v_consensus_base"])
    v_surprise_bull = compute_surprise_vector(v_actual, consensus_dict["v_consensus_bull"])

    logger.success("All 3 surprise vectors computed ✓")

    return {
        "v_surprise_bear": v_surprise_bear,
        "v_surprise_base": v_surprise_base,
        "v_surprise_bull": v_surprise_bull,
    }


def magnitude(v_surprise: np.ndarray) -> float:
    """
    Returns the magnitude (length) of a surprise vector.
    Bigger magnitude = bigger surprise.
    This is the Euclidean norm: sqrt(sum of squares of all 768 numbers).
    """
    return float(np.linalg.norm(v_surprise))


def direction(v_surprise: np.ndarray, positive_axis: np.ndarray) -> int:
    """
    Determines whether the surprise points in a "positive" (bullish)
    or "negative" (bearish) direction.

    positive_axis is a reference vector representing "clearly good news"
    (we'll define this properly later — for now this is a placeholder
    that uses the dot product sign).

    Returns: +1 (bullish), -1 (bearish), or 0 (perfectly neutral)
    """
    dot_product = np.dot(v_surprise, positive_axis)
    if dot_product > 0:
        return 1
    elif dot_product < 0:
        return -1
    else:
        return 0