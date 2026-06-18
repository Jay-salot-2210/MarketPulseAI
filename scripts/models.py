def analyze_market_sentiment(text_content:str) -> tuple[str,float]:
    """
    ML TASK 1: Determine if the news is bullish, bearish, or neutral.
    (Drop your HuggingFace/FinBERT logic here)
    """
    # Replace with actual ML inference
    import random
    direction = random.choice(["bullish", "bearish", "neutral"])
    confidence = round(random.uniform(70.0, 99.9), 2)
    
    return direction, confidence

def generate_text_embeddings(text_content : str)-> list[float]:
    """
    ML TASK 2: Convert the text into a 768-dimensional float array.
    (Drop your sentence-transformers logic here)
    """
    # Replace with actual vector generation   
    import random
    return [round(random.uniform(-1,1),4) for _ in range(768)]