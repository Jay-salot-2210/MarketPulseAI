import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("CRITICAL: Supabase credentials are missing. Check your .env file.")

# Initialize the global Supabase client
# Other files will simply run: from config.settings import db
db: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# API KEYS
# ==========================================
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

# ==========================================
# SYSTEM FEATURE FLAGS & MODEL PATHS
# ==========================================
# This flag lets Role 1 easily switch to the fine-tuned model once training is done
USE_FINETUNED_MODEL = False 
HF_MODEL_REPO = "ProsusAI/finbert" # Default base model

# ==========================================
# GCSV & SURPRISE THRESHOLDS
# ==========================================
# Base thresholds for the Signal Scanner (Pipeline C)
SURPRISE_THRESHOLD_HIGH = 0.40
SURPRISE_THRESHOLD_MEDIUM = 0.25
SURPRISE_THRESHOLD_LOW = 0.15

# Transcript Divergence Limit (Innovation 3)
THRESH_HIGH_DIVERGENCE = 0.25