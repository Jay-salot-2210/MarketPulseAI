from transformers import AutoTokenizer, AutoModel
import torch
from loguru import logger

# This downloads ProsusAI/finbert (~440MB) the FIRST time you run it.
# After that, it's cached locally and loads instantly — no internet needed.
logger.info("Loading FinBERT model (first run downloads ~440MB)...")
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModel.from_pretrained("ProsusAI/finbert", use_safetensors=True)
model.eval()  # inference mode, not training mode
logger.success("FinBERT loaded and ready ✓")


def get_embedding(text: str) -> list[float]:
    """
    Converts text into a 768-dimensional vector using FinBERT,
    running locally on your CPU — no API calls needed.
    """

    # Tokenize the text (truncate to FinBERT's 512-token limit)
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True
    )

    # Run the model — no_grad means "don't track gradients", saves memory
    with torch.no_grad():
        outputs = model(**inputs)

    # outputs.last_hidden_state shape: (1, num_tokens, 768)
    # Mean-pool across tokens to get a single 768-dim vector
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze()

    embedding_list = embedding.tolist()

    assert len(embedding_list) == 768, (
        f"Expected 768 dimensions, got {len(embedding_list)}"
    )

    return embedding_list