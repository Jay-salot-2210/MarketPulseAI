import os
from dotenv import load_dotenv
from config.settings import db
from strategies.finbert_analyzer import analyze_sentiment
from vectorizer.embed_article import embed_article
load_dotenv()

def process_latest_news():
    print("Launching MarketPulse AI Processing Engine ...")
    #left join because we wont fetch matching rows in the embeddings table
    try :
        response = db.table("raw_articles") \
            .select("*") \
            .neq("ticker","GEN") \
            .execute()
        
        articles = response.data
    except Exception as e:
        print(f"Failed to read raw_articles : {e}")
        return
    
    if not articles:
        print("No ticker-specific SEC articles found in queue.")
        return
    
    print(f"Found {len(articles)} corporate articles. Routing to ML models ...")

    for article in articles:
        article_id = article["id"]
        ticker = article["ticker"]
        text_content = article["body_prepared"]

        try:
            raw_ml_output = analyze_sentiment(text_content)

            if isinstance(raw_ml_output,tuple):
                raw_label = raw_ml_output[0]
                confidence_val = raw_ml_output[1] if len(raw_ml_output)>1 else 0.0
            elif isinstance(raw_ml_output,dict):
                raw_label = raw_ml_output.get("label",raw_ml_output.get("sentiment","neutral"))
                confidence_val = raw_ml_output.get("score",0.0)
            elif isinstance(raw_ml_output,str):
                raw_label = raw_ml_output
                confidence_val = 0.0
            
            sentiment_map={
                "positive":"bullish",
                "negative":"bearish",
                "neutral":"neutral"
            }
            sentiment = sentiment_map.get(str(raw_label).lower(),"neutral")
            confidence_str = f"{abs(float(confidence_val))*100:.2f}%"
            
            actual_vector = embed_article(text_content)

            embedding_payload ={
                "article_id":article_id,
                "v_actual":actual_vector
            }
            db.table("embeddings").insert(embedding_payload).execute()
            # print(f"Vectorized article {article_id[:8]}...")

            signal_payload = {
                "ticker":ticker,
                "direction_label":sentiment,
                "confidence":confidence_str,
                "uncertainty_score":0.15,
                "regime_adjusted_tier":"Tier-1"
            }
            db.table("trading_signals").insert(signal_payload).execute()
            print(f"Generated LIVE {sentiment.upper()} signal for {ticker}")

        except Exception as e:
            print(f"Skipped or processed article {article_id[:8]} :{e}")

    print("\n Transformation cycle completed. Data layers enriched succesfully!")

if __name__ == "__main__":
    process_latest_news()