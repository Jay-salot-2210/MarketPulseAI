from fastapi import FastAPI , HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from config.settings import db

app = FastAPI(title="MarketPulse AI REST API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers = ["*"],
)

@app.get("/")
def health_check():
    return {"status":"MarketPulse Engine is Online"}

@app.get("/api/signals/latest")
def get_latest_signals(limit:int=5):
    """Fetches the latest trading signals with kelly allocations"""
    try:
        response = db.table("trading_signals") \
            .select("ticker, direction_label, confidence, suggested_allocations_pct, created_at")\
            .neq("ticker","GEN")\
            .order("created_at",desc=True)\
            .limit(limit)\
            .execute()
        return {"signals":response.data}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@app.get("/api/surprise-scores/{ticker}")
def get_surprise_scores(ticker:str):
    try:
        response = db.table("consensus_baseline")\
            .select("regime, analyst_options_divergence, created_at")\
            .eq("ticker",ticker.upper())\
            .order("created_at",desc=True) \
            .limit(1)\
            .execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    if not response.data:
        raise HTTPException(status_code = 404, detail=f"No baseline found for {ticker}")

    return {"consensus_baseline": response.data[0]}

if __name__=="__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)