import uuid
from config.settings import db
from consensus.baseline_aggregator import fetch_wall_street_consensus
from vectorizer.embed_article import embed_article

def generate_and_store_consensus(ticker:str):
    print(f"Generating semantic consensus narratives for {ticker}...")

    stats = fetch_wall_street_consensus(ticker)

    # Mansi will connect here onwards right now static for testing purposes
    # For now, we format deterministic strings so you can test the vectorizer and database.

    base_text = f"{ticker} is expected to report an EPS of ${stats['forward_eps']} in a {stats['market_regime']} market. Wall street target is ${stats['target_mean_price']} with a {stats['wall_street_sentiment']} rating. This re[resent the zero surprise baseline."
    bull_text = f"{ticker} significantly beat exceptions, surpassing the EPS of ${stats['forward_eps']}. Guidance was raised above the ${stats['target_mean_price']} target in a {stats['market_regime']} enviroment."
    bear_text = f"{ticker} missed estimates , falling short of the ${stats['forward_eps']} EPS. Guidance was lowered below the ${stats['target_mean_price']} target amid a {stats['market_regime']} enviroment."
    options_text = f"Options market pricing for {ticker} implies standard expected volatility heading into earnings."

    try:
        print("Vectorizing synthetic narratives into 768-dimension space...")
        v_base = embed_article(base_text)
        v_bull = embed_article(bull_text)
        v_bear = embed_article(bear_text)
        v_options = embed_article(options_text)

        baseline_payload={
            "id":str(uuid.uuid4()),
            "ticker":ticker,
            "regime":stats['market_regime'],
            "v_consensus_base":v_base,
            "v_consensus_bear":v_bear,
            "v_consensus_options":v_options,
            "analyst_options_divergence":0.05 #mock divergence metric 
        }

        db.table("consensus_baseline").insert(baseline_payload).execute()
        print(f"Successfully locked {ticker} consensus baseline into database!")

    except Exception as e:
        print(f"Failed to generate or store consensus for {ticker} :{e}")

def run_narrative_engine():
    print("Launching Narrative Generation engine...")
    target_tickers = ["AAPL","TSLA","MSFT"]

    for ticker in target_tickers:
        generate_and_store_consensus(ticker)

if __name__=="__main__":
    run_narrative_engine()