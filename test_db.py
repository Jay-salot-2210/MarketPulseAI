from config.settings import db

def verify_consensus_table():
    print("🔍 Querying Table 3: consensus_baseline...\n")
    
    try:
        # We fetch everything except the massive vector columns to keep the terminal clean
        response = db.table("consensus_baseline") \
            .select("id, ticker, regime, analyst_options_divergence, created_at") \
            .order("created_at", desc=True) \
            .limit(3) \
            .execute()
            
        records = response.data
        
        if not records:
            print("⚠️ Table is empty. No records found!")
            return
            
        print(f"✅ Found {len(records)} recent records in the database:")
        print("-" * 50)
        
        for row in records:
            print(f"Ticker:     {row['ticker']}")
            print(f"Regime:     {row['regime']}")
            print(f"Divergence: {row['analyst_options_divergence']}")
            print(f"Record ID:  {row['id']}")
            print(f"Timestamp:  {row['created_at']}")
            print("-" * 50)
            
    except Exception as e:
        print(f"❌ Database query failed: {e}")

if __name__ == "__main__":
    verify_consensus_table()