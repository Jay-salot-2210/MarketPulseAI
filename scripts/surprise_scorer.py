import numpy as np
import json
from config.settings import db

def parse_vector(v):
    if isinstance(v, str):
        return np.array(json.loads(v))
    return np.array(v)

def calculate_cosine_similarity(v1,v2):
    dot_product = np.dot(v1,v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return dot_product / (norm_v1 * norm_v2)

def calculate_euclidean_distance(v1,v2):
    return np.linalg.norm(v1-v2)

def calculate_surprise_score(ticker:str):
    print(f"Calculating Hybrid Surprise score for {ticker}...")

    try:
        # fetching baseline
        res_baseline = db.table("consensus_baseline").select("v_consensus_base").eq("ticker",ticker).order("created_at",desc=True).limit(1).execute()
        if not res_baseline.data:return
        v_base = parse_vector(res_baseline.data[0]["v_consensus_base"])

        #fetch actual
        res_article = db.table("raw_articles").select("id,title").eq("ticker",ticker).order("published_at",desc= True).limit(1).execute()
        if not res_article.data:return
        article_title = res_article.data[0]["title"]
        res_actual = db.table("embeddings").select("v_actual").eq("article_id",res_article.data[0]["id"]).execute()
        if not res_actual.data :return
        v_actual = parse_vector(res_actual.data[0]["v_actual"])


        cos_sim = calculate_cosine_similarity(v_base,v_actual)
        euc_dist = calculate_euclidean_distance(v_base,v_actual)

        # Hybrid blend
        dir_surprise = (1.0-cos_sim)
        mag_surprise = min(euc_dist/15.0,1.0) #cap at 15 for scoring purposes

        hybrid_score = ((dir_surprise*0.6)+(mag_surprise*0.4))*100
        print(f"Latest Filing: {article_title}")
        print(f"Angle Match (Cosine):  {cos_sim:.4f}")
        print(f"Magnitude Diff (L2):   {euc_dist:.4f}")
        print(f"HYBRID SURPRISE:     {hybrid_score:.2f} / 100")
        
        if hybrid_score > 15.0:
            print(f"ACTION: High divergence detected! Generating Tier-1 Trade Signal.")
        else:
            print(f"ACTION: Priced in. No trade edge detected.")
        print("-" * 50)
        
    except Exception as e:
        print(f"Calculation failed for {ticker}: {e}")      

def run_scoring_engine():
    print("Launching AI vector surprise calculator...")
    print("="*50)
    target_tickers = ["AAPL","TSLA","MSFT"]

    for ticker in target_tickers:
        calculate_surprise_score(ticker)

if __name__ =="__main__":
    run_scoring_engine()