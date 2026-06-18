from models import analyze_market_sentiment , generate_text_embeddings

def run_local_test():
    print("Initiating local ML sandbox test...\n")
    sample_text = "The Federal Reserve announced a surprise interest rate cut today, sending tech stocks soaring while bond yield plummeted."
    print(f"Testing Article :'{sample_text}'\n")
    direction, confidence = analyze_market_sentiment(sample_text)
    print(f"Sentiment Output :{direction.upper()} (Confidence :{confidence}%)")
    vector = generate_text_embeddings(sample_text)
    print(f"Vector Output : Array of length{len(vector)}")
    print(f"Sample dimension: {vector[:5]}...\n")
    if len(vector) == 768:
        print("Success : Vector matches the required 768 dimension for the database!")
    else:
        print("Error : Vector is not 768 dimension")

if __name__ == "__main__":
    run_local_test()