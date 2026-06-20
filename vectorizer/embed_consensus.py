from loguru import logger
from vectorizer.embed_article import embed_article


def embed_consensus_narratives(bear_text: str, base_text: str, bull_text: str) -> dict:
    """
    Embeds the three consensus scenario narratives (bear/base/bull)
    into three separate 768-dim vectors.

    Returns a dict:
        {
            "v_consensus_bear": [768 floats],
            "v_consensus_base": [768 floats],
            "v_consensus_bull": [768 floats]
        }

    These three vectors are the "expectation baselines" that
    v_actual will later be subtracted against (GCSV).
    """

    logger.info("Embedding BEAR consensus narrative...")
    v_bear = embed_article(bear_text)

    logger.info("Embedding BASE consensus narrative...")
    v_base = embed_article(base_text)

    logger.info("Embedding BULL consensus narrative...")
    v_bull = embed_article(bull_text)

    logger.success("All 3 consensus vectors generated ✓")

    return {
        "v_consensus_bear": v_bear,
        "v_consensus_base": v_base,
        "v_consensus_bull": v_bull,
    }