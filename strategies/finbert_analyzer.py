from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from loguru import logger

# Note: this loads FinBERT a SECOND time, but with its classification
# head intact (instead of dropping it, like hf_client.py does for embeddings).
# This is a separate model instance because it serves a different purpose.
logger.info("Loading FinBERT sentiment classifier...")
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
model.eval()
logger.success("FinBERT sentiment classifier loaded ✓")

# FinBERT's label order (confirmed from the model's config)
LABELS = ["positive", "negative", "neutral"]


def analyze_sentiment(text: str) -> dict:
    """
    Reads financial text and returns a real sentiment value,
    replacing random.uniform mock data.

    Returns:
        {
            "label": "positive" | "negative" | "neutral",
            "sentiment_score": float between -1.0 and +1.0,
            "probabilities": {"positive": x, "negative": y, "neutral": z}
        }
    """

    if not text or not text.strip():
        raise ValueError("Cannot analyze empty text")

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True
    )

    with torch.no_grad():
        outputs = model(**inputs)

    # Convert raw model output (logits) into probabilities that sum to 1
    probabilities = torch.softmax(outputs.logits, dim=1).squeeze().tolist()

    prob_dict = {
        LABELS[i]: round(probabilities[i], 4)
        for i in range(len(LABELS))
    }

    # The label with the highest probability wins
    predicted_label = max(prob_dict, key=prob_dict.get)

    # Single sentiment score: positive prob minus negative prob
    # Range: -1.0 (fully negative) to +1.0 (fully positive)
    sentiment_score = round(prob_dict["positive"] - prob_dict["negative"], 4)

    logger.info(f"Sentiment: {predicted_label} (score={sentiment_score}) "
               f"for text: '{text[:60]}...'")

    return {
        "label": predicted_label,
        "sentiment_score": sentiment_score,
        "probabilities": prob_dict
    }