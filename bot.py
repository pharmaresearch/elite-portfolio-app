import yfinance as yf
import pandas as pd
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })
    print("Telegram response:", response.text)

print("🚀 Bot started")

# ===== MARKET =====
market_status = "UNKNOWN"

try:
    nifty = yf.download("^NSEI", period="3mo", progress=False)
    close = nifty["Close"]

    if len(close) >= 50:
        price = float(close.iloc[-1])
        ma50 = float(close.rolling(50).mean().iloc[-1])

        if price < ma50:
            market_status = "⚠️ BEARISH"
        else:
            market_status = "✅ BULLISH"
except Exception as e:
    print("Market error:", e)

# ===== STOCK LIST =====
stocks = [
    "HDFCBANK.NS","ICICIBANK.NS","LT.NS","ITC.NS",
    "TATAPOWER.NS","KPITTECH.NS","DIXON.NS"
]

results = []

# ===== SCAN =====
for ticker in stocks:
    try:
        data = yf.download(ticker, period="3mo", progress=False)

        if data.empty:
            continue

        close = data["Close"]

        if len(close) < 50:
            continue

        price = float(close.iloc[-1])
        ma20 = float(close.rolling(20).mean().iloc[-1])
        ma50 = float(close.rolling(50).mean().iloc[-1])

        momentum = price / ma20
        trend = ma20 / ma50
        strength = (price - ma50) / ma50

        score = (momentum*40)+(trend*30)+(strength*30)

        results.append({
            "ticker": ticker,
            "price": price,
            "score": score,
            "ma20": ma20
        })

    except Exception as e:
        print("Error:", ticker, e)

df = pd.DataFrame(results)

if df.empty:
    send_telegram(f"📊 Market: {market_status}\nNo trades found.")
    exit()

df = df.sort_values(by="score", ascending=False)
top3 = df.head(3)

message = f"📊 TOP STOCKS\nMarket: {market_status}\n\n"

for _, row in top3.iterrows():
    entry = round(row["ma20"], 2)
    sl = round(entry * 0.93, 2)
    target = round(entry * 1.12, 2)

    message += f"""
{row['ticker']}
₹{round(row['price'],2)}
Entry: {entry}
SL: {sl}
Target: {target}
"""

print(message)

send_telegram(message)

print("✅ Done")
