import os
from dotenv import load_dotenv
from config.settings import db
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce , QueryOrderStatus

load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

trading_client = TradingClient(ALPACA_API_KEY,ALPACA_SECRET_KEY,paper=True)

def execute_pending_trades():
    print("Launching Alpaca execution engine ...")

    try:
        response = db.table("trading_signals").select("*").order("created_at",desc =True).limit(5).execute()
        signals = response.data
    except Exception as e:
        print(f"Falied to read trading signals{e}")
        return
    if not signals:
        print("No trading signals found.")
        return
    
    seen_tickers = set()
    unique_signals =[]
    for signal in signals:
        ticker = signal["ticker"]
        if ticker not in seen_tickers:
            seen_tickers.add(ticker)
            unique_signals.append(signal)

    for signal in signals:
        ticker = signal["ticker"]
        direction = signal["direction_label"]
        qty = 1 

        if direction == "neutral":
            print(f"Signal for {ticker} is NEUTRAL. No execution required.")
            continue

        try:
            order_filter = GetOrdersRequest(
                status = QueryOrderStatus.OPEN,
                symbols = [ticker]
            )
            open_orders = trading_client.get_orders(filter=order_filter)

            if open_orders:
                print(f"Found active open orders for {ticker}. Clearing path to prevent wash trades ...")
                for order in open_orders:
                    trading_client.cancel_order_by_id(order.id)
                    
            if direction == "bullish":
                order_data = MarketOrderRequest(
                    symbol = ticker,
                    qty = qty,
                    side = OrderSide.BUY,
                    time_in_force = TimeInForce.DAY
                )
                trading_client.submit_order(order_data = order_data)
                print(f"Executed BUY order for {qty} share(s) of {ticker}")

            elif direction == "bearish":
                order_data = MarketOrderRequest(
                    symbol = ticker,
                    qty=qty,
                    side = OrderSide.SELL,
                    time_in_force = TimeInForce.DAY
                )
                trading_client.submit_order(order_data=order_data)
                print(f"Executed SELL order for {qty} share(s) of {ticker}")

        except Exception as e:
            print(f"Failed to execute trade for {ticker} :{e}")
        

if __name__ == "__main__":
    execute_pending_trades()