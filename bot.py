import yfinance as yf
import pandas as pd
import requests
import os
from datetime import datetime
import pytz  # Add this: pip install pytz

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    })
    print("Telegram:", response.text)

print("🚀 Telegram Market Scanner Bot Started")

# ===== PROPER IST TIME CHECK =====
ist = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(ist)
hour = now_ist.hour
minute = now_ist.minute
weekday = now_ist.weekday()  # 0=Mon ... 4=Fri, 5=Sat, 6=Sun

# Market is generally open Mon-Fri 09:15 to 15:30 IST
is_weekday = weekday < 5
is_trading_hours = (hour > 9 or (hour == 9 and minute >= 15)) and (hour < 15 or (hour == 15 and minute <= 30))

market_open = is_weekday and is_trading_hours

# ===== BETTER MARKET STATUS CHECK =====
market_status = "UNKNOWN"
try:
    # Use Ticker for more reliable info + recent price
    nifty = yf.Ticker("^NSEI")
    info = nifty.info
    hist = nifty.history(period="5d")
    
    if hist.empty:
        market_open = False
    else:
        price = float(hist['Close'].iloc[-1])
        close_series = hist['Close']
        
        if len(close_series) >= 50:
            ma50 = float(close_series.rolling(50).mean().iloc[-1])
            market_status = "⚠️ BEARISH" if price < ma50 else "✅ BULLISH"
        else:
            market_status = "✅ BULLISH"  # default if not enough data
except Exception as e:
    print(f"Market status check error: {e}")
    market_open = False  # fallback safe

# Weekend + after-hours override
if not is_weekday:
    market_open = False
    market_status = "🛑 WEEKEND"

print(f"Current IST: {now_ist.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Market Open: {market_open} | Status: {market_status}")

# ===== IF MARKET CLOSED =====
if not market_open:
    message = f"""
📊 <b>MARKET CLOSED</b>

🕒 {now_ist.strftime('%Y-%m-%d %H:%M:%S')} IST
Status: {market_status}

No live signals today.
Bot will check again in next session.
"""
    send_telegram(message)
    print("Market closed. Exiting.")
    exit()

# ===== STOCK LIST =====
stocks = [
    "HDFCBANK.NS", "ICICIBANK.NS", "LT.NS", "ITC.NS",
    "TATAPOWER.NS", "KPITTECH.NS", "DIXON.NS"
]

results = []

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

        if ma20 == 0 or ma50 == 0:
            continue

        momentum = price / ma20
        trend = ma20 / ma50
        strength = (price - ma50) / ma50

        # Weighted score (you can tune these weights)
        score = (momentum * 40) + (trend * 30) + (strength * 30)

        results.append({
            "ticker": ticker.replace(".NS", ""),
            "price": round(price, 2),
            "score": round(score, 4),
            "ma20": round(ma20, 2)
        })
    except Exception as e:
        print(f"Error scanning {ticker}: {e}")
        continue

if not results:
    send_telegram(f"📊 Market: {market_status}\n\nNo valid stocks found for scanning.")
    exit()

df = pd.DataFrame(results)
df = df.sort_values(by="score", ascending=False)
top3 = df.head(3)

# ===== BUILD MESSAGE =====
message = f"""
📊 <b>TOP STOCK SIGNALS</b>

🕒 {now_ist.strftime('%Y-%m-%d %H:%M:%S')} IST
Market: {market_status}

"""

for _, row in top3.iterrows():
    entry = row["ma20"]
    sl = round(entry * 0.93, 2)
    target = round(entry * 1.12, 2)

    message += f"""
<b>{row['ticker']}</b>
Price: ₹{row['price']}
Entry ~ ₹{entry}
SL: ₹{sl}
Target: ₹{target}
Score: {row['score']}
"""

message += "\n⚠️ This is not trading advice. Use at your own risk."

send_telegram(message)
print("✅ Scan completed and message sent")
