import os
import hashlib
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
from config.settings import db

# Load environment variables
load_dotenv()
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

def fetch_latest_news():
    print("Initiating Finnhub Data Extraction...")
    url = f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_API_KEY}"
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ Failed to fetch news: {response.text}")
        return

    news_items = response.json()
    inserted_count = 0
    
    # Process the top 15 most recent articles
    for item in news_items[:15]: 
        # 1. URL Hash (Matches schema)
        article_url = item.get('url', '').strip()
        url_hash = hashlib.md5(article_url.encode()).hexdigest()
        
        # 2. Title (Matches schema)
        title = item.get('headline', '').strip()
        
        # 3. Body Prepared (Matches schema)
        summary = item.get('summary', '').strip()
        body_prepared = f"{title}. {summary}"
        
        # 4. Source (Matches schema)
        source = item.get('source', '').strip()
        if not source:
            source = 'Finnhub'
        
        # 5. Ticker (Matches schema)
        ticker = item.get('related', '')
        if not ticker:
            ticker = 'GEN'
            
        # 6. Published At (Matches schema - required 'timestamptz')
        unix_time = item.get('datetime')
        if unix_time:
            # Convert Finnhub's UNIX time to PostgreSQL timestamptz
            published_at = datetime.fromtimestamp(unix_time, tz=timezone.utc).isoformat()
        else:
            published_at = datetime.now(timezone.utc).isoformat()
            
        # Payload mapped 1:1 with your provided SQL schema
        data = {
            "url_hash": url_hash,
            "ticker": ticker,
            "source": source,
            "title": title,
            "body_prepared": body_prepared,
            "published_at": published_at
        }
        
        try:
            db.table("raw_articles").upsert(data).execute()
            inserted_count += 1
        except Exception as e:
            print(f"⚠️ Insertion failed for ticker {ticker}: {e}")
            
    print(f"✅ Successfully ingested {inserted_count} new articles into Supabase.")

if __name__ == "__main__":
    fetch_latest_news()