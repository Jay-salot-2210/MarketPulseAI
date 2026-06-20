import numpy as np
from loguru import logger
from vectorizer.hf_client import get_embedding


# FinBERT's limit is 512 tokens. We use words as a rough proxy
# (1 word ≈ 1.3 tokens on average), so we stay safely under the limit.
WORDS_PER_CHUNK = 350
OVERLAP_WORDS = 50


def chunk_text(text: str) -> list[str]:
    """
    Splits a long article into overlapping word chunks.
    Overlap prevents losing meaning that straddles a chunk boundary.

    Example: a 700-word article becomes 2 chunks of ~350 words each,
    with the last 50 words of chunk 1 repeated at the start of chunk 2.
    """
    words = text.split()

    # Short article — no need to chunk
    if len(words) <= WORDS_PER_CHUNK:
        return [text]

    chunks = []
    start = 0

    while start < len(words):
        end = start + WORDS_PER_CHUNK
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))

        # Move forward, but step back by OVERLAP_WORDS so chunks overlap
        start += (WORDS_PER_CHUNK - OVERLAP_WORDS)

    logger.info(f"Article split into {len(chunks)} chunks "
                f"(original length: {len(words)} words)")
    return chunks


def embed_article(text: str) -> list[float]:
    """
    Converts a full article into a single 768-dim vector (v_actual).

    Handles articles of any length by chunking, embedding each chunk,
    then mean-pooling all chunk vectors into one final vector.
    """

    if not text or not text.strip():
        raise ValueError("Cannot embed empty article text")

    chunks = chunk_text(text)

    # Embed every chunk separately
    chunk_embeddings = []
    for i, chunk in enumerate(chunks):
        logger.info(f"Embedding chunk {i + 1}/{len(chunks)}")
        embedding = get_embedding(chunk)
        chunk_embeddings.append(embedding)

    # If there was only 1 chunk, just return it directly
    if len(chunk_embeddings) == 1:
        return chunk_embeddings[0]

    # Multiple chunks — mean pool them into a single vector
    embeddings_array = np.array(chunk_embeddings)  # shape: (num_chunks, 768)
    pooled = embeddings_array.mean(axis=0)          # shape: (768,)

    final_vector = pooled.tolist()

    assert len(final_vector) == 768, (
        f"Pooled vector has wrong dimensions: {len(final_vector)}"
    )

    logger.success(f"Article embedded — pooled from {len(chunks)} chunks "
                   f"into 1 vector of {len(final_vector)} dimensions")

    return final_vector