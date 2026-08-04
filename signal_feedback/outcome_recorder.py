import os
import yfinance as yf
from datetime import datetime , timezone
from dotenv import load_dotenv
from config.settings import db

load_dotenv()

def record_signal_outcomes():
    print("Launching Signal Self-Evaluation Feedback Loop...")
    try:
        response = db.table("trading_signals").select("*").order("created_at",desc = True).limit(10).execute()
        signals = response.data
    except Exception as e :
        print(f"Failed to read trading signals :{e}")
        return
    if not signals:
        print("NO active trading signal found to evaluate")
        return
    print(f"Evaluating realized return for {len(signals)} recent signals...")

    for signal in signals:
        signal_id = signal.get("id")
        ticker = signal.get("ticker")
        direction = signal.get("direction_label")

        if ticker == "GEN":
            print("Skipping general macro signal (GEN) - no individual asset price")
            continue

        print(f"Fetching current market price for {ticker}..")

        try:
            stock = yf.Ticker(ticker)
            todays_data = stock.history(period="1d")
            if todays_data.empty:
                print(f"Could not find market price data for {ticker}.")
                continue
            entry_price = float(todays_data['Open'].iloc[-1])
            current_price = float(todays_data['Close'].iloc[-1])

            # print(f"$ Current price for {ticker}: ${current_price : .2f}")
            # mock_entry_price = current_price * 0.985 if direction == "bullish" else current_price * 1.015
            realized_return = ((current_price - entry_price)/entry_price)*100
            is_correct = False
            if direction == "bullish" and realized_return>0:
                is_correct = True
            elif direction == "bearish" and realized_return<0:
                is_correct = True
            elif direction == "neutral" and abs(realized_return)<1.0:
                is_correct = True 

            print(f"Open: ${entry_price:.2f} | Close: ${current_price:.2f} | Return: {realized_return:.2f}%")
            # print(f"Signal ID {signal_id} Result : Return: {realized_return:.2f}% | Correct Prediction : {is_correct}")

            outcome_payload={
                "signal_id":signal_id,
                "horizon": "24h",
                "accuracy_score":1.0 if is_correct else 0.0,
                "ci_covered":True
            }

            db.table("signal_outcome").insert(outcome_payload).execute()
            print(f"Recorded 24h outcome for {ticker} | Accuracy: {outcome_payload['accuracy_score']}")

        except Exception as e:
            err_msg = str(e).lower()
            if "duplicated" in err_msg or "23505" in err_msg:
                print(f"Outcome already recorded for signal {signal_id[:8]}")
            else:
                print(f"Evaluation failed for signal on {ticker} :{e}")

if __name__ == "__main__":
    record_signal_outcomes()
