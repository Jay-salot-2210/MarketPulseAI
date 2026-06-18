import os
import hashlib
import requests
from dotenv import load_dotenv
from config.settings import db

load_dotenv()
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

def fetch_latest_news():
    print("Initiating Finnhub Data Extraction..")
    url = f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200 :
        print(f"Failed to fetch news : {response.text}")
        return
    news_items = response.json()
    inserted_count = 0

    for item in news_items[:15]:
        url_hash = hashlib.md5(item['url'].encode()).hexdigest()
        headline = item.get('headline','').strip()
        summary = item.get('summary','').strip()

        body_prepared = f"{headline}.{summary}"

        ticker = item.get('related','GEN')
        if not ticker:
            ticker = 'GEN'
        data = {
            "url_hash" : url_hash,
            "ticker" : ticker,
            "body_prepared":body_prepared
        }
        try:
            db.table("raw_articles").upsert(data).execute()
            inserted_count +=1
        except Exception as e :
            pass

    print(f"Successfully ingested {inserted_count} new articles into Supabase.")

if __name__ == "__main__":
    fetch_latest_news()