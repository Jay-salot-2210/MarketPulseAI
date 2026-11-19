import re
import requests
import hashlib
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from config.settings import db

def fetch_edgar_8k(ticker):
    print(f"Fetching SEC EDGAR 8-K filings for {ticker} via RSS Feed...")
    
    # The Official SEC RSS/Atom Feed: specifically designed for automated scraping
    url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=8-K&owner=exclude&count=10&output=atom"
    
    # The SEC still requires the Honest Bot header, but they are much more forgiving here
    headers = {
        "User-Agent": "MarketPulseAI jaykalpeshsalot@gmail.com" 
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"SEC API rejected the request. Status: {response.status_code}")
            return
            
        # Parse the XML Atom Feed
        root = ET.fromstring(response.content)
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = root.findall('atom:entry', namespace)
        
        if not entries:
            print(f" No recent 8-K filings found for {ticker}.")
            return
            
        for entry in entries[:3]:  # Grab the latest 3 filings
            title = entry.find('atom:title', namespace).text
            link = entry.find('atom:link', namespace).attrib['href']
            # filing_date = entry.find('atom:updated', namespace).text[:10]
            updated_str = entry.find('atom:updated',namespace).text
            try:
                published_dt = datetime.fromisoformat(updated_str.replace('Z','+00:00')).isoformat()
            except Exception:
                published_dt = datetime.now(timezone.utc).isoformat()
            
            summary_tag = entry.find('atom:summary', namespace)
            raw_summary = summary_tag.text if summary_tag is not None else "8-K Material Event Filing"
            clean_summary = re.sub(r'<[^>]+>', ' ', raw_summary)
            clean_summary = re.sub(r'\s+', ' ', clean_summary).strip()
            summary_text = clean_summary if clean_summary else f"SEC 8-K Material Filing for {ticker}"
            
            # Extract the unique SEC Accession Number to use as our database ID
            filing_id = entry.find('atom:id', namespace).text.split(':')[-1]

            article_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, filing_id))
            url_hash_val = hashlib.sha256(link.encode('utf-8')).hexdigest()

            article_payload = {
                "id": article_uuid,
                "url_hash" : url_hash_val,
                "ticker": ticker,
                "source":"SEC EDGAR",
                "body_text":summary_text,
                "title": f"SEC 8-K: {title}",
                "body_prepared": f"{summary_text} For full details, see: {link}",
                "published_at":published_dt
            }
            
            # Insert into Supabase
            try:
                db.table("raw_articles").insert(article_payload).execute()
                print(f" Ingested official filing: {title[:60]}...")
            except Exception as e:
                err_msg = str(e).lower()
                if "duplicate" in err_msg or "unique constraint" in err_msg or "23505" in err_msg:
                    print(f"⏭️ Skipped {filing_id} (Already exists in database)")
                else:
                    print(f"Insert failed for {filing_id}:{e}")
                
    except Exception as e:
        print(f"EDGAR Fetch Failed: {e}")

def run_edgar_pipeline():
    print("Initializing Institutional Data Pipeline (RSS Bypass Mode)...")
    
    # We test with the biggest, most actively filed tickers
    target_tickers = ["AAPL", "TSLA", "MSFT"]
    
    for ticker in target_tickers:
        fetch_edgar_8k(ticker)

if __name__ == "__main__":
    run_edgar_pipeline()