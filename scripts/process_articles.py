import os
import random
from dotenv import load_dotenv
from config.settings import db

load_dotenv()

def process_latest_news():
    print("Launching MarketPulse AI Processing Engine ...")
    #left join because we wont fetch matching rows in the embeddings table
    try :
        response = db.table("raw_articles").select("id, ticker, title, body_prepared").limit(10).execute()
        articles = response.data
    except Exception as e:
        print(f"Failed to read raw_articles : {e}")
        return
    if not articles:
        print("No new articles found requiring processing.")
        return
    print(f"Found {len(articles)} article. Executing transformation pipeline ...")

    for article in articles:
        article_id = article["id"]
        ticker = article["ticker"]

        sentiment = random.choice(["bullish","bearish","neutral"])
        confidence_percentage = f"{random.uniform(70,99)}%"

        mock_768_vector = [round(random.uniform(-1,1),4) for _ in range(768)]

        try:
            embedding_payload={
                "article_id" : article_id,
                "v_actual": mock_768_vector
            }            
            db.table("embeddings").insert(embedding_payload).execute()
            print(f"Vectorized article {article_id[:8]}...")
            signal_payload = {
                "ticker":ticker,
                "direction_label":sentiment,
                "confidence":confidence_percentage,
                "uncertainty_score":round(random.uniform(0.0,0.5),2),
                "regime_adjusted_tier":"Tier-1"
            }
            db.table("trading_signals").insert(signal_payload).execute()
            print(f"Generated {sentiment.upper()} signal for {ticker}")

        except Exception as e:
            print(f"Transformation failed for article {article_id[:8]} :{e}")

    print("\n Transformation cycle complated. Data layers enriched succesfully!")

if __name__ == "__main__":
    process_latest_news()