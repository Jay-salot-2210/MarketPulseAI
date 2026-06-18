import os
import hashlib
import requests
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
        article_url = item.get('url', '').strip()
        url_hash = hashlib.md5(article_url.encode()).hexdigest()
        
        headline = item.get('headline', '').strip()
        summary = item.get('summary', '').strip()
        
        # Grab source safely
        news_source = item.get('source', '').strip()
        if not news_source:
            news_source = 'Finnhub'
        
        # Combined field for pipeline text intelligence
        body_prepared = f"{headline}. {summary}"
        
        ticker = item.get('related', 'GEN')
        if not ticker:
            ticker = 'GEN'
            
        # Build payload satisfying all NOT NULL constraints in your schema
        data = {
            "url_hash": url_hash,
            "ticker": ticker,
            "source": news_source,
            "title": headline,          
            "url": article_url,          
            "body_prepared": body_prepared
        }
        
        try:
            db.table("raw_articles").upsert(data).execute()
            inserted_count += 1
        except Exception as e:
            print(f"⚠️ Insertion failed for ticker {ticker}: {e}")
            
    print(f"✅ Successfully ingested {inserted_count} new articles into Supabase.")

if __name__ == "__main__":
    fetch_latest_news()