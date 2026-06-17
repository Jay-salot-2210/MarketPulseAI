import os
import json
import asyncio
import httpx
import websockets
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="MarketPulse AI Webhook Receiver")

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# Make sure to update this with your actual GitHub repo path
GITHUB_REPO = "JaySalot/Market_Pulse_AI" 

async def trigger_github_action():
    """Fires a workflow_dispatch event to wake up the news ingestion pipeline."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/ingest_news.yml/dispatches"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"ref": "main"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        if response.status_code == 204:
            print("Successfully triggered GitHub Action: ingest_news.yml")
        else:
            print(f"Failed to trigger Action: {response.status_code} - {response.text}")

async def listen_to_finnhub():
    """Maintains a resilient websocket connection to the live news feed."""
    websocket_url = f"wss://ws.finnhub.io?token={FINNHUB_API_KEY}"
    
    while True:
        try:
            async with websockets.connect(websocket_url) as ws:
                print("Connected to Finnhub WebSocket.")
                # Example: Subscribing to general news updates or specific high-volume tracking symbols
                await ws.send(json.dumps({"type": "subscribe", "symbol": "BINANCE:BTCUSDT"}))
                
                while True:
                    message = await ws.recv()
                    data = json.loads(message)
                    if data.get("type") == "news":
                        print("Live breaking news detected! Triggering pipeline...")
                        await trigger_github_action()
                        
        except Exception as e:
            print(f"WebSocket connection dropped: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

@app.on_event("startup")
async def startup_event():
    """Launches the background websocket worker daemon immediately upon app launch."""
    asyncio.create_task(listen_to_finnhub())

@app.get("/")
def health_check():
    return {"status": "MarketPulse AI Webhook Receiver is active and listening."}