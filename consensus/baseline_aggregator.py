import yfinance as yf
from datetime import datetime,timezone
import json
from config.settings import db

def get_latest_market_regime():
    """fetch most recent macroeconomin regime from the database."""
    try:
        response = db.table("market_regimes").select("regime_label").order("created_at",desc = True).limit(1).execute()
        if response.data:
            return response.data[0]["regime_label"]
    except Exception as e:
        print(f"Could not fetch market regime , defaulting to Neutral :{e}")

    return "cautions neutral"

def fetch_wall_street_consensus(ticker:str):
    print(f"Fetching Wall street quantitative consensus for {ticker}...")
    stock =  yf.Ticker(ticker)
    info = stock.info

    forward_eps = info.get('forwardEps','N/A')
    trailing_eps = info.get('trailingEPS','N/A')
    target_price = info.get('targetMeanPrice','N/A')
    recommendation = info.get('recommendationKey','N/A').replace('_',' ')
    current_price = info.get('currentPrice','N/A')

    regime = get_latest_market_regime()

    consensus_payload ={
        "ticker":ticker,
        "market_regime":regime,
        "current_price":current_price,
        "target_mean_price":target_price,
        "forward_eps":forward_eps,
        "trailing_eps":trailing_eps,
        "wall_street_sentiment":recommendation,
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    print(f"{ticker} Baseline Anchor: EPS ${forward_eps} | Target: ${target_price} | Rec: {recommendation.upper()} | Regime: {regime}")
    # returning just for testing purposes in final we will pass to teammate
    return consensus_payload

def run_aggregator():
    print("Initializing Consensus Baseline Aggregator...")

    target_tickers = ["AAPL","TSLA","MSFT"]

    collected_baseline={}
    for ticker in target_tickers:
        collected_baseline[ticker] = fetch_wall_street_consensus(ticker)

    print("\n Payload ready for LLM translation:")
    print(json.dumps(collected_baseline, indent=2))

if __name__ == "__main__":
    run_aggregator()