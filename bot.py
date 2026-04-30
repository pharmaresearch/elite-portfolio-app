import yfinance as yf
import pandas as pd
import requests
import os
from datetime import datetime
import pytz
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    })
    print("Telegram sent:", response.status_code)

print("🚀 Market Scanner Bot Started - Running every 2 hours during market time")

# ====================== MAIN LOOP ======================
while True:
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    hour = now_ist.hour
    minute = now_ist.minute
    weekday = now_ist.weekday()

    # Market is open only Mon-Fri between 9:15 and 15:30
    is_weekday = weekday <= 4
    is_market_open = is_weekday and ((hour > 9 or (hour == 9 and minute >= 15)) and 
                                    (hour < 15 or (hour == 15 and minute <= 30)))

    if not is_market_open:
        print(f"[{now_ist.strftime('%H:%M')}] Market closed. Sleeping...")
        time.sleep(300)   # Check every 5 minutes when market is closed
        continue

    print(f"[{now_ist.strftime('%Y-%m-%d %H:%M')}] Market is OPEN → Starting scan")

    # ===== STOCK LIST (Updated with your new stocks) =====
    stocks = [
        "HDFCBANK.NS", "ICICIBANK.NS", "LT.NS", "ITC.NS",
        "TATAPOWER.NS", "KPITTECH.NS", "DIXON.NS",
        "SUVEN.NS", "SIGACHI.NS", "COHANCE.NS", "SUZLON.NS"
    ]

    results = []
    market_status = "✅ BULLISH"

    # Quick Nifty trend for market status
    try:
        nifty = yf.Ticker("^NSEI").history(period="5d")
        if not nifty.empty:
            price = float(nifty['Close'].iloc[-1])
            ma20 = float(nifty['Close'].rolling(20).mean().iloc[-1]) if len(nifty) >= 20 else price
            market_status = "⚠️ BEARISH" if price < ma20 else "✅ BULLISH"
    except:
        pass

    # ===== SCAN STOCKS =====
    for ticker in stocks:
        try:
            data = yf.download(ticker, period="3mo", progress=False, auto_adjust=True)
            if data.empty or len(data) < 50:
                continue

            close = data["Close"]
            price = float(close.iloc[-1])
            ma20 = float(close.rolling(20).mean().iloc[-1])
            ma50 = float(close.rolling(50).mean().iloc[-1])

            momentum = price / ma20
            trend = ma20 / ma50
            strength = (price - ma50) / ma50

            score = (momentum * 40) + (trend * 30) + (strength * 30)

            results.append({
                "ticker": ticker.replace(".NS", ""),
                "price": round(price, 2),
                "score": round(score, 4),
                "ma20": round(ma20, 2)
            })
        except Exception as e:
            print(f"Error with {ticker}: {e}")
            continue

    if not results:
        send_telegram("📊 Market Open\nNo valid data found for scanning.")
    else:
        df = pd.DataFrame(results)
        df = df.sort_values(by="score", ascending=False)
        top3 = df.head(3)

        message = f"""
📊 <b>TOP STOCK SIGNALS</b>

🕒 {now_ist.strftime('%Y-%m-%d %H:%M:%S')} IST
Market Trend: {market_status}

"""

        for _, row in top3.iterrows():
            entry = row["ma20"]
            sl = round(entry * 0.93, 2)
            target = round(entry * 1.12, 2)

            message += f"""
<b>{row['ticker']}</b>
Price : ₹{row['price']}
Entry ~ ₹{entry}
SL    : ₹{sl}
Target: ₹{target}
Score : {row['score']}
"""

        message += "\n⚠️ Not trading advice. Manage risk properly."

        send_telegram(message)
        print("✅ Scan completed and message sent")

    # Sleep for 2 hours (7200 seconds)
    print("⏳ Next scan in 2 hours...\n")
    time.sleep(7200)
