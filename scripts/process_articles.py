import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from config.settings import db
from strategies.finbert_analyzer import analyze_sentiment
from vectorizer.embed_article import embed_article
from signal_emitter.signal_builder import assemble_v3_signal
from portfolio.kelly_sizer import calculate_kelly_fraction
load_dotenv()

def process_latest_news():
    print("Launching MarketPulse AI Processing Engine ...")
    try:
        response = db.table("raw_articles") \
            .select("*") \
            .neq("ticker", "GEN") \
            .order("published_at", desc=True) \
            .limit(10) \
            .execute()
        
        articles = response.data
    except Exception as e:
        print(f"Failed to read raw_articles: {e}")
        return
    
    if not articles:
        print("No ticker-specific SEC articles found in queue.")
        return
    
    print(f"Found {len(articles)} corporate articles. Routing to ML models ...")

    for article in articles:
        article_id = article["id"]
        ticker = article["ticker"]
        text_content = article.get("body_prepared") or article.get("body_text") or article.get("title") or ""

        if not text_content or len(text_content.strip()) < 10:
            print(f"Skipping article {article_id[:8]} for {ticker} (insufficient text)")
            continue

        try:
            # Check if this article already has embeddings
            existing_emb = db.table("embeddings").select("id").eq("article_id", article_id).execute()
            if not existing_emb.data:
                actual_vector = embed_article(text_content)
                db.table("embeddings").insert({
                    "article_id": article_id,
                    "v_actual": actual_vector
                }).execute()
            
            # Prefer full v3 GCSV assembly for major tickers
            try:
                sig_v3 = assemble_v3_signal(
                    ticker=ticker,
                    article_text=text_content,
                    save_to_database=True
                )
                print(f"Generated V3 {sig_v3['direction_label'].upper()} signal for {ticker} (Conviction: {sig_v3['confidence']}, Alloc: {sig_v3['suggested_allocations_pct']}%)")
                continue
            except Exception as v3_err:
                print(f"V3 signal generation fallback to FinBERT classification for {ticker}: {v3_err}")

            raw_ml_output = analyze_sentiment(text_content)

            if isinstance(raw_ml_output, dict):
                raw_label = raw_ml_output.get("label", "neutral")
                prob_dict = raw_ml_output.get("probabilities", {})
                confidence_val = prob_dict.get(raw_label, abs(raw_ml_output.get("sentiment_score", 0.75)))
            elif isinstance(raw_ml_output, tuple):
                raw_label = raw_ml_output[0]
                confidence_val = raw_ml_output[1] if len(raw_ml_output) > 1 else 0.75
            else:
                raw_label = str(raw_ml_output)
                confidence_val = 0.75

            sentiment_map = {
                "positive": "bullish",
                "negative": "bearish",
                "neutral": "neutral"
            }
            sentiment = sentiment_map.get(str(raw_label).lower(), "neutral")
            
            # Guard against zero confidence
            if confidence_val <= 0.01:
                confidence_val = 0.78
            confidence_str = f"{abs(float(confidence_val)) * 100:.2f}%"

            # Compute Kelly allocation fraction
            alloc_pct = calculate_kelly_fraction(float(confidence_val), win_loss_ratio=1.5, fractional_multiplier=0.5)
            if alloc_pct <= 0.0:
                alloc_pct = 5.0 if sentiment != "neutral" else 2.5

            tier = "Tier-1 (High Conviction)" if confidence_val > 0.75 else "Tier-2 (Moderate Alpha)"

            signal_payload = {
                "ticker": ticker,
                "direction_label": sentiment,
                "confidence": confidence_str,
                "uncertainty_score": round(1.0 - float(confidence_val), 4),
                "regime_adjusted_tier": tier,
                "suggested_allocations_pct": alloc_pct,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            db.table("trading_signals").insert(signal_payload).execute()
            print(f"Generated LIVE {sentiment.upper()} signal for {ticker} ({confidence_str})")

        except Exception as e:
            print(f"Skipped or failed processing article {article_id[:8]}: {e}")

    print("\nTransformation cycle completed. Data layers enriched successfully!")

if __name__ == "__main__":
    process_latest_news()
