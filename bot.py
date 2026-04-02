import yfinance as yf
import pandas as pd
import requests
import os

# ================= TELEGRAM =================
BOT_TOKEN = os.getenv("8512585881:AAFEDRdPE-lH70oGLgtrEHkhgBgONOLFY0Q")
CHAT_ID = os.getenv("5522893777")

def send_telegram(message):
    url = f"https://api.telegram.org/bot8512585881:AAFEDRdPE-lH70oGLgtrEHkhgBgONOLFY0Q/sendMessage"
    requests.post(url, data={"5522893777": CHAT_ID, "text": message})

print("🚀 Running Automated Elite Engine...\n")

# ================= MARKET =================
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
except:
    pass

# ================= STOCK LIST =================
stocks = [
    "HDFCBANK.NS","ICICIBANK.NS","LT.NS","ITC.NS","TATAPOWER.NS",
    "ABB.NS","KPITTECH.NS","DIXON.NS","IRFC.NS","IRCTC.NS",
    "KALYANKJIL.NS","CLEAN.NS","SUZLON.NS"
]

results = []

# ================= SCAN =================
for ticker in stocks:
    try:
        data = yf.download(ticker, period="3mo", progress=False)
        close = data["Close"]

        if len(close) < 50:
            continue

        price = float(close.iloc[-1])
        ma20 = float(close.rolling(20).mean().iloc[-1])
        ma50 = float(close.rolling(50).mean().iloc[-1])

        momentum = price / ma20
        trend = ma20 / ma50
        strength = (price - ma50) / ma50

        score = (momentum*40) + (trend*30) + (strength*30)

        if market_status == "⚠️ BEARISH" and momentum < 1.02:
            continue

        results.append({
            "ticker": ticker,
            "price": price,
            "score": score,
            "ma20": ma20
        })

    except:
        continue

df = pd.DataFrame(results)

if df.empty:
    message = f"📊 Market: {market_status}\nNo opportunities today."
    send_telegram(message)

else:
    df = df.sort_values(by="score", ascending=False)
    top3 = df.head(3)

    total_capital = 4000000

    top3["weight"] = top3["score"] / top3["score"].sum()
    top3["allocation"] = (top3["weight"] * total_capital).round(0)

    # ===== REBALANCING =====
    previous = ["HDFCBANK.NS", "ICICIBANK.NS"]  # update manually initially
    current = list(top3["ticker"])

    to_sell = [s for s in previous if s not in current]
    to_buy = [s for s in current if s not in previous]

    message = f"📊 TOP 3 STOCKS\nMarket: {market_status}\n\n"

    for _, row in top3.iterrows():
        entry = round(row["ma20"], 2)
        sl = round(entry * 0.93, 2)
        target = round(entry * 1.12, 2)

        message += f"""
{row['ticker']}
₹{round(row['price'],2)}
Alloc: ₹{int(row['allocation'])}

Entry: {entry} | SL: {sl} | Target: {target}
"""

    message += "\n🔁 REBALANCING:\n"

    for s in to_sell:
        message += f"SELL: {s}\n"

    for s in to_buy:
        message += f"BUY: {s}\n"

    send_telegram(message)

print("✅ Done!")
