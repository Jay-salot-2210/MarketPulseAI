import json 
from config.settings import db

def calculate_kelly_fraction(win_prob,win_loss_ratio=2.0,fractional_multiplier = 0.5):
    if win_prob <=0:
        return 0.0

    kelly_pct = win_prob - ((1.0 - win_prob)/win_loss_ratio)

    if kelly_pct<0:
        return 0.0

    return round((kelly_pct*fractional_multiplier)*100,2)

def run_portfolio_allocator():
    print("Initializing kelly criterion position sizer...")

    try:
        response = db.table("trading_signals")\
        .select("id, ticker, direction_label, confidence, suggested_allocations_pct")\
        .order("created_at",desc = True)\
        .limit(10)\
        .execute()

        signals = response.data
        if not signals:
            print("No signal found to allocate")
            return
        for signal in signals:
            ticker = signal["ticker"]
            if ticker == "GEN" or signal.get("suggested_allocations_pct") is not None:
                continue

            conf_str = signal.get("confidence", "50.0%").replace('%','')
            win_prob = float(conf_str)/100.0

            allocation_pct = calculate_kelly_fraction(win_prob,win_loss_ratio = 2.0)

            db.table("trading_signals")\
            .update({"suggested_allocations_pct": allocation_pct})\
            .eq("id",signal["id"])\
            .execute()

            print(f"{ticker} ({signal['direction_label'].upper()}): Allocated {allocation_pct}% of capital (Win Prob: {win_prob*100 :.1f}%)")

        print("\n Portfolio sizing complete. Capital allocated efficiently.")

    except Exception as e:
        print(f"Allocation failed: {e}")

if __name__ == "__main__":
    run_portfolio_allocator()