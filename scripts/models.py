import sys
import os

# Make sure Python can find your vectorizer and strategies folders
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.finbert_analyzer import analyze_sentiment
from vectorizer.embed_article import embed_article


def analyze_market_sentiment(text_content: str) -> tuple[str, float]:
    """
    ML TASK 1: Determine if the news is bullish, bearish, or neutral.
    Uses real FinBERT sentiment classification.
    """
    result = analyze_sentiment(text_content)

    label_map = {
        "positive": "bullish",
        "negative": "bearish",
        "neutral":  "neutral"
    }
    direction  = label_map[result["label"]]
    confidence = round(result["probabilities"][result["label"]] * 100, 2)

    return direction, confidence


def generate_text_embeddings(text_content: str) -> list[float]:
    """
    ML TASK 2: Convert text into a 768-dimensional float array.
    Uses real FinBERT embeddings.
    """
    return embed_article(text_content)