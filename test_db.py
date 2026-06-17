import os
import sys

# Force Python to recognize the root folder for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import db

print("Initiating MarketPulse AI Database Check...\n")

expected_tables = [
    "raw_articles",
    "market_regimes",
    "consensus_baselines",
    "embeddings",
    "trading_signals",
    "signal_outcome"
]

def run_diagnostics():
    all_passed = True
    try:
        for table in expected_tables:
            response = db.table(table).select("id").limit(1).execute()
            print(f"✅ [SUCCESS] Table '{table}' is live and accessible.")
    except Exception as e:
        all_passed = False
        print(f"❌ [FAILED] Error accessing table: {e}")
    
    if all_passed:
        print("\n🚀 ALL SYSTEMS GO: Your local environment is perfectly connected to Supabase!")

if __name__ == "__main__":
    run_diagnostics()